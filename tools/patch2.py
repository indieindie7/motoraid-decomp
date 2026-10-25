s=open('gen_i960.py').read()
s=s.replace("""for opc, mn, d, body in loads:
    ctor(mn, 'ea,rd_r', 'op8=0x%02x & ea & rd_r' % opc, body)""","""LD = {'ldl': ('dstp', 'dstp = *:8 ea;'), 'ldt': ('dstt', 'dstt = *:12 ea;'), 'ldq': ('dstq', 'dstq = *:16 ea;')}
for opc, mn, d, body in loads:
    if mn in LD:
        d, body = LD[mn]
    else:
        d = 'rd_r'
    ctor(mn, 'ea,' + d, 'op8=0x%02x & ea & %s' % (opc, d), body)""")
s=s.replace("""for opc, mn, body in stores:
    ctor(mn, 'rd_r,ea', 'op8=0x%02x & ea & rd_r' % opc, body)""","""ST = {'stl': ('dstp', '*:8 ea = dstp;'), 'stt': ('dstt', '*:12 ea = dstt;'), 'stq': ('dstq', '*:16 ea = dstq;')}
for opc, mn, body in stores:
    d = 'rd_r'
    if mn in ST:
        d, body = ST[mn]
    ctor(mn, d + ',ea', 'op8=0x%02x & ea & %s' % (opc, d), body)""")
open('gen_i960.py','w').write(s)
