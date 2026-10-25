L=open('gen_i960.py').read().split('\n')
# locate blocks
a=next(i for i,l in enumerate(L) if l.startswith('def gen_ea'))
b=next(i for i,l in enumerate(L) if l.startswith("for _n, _k in"))
c=b+3  # through gen_ea(_n+'8'...)
new_ea='''def gen_ea4(name, kind):
    """4-byte forms. all: A0 const (value export), A1/4/7 var. const: A0 only (address export). var: A1/4/7."""
    if kind in ('all', 'const'):
        if kind == 'const':
            w('%s: off12 is mb=0 & ma=0 & off12 { export *:4 off12; }' % name)
        else:
            w('%s: off12 is mb=0 & ma=0 & off12 { export *[const]:4 off12; }' % name)
    if kind in ('all', 'var'):
        w('%s: off12^"("^rb_r^")" is mb=0 & ma=1 & off12 & rb_r { local t:4 = rb_r + off12; export t; }' % name)
        w('%s: "("^rb_r^")" is memmode=4 & mb56=0 & scale<=4 & rb_r { export rb_r; }' % name)
        for sc in range(5):
            sfx = '' if sc == 0 else '*%d' % (1 << sc)
            w('%s: "("^rb_r^")["^ra_r^"%s]" is memmode=7 & mb56=0 & scale=%d & rb_r & ra_r { local t:4 = rb_r + (ra_r << %d); export t; }' % (name, sfx, sc, sc))


def gen_ea8(name, kind):
    """8-byte forms: table over the first token only, exports the base; the parent adds the displacement word."""
    if kind in ('all',):
        w('%s: "" is memmode=12 & mb56=0 & scale<=4 { local t:4 = 0; export t; }' % name)
        w('%s: "(ip)" is memmode=5 & mb56=0 & scale<=4 { local t:4 = inst_next; export t; }' % name)
    w('%s: "("^rb_r^")" is memmode=13 & mb56=0 & scale<=4 & rb_r { export rb_r; }' % name)
    for sc in range(5):
        sfx = '' if sc == 0 else '*%d' % (1 << sc)
        w('%s: "["^ra_r^"%s]" is memmode=14 & mb56=0 & scale=%d & ra_r { local t:4 = (ra_r << %d); export t; }' % (name, sfx, sc, sc))
        w('%s: "("^rb_r^")["^ra_r^"%s]" is memmode=15 & mb56=0 & scale=%d & rb_r & ra_r { local t:4 = rb_r + (ra_r << %d); export t; }' % (name, sfx, sc, sc))


gen_ea4('ea4', 'all')
gen_ea4('eaK4', 'const')
gen_ea4('eaV4', 'var')
gen_ea8('ea8', 'all')
gen_ea8('eaV8', 'var')
w('ktgt: extd is extd { export *:4 extd; }')
w('ktgt5: res is extds [ res = (inst_next + extds) & 0xffffffff; ] { export *:4 res; }')'''.split('\n')
L[a:c]=new_ea
s='\n'.join(L)
# mctor
i=s.index('def mctor'); j=s.index('def ctor')
s=s[:i]+'''def mctor(mn, disp, pat, body):
    f4 = lambda t: re.sub(r'\bea(K|V)?\b( \.\.\.)?', lambda m: 'ea' + (m.group(1) or '') + '4', t)
    ctor(mn, f4(disp), f4(pat), f4(body))
    if 'eaK' in pat:
        return
    v = 'eaV8' if 'eaV' in pat else 'ea8'
    d = re.sub(r'\bea(V)?\b', 'extd^' + v, disp)
    p = re.sub(r'\bea(V)?\b( \.\.\.)?', v, pat) + ' ; extd'
    b = 'local ea:4 = %s + extd;\n' % v + re.sub(r'\bea(V)?\b', 'ea', body)
    ctor(mn, d, p, b)


'''+s[j:]
# K forms for bx/callx/balx at 8 bytes
s=s.replace("w('')\n\n# ---------------------------------------------------------------- REG format","""ctor('bx', 'ktgt', 'op8=0x84 & memmode=12 & mb56=0 & scale<=4 ; ktgt', 'goto ktgt;')
ctor('bx', 'ktgt5', 'op8=0x84 & memmode=5 & mb56=0 & scale<=4 ; ktgt5', 'goto ktgt5;')
ctor('callx', 'ktgt', 'op8=0x86 & memmode=12 & mb56=0 & scale<=4 ; ktgt', 'call ktgt;')
ctor('callx', 'ktgt5', 'op8=0x86 & memmode=5 & mb56=0 & scale<=4 ; ktgt5', 'call ktgt5;')
ctor('balx', 'ktgt,rd_r', 'op8=0x85 & rd_r & memmode=12 & mb56=0 & scale<=4 ; ktgt', 'rd_r = inst_next;\ncall ktgt;')
ctor('balx', 'ktgt5,rd_r', 'op8=0x85 & rd_r & memmode=5 & mb56=0 & scale<=4 ; ktgt5', 'rd_r = inst_next;\ncall ktgt5;')
w('')

# ---------------------------------------------------------------- REG format""",1)
open('gen_i960.py','w').write(s)
