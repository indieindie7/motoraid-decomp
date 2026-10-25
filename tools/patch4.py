import re
s=open('gen_i960.py').read()
# gen_ea with ext flag
s=s.replace("def gen_ea(name, kind):","def gen_ea(name, kind, ext):")
s=s.replace("""    if want_const:
        w('%s: off12 is""","""    if want_const and not ext:
        w('%s: off12 is mb=0 & ma=0 & off12 { %s }' % (name, exp_const('off12')))
    if want_const and ext:
        w('%s: off12 is""")
# remove the stale off12 line inside ext block
s=s.replace("""    if want_const and ext:
        w('%s: off12 is mb=0 & ma=0 & off12 { %s }' % (name, exp_const('off12')))
""","""    if want_const and ext:
""")
s=s.replace("""    if want_var:
        w('%s: off12^"("^rb_r^")" is""","""    if want_var and not ext:
        w('%s: off12^"("^rb_r^")" is""")
# split var block: modes 13-15 into ext block
s=s.replace("""        w('%s: extd^"("^rb_r^")" is mb=1 & memmode=13""","""    if want_var and ext:
        w('%s: extd^"("^rb_r^")" is mb=1 & memmode=13""")
s=s.replace("""gen_ea('ea', 'all')
gen_ea('eaK', 'const')
gen_ea('eaV', 'var')""","""for _n, _k in (('ea', 'all'), ('eaK', 'const'), ('eaV', 'var')):
    gen_ea(_n + '4', _k, False)
    gen_ea(_n + '8', _k, True)""")
# mem ctors
s=s.replace("def ctor(mn, disp, pat, body):","""def mctor(mn, disp, pat, body):
    for sz in ('4', '8'):
        f = lambda t: re.sub(r'\bea(K|V)?\b( \.\.\.)?', lambda m: 'ea' + (m.group(1) or '') + sz, t)
        ctor(mn, f(disp), f(pat), f(body))


def ctor(mn, disp, pat, body):""")
s=s.replace("import sys, os","import sys, os, re")
s=s.replace("    ctor(mn, 'ea,' + d,","    mctor(mn, 'ea,' + d,")
s=s.replace("    ctor(mn, d + ',ea',","    mctor(mn, d + ',ea',")
for m in ("ctor('dcinva'","ctor('bx'","ctor('callx'","ctor('balx'"):
    s=s.replace(m,"m"+m)
open('gen_i960.py','w').write(s)
