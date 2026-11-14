
#!/bin/bash

echo "=== Network Interface Information ==="

if command -v ip >/dev/null 2>&1; then
    ip -br addr
else
    echo "The ip command is not installed."
fi

echo ""
echo "=== Default Route ==="

ip route show default
