#!/usr/bin/env python3
"""IP Address Calculator

Supports IPv4/IPv6 addresses and CIDR networks (e.g. 192.168.1.10/24).

Usage:
    python ip_calculator.py                    # interactive mode
    python ip_calculator.py 8.8.8.8 10.0.0.5/24 2001:db8::1
    python ip_calculator.py 192.168.0.0/24 --subnets 26
"""

import argparse
import ipaddress
import sys


def ipv4_class(ip: ipaddress.IPv4Address) -> str:
    first = int(ip) >> 24
    if first < 128:
        return "A"
    if first < 192:
        return "B"
    if first < 224:
        return "C"
    if first < 240:
        return "D (multicast)"
    return "E (reserved)"


def classify(ip) -> str:
    """Return a human-readable category for the address."""
    checks = [
        ("Loopback", ip.is_loopback),
        ("Link-local", ip.is_link_local),
        ("Multicast", ip.is_multicast),
        ("Unspecified", ip.is_unspecified),
        ("Reserved", ip.is_reserved),
        ("Private", ip.is_private),
        ("Global (public)", ip.is_global),
    ]
    return next((name for name, flag in checks if flag), "Unknown")


def print_section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def row(label: str, value) -> None:
    print(f"{label:<22}: {value}")


def show_address(ip) -> None:
    print_section("IP Address Information")
    row("IP Address", ip)
    row("IP Version", f"IPv{ip.version}")
    row("Category", classify(ip))
    row("Is Private", ip.is_private)
    row("Is Global", ip.is_global)
    row("Is Loopback", ip.is_loopback)
    row("Is Link-local", ip.is_link_local)
    row("Is Multicast", ip.is_multicast)
    row("Is Reserved", ip.is_reserved)

    print_section("Representations")
    row("Integer", int(ip))
    row("Hex", hex(int(ip)))
    if ip.version == 4:
        row("Binary", ".".join(f"{o:08b}" for o in ip.packed))
        row("Class", ipv4_class(ip))
    else:
        row("Exploded", ip.exploded)
        row("Compressed", ip.compressed)
        if ip.ipv4_mapped:
            row("IPv4-mapped", ip.ipv4_mapped)
    row("Reverse DNS pointer", ip.reverse_pointer)


def show_network(net, subnet_prefix: int | None = None) -> None:
    print_section("Network Information")
    row("Network", net)
    row("Network address", net.network_address)
    row("Prefix length", f"/{net.prefixlen}")
    row("Netmask", net.netmask)
    if net.version == 4:
        row("Wildcard mask", net.hostmask)
        row("Broadcast", net.broadcast_address)
    else:
        row("Last address", net.broadcast_address)
    row("Total addresses", f"{net.num_addresses:,}")

    if net.version == 4:
        usable = max(net.num_addresses - 2, 0) if net.prefixlen < 31 else net.num_addresses
        row("Usable hosts", f"{usable:,}")
        if usable and net.prefixlen < 31:
            row("First host", net.network_address + 1)
            row("Last host", net.broadcast_address - 1)

    if subnet_prefix is not None:
        print_section(f"Subnets (/{subnet_prefix})")
        if subnet_prefix <= net.prefixlen or subnet_prefix > net.max_prefixlen:
            print(f"Prefix must be between /{net.prefixlen + 1} and /{net.max_prefixlen}.")
            return
        count = 2 ** (subnet_prefix - net.prefixlen)
        row("Subnet count", f"{count:,}")
        for i, sub in enumerate(net.subnets(new_prefix=subnet_prefix)):
            if i >= 16:
                print(f"... and {count - 16:,} more")
                break
            print(f"  {i + 1:>2}. {sub}")


def analyze(text: str, subnet_prefix: int | None = None) -> bool:
    text = text.strip()
    if not text:
        return False
    try:
        if "/" in text:
            iface = ipaddress.ip_interface(text)
            show_address(iface.ip)
            show_network(iface.network, subnet_prefix)
        else:
            show_address(ipaddress.ip_address(text))
        return True
    except ValueError as exc:
        print(f"\nInvalid input '{text}': {exc}")
        return False


def interactive() -> None:
    print("=== IP Address Calculator ===")
    print("Enter an IP (8.8.8.8) or CIDR (192.168.1.10/24). Type 'q' to quit.")
    while True:
        try:
            text = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if text.lower() in {"q", "quit", "exit"}:
            break
        analyze(text)


def main() -> int:
    parser = argparse.ArgumentParser(description="IP address & network calculator")
    parser.add_argument("addresses", nargs="*", help="IPs or CIDR networks")
    parser.add_argument("--subnets", type=int, metavar="PREFIX",
                        help="split CIDR network into /PREFIX subnets")
    args = parser.parse_args()

    if not args.addresses:
        interactive()
        return 0

    ok = all([analyze(a, args.subnets) for a in args.addresses])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
