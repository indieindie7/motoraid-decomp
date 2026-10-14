"""gaps.py: ret-terminated code runs in the unidasm listings that no Ghidra function covers (candidates for missed functions)."""
import re
F = []
for l in open('funcinfo_0.tsv'):
    p = l.split()
    if p and p[0] == 'F': F.append((int(p[1], 16), int(p[4])))
cov = set()
for a, n in F:
    cov.update(range(a, a + n))
miss = []; rets = 0
for f, lo, hi in (('prog.dis', 0x5e0, 0x100000), ('ram200.dis', 0x200000, 0x220000)):
    start = None
    for l in open(f):
        m = re.match(r'([0-9a-f]+): +\S+(?: +\S+)? +(\S+)', l)
        if not m: continue
        a = int(m.group(1), 16)
        if not lo <= a < hi or 0xb0000 <= a < 0xd0000 and lo == 0x5e0: continue
        if m.group(2) == 'ret':
            rets += 1
            if a not in cov: miss.append(a)
print('rets', rets, 'uncovered rets', len(miss))
print(' '.join(hex(x) for x in miss[:20]))
# seeds: for each uncovered ret, walk back to the previous ret / padding / '?' and seed the first instruction after it
seeds = set()
for f, lo, hi in (('prog.dis', 0x5e0, 0x100000), ('ram200.dis', 0x200000, 0x220000)):
    rows = []
    for l in open(f):
        m = re.match(r'([0-9a-f]+): +(\S+)(?: +\S+)? +(\S+)', l)
        if m: rows.append((int(m.group(1), 16), m.group(3), m.group(2)))
    idx = {a: i for i, (a, _, _) in enumerate(rows)}
    for r in miss:
        if r not in idx: continue
        i = idx[r]
        while i > 0 and rows[i - 1][1] not in ('ret', '?') and rows[i - 1][2] != '00000000' and rows[i - 1][0] not in cov:
            i -= 1
        a = rows[i][0]
        if a % 4 == 0 and a not in cov: seeds.add(a)
open('seeds2.txt', 'w').write(''.join('0x%08x\n' % s for s in sorted(seeds)))
print('gap seeds', len(seeds))
