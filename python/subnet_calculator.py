#!/usr/bin/env python3
"""Subnet Calculator

Usage:
    python subnet_calculator.py                          # interactive mode
    python subnet_calculator.py 192.168.1.0/24
    python subnet_calculator.py 192.168.1.0/24 --split 26
    python subnet_calculator.py 10.0.0.0/16 --hosts 500
    python subnet_calculator.py 10.0.0.0/16 --vlsm 200 50 20 2
    python subnet_calculator.py 192.168.1.0/24 --contains 192.168.1.77
    python subnet_calculator.py 192.168.1.0/24 --json
"""

import argparse
import ipaddress
import json
import math
import sys

MAX_LIST = 32  # cap on how many subnets we print


def usable_hosts(net) -> int:
    """Usable host count, with correct handling of /31, /32 (and IPv6)."""
    if net.version == 6:
        return net.num_addresses
    if net.prefixlen == 32:
        return 1
    if net.prefixlen == 31:
        return 2  # point-to-point link (RFC 3021)
    return net.num_addresses - 2


def host_range(net):
    """Return (first, last) usable addresses."""
    if net.version == 4 and net.prefixlen < 31:
        return net.network_address + 1, net.broadcast_address - 1
    return net.network_address, net.broadcast_address


def binary_mask(net) -> str:
    if net.version == 4:
        return ".".join(f"{o:08b}" for o in net.netmask.packed)
    return f"{'1' * net.prefixlen}{'0' * (128 - net.prefixlen)}"


def info(net) -> dict:
    first, last = host_range(net)
    data = {
        "network": str(net),
        "network_address": str(net.network_address),
        "prefix_length": net.prefixlen,
        "netmask": str(net.netmask),
        "wildcard_mask": str(net.hostmask),
        "total_addresses": net.num_addresses,
        "usable_hosts": usable_hosts(net),
        "first_host": str(first),
        "last_host": str(last),
        "is_private": net.is_private,
    }
    if net.version == 4:
        data["broadcast_address"] = str(net.broadcast_address)
        data["binary_mask"] = binary_mask(net)
    else:
        data["last_address"] = str(net.broadcast_address)
    return data


LABELS = {
    "network": "Network (CIDR)",
    "network_address": "Network Address",
    "broadcast_address": "Broadcast Address",
    "last_address": "Last Address",
    "netmask": "Subnet Mask",
    "wildcard_mask": "Wildcard Mask",
    "binary_mask": "Binary Mask",
    "prefix_length": "Prefix Length",
    "total_addresses": "Total Addresses",
    "usable_hosts": "Usable Hosts",
    "first_host": "First Host",
    "last_host": "Last Host",
    "is_private": "Is Private",
}


def print_info(net) -> None:
    print("\nSubnet Information")
    print("------------------")
    for key, value in info(net).items():
        if isinstance(value, int) and not isinstance(value, bool):
            value = f"{value:,}" if key != "prefix_length" else f"/{value}"
        print(f"{LABELS[key]:<20}: {value}")


def split_by_prefix(net, new_prefix: int) -> None:
    if not net.prefixlen < new_prefix <= net.max_prefixlen:
        print(f"\nSplit prefix must be between /{net.prefixlen + 1} "
              f"and /{net.max_prefixlen}.")
        return
    count = 2 ** (new_prefix - net.prefixlen)
    print(f"\nSplit into /{new_prefix} subnets ({count:,} total)")
    print("-" * 40)
    for i, sub in enumerate(net.subnets(new_prefix=new_prefix), 1):
        if i > MAX_LIST:
            print(f"... and {count - MAX_LIST:,} more")
            break
        first, last = host_range(sub)
        print(f"{i:>3}. {str(sub):<20} {first} - {last}")


def prefix_for_hosts(hosts: int, version: int) -> int:
    """Smallest prefix that fits the requested number of hosts."""
    if version == 6:
        return 128 - max(1, math.ceil(math.log2(hosts)))
    needed = hosts + 2 if hosts > 2 else hosts  # network + broadcast
    return 32 - max(1, math.ceil(math.log2(needed)))


