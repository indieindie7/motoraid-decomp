s=open('gen_i960.py').read()
a="        ctor(mn, f(disp), f(pat), f(body))"
b="""        p = f(pat)
        if sz == '8':
            i = p.rindex(' & ea')
            p = '(' + p[:i] + ') ... ' + p[i:]
        ctor(mn, f(disp), p, f(body))"""
assert a in s
open('gen_i960.py','w').write(s.replace(a,b))
