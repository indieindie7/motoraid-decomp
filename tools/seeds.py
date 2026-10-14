"""seeds.py <out>: function seeds from unidasm listings (call/callx/bal/balx absolute targets) of ROM and the RAM copy.
ROM 0xb0000..0xcffff is the copy source of RAM 0x200000..0x21ffff: skip it in the ROM listing."""
import re, sys
seeds = {0x5e0}
for f, lo, hi in (('ghidra/prog.dis', 0, 0x100000), ('ghidra/ram200.dis', 0x200000, 0x220000)):
    for l in open(f):
        m = re.match(r'([0-9a-f]+): .*?\b(call|callx|bal|balx)\s+(0x[0-9a-f]+)\s*$', l)
        if not m: continue
        a = int(m.group(1), 16); t = int(m.group(3), 16)
        if lo == 0 and 0xb0000 <= a < 0xd0000: continue
        if (t < 0x100000 and not 0xb0000 <= t < 0xd0000) or 0x200000 <= t < 0x220000:
            seeds.add(t)
open(sys.argv[1], 'w').write(''.join('0x%08x\n' % s for s in sorted(seeds)))
print(len(seeds), sum(1 for s in seeds if s >= 0x200000))
