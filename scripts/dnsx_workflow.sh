#!/usr/bin/env bash
# dnsx_workflow_v3.sh
# Riferimento operativo completo. Solo target autorizzati.
# Le note spiegano il perché e il quando, non solo il cosa.

INPUT_LIST="<FILE_CON_SOTTODOMINI>"
DOMAIN="<DOMINIO_TARGET>"
OUT="<PREFISSO_OUTPUT>"

# ---------------------------------------------------------------
# Prerequisiti
# dnsx usa resolver di default (Cloudflare, Google, Quad9).
# Non richiede API key. Non richiede browser.
# Default record: A. Default rcode mostrato: solo NOERROR.
# ---------------------------------------------------------------
dnsx -version

# ---------------------------------------------------------------
# Risoluzione base
# Il default è query A record. L'output mostra solo NOERROR.
# NXDOMAIN, SERVFAIL, REFUSED vengono silenziosamente scartati.
# ---------------------------------------------------------------

# Solo i domini che risolvono.
dnsx -l "$INPUT_LIST" -silent -o "$OUT.resolved.txt"

# Con risposta DNS accanto al dominio. -re = resp.
dnsx -l "$INPUT_LIST" -a -re -silent -o "$OUT.resolved_with_ip.txt"

# Solo la risposta (IP), senza il dominio. -ro = resp-only.
dnsx -l "$INPUT_LIST" -a -ro -silent -o "$OUT.ips_only.txt"

# ---------------------------------------------------------------
# Query multi-record
# Ogni flag di record è indipendente. Puoi passarne più di uno.
# ---------------------------------------------------------------

# A + AAAA + CNAME.
dnsx -l "$INPUT_LIST" -a -aaaa -cname -re -silent -o "$OUT.multi_record.txt"

# Record per servizi: MX, TXT, NS.
dnsx -l "$INPUT_LIST" -mx -txt -ns -re -silent -o "$OUT.services.txt"

# ---------------------------------------------------------------
# Wildcard filtering: il cuore di dnsx
#
# Il problema: su domini con wildcard DNS, ogni sottodominio
# inventato risolve (es. random.domain.com -> 1.2.3.4).
# Questo inquina la pipeline con falsi positivi.
#
# Meccanismo: dnsx tiene traccia di quanti sottodomini puntano
# allo stesso IP. Se superano la soglia (-wt, default 5),
# scatta il filtering iterativo.
#
# ATTENZIONE: quando usi -wd, gli altri flag DNS vengono
# IGNORATI. La documentazione ufficiale dice: "The DNS record
# flag cannot be used when using wildcard filtering".
# Per questo la pipeline usa DUE passaggi separati.
# ---------------------------------------------------------------

# Passaggio 1: filtra i wildcard. -wd richiede il dominio base.
# Nessun flag di record qui, altrimenti vengono ignorati.
dnsx -l "$INPUT_LIST" -wd "$DOMAIN" -silent -o "$OUT.no_wildcard.txt"

# Soglia personalizzata: -wt 10 significa "filtra solo se
# 10+ sottodomini puntano allo stesso IP". Default 5.
dnsx -l "$INPUT_LIST" -wd "$DOMAIN" -wt 10 -silent -o "$OUT.no_wildcard_strict.txt"

# Nota: -aw (auto-wildcard) esiste in alcune versioni, ma non è
# documentato nella usage ufficiale ProjectDiscovery.
# Se lo usi, verifica la tua versione con dnsx -h. Non è
# combinabile con -wd.

# ---------------------------------------------------------------
# Rcode: vedere anche i fallimenti
# Di default dnsx mostra solo NOERROR.
# Per vedere NXDOMAIN, SERVFAIL, REFUSED, devi passare -rcode esplicito.
# ---------------------------------------------------------------

# Tutti gli rcode, per debug.
dnsx -l "$INPUT_LIST" -rcode noerror,nxdomain,servfail,refused -re -silent -o "$OUT.all_rcode.txt"

