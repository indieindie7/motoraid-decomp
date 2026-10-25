"""m2model.py <id> [<id>...] --out <dir> [--png] [--uv] [--all]
Export Motor Raid (Sega Model 2A) models to Wavefront OBJ.
Model table in prog.bin at 0x4f500, 16 bytes/entry: tpa, tha, oba, obc (LE u32).
  tpa = texture point (UV) address, tha = texture header address (16-bit word index into texture ROM),
  oba = object address (bit 23 set = polygon ROM, low bits = 32-bit word index), obc = max link count.
Polygon stream (32-bit words, floats are IEEE LE):
  P0, P1 (3 floats each), then per polygon: attr, normal(3f), Pa(3f), Pb(3f)
  attr&3==0 end; attr&1 quad (3 = quad, 2 = triangle; triangle ignores Pb)
  attr bits 8-9 link type (0 = polygon not drawn by the hardware, shares both pts with previous),
  bits 12-16 signed texture-header step, 17 double sided, 18-22 material param.
  Quad verts: [P1prev, P0prev, Pa, Pb]; tri: [P1prev, P0prev, Pa].
  After each polygon (prev pair update): link 0/2 -> (P0,P1)=(Pa,Pb); 1 -> P1=Pa; 3 -> P0=Pb.
"""
import sys, struct, os, argparse
ROM = r'C:\Users\john\Documents\MotorRaid\rom\motoraid\motoraid'
PROG = r'C:\Users\john\Documents\MotorRaid\ghidra\prog.bin'
TABLE = 0x4f500

def inter(lo, hi, base, out):
    a = open(os.path.join(ROM, lo), 'rb').read(); b = open(os.path.join(ROM, hi), 'rb').read()
    out[base*1:base+len(a)*2:4] = a[0::2]; out[base+1:base+len(a)*2:4] = a[1::2]
    out[base+2:base+len(a)*2:4] = b[0::2]; out[base+3:base+len(a)*2:4] = b[1::2]

def load_poly():
    img = bytearray(0x2000000)
    # note slices need exact length: len(a)*2/4 = len(a)/2 items each
    for lo, hi, base in (('mpr-20023.16', 'mpr-20026.20', 0), ('mpr-20024.17', 'mpr-20027.21', 0x800000),
                         ('mpr-20025.18', 'mpr-20028.22', 0x1000000)):
        inter(lo, hi, base, img)
    return img

def load_tex():
    img = bytearray(0x1000000)
    inter('mpr-20022.25', 'mpr-20021.24', 0, img)
    return img

