# Profili e flag vietati

🌐 **Italiano** · [English](en/04-profili.md) · [中文](zh/04-profili.md)

| Profilo | Cosa fa | Rumore | Root |
|---|---|---|---|
| `risolvi` | Record A con la risposta. | basso | no |
| `solo-ip` | Solo gli indirizzi IP, uno per riga. | basso | no |
| `record` | A, AAAA e CNAME. | basso | no |
| `servizi` | MX, TXT e NS. | basso | no |
| `arricchito` | A con CDN e ASN. | basso | no |
| `codici` | Tutti i codici di risposta, anche gli errori. | basso | no |
| `jsonl` | A, AAAA e CNAME in JSON. | basso | no |
| `prudente` | Con limiti su thread e frequenza. | basso | no |

`dnsx-cli profili` stampa i flag esatti di ciascuno.

## Cosa fa ciascun profilo

**risolvi** (`-a -re -silent`). Record A con la risposta. Il passo normale dopo l'enumerazione dei sottodomini: chi risolve davvero?

**solo-ip** (`-a -ro -silent`). Solo gli indirizzi IP, uno per riga. Quando l'output deve alimentare un tool che vuole solo IP, per esempio una scansione di porte.

**record** (`-a -aaaa -cname -re -silent`). A, AAAA e CNAME. Per vedere anche IPv6 e gli alias (un CNAME verso un servizio terzo è un indizio di takeover).

**servizi** (`-mx -txt -ns -re -silent`). MX, TXT e NS. Posta, verifiche di proprieta' (SPF, DKIM) e name server.

**arricchito** (`-a -re -cdn -asn -silent`). A con CDN e ASN. Per capire quali host stanno dietro una CDN: scansionarli non significa scansionare il cliente.

**codici** (`-rcode noerror,nxdomain,servfail,refused -re -silent`). Tutti i codici di risposta, anche gli errori. Per distinguere un nome inesistente (NXDOMAIN) da un server che rifiuta o fallisce.

**jsonl** (`-a -aaaa -cname -j -or`). A, AAAA e CNAME in JSON. Per elaborare il risultato con altri strumenti.

**prudente** (`-a -re -t 50 -rl 50 -retry 2 -silent`). Con limiti su thread e frequenza. Quando non vuoi saturare il resolver o farti limitare.

## Passare flag a mano

Tutto ciò che scrivi dopo `--` finisce a dnsx, dopo i flag del profilo, a patto che non sia nell'elenco dei vietati. Il confronto non distingue maiuscole e minuscole e accetta sia `-flag valore` sia `-flag=valore`, con uno o due trattini.

```sh
dnsx-cli lancia risolvi www.example.org --scope scope.toml -- -timeout 5
```

## Elenco dei vietati

| Flag | Perché |
|---|---|
| `-l`, `-list` | i target arrivano dal file validato contro lo scope |
| `-d`, `-domain`, `-w`, `-wordlist` | il brute force di sottodomini genera nomi che lo scope non ha mai visto |
| `-o`, `-output` | l'output lo gestisce dnsx-cli |
| `-resume` | riprende un lancio che non è passato dal controllo dello scope |
| `-up`, `-update` | l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato |

## Quello che il filtro non fa

Non è una sandbox. Se vuoi aggirarlo ci riesci, per esempio chiamando `dnsx` direttamente. Serve a fermare gli errori e le abitudini sbagliate, non un malintenzionato che ha già accesso al tuo terminale. Se ti serve un flag vietato per un'attività concordata con il cliente, usa dnsx direttamente e annota la scelta nell'ingaggio.
