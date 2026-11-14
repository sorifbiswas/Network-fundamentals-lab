
import ipaddress

print("=== IP Address Calculator ===")

ip_input = input("Enter an IP address: ")

try:
    ip = ipaddress.ip_address(ip_input)

    print("\nIP Address Information")
    print("----------------------")
    print("IP Address:", ip)
    print("IP Version:", ip.version)
    print("Is Private:", ip.is_private)
    print("Is Global:", ip.is_global)
    print("Is Loopback:", ip.is_loopback)

except ValueError:
    print("Invalid IP address!")
