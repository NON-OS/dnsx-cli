# 配置与被禁标志

🌐 [Italiano](../04-profili.md) · [English](../en/04-profili.md) · **中文**

> ⚠️ 本页为机器翻译草稿，正式发布前需母语者校对。

| 配置 | 作用 | 噪声 | Root |
|---|---|---|---|
| `risolvi` | A 记录及其响应。 | 低 | 否 |
| `solo-ip` | 仅 IP 地址，每行一个。 | 低 | 否 |
| `record` | A、AAAA 和 CNAME。 | 低 | 否 |
| `servizi` | MX、TXT 和 NS。 | 低 | 否 |
| `arricchito` | A 记录，并附带 CDN 和 ASN。 | 低 | 否 |
| `codici` | 所有响应码，包括错误。 | 低 | 否 |
| `jsonl` | A、AAAA 和 CNAME，以 JSON 输出。 | 低 | 否 |
| `prudente` | 带线程数和频率限制。 | 低 | 否 |

`dnsx-cli profili` 会打印每个配置的具体标志。

## 各配置的作用

**risolvi** (`-a -re -silent`). A 记录及其响应。 子域名枚举之后的常规步骤：哪些才真正可解析？

**solo-ip** (`-a -ro -silent`). 仅 IP 地址，每行一个。 当输出需要提供给只接受 IP 的工具时，例如端口扫描。

**record** (`-a -aaaa -cname -re -silent`). A、AAAA 和 CNAME。 用于同时查看 IPv6 和别名（指向第三方服务的 CNAME 是子域接管的线索）。

**servizi** (`-mx -txt -ns -re -silent`). MX、TXT 和 NS。 邮件、域名所有权验证（SPF、DKIM）和域名服务器。

**arricchito** (`-a -re -cdn -asn -silent`). A 记录，并附带 CDN 和 ASN。 用于了解哪些主机位于 CDN 之后：扫描它们并不等于扫描客户。

**codici** (`-rcode noerror,nxdomain,servfail,refused -re -silent`). 所有响应码，包括错误。 用于区分不存在的域名（NXDOMAIN）和拒绝或失败的服务器。

**jsonl** (`-a -aaaa -cname -j -or`). A、AAAA 和 CNAME，以 JSON 输出。 用于使用其他工具处理结果。

**prudente** (`-a -re -t 50 -rl 50 -retry 2 -silent`). 带线程数和频率限制。 当你不想让解析器过载或被限速时使用。

## 手动传入标志

`--` 之后写的所有内容都会追加在配置标志之后传给 dnsx，前提是不在被禁清单中。比对时不区分大小写，`-flag valore` 和 `-flag=valore` 两种写法都能识别，一个或两个短横线均可。

```sh
dnsx-cli lancia risolvi www.example.org --scope scope.toml -- -timeout 5
```

## 被禁标志清单

| 标志 | 原因 |
|---|---|
| `-l`, `-list` | 目标来自经过作用域校验的文件 |
| `-d`, `-domain`, `-w`, `-wordlist` | 子域名暴力破解会生成作用域中从未出现过的名称 |
| `-o`, `-output` | 输出由 dnsx-cli 管理 |
| `-resume` | 会恢复一次未经过作用域检查的任务 |
| `-up`, `-update` | 程序更新应单独进行，而不是在一次授权任务中进行 |

## 过滤器做不到的事

它不是沙箱。想绕过它并不难，比如直接调用 `dnsx`。它的作用是拦住失误和坏习惯，而不是拦住一个已经能访问你终端的恶意人员。如果某项与客户约定好的活动需要用到被禁标志，请直接使用 dnsx，并在项目记录中注明这一选择。
