
ports = {
    20: "FTP Data",
    21: "FTP Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP Server",
    68: "DHCP Client",
    80: "HTTP",
    110: "POP3",
    123: "NTP",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP Alternative"
}

print("=== Common Network Ports ===")

for port, service in sorted(ports.items()):
    print(f"Port {port:<5} : {service}")

search = input("\nEnter a port number to search: ")

if search.isdigit():
    port = int(search)
    print("Service:", ports.get(port, "Unknown or not listed"))
else:
    print("Please enter a valid port number.")
