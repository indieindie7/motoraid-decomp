import re,collections
D=r'C:\Users\john\Documents\MotorRaid\ghidra'
ref={}
for l in open(D+r'\prog.dis'):
    m=re.match(r'([0-9a-f]+): ([0-9a-f]{8}) (?:([0-9a-f]{8}) )?\s*(\S+)\s*(.*)',l)
    if m: ref[int(m.group(1),16)]=(m.group(2),m.group(4),m.group(5))
c=collections.Counter();ex={}
for l in open(D+r'\ghidra_listing.txt'):
    a,mn,ops,ln=l.strip().split('|'); a=int(a,16)
    if mn=='??':
        w,m,o=ref[a]; k=(m,re.sub(r'[0-9a-fx]+','N',o)); c[k]+=1; ex.setdefault(k,(hex(a),w,o))
for k,v in c.most_common(25): print(v,k,ex[k])