# Solo i fallimenti: utile per capire problemi di risoluzione.
dnsx -l "$INPUT_LIST" -rcode servfail,refused -re -silent -o "$OUT.failures.txt"

# ---------------------------------------------------------------
# Arricchimento: CDN e ASN
# -cdn mostra il nome della CDN. -asn mostra l'ASN dell'IP.
# Utile per capire se un host è dietro un CDN o esposto.
# ---------------------------------------------------------------
dnsx -l "$INPUT_LIST" -a -re -cdn -asn -silent -o "$OUT.enriched.txt"

# ---------------------------------------------------------------
# Output strutturato
# -j produce JSONL. -or rimuove la risposta DNS raw dal JSON.
# Nota: la documentazione ufficiale avverte che quando usi
# il wildcard filtering, "only json output is supported"
# (in alcune versioni/guide). Se usi -wd con
# output non-JSON, verifica il comportamento sulla tua versione.
# ---------------------------------------------------------------
dnsx -l "$INPUT_LIST" -a -aaaa -cname -j -or -o "$OUT.jsonl"

# ---------------------------------------------------------------
# Rate limiting
# -t: thread concorrenti (default 100).
# -rl: richieste DNS al secondo (default -1 = illimitato).
# -retry: tentativi per query (default 2).
# ---------------------------------------------------------------

# Conservativo per resolver pubblici.
dnsx -l "$INPUT_LIST" -a -re -t 50 -rl 50 -retry 2 -silent -o "$OUT.safe.txt"

# Custom resolver: se i default sono bloccati o lenti.
# dnsx -l "$INPUT_LIST" -a -re -r /path/to/resolvers.txt -silent -o "$OUT.custom_resolver.txt"

# ---------------------------------------------------------------
# Pipeline: subfinder → dnsx (wildcard filtering) → dnsx (resolve) → httpx → nuclei
#
# Due passaggi dnsx sono necessari perché -wd ignora i flag
# di record. Prima filtra i wildcard, poi risolve.
# ---------------------------------------------------------------

# Step 1: subfinder produce sottodomini.
subfinder -d "$DOMAIN" -all -silent -o /tmp/subs.txt

# Step 2: dnsx filtra i wildcard. Solo -wd, nessun record flag.
if command -v dnsx &>/dev/null; then
    dnsx -l /tmp/subs.txt -wd "$DOMAIN" -silent -o /tmp/no_wildcard.txt
else
    echo "dnsx non installato. Salto wildcard filtering."
    cp /tmp/subs.txt /tmp/no_wildcard.txt
fi

# Step 3: dnsx risolve i sottodomini filtrati.
# Ora posso usare -a perché -wd non è più attivo.
if command -v dnsx &>/dev/null; then
    dnsx -l /tmp/no_wildcard.txt -a -re -silent -o /tmp/resolved.txt
else
    echo "dnsx non installato. Salto risoluzione."
    cp /tmp/no_wildcard.txt /tmp/resolved.txt
fi

# Step 4: httpx verifica quali host sono vivi.
if command -v httpx &>/dev/null; then
    cat /tmp/resolved.txt | httpx -silent -sc -title -td -mc 200,401,403 -o /tmp/live_hosts.txt
else
    echo "httpx non installato. Pipeline fermata."
    exit 1
fi

# Step 5: nuclei sui vivi.
if command -v nuclei &>/dev/null; then
    nuclei -l /tmp/live_hosts.txt -severity critical,high -exclude-tags intrusive,dos -jsonl -o /tmp/nuclei_findings.jsonl
else
    echo "nuclei non installato. Pipeline fermata a live_hosts.txt."
fi

# ---------------------------------------------------------------
# Comando di produzione completo
# Risoluzione con arricchimento, rate limitato, output JSONL.
# ---------------------------------------------------------------
dnsx -l "$INPUT_LIST" \
  -a -aaaa -cname \
  -re -cdn -asn \
  -t 50 -rl 50 -retry 2 \
  -j -or \
  -o "$OUT.jsonl"
