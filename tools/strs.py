import re, sys
d = open(sys.argv[1], 'rb').read()
s = [(m.start(), m.group().decode()) for m in re.finditer(rb'[\x20-\x7e]{8,}', d)]
print(len(s))
for o, t in s[:int(sys.argv[2])]: print(hex(o), t[:70])
