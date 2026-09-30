"""Dựng sơ đồ ranh khu đất (SVG) từ bảng tọa độ VN-2000 trong bản scan.

- P1: ranh hiện trạng 11.617,1 m² (Sơ đồ hiện trạng vị trí, 18/04/2026) — 40 điểm, đọc rõ.
- P2: ranh giao–thuê 17.356,5 m² (Sơ đồ vị trí nhà đất để lập thủ tục giao–thuê) — 33 điểm;
  điểm 4–5 trên bản scan bị mờ, đã hiệu chỉnh để khớp diện tích (xem README).
Chạy: python make_siteplan.py  -> ../assets/site-plan.svg
"""
import math, os
from coords import P1, P2, area

P2f = list(P2)
P2f[3] = (921.17, 384.30)   # điểm 4 (scan đọc 1190891.17 — mờ)
P2f[4] = (896.17, 288.01)   # điểm 5 (scan đọc 1190891.17 — mờ)

# X = northing (1190xxx), Y = easting (590xxx); lưu phần lẻ
E0, E1, N0, N1 = 250, 505, 790, 930
W = 1000
S = W / (E1 - E0)             # px / m
H = round((N1 - N0) * S)

def pt(p):
    n, e = p
    return (round((e - E0) * S, 1), round((N1 - n) * S, 1))

def poly(P):
    return " ".join(f"{x},{y}" for x, y in map(pt, P))

def arc_path(a, b, bulge):
    """cung tròn qua a,b lồi về phía bắc (bulge m)"""
    (x1, y1), (x2, y2) = pt(a), pt(b)
    c = math.dist((x1, y1), (x2, y2)); h = bulge * S
    r = (c * c / 4 + h * h) / (2 * h)
    return f"A{r:.1f},{r:.1f} 0 0 1 {x2},{y2}"

out = []
out.append(f'<svg viewBox="-20 -40 {W+40} {H+90}" xmlns="http://www.w3.org/2000/svg" role="img" '
           f'aria-label="Sơ đồ ranh khu đất theo tọa độ VN-2000" class="siteplan">')
# lưới 20 m
for e in range(260, 505, 20):
    x = (e - E0) * S
    out.append(f'<line class="grid" x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H}"/>')
for n in range(800, 930, 20):
    y = (N1 - n) * S
    out.append(f'<line class="grid" x1="0" y1="{y:.1f}" x2="{W}" y2="{y:.1f}"/>')
out.append(f'<text class="gridlbl" x="2" y="{H+16}">lưới 20 m · VN-2000, KTT 105°45′, múi 3°</text>')

# P2 với 2 đoạn cung (3→4→5)
p = [pt(q) for q in P2f]
d = f"M{p[0][0]},{p[0][1]} L{p[1][0]},{p[1][1]} L{p[2][0]},{p[2][1]} "
d += arc_path(P2f[2], P2f[3], 3.1) + " " + arc_path(P2f[3], P2f[4], 9.3) + " "
d += " ".join(f"L{x},{y}" for x, y in p[5:]) + " Z"
out.append(f'<path class="p2" d="{d}"/>')
out.append(f'<polygon class="p1" points="{poly(P1)}"/>')

# mương phía nam (song song cạnh 33→40 của P1, lệch ~6 m)
m = [pt((n - 6, e + 1)) for n, e in P1[32:40]]
out.append('<polyline class="water" points="' + " ".join(f"{x},{y}" for x, y in m) + '"/>')
mx, my = pt((822, 405))
out.append(f'<text class="lbl water-t" x="{mx}" y="{my+26}" transform="rotate(-24 {mx} {my+26})">Mương thủy lợi (DTL)</text>')

# ranh giải tỏa kênh (cạnh 13→17 của P1)
k = [pt(q) for q in P1[12:17]]
out.append('<polyline class="canal" points="' + " ".join(f"{x},{y}" for x, y in k) + '"/>')
kx, ky = pt((844, 283))
out.append(f'<text class="lbl canal-t" x="{kx-22}" y="{ky+22}" transform="rotate(43.3 {kx-22} {ky+22})">Ranh giải tỏa kênh Tham Lương – Bến Cát</text>')

# nhãn các thửa (P1, theo tài liệu 02/CT-UB)
for name, (n, e) in {"Thửa 37 · L · 4.169 m²": (872, 345), "Thửa 41 · L · 2.376 m²": (872, 395),
                     "Thửa 92 · L · 1.802": (870, 430), "Thửa 93 · L · 1.037": (880, 452),
                     "Thửa 35–36 · Ao": (850, 305)}.items():
    x, y = pt((n, e))
    out.append(f'<text class="lbl parcel" x="{x}" y="{y}" text-anchor="middle">{name}</text>')
ax, ay = pt((914, 380))
out.append(f'<text class="lbl road" x="{ax}" y="{ay-44}" text-anchor="middle">Đường quy hoạch · lộ giới 20 m (ranh cung tròn)</text>')

# đánh số điểm góc chính
for i in [0, 5, 6, 7, 13, 14, 16, 20, 32, 36, 37, 39]:
    x, y = pt(P1[i])
    out.append(f'<circle class="pt" cx="{x}" cy="{y}" r="3.2"/><text class="ptl" x="{x+5}" y="{y-5}">{i+1}</text>')

# kích thước cạnh chính P1
for i in [0, 4, 6, 13, 37, 38, 39]:
    a, b = P1[i], P1[(i + 1) % len(P1)]
    (x1, y1), (x2, y2) = pt(a), pt(b)
    L = math.dist(a, b)
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    out.append(f'<text class="dim" x="{cx:.1f}" y="{cy-4:.1f}" text-anchor="middle" '
               f'transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})">{L:.2f}</text>')

# mũi tên bắc + thước tỷ lệ
out.append(f'<g transform="translate({W-30},10)"><path class="north" d="M0,-18 L9,14 L0,7 L-9,14 Z"/>'
           f'<text class="ptl" x="0" y="32" text-anchor="middle">B</text></g>')
sb = 50 * S
out.append(f'<g transform="translate(0,{H+34})"><rect class="sb1" x="0" y="0" width="{sb/2:.1f}" height="6"/>'
           f'<rect class="sb2" x="{sb/2:.1f}" y="0" width="{sb/2:.1f}" height="6"/>'
           f'<text class="gridlbl" x="0" y="20">0</text><text class="gridlbl" x="{sb/2:.1f}" y="20" text-anchor="middle">25</text>'
           f'<text class="gridlbl" x="{sb:.1f}" y="20" text-anchor="middle">50 m</text></g>')
out.append('</svg>')

svg = "\n".join(out)
dst = os.path.join(os.path.dirname(__file__), "..", "assets", "site-plan.svg")
open(dst, "w", encoding="utf-8").write(svg)
print("P1 area", round(area(P1), 1), "| P2 polygon", round(area(P2f), 1), "+ 2 cung ≈ 823 m² → ≈ 17.354 m²")
