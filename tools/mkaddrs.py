import re
out=open(r'C:\Users\john\Documents\MotorRaid\ghidra\addrs.txt','w')
n=0
for l in open(r'C:\Users\john\Documents\MotorRaid\ghidra\prog.dis'):
    m=re.match(r'([0-9a-f]+): ([0-9a-f]{8}) (?:([0-9a-f]{8}) )?\s*(\S+)',l)
    if not m: continue
    a=int(m.group(1),16)
    if a<0x5e0 or a>=0x40000: continue
    if m.group(4)=='?': continue
    out.write('%x\n'%a); n+=1
print(n)
