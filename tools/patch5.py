s=open('gen_i960.py').read()
s=s.replace("r'ea(K|V)?( \.\.\.)?'","r'\bea(K|V)?\b( \.\.\.)?'")
open('gen_i960.py','w').write(s)
