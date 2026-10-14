"""interleave.py <lo16.bin> <hi16.bin> <out.bin>: Model 2 ROM_LOAD32_WORD pair -> one little-endian 32-bit image."""
import sys
a = open(sys.argv[1], 'rb').read(); b = open(sys.argv[2], 'rb').read()
out = bytearray()
for i in range(0, len(a), 2):
    out += a[i:i+2] + b[i:i+2]
open(sys.argv[3], 'wb').write(out)
