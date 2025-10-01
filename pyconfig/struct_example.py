
import struct


# Code	Meaning	Python Type	Size (Common)
# i	Standard Integer	int	4 bytes
# h	Short Integer	int	2 bytes
# f	Float (Decimal Number)	float	4 bytes
# ?	Boolean (True/False)	bool	1 byte
# 5s	String (5 characters/bytes)	bytes	5 bytes

# Export to Sheets


# Our Blueprint: '<i?'
# < : Little-endian (a specific order for multi-byte data, like a reading direction)
# i : A 4-byte Integer
# ? : A 1-byte Boolean
# '<i?'

my_age = 29
is_active = True

# 1. PACKING (Putting Data into the Lockbox/Bytes)
# Converts (29, True) into a single bytes object.

byte_package = struct.pack('<i?', my_age, is_active)

print(f"Original Data: (Age: {my_age}, Active: {is_active})")
print(f"Blueprint: '<i?' (4 bytes + 1 byte)")
print(f"Lockbox (Bytes): {byte_package}")
print(f"Total Size: {len(byte_package)} bytes")


# 2. UNPACKING (Taking Data out of the Lockbox/Bytes)
# Converts the bytes object back into a tuple of Python values.
unpacked_data = struct.unpack('<i?', byte_package)

print(f"\nUnpacked Data: {unpacked_data}")
# Result: (35, True)