def split_by_hosts(net, hosts: int) -> None:
    prefix = prefix_for_hosts(hosts, net.version)
    if prefix < net.prefixlen:
        print(f"\nA network of {hosts:,} hosts doesn't fit inside {net}.")
        return
    print(f"\nTo fit {hosts:,} hosts you need a /{prefix} "
          f"({usable_hosts(ipaddress.ip_network((net.network_address, prefix))):,} usable each).")
    split_by_prefix(net, prefix) if prefix > net.prefixlen else print(
        f"{net} itself already matches.")


def vlsm(net, host_counts) -> None:
    """Allocate variable-length subnets, largest requirement first."""
    print(f"\nVLSM allocation inside {net}")
    print("-" * 40)
    cursor = int(net.network_address)
    end = int(net.broadcast_address)
    for hosts in sorted(host_counts, reverse=True):
        prefix = prefix_for_hosts(hosts, net.version)
        size = 2 ** (net.max_prefixlen - prefix)
        cursor = (cursor + size - 1) // size * size  # align to block size
        if cursor + size - 1 > end:
            print(f"Out of space: no room for {hosts:,} hosts.")
            return
        sub = ipaddress.ip_network((cursor, prefix))
        first, last = host_range(sub)
        print(f"{hosts:>8,} hosts -> {str(sub):<20} {first} - {last}")
        cursor += size
    left = end - cursor + 1
    print(f"\nAddresses remaining: {left:,}")


def contains(net, address: str) -> None:
    try:
        ip = ipaddress.ip_address(address)
    except ValueError as exc:
        print(f"\nInvalid address: {exc}")
        return
    if ip.version != net.version:
        print(f"\n{ip} is IPv{ip.version}; {net} is IPv{net.version}.")
        return
    verdict = "IS" if ip in net else "is NOT"
    print(f"\n{ip} {verdict} inside {net}")


def parse_network(text: str):
    try:
        net = ipaddress.ip_network(text.strip(), strict=False)
    except ValueError as exc:
        print(f"\nInvalid network '{text}': {exc}")
        return None
    if str(net) != text.strip():
        print(f"(Host bits cleared: using {net})")
    return net


def interactive() -> None:
    print("=== Subnet Calculator ===")
    print("Commands after entering a network:  split <prefix> | hosts <n> | "
          "contains <ip> | vlsm <n n n> | new | q")
    net = None
    while True:
        if net is None:
            try:
                text = input("\nEnter network (example: 192.168.1.0/24): ")
            except (EOFError, KeyboardInterrupt):
                print()
                return
            if text.strip().lower() in {"q", "quit", "exit"}:
                return
            net = parse_network(text)
            if net:
                print_info(net)
            continue

        try:
            cmd = input(f"\n[{net}] > ").strip().split()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not cmd:
            continue
        name, args = cmd[0].lower(), cmd[1:]
        try:
            if name in {"q", "quit", "exit"}:
                return
            elif name == "new":
                net = None
            elif name == "split":
                split_by_prefix(net, int(args[0].lstrip("/")))
            elif name == "hosts":
                split_by_hosts(net, int(args[0]))
            elif name == "contains":
                contains(net, args[0])
            elif name == "vlsm":
                vlsm(net, [int(a) for a in args])
            else:
                print("Unknown command.")
        except (IndexError, ValueError):
            print("Missing or invalid argument.")


def main() -> int:
    p = argparse.ArgumentParser(description="Subnet calculator (IPv4 & IPv6)")
    p.add_argument("network", nargs="?", help="e.g. 192.168.1.0/24")
    p.add_argument("--split", type=int, metavar="PREFIX",
                   help="split into subnets of this prefix length")
    p.add_argument("--hosts", type=int, metavar="N",
                   help="split into subnets that each fit N hosts")
    p.add_argument("--vlsm", type=int, nargs="+", metavar="N",
                   help="allocate subnets for these host counts")
    p.add_argument("--contains", metavar="IP",
                   help="check whether an IP is in the network")
    p.add_argument("--json", action="store_true", help="output info as JSON")
    args = p.parse_args()

    if not args.network:
        interactive()
        return 0

    net = parse_network(args.network)
    if net is None:
        return 1

    if args.json:
        print(json.dumps(info(net), indent=2))
    else:
        print_info(net)
    if args.split:
        split_by_prefix(net, args.split)
    if args.hosts:
        split_by_hosts(net, args.hosts)
    if args.vlsm:
        vlsm(net, args.vlsm)
    if args.contains:
        contains(net, args.contains)
    return 0


if __name__ == "__main__":
    sys.exit(main())
