import re
s=open('gen_i960.py').read()
s=s.replace("'op8=0x%02x & cbit0=0' % (0x20 + i), 'local t","'op8=0x%02x & rd_r' % (0x20 + i), 'local t")
s=s.replace("'op8=0x%02x & ea & %s' % (opc, d)","'op8=0x%02x & %s & ea ...' % (opc, d)")
s=s.replace("'op8=0xad & ea'","'op8=0xad & ea ...'")
for t in ('eaK','eaV'):
    s=re.sub(r"'(op8=0x8[456]) & %s( & rd_r)?'"%t, lambda m:"'%s%s & %s ...'"%(m.group(1),m.group(2) or '',t), s)
open('gen_i960.py','w').write(s)
