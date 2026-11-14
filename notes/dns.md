
# DNS Fundamentals

DNS stands for Domain Name System.

DNS translates domain names into IP addresses.

## Example

When you visit:

www.google.com

Your device uses DNS to find the corresponding IP address.

## Common DNS Record Types

| Record | Purpose |
|---|---|
| A | Maps a name to an IPv4 address |
| AAAA | Maps a name to an IPv6 address |
| CNAME | Creates an alias |
| MX | Specifies mail servers |
| NS | Identifies authoritative name servers |
| TXT | Stores text information |
| PTR | Used for reverse DNS lookup |

## DNS Lookup Commands

Linux:

```bash
nslookup example.com
```

Or:

```bash
dig example.com
```

## Why DNS Matters in Cybersecurity

- DNS monitoring
- Domain investigation
- Security analysis
- Troubleshooting

## Practice Questions

1. What is DNS?
2. What is an A record?
3. What is an MX record?
4. What is reverse DNS?
