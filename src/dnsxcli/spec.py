"""Descrizione di dnsx: profili, flag vietati, formato dei risultati."""

from __future__ import annotations

from dnsxcli.profili import Profilo
from dnsxcli.risultati import Voce, righe_json

NOME = "dnsx"
BINARIO = "dnsx"
DESCRIZIONE = "Risoluzione DNS massiva con scope validato, dry-run di default e audit a catena di hash."
MODO = "host"
PASSA = ("file", "-l")
UNO_EXTRA: tuple[str, ...] = ()  # solo ffuf lavora "un comando per target"
USCITA = "-o"
VERSIONE = ("-version",)
RICONOSCI = "current version"  # testo che il binario vero stampa con {VERSIONE}: distingue da programmi omonimi
INSTALLAZIONE = (
    "Kali/Debian: sudo apt install dnsx. Ovunque con Go: go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
)
SEGRETI: frozenset[str] = frozenset()
GRUPPO = "Esito DNS"
NOTA_ATTIVITA = (
    "interroga i resolver DNS e, a cascata, i name server del dominio: il lavoro è visibile ai loro amministratori."
)

PROFILI = {
    p.nome: p
    for p in (
        Profilo("risolvi", "Record A con la risposta.", ("-a", "-re", "-silent"), "basso",
                "Il passo normale dopo l'enumerazione dei sottodomini: chi risolve davvero?"),
        Profilo("solo-ip", "Solo gli indirizzi IP, uno per riga.", ("-a", "-ro", "-silent"), "basso",
                "Quando l'output deve alimentare un tool che vuole solo IP, per esempio una scansione di porte."),
        Profilo("record", "A, AAAA e CNAME.", ("-a", "-aaaa", "-cname", "-re", "-silent"), "basso",
                "Per vedere anche IPv6 e gli alias (un CNAME verso un servizio terzo è un indizio di takeover)."),
        Profilo("servizi", "MX, TXT e NS.", ("-mx", "-txt", "-ns", "-re", "-silent"), "basso",
                "Posta, verifiche di proprieta' (SPF, DKIM) e name server."),
        Profilo("arricchito", "A con CDN e ASN.", ("-a", "-re", "-cdn", "-asn", "-silent"), "basso",
                "Per capire quali host stanno dietro una CDN: scansionarli non significa scansionare il cliente."),
        Profilo("codici", "Tutti i codici di risposta, anche gli errori.",
                ("-rcode", "noerror,nxdomain,servfail,refused", "-re", "-silent"), "basso",
                "Per distinguere un nome inesistente (NXDOMAIN) da un server che rifiuta o fallisce."),
        Profilo("jsonl", "A, AAAA e CNAME in JSON.", ("-a", "-aaaa", "-cname", "-j", "-or"), "basso",
                "Per elaborare il risultato con altri strumenti.", uscita="jsonl"),
        Profilo("prudente", "Con limiti su thread e frequenza.",
                ("-a", "-re", "-t", "50", "-rl", "50", "-retry", "2", "-silent"), "basso",
                "Quando non vuoi saturare il resolver o farti limitare."),
    )
}  # fmt: skip

VIETATI = {
    "l": "i target arrivano dal file validato contro lo scope",
    "list": "i target arrivano dal file validato contro lo scope",
    "d": "il brute force di sottodomini genera nomi che lo scope non ha mai visto",
    "domain": "il brute force di sottodomini genera nomi che lo scope non ha mai visto",
    "w": "il brute force di sottodomini genera nomi che lo scope non ha mai visto",
    "wordlist": "il brute force di sottodomini genera nomi che lo scope non ha mai visto",
    "o": "l'output lo gestisce dnsx-cli",
    "output": "l'output lo gestisce dnsx-cli",
    "resume": "riprende un lancio che non è passato dal controllo dello scope",
    "up": "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato",
    "update": "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato",
}

ESEMPI_VIETATI = [["-l", "x.txt"], ["-d", "example.org"], ["-w", "parole.txt"], ["-o", "x"], ["-resume"]]
ESEMPI_AMMESSI = [["-retry", "3"], ["-t", "20"]]


def voci(testo: str) -> list[Voce]:
    out = []
    for r in righe_json(testo):
        if isinstance(r, dict):
            host = str(r.get("host", "")).lower()
            if host:
                out.append(Voce(host, host, str(r.get("status_code", ""))))
        else:
            host = r.split()[0].lower()
            out.append(Voce(host, r))
    return out


