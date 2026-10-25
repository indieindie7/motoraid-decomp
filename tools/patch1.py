s=open('gen_i960.py').read()
R=[("w('%s: %s is %s=0 & %s=0 & %s { export %s; }' % (nmp, r, m, s, r, pf))","w('%s: %s is %s=0 & %s=0 & %s { export %s; }' % (nmp, pf, m, s, pf, pf))"),
("w('src1t: ra_r is m1=0 & s1=0 & ra_r { export ra_t; }')","w('src1t: ra_t is m1=0 & s1=0 & ra_t { export ra_t; }')"),
("w('src1q: ra_r is m1=0 & s1=0 & ra_r { export ra_q; }')","w('src1q: ra_q is m1=0 & s1=0 & ra_q { export ra_q; }')"),
("w('dstp: rd_r is m3=0 & rd_r { export rd_p; }')","w('dstp: rd_p is m3=0 & rd_p { export rd_p; }')"),
("w('dstt: rd_r is m3=0 & rd_r { export rd_t; }')","w('dstt: rd_t is m3=0 & rd_t { export rd_t; }')"),
("w('dstq: rd_r is m3=0 & rd_r { export rd_q; }')","w('dstq: rd_q is m3=0 & rd_q { export rd_q; }')"),
("w('%s: %s is %s=0 & %s { export %s; }' % (d, r, m, r, p))","w('%s: %s is %s=0 & %s { export %s; }' % (d, p, m, p, p))"),
("w('fdstd: rd_r is m3=0 & rd_r { export rd_p; }')","w('fdstd: rd_p is m3=0 & rd_p { export rd_p; }')")]
for a,b in R:
    assert a in s,a
    s=s.replace(a,b)
open('gen_i960.py','w').write(s)
