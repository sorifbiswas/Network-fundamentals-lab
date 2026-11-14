
import ipaddress

print("=== Subnet Calculator ===")

network_input = input("Enter network (example: 192.168.1.0/24): ")

try:
    network = ipaddress.ip_network(network_input, strict=False)

    print("\nSubnet Information")
    print("------------------")
    print("Network Address:", network.network_address)
    print("Broadcast Address:", network.broadcast_address)
    print("Subnet Mask:", network.netmask)
    print("Prefix Length:", network.prefixlen)
    print("Total Addresses:", network.num_addresses)

    if network.version == 4:
        print("Usable Hosts:", max(0, network.num_addresses - 2))

except ValueError:
    print("Invalid network address!")