# -- lingua -------------------------------------------------------------------
# Testi tradotti, generati da l10n/. L'italiano resta quello definito sopra.
_TR_TESTI: dict[str, dict[str, str]] = {
    "en": {
        "descrizione": "Bulk DNS resolution with a validated scope, dry-run by default and a hash-chained audit.",
        "nota_attivita": "it queries DNS resolvers and, in turn, the domain's name servers: the work is visible to their administrators.",
        "installazione": "Kali/Debian: sudo apt install dnsx. Anywhere with Go: go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
        "gruppo": "DNS result",
    },
    "zh": {
        "descrizione": "大规模 DNS 解析，带作用域校验、默认 dry-run 以及哈希链审计。",
        "nota_attivita": "查询 DNS 解析器，并进而查询该域名的域名服务器：这些动作对它们的管理员是可见的。",
        "installazione": "Kali/Debian：sudo apt install dnsx。任何装了 Go 的环境：go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
        "gruppo": "DNS 结果",
    },
}
_TR_PROFILI: dict[str, dict[str, list[str]]] = {
    "en": {
        "risolvi": [
            "A records with the answer.",
            "The normal step after subdomain enumeration: which ones actually resolve?",
        ],
        "solo-ip": [
            "IP addresses only, one per line.",
            "When the output needs to feed a tool that only wants IPs, for example a port scan.",
        ],
        "record": [
            "A, AAAA and CNAME.",
            "To also see IPv6 and aliases (a CNAME to a third-party service is a takeover hint).",
        ],
        "servizi": ["MX, TXT and NS.", "Mail, ownership checks (SPF, DKIM) and name servers."],
        "arricchito": [
            "A with CDN and ASN.",
            "To see which hosts sit behind a CDN: scanning them isn't scanning the client.",
        ],
        "codici": [
            "All response codes, errors included.",
            "To tell a nonexistent name (NXDOMAIN) apart from a server that refuses or fails.",
        ],
        "jsonl": ["A, AAAA and CNAME in JSON.", "To process the result with other tools."],
        "prudente": [
            "With thread and rate limits.",
            "When you don't want to saturate the resolver or get rate-limited.",
        ],
    },
    "zh": {
        "risolvi": ["A 记录及其响应。", "子域名枚举之后的常规步骤：哪些才真正可解析？"],
        "solo-ip": ["仅 IP 地址，每行一个。", "当输出需要提供给只接受 IP 的工具时，例如端口扫描。"],
        "record": ["A、AAAA 和 CNAME。", "用于同时查看 IPv6 和别名（指向第三方服务的 CNAME 是子域接管的线索）。"],
        "servizi": ["MX、TXT 和 NS。", "邮件、域名所有权验证（SPF、DKIM）和域名服务器。"],
        "arricchito": ["A 记录，并附带 CDN 和 ASN。", "用于了解哪些主机位于 CDN 之后：扫描它们并不等于扫描客户。"],
        "codici": ["所有响应码，包括错误。", "用于区分不存在的域名（NXDOMAIN）和拒绝或失败的服务器。"],
        "jsonl": ["A、AAAA 和 CNAME，以 JSON 输出。", "用于使用其他工具处理结果。"],
        "prudente": ["带线程数和频率限制。", "当你不想让解析器过载或被限速时使用。"],
    },
}
_TR_VIETATI: dict[str, dict[str, str]] = {
    "en": {
        "i target arrivano dal file validato contro lo scope": "targets come from the file validated against the scope",
        "il brute force di sottodomini genera nomi che lo scope non ha mai visto": "subdomain brute force generates names the scope has never seen",
        "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato": "updating the program is done separately, not inside an authorized run",
        "l'output lo gestisce dnsx-cli": "output is handled by dnsx-cli",
        "riprende un lancio che non è passato dal controllo dello scope": "resumes a run that didn't go through the scope check",
    },
    "zh": {
        "i target arrivano dal file validato contro lo scope": "目标来自经过作用域校验的文件",
        "il brute force di sottodomini genera nomi che lo scope non ha mai visto": "子域名暴力破解会生成作用域中从未出现过的名称",
        "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato": "程序更新应单独进行，而不是在一次授权任务中进行",
        "l'output lo gestisce dnsx-cli": "输出由 dnsx-cli 管理",
        "riprende un lancio che non è passato dal controllo dello scope": "会恢复一次未经过作用域检查的任务",
    },
}
_ORIGINALI = (DESCRIZIONE, NOTA_ATTIVITA, INSTALLAZIONE, GRUPPO, PROFILI, VIETATI)


def applica_lingua(lingua: str) -> None:
    """Passa testi, profili e motivi dei flag vietati alla lingua scelta. Ripartendo
    sempre dagli originali italiani, chiamarla più volte non accumula niente."""
    global DESCRIZIONE, NOTA_ATTIVITA, INSTALLAZIONE, GRUPPO, PROFILI, VIETATI
    from dataclasses import replace

    DESCRIZIONE, NOTA_ATTIVITA, INSTALLAZIONE, GRUPPO, PROFILI, VIETATI = _ORIGINALI
    testi = _TR_TESTI.get(lingua)
    if not testi:
        return
    DESCRIZIONE = testi["descrizione"] or DESCRIZIONE
    NOTA_ATTIVITA = testi["nota_attivita"] or NOTA_ATTIVITA
    INSTALLAZIONE = testi["installazione"] or INSTALLAZIONE
    GRUPPO = testi["gruppo"] or GRUPPO
    prof = _TR_PROFILI.get(lingua, {})
    PROFILI = {
        n: replace(p, descrizione=prof[n][0] or p.descrizione, quando=prof[n][1] or p.quando) if n in prof else p
        for n, p in PROFILI.items()
    }
    viet = _TR_VIETATI.get(lingua, {})
    VIETATI = {k: viet.get(v, v) for k, v in VIETATI.items()}
