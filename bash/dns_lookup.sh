
#!/bin/bash

echo "=== DNS Lookup Tool ==="

read -p "Enter a domain name: " domain

if [ -z "$domain" ]; then
    echo "Please enter a domain name."
    exit 1
fi

echo ""
echo "=== DNS Information ==="

if command -v dig >/dev/null 2>&1; then
    dig "$domain" A +noall +answer
elif command -v nslookup >/dev/null 2>&1; then
    nslookup "$domain"
else
    echo "Install dnsutils or use an available DNS lookup tool."
fi