def export(mid, poly, tex, prog, outdir, uv=False, keep_hidden=False):
    tpa, tha, oba, obc = struct.unpack_from('<4I', prog, TABLE + mid*16)
    if not (oba & 0x800000):
        print('id 0x%x: oba %06x not in polygon ROM' % (mid, oba)); return None
    p = (oba & 0x7fffff) * 4
    if obc == 0: obc = 0xfffff
    def f3():
        nonlocal p
        v = struct.unpack_from('<3f', poly, p); p += 12; return v
    P0 = f3(); P1 = f3()
    tpw = tpa & 0x7fffff; thw = tha & 0x7fffff   # 16-bit word indexes (texture ROM only)
    verts = {}; vlist = []; faces = []; uvs = []
    def vid(v):
        k = tuple(round(c, 4) for c in v)
        if k not in verts: verts[k] = len(vlist)+1; vlist.append(k)
        return verts[k]
    tw = lambda i: struct.unpack_from('<H', tex, (i*2) & 0xffffff)[0]
    for _ in range(obc):
        attr = struct.unpack_from('<I', poly, p)[0]; p += 4
        if attr & 3 == 0: break
        p += 12  # normal
        Pa = f3(); Pb = f3()
        quad = bool(attr & 1); link = (attr >> 8) & 3
        n = 4 if quad else 3
        vs = [P1, P0, Pa, Pb][:n]
        th = tuple(tw(thw+i) for i in range(4))
        tuv = [(tw(tpw+2*i+1), tw(tpw+2*i)) for i in range(n)]  # (u, v) raw
        tpw += n*2
        step = (attr >> 12) & 0x1f
        if step & 0x10: step -= 32
        thw += step*4
        if link != 0 or keep_hidden:
            faces.append((th, [vid(v) for v in vs], tuv, link))
        if link in (0, 2): P0, P1 = Pa, (Pb if quad else Pa)
        elif link == 1: P1 = Pa
        else: P0 = (Pb if quad else Pa)
    # normalize degenerate
    os.makedirs(outdir, exist_ok=True)
    fn = os.path.join(outdir, 'model_%04x.obj' % mid)
    mats = {}
    with open(fn, 'w') as f:
        f.write('# Motor Raid model 0x%x tpa=%06x tha=%06x oba=%06x obc=%d\n' % (mid, tpa, tha, oba, obc))
        for v in vlist: f.write('v %.4f %.4f %.4f\n' % v)
        if uv:
            for fc in faces:
                for u, v in fc[2]: f.write('vt %.4f %.4f\n' % (u/8.0, v/8.0))
        t = 0
        for th, ids, tuv, link in sorted(faces, key=lambda x: x[0]):
            pass
        order = sorted(range(len(faces)), key=lambda i: faces[i][0])
        # vt indexes follow original face order
        offs = []; c = 0
        for fc in faces: offs.append(c); c += len(fc[1])
        cur = None
        for i in order:
            th, ids, tuv, link = faces[i]
            if th != cur:
                cur = th; f.write('g tex_%04x_%04x_%04x_%04x\n' % th)
            if uv: f.write('f ' + ' '.join('%d/%d' % (a, offs[i]+j+1) for j, a in enumerate(ids)) + '\n')
            else: f.write('f ' + ' '.join(str(a) for a in ids) + '\n')
    if vlist:
        bb = [(min(v[a] for v in vlist), max(v[a] for v in vlist)) for a in range(3)]
    else: bb = [(0, 0)]*3
    nq = sum(1 for fc in faces if len(fc[1]) == 4)
    print('id 0x%04x: verts %d polys %d (quads %d tris %d) bbox x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f] -> %s' %
          (mid, len(vlist), len(faces), nq, len(faces)-nq, *bb[0], *bb[1], *bb[2], fn))
    return vlist, faces, bb

def png(mid, res, outdir):
    from PIL import Image, ImageDraw
    vlist, faces, bb = res
    if not vlist: return
    W = 520
    views = [(0, 1, 'X-Y front'), (2, 1, 'Z-Y side'), (0, 2, 'X-Z top')]
    img = Image.new('RGB', (W*3, W), 'white'); d = ImageDraw.Draw(img)
    ext = max(b[1]-b[0] for b in bb) or 1; s = (W-40)/ext
    for k, (a, b, name) in enumerate(views):
        ca = (bb[a][0]+bb[a][1])/2; cb = (bb[b][0]+bb[b][1])/2
        pt = lambda v: (k*W + W/2 + (v[a]-ca)*s, W/2 - (v[b]-cb)*s) if b == 1 or True else None
        for th, ids, tuv, link in faces:
            pts = [pt(vlist[i-1]) for i in ids]
            d.line(pts + [pts[0]], fill=(30, 60, 160), width=1)
        d.text((k*W+8, 6), name + '  id 0x%x  extent %.2f' % (mid, ext), fill='black')
    img.save(os.path.join(outdir, 'model_%04x.png' % mid))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('ids', nargs='+'); ap.add_argument('--out', default='.')
    ap.add_argument('--png', action='store_true'); ap.add_argument('--uv', action='store_true')
    ap.add_argument('--all', action='store_true', help='keep link-type-0 polygons')
    a = ap.parse_args()
    poly = load_poly(); tex = load_tex(); prog = open(PROG, 'rb').read()
    for s in a.ids:
        mid = int(s, 0)
        r = export(mid, poly, tex, prog, a.out, a.uv, a.all)
        if r and a.png: png(mid, r, a.out)
