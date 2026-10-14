"""m2rules.py <decomp.c> <rules_out> <hints_out>: decider for Sega Model 2A (i960) dumps.
Names: ret-only bodies -> stub_<addr>, constant-return bodies -> ret<N>_<addr>.
Hints: hardware blocks touched (absolute addresses in the decompile), float use, string literals."""
import re, sys

HW = [  # (lo, hi, tag) from MAME model2.cpp (model2_base_mem + model2a_crx_mem)
    (0x00800000, 0x00803fff, 'geo'), (0x00804000, 0x0080ffff, 'tgp_fifo'), (0x00880000, 0x0088ffff, 'copro'),
    (0x00900000, 0x0097ffff, 'bufferram'), (0x00980000, 0x0098003f, 'videoctl'),
    (0x00e00000, 0x00e00037, 'cpuctl'), (0x00e80000, 0x00e80007, 'irq'), (0x00f00000, 0x00f0000f, 'timer'),
    (0x00f80000, 0x00f8ffff, 'ramctl'),
    (0x01000000, 0x0111ffff, 'tile'), (0x01800000, 0x01803fff, 'palette'), (0x01810000, 0x0181bfff, 'colorxlat'),
    (0x0181c000, 0x0181c003, 'zclip'), (0x01a00000, 0x01a1ffff, 'comm'),
    (0x01c00000, 0x01c0001f, 'io'), (0x01c80000, 0x01c80003, 'uart'),
    (0x01d00000, 0x01d03fff, 'backup'), (0x02000000, 0x03ffffff, 'main_data'), (0x06000000, 0x06ffffff, 'extra_data'),
    (0x10000000, 0x10ffffff, 'render'),
]

def tag(a):
    for lo, hi, t in HW:
        if lo <= a <= hi: return t
    return None

src, rout, hout = sys.argv[1:4]
blocks = []; cur = None
for l in open(src, encoding='utf-8', errors='replace'):
    m = re.match(r'// ==== (\S+) @ ([0-9a-fA-F]+) ', l)
    if m:
        cur = [int(m.group(2), 16), m.group(1), []]; blocks.append(cur)
    elif cur: cur[2].append(l)
rules = []; hints = []
for a, name, body in blocks:
    t = ''.join(body)
    code = re.sub(r'\s+', ' ', t[t.find('{') + 1:t.rfind('}')]).strip()
    if name.startswith('FUN_'):
        if code in ('', 'return;'):
            rules.append('0x%08x func stub_%08x hand decider: empty body' % (a, a))
        else:
            m = re.fullmatch(r'return (0x[0-9a-f]+|\d+);', code)
            if m: rules.append('0x%08x func ret%d_%08x hand decider: returns constant' % (a, int(m.group(1), 0), a))
    hw = set()
    for x in re.findall(r'(?:DAT_|0x)([0-9a-f]{8})\b', t):
        g = tag(int(x, 16))
        if g: hw.add(g)
    h = []
    if hw: h.append('hw=' + ','.join(sorted(hw)))
    nf = len(re.findall(r'\bfloat\b|\bdouble\b', t))
    if nf: h.append('float=%d' % nf)
    s = re.findall(r'"([^"\n]{3,40})"', t) + [x.replace('_', ' ').strip() for x in re.findall(r'\bs_([A-Za-z0-9_]{3,60}?)_[0-9a-f]{8}\b', t)]
    if s: h.append('str=' + ' | '.join(dict.fromkeys(s))[:120])
    if h: hints.append('0x%08x %s' % (a, ' '.join(h)))
open(rout, 'w').write(''.join(r + '\n' for r in rules))
open(hout, 'w', encoding='utf-8').write(''.join(x + '\n' for x in hints))
print('blocks', len(blocks), 'names', len(rules), 'hints', len(hints))
