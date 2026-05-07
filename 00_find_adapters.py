"""Prints name and description of available network adapters."""

import pysoem


print("\n" + "="*70)
print("AVAILABLE NETWORK ADAPTERS")
print("="*70 + "\n")

adapters = pysoem.find_adapters()

if not adapters:
    print("ERROR: No network adapters found!")
    exit(1)

for i, adapter in enumerate(adapters):
    print(f'[{i}] {adapter.desc}')
    print(f'    Name: {adapter.name}')
    print()

print("="*70)
print("NEXT STEPS:")
print("  1. Identify the adapter connected to your EtherCAT slave")
print("  2. Copy the adapter 'Name' (e.g., \\Device\\NPF_{{...}})")
print("  3. Paste it into ecat_common_func.py, line 6 (ifname variable)")
print("="*70 + "\n")