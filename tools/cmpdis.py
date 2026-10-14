import re, sys, collections
D=r'ghidra'
ref={}
for l in open(D+r'\prog.dis'):
    m=re.match(r'([0-9a-f]+): ([0-9a-f]{8}) (?:([0-9a-f]{8}) )?\s*(\S+)\s*(.*)',l)
    if m: ref[int(m.group(1),16)]=(m.group(4),m.group(5).strip())
gh={}
for l in open(D+r'\ghidra_listing.txt'):
    a,mn,ops,ln=l.rstrip('\n').split('|')
    gh[int(a,16)]=(mn,ops,int(ln))
def norm(o):
    o=o.lower().replace(' ','')
    o=re.sub(r'fp([0-3])s',r'fp',o)
    o=o.replace(',,',',').rstrip(',').replace(',(','(').replace(',[','[')
    # collapse pair/triple/quad register names like g4g5g6g7 -> g4
    o=re.sub(r'((?:[rg]\d+|pfp|sp|rip|fp(?![0-3]))(?:[rg]\d+|pfp|sp|rip|fp)+)',lambda m:re.match(r'[rg]\d+|pfp|sp|rip|fp',m.group(1)).group(0),o)
    o=re.sub(r'(?<![a-z0-9])(0x[0-9a-f]+|\d+)(?![a-z0-9])',lambda m:str(int(m.group(1),0)),o)
    o=o.replace('+1.0','1.0').replace('+0.0','0.0')
    return o
tot=mm=om=0; cnt=collections.Counter(); ex={}
for a,(mn,ops,ln) in sorted(gh.items()):
    r=ref.get(a)
    if not r or r[0]=='?': continue
    if mn=='??': cnt[('UNDECODED',r[0])]+=1; ex.setdefault(('UNDECODED',r[0]),a); continue
    tot+=1
    if mn.lower()==r[0].lower():
        mm+=1
        if norm(ops)==norm(r[1]): om+=1
        else:
            cnt[('OPS',mn)]+=1; ex.setdefault(('OPS',mn),(a,r[1],ops))
    else:
        cnt[(r[0],mn)]+=1; ex.setdefault((r[0],mn),a)
n=len([1 for a in gh if ref.get(a) and ref[a][0]!='?'])
print('ref instr %d decoded %d mnemonic-agree %d (%.2f%% of decoded, %.2f%% of ref) operand-agree %d'%(n,tot,mm,100*mm/max(tot,1),100*mm/max(n,1),om))
for k,v in cnt.most_common(40): print(v,k,hex(ex[k]) if isinstance(ex[k],int) else ex[k])
