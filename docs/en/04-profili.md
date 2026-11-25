# Profiles and forbidden flags

🌐 [Italiano](../04-profili.md) · **English** · [中文](../zh/04-profili.md)

| Profile | What it does | Noise | Root |
|---|---|---|---|
| `risolvi` | A records with the answer. | low | no |
| `solo-ip` | IP addresses only, one per line. | low | no |
| `record` | A, AAAA and CNAME. | low | no |
| `servizi` | MX, TXT and NS. | low | no |
| `arricchito` | A with CDN and ASN. | low | no |
| `codici` | All response codes, errors included. | low | no |
| `jsonl` | A, AAAA and CNAME in JSON. | low | no |
| `prudente` | With thread and rate limits. | low | no |

`dnsx-cli profili` prints the exact flags of each one.

## What each profile does

**risolvi** (`-a -re -silent`). A records with the answer. The normal step after subdomain enumeration: which ones actually resolve?

**solo-ip** (`-a -ro -silent`). IP addresses only, one per line. When the output needs to feed a tool that only wants IPs, for example a port scan.

**record** (`-a -aaaa -cname -re -silent`). A, AAAA and CNAME. To also see IPv6 and aliases (a CNAME to a third-party service is a takeover hint).

**servizi** (`-mx -txt -ns -re -silent`). MX, TXT and NS. Mail, ownership checks (SPF, DKIM) and name servers.

**arricchito** (`-a -re -cdn -asn -silent`). A with CDN and ASN. To see which hosts sit behind a CDN: scanning them isn't scanning the client.

**codici** (`-rcode noerror,nxdomain,servfail,refused -re -silent`). All response codes, errors included. To tell a nonexistent name (NXDOMAIN) apart from a server that refuses or fails.

**jsonl** (`-a -aaaa -cname -j -or`). A, AAAA and CNAME in JSON. To process the result with other tools.

**prudente** (`-a -re -t 50 -rl 50 -retry 2 -silent`). With thread and rate limits. When you don't want to saturate the resolver or get rate-limited.

## Passing flags by hand

Everything you write after `--` goes to dnsx, after the profile flags, provided it is not on the forbidden list. The check is case-insensitive and accepts both `-flag valore` and `-flag=valore`, with one or two dashes.

```sh
dnsx-cli lancia risolvi www.example.org --scope scope.toml -- -timeout 5
```

## Forbidden list

| Flag | Why |
|---|---|
| `-l`, `-list` | targets come from the file validated against the scope |
| `-d`, `-domain`, `-w`, `-wordlist` | subdomain brute force generates names the scope has never seen |
| `-o`, `-output` | output is handled by dnsx-cli |
| `-resume` | resumes a run that didn't go through the scope check |
| `-up`, `-update` | updating the program is done separately, not inside an authorized run |

## What the filter does not do

It is not a sandbox. If you want to get around it you can, for example by calling `dnsx` directly. It is there to stop mistakes and bad habits, not an attacker who already has access to your terminal. If you need a forbidden flag for an activity agreed with the client, use dnsx directly and record the decision in the engagement.
