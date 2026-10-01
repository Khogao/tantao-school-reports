"""Sinh ../MO_HINH_DAU_TU_V1.html từ fin_invest.py (dùng lại CSS của báo cáo kế hoạch)."""
import os, re
from fin_invest import run, sens, A, QLAB, compare, PA_TEN

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
r = run(); S = sens(); a = r["a"]; Q = r["Q"]; CMP = compare()
USD = 26278  # đ/USD, bình quân Q4/2025 (QĐ 425/QĐ-BXD)
f1 = lambda v: f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
f0 = lambda v: f"{v:,.0f}".replace(",", ".")
pct = lambda v: f"{v*100:.0f}%"

tpl = open(os.path.join(HERE, "report.template.html"), encoding="utf-8").read()
css = tpl[tpl.index("<style>") + 7: tpl.index("</style>")]

SER = [("dat", "Đất, pháp lý", "#3a6ec0"), ("xd", "Xây dựng", "#d95c3a"),
       ("tb", "Thiết bị", "#16977f"), ("khac", "QLDA, tư vấn, dự phòng, lãi vay", "#a15fcb")]

def stacked_chart():
    W, H, L, B, T = 900, 330, 56, 44, 28
    vmax = max(q["tong"] for q in Q); top = 20 * (int(vmax / 20) + 1)
    bw = (W - L - 10) / len(Q); g = []
    for t in range(0, top + 1, 20 if top <= 120 else 40):
        y = T + (H - T - B) * (1 - t / top)
        g.append(f'<line x1="{L}" x2="{W-10}" y1="{y:.1f}" y2="{y:.1f}" class="ch-grid"/>'
                 f'<text x="{L-8}" y="{y+4:.1f}" class="ch-ax" text-anchor="end">{t}</text>')
    for i, q in enumerate(Q):
        x = L + i * bw + 3; y0 = H - B
        segs = []
        for k, name, col in SER:
            h = (H - T - B) * q[k] / top
            if h <= 0.01: continue
            segs.append((y0 - h, h, col))
            y0 -= h
        for j, (y, h, col) in enumerate(segs):
            hh = max(0.0, h - (2 if j < len(segs) - 1 else 0))  # 2px khe giữa các lớp
            rx = 4 if j == len(segs) - 1 else 0
            g.append(f'<rect x="{x:.1f}" y="{y+ (2 if j < len(segs)-1 else 0):.1f}" width="{bw-6:.1f}" height="{hh:.1f}" fill="{col}" rx="{rx}"/>')
        tip = " · ".join(f"{n}: {f1(q[k])}" for k, n, c in SER if q[k] > 0.05)
        g.append(f'<rect x="{x-3:.1f}" y="{T}" width="{bw:.1f}" height="{H-T-B}" fill="transparent" class="hit" '
                 f'data-tip="{QLAB[i]} — tổng {f1(q["tong"])} tỷ&#10;{tip}"/>')
        g.append(f'<text x="{x+(bw-6)/2:.1f}" y="{H-B+16}" class="ch-ax" text-anchor="middle">{QLAB[i]}</text>')
    for i in (3, 10, 13):   # nhãn trực tiếp các quý đỉnh
        q = Q[i]; x = L + i * bw + 3 + (bw - 6) / 2; y = T + (H - T - B) * (1 - q["tong"] / top) - 6
        g.append(f'<text x="{x:.1f}" y="{y:.1f}" class="ch-lbl" text-anchor="middle">{f1(q["tong"])}</text>')
    g.append(f'<text x="{L-8}" y="12" class="ch-ax" text-anchor="end">tỷ đ</text>')
    return f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Giải ngân theo quý">{"".join(g)}</svg>'

def source_chart():
    W, H, L, B, T = 900, 270, 56, 44, 28
    vmax = max(q["csh"] + q["vay"] for q in Q); top = 20 * (int(vmax / 20) + 1)
    bw = (W - L - 10) / len(Q); g = []
    for t in range(0, top + 1, 40):
        y = T + (H - T - B) * (1 - t / top)
        g.append(f'<line x1="{L}" x2="{W-10}" y1="{y:.1f}" y2="{y:.1f}" class="ch-grid"/><text x="{L-8}" y="{y+4:.1f}" class="ch-ax" text-anchor="end">{t}</text>')
    for i, q in enumerate(Q):
        x = L + i * bw + 3; y0 = H - B
        parts = [(q["csh"], "#3a6ec0"), (q["vay"], "#16977f")]
        parts = [p for p in parts if p[0] > 0.01]
        for j, (v, col) in enumerate(parts):
            h = (H - T - B) * v / top
            gap = 2 if j < len(parts) - 1 else 0
            g.append(f'<rect x="{x:.1f}" y="{y0-h+gap:.1f}" width="{bw-6:.1f}" height="{max(0,h-gap):.1f}" fill="{col}" rx="{4 if j==len(parts)-1 else 0}"/>')
            y0 -= h
        g.append(f'<rect x="{x-3:.1f}" y="{T}" width="{bw:.1f}" height="{H-T-B}" fill="transparent" class="hit" data-tip="{QLAB[i]}&#10;Vốn chủ sở hữu: {f1(q["csh"])} · Vốn vay: {f1(q["vay"])}"/>')
        g.append(f'<text x="{x+(bw-6)/2:.1f}" y="{H-B+16}" class="ch-ax" text-anchor="middle">{QLAB[i]}</text>')
    g.append(f'<text x="{L-8}" y="12" class="ch-ax" text-anchor="end">tỷ đ</text>')
    return f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Nguồn vốn theo quý">{"".join(g)}</svg>'

tot = r["total"]; dat_grp = r["dat"] + r["dat_phi"] + a["phap_ly"]
cons = r["xd_total"] + r["tb"] + r["khac"] + r["dp"]
per_hs = (tot - dat_grp) / r["hs"] * 1000

item_rows = "".join(
    f'<tr><td>{x["ten"]}</td><td class="td-right">{f0(x["qty"])} {x["unit"]}</td><td class="td-right">{f1(x["dg"])}</td>'
    f'<td>{x["code"]}</td><td class="td-right">{f1(x["k"])}</td><td class="td-right td-bold">{f1(x["val"])}</td></tr>' for x in r["rows"])

tmdt = [
    ("1", "Chi phí đất và pháp lý", dat_grp, "Nhận chuyển nhượng 16.500 m² × 10 triệu/m² (giả định); lệ phí; tư vấn pháp lý, điều chỉnh QH, đo đạc"),
    ("2", "Chi phí xây dựng", r["xd_total"], "9 hạng mục, đơn giá QĐ 425/QĐ-BXD × hệ số chuẩn quốc tế × trượt giá"),
    ("3", "Chi phí thiết bị chuyên dụng", r["tb"], "60 triệu/HS: phòng thí nghiệm, CNTT 1:1, nghe nhìn, thư viện, nội thất, sân khấu"),
    ("4", "Quản lý dự án, tư vấn, chi phí khác", r["khac"], "10% của (2)+(3): thiết kế, thẩm tra, giám sát, QLDA, bảo hiểm"),
    ("5", "Dự phòng khối lượng", r["dp"], "5% của (2)+(3)+(4); trượt giá đã tính trong đơn giá"),
    ("6", "Lãi vay trong thời gian xây dựng", r["lai"], "Vốn hóa, trả bằng vốn chủ sở hữu"),
]
tmdt_rows = "".join(f'<tr><td>{n}</td><td class="td-bold">{t}</td><td class="td-right">{f1(v)}</td><td class="td-right">{pct(v/tot)}</td><td>{d}</td></tr>' for n, t, v, d in tmdt)

q_rows = "".join(
    f'<tr><td>{QLAB[i]}</td><td class="td-right">{f1(q["dat"])}</td><td class="td-right">{f1(q["xd"])}</td><td class="td-right">{f1(q["tb"])}</td>'
    f'<td class="td-right">{f1(q["khac"])}</td><td class="td-right td-bold">{f1(q["tong"])}</td><td class="td-right">{f1(q["csh"])}</td>'
    f'<td class="td-right">{f1(q["vay"])}</td><td class="td-right">{f1(q["luy_ke"])}</td></tr>' for i, q in enumerate(Q))

def dot(i0, i1): return sum(Q[i]["csh"] for i in range(i0, i1 + 1))
dots = [("Đợt 1", "Q4/26 – Q2/27", "Pháp lý, điều chỉnh QH, đặt cọc có điều kiện 10%", dot(0, 2), "Khi HĐQT thông qua giai đoạn chuẩn bị"),
        ("Đợt 2", "Q3/27 – Q4/27", "Thanh toán nhận chuyển nhượng đất 90%", dot(3, 4), "Sau khi có quyết định điều chỉnh QH"),
        ("Đợt 3", "Q1/28 – Q4/28", "Thiết kế, khởi công, phần vốn đối ứng xây dựng", dot(5, 8), "Sau quyết định chấp thuận chủ trương đầu tư"),
        ("Đợt 4", "Q1/29 – Q4/29", "Vốn đối ứng thi công giai đoạn 1–2, lãi vay", dot(9, 12), "Theo tiến độ thi công"),
        ("Đợt 5", "Q1/30 – Q3/30", "Hoàn thiện, thiết bị, lãi vay", dot(13, 15), "Trước nghiệm thu, cho phép hoạt động")]
dot_rows = "".join(f'<tr><td class="td-bold">{d}</td><td>{t}</td><td>{c}</td><td class="td-right td-bold">{f1(v)}</td><td class="td-right">{pct(v/r["equity"])}</td><td>{k}</td></tr>' for d, t, c, v, k in dots)

def _sr(i, n, t, e, l):
    base = ' class="tr-base"' if i == 0 else ''
    d = "—" if i == 0 else (("+" if t - S[0][1] >= 0 else "−") + f1(abs(t - S[0][1])))
    return (f'<tr{base}><td class="td-bold">{n}</td><td class="td-right">{f1(t)}</td><td class="td-right">{d}</td>'
            f'<td class="td-right">{f1(e)}</td><td class="td-right">{f1(l)}</td></tr>')
sens_rows = "".join(_sr(i, *x) for i, x in enumerate(S))

gfa = r["gfa"]
def _cmp_row(c):
    ok = c["md"] <= 0.40
    cls = ' class="tr-base"' if c["pa"] == a["phuong_an"] else ''
    tag = '<span class="tag ok">Đạt</span>' if ok else '<span class="tag no">Vượt</span>'
    return (f'<tr{cls}><td class="td-bold">{c["ten"]}</td><td class="td-right">{f0(c["gfa"])}</td><td class="td-right">{f0(c["fp"])}</td>'
            f'<td class="td-right">{pct(c["md"])} {tag}</td><td class="td-right">{f1(c["hs_sd"]).replace(",0","")}</td>'
            f'<td class="td-right">{f1(c["open_hs"])}</td><td class="td-right">{f0(c["total"])}</td></tr>')
cmp_rows = "".join(_cmp_row(c) for c in CMP)
html = f'''<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mô Hình Đầu Tư — Trường Liên Cấp Tân Tạo</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>{css}
  .chart{{width:100%;min-width:720px;height:auto;display:block}}
  .chart .ch-grid{{stroke:#e3e9ee;stroke-width:1}}
  .chart .ch-ax{{font:11px Inter,sans-serif;fill:var(--ink-soft)}}
  .chart .ch-lbl{{font:600 12px Inter,sans-serif;fill:var(--ink)}}
  .chart .hit{{cursor:crosshair}} .chart .hit:hover{{fill:rgba(30,45,69,0.05)}}
  .chart-box{{background:#fff;border:1px solid var(--border);border-radius:3px;padding:16px;overflow-x:auto;position:relative}}
  .legend-row{{display:flex;flex-wrap:wrap;gap:6px 20px;font-size:12.5px;color:var(--ink-mid);margin:0 0 10px}}
  .legend-row i{{display:inline-block;width:12px;height:12px;border-radius:2px;vertical-align:-1px;margin-right:6px}}
  #tip{{position:fixed;pointer-events:none;background:var(--deep);color:#fff;font:12.5px/1.5 Inter,sans-serif;padding:8px 11px;border-radius:3px;white-space:pre-line;z-index:200;display:none;max-width:320px;box-shadow:0 4px 14px rgba(0,0,0,.18)}}
  .tbl-sm table{{font-size:13px}} .tbl-sm td,.tbl-sm th{{padding:8px 10px}}
</style></head><body>
<nav id="sidebar" aria-label="Mục lục">
  <div class="sb-header"><div class="sb-logo"><div class="sb-diamond"></div><div class="sb-logo-text">Trường Liên Cấp<br>Tân Tạo</div></div>
  <div class="sb-tagline">Mô hình đầu tư giai đoạn xây dựng<br>Chuẩn quốc tế · tham chiếu SSIS</div></div>
  <div class="sb-nav"><div class="nav-label">Nội dung</div>
    <a class="nav-item" href="#s1">1. Tóm tắt</a><a class="nav-item" href="#s2">2. Cơ sở và giả định</a><a class="nav-item" href="#pa">2b. Hạng mục cho 1,7 ha</a>
    <a class="nav-item" href="#s3">3. Tổng mức đầu tư</a><a class="nav-item" href="#s4">4. Lịch giải ngân</a>
    <a class="nav-item" href="#s5">5. Nguồn vốn &amp; góp vốn</a><a class="nav-item" href="#s6">6. Độ nhạy</a>
    <a class="nav-item" href="#s7">7. Ghi chú &amp; kiến nghị</a>
    <div class="nav-label" style="margin-top:14px">Tài liệu liên quan</div>
    <a class="nav-item" href="KE_HOACH_THUC_HIEN_V1.html">Kế hoạch thực hiện V1</a></div>
  <div class="sb-footer">Phiên bản V1 — Tháng 9/2026<br><strong>Người lập:</strong> Bộ phận Đầu tư<br>Tài liệu nội bộ — số liệu sơ bộ</div>
</nav>
<main id="main">
<header class="hero">
  <div class="hero-tag"><div class="hero-tag-dot"></div><span>Tài liệu nội bộ — Mô hình đầu tư sơ bộ</span></div>
  <h1>Tổng Mức Đầu Tư &amp; Nguồn Vốn<br>Giai Đoạn Xây Dựng Cơ Sở Vật Chất</h1>
  <p class="hero-sub">Trường liên cấp chuẩn quốc tế, tham chiếu Saigon South International School (SSIS) · {f0(r["hs"])} học sinh, 100 chỗ nội trú · Khu đất 17.356,5 m² · Giải ngân 10/2026 – 9/2030</p>
  <div class="hero-stats">
    <div class="stat-box"><div class="stat-label">Tổng mức đầu tư</div><div class="stat-value">{f0(tot)}<span class="stat-unit"> tỷ đ</span></div><div class="stat-note">≈ {f1(tot*1e9/USD/1e6)} triệu USD</div></div>
    <div class="stat-box"><div class="stat-label">Vốn chủ sở hữu</div><div class="stat-value">{f0(r["equity"])}<span class="stat-unit"> tỷ đ</span></div><div class="stat-note">{pct(r["equity"]/tot)} tổng mức đầu tư · góp 5 đợt</div></div>
    <div class="stat-box"><div class="stat-label">Vốn vay</div><div class="stat-value">{f0(r["loan"])}<span class="stat-unit"> tỷ đ</span></div><div class="stat-note">{pct(r["loan"]/tot)} · giải ngân từ Q3/2028</div></div>
    <div class="stat-box"><div class="stat-label">Suất đầu tư (không gồm đất)</div><div class="stat-value">{f0(per_hs)}<span class="stat-unit"> tr/HS</span></div><div class="stat-note">≈ {f0(per_hs*1e6/USD)} USD/học sinh</div></div>
  </div>
</header>
<div class="content">

<section class="section" id="s1">
  <div class="sec-header"><div class="sec-num">01</div><div><div class="sec-label">Phần 1</div><h2 class="sec-title">Tóm Tắt</h2></div></div>
  <p>Bộ phận Đầu tư lập mô hình sơ bộ cho <strong>giai đoạn đầu tư xây dựng cơ sở vật chất</strong>: tổng mức đầu tư, lịch giải ngân khớp tiến độ trong Kế hoạch thực hiện V1, và cơ cấu nguồn vốn. Mô hình chưa gồm chi phí vận hành, doanh thu học phí và chi phí trước khai giảng; các phần này sẽ trình ở phương án kinh doanh.</p>
  <div class="card-grid three">
    <div class="card deep"><div class="card-kicker">Đất và pháp lý</div><div class="card-title">{f0(dat_grp)} tỷ · {pct(dat_grp/tot)}</div><p>Giải ngân chủ yếu Q3–Q4/2027, sau khi có quyết định điều chỉnh quy hoạch. Toàn bộ bằng vốn chủ sở hữu.</p></div>
    <div class="card coral"><div class="card-kicker">Xây dựng và thiết bị</div><div class="card-title">{f0(r["xd_total"]+r["tb"])} tỷ · {pct((r["xd_total"]+r["tb"])/tot)}</div><p>Khoảng {f0(gfa)} m² sàn; thi công 07/2028 – 05/2030 theo hai giai đoạn. Vốn vay chiếm {pct(a["ty_le_vay_xd"])} phần này.</p></div>
    <div class="card teal"><div class="card-kicker">Đối chiếu quy định</div><div class="card-title">Vượt mức tối thiểu</div><p>Suất đầu tư không gồm đất khoảng {f0(per_hs)} triệu/HS, cao hơn nhiều mức tối thiểu cho trường phổ thông tư thục theo quy định hiện hành. Vốn chủ sở hữu {pct(r["equity"]/tot)}, trên mức tối thiểu 20% cho dự án dưới 20 ha.</p></div>
  </div>
  <div class="callout"><p><strong>Điểm quyết định về vốn.</strong> Trước khi có ý kiến chủ trương điều chỉnh quy hoạch (dự kiến Q1/2027), vốn cần góp chỉ khoảng <strong>{f1(dot(0,2))} tỷ đồng</strong>, gồm pháp lý và đặt cọc có điều kiện. Khoản lớn nhất (đợt 2, khoảng {f0(dot(3,4))} tỷ, dùng để thanh toán đất) chỉ phát sinh khi quy hoạch đã cho phép đất giáo dục.</p></div>
</section>

<section class="section" id="s2">
  <div class="sec-header"><div class="sec-num">02</div><div><div class="sec-label">Phần 2</div><h2 class="sec-title">Cơ Sở Lập &amp; Giả Định</h2></div></div>
  <div class="subsec"><h3 class="subsec-title">Chuẩn tham chiếu SSIS và quy mô đề xuất</h3>
  <div class="tbl-wrap"><table class="tbl-compare">
    <thead><tr><th>Chỉ tiêu</th><th>SSIS (Phú Mỹ Hưng)</th><th>Trường Liên cấp Tân Tạo (đề xuất)</th></tr></thead>
    <tbody>
      <tr><td class="td-bold">Diện tích khuôn viên</td><td>Khoảng 6 ha</td><td>Khoảng 1,7 ha (16.800 m² sử dụng)</td></tr>
      <tr><td class="td-bold">Học sinh</td><td>Trên 1.500 (mầm non – lớp 12)</td><td>{f0(r["hs"])} (tiểu học {A["hs"]["Tiểu học"]}, THCS {A["hs"]["THCS"]}, THPT {A["hs"]["THPT"]}); 48 lớp, sĩ số khoảng 22</td></tr>
      <tr><td class="td-bold">Thể thao</td><td>2 nhà thi đấu có điều hòa, bể bơi 6 làn, 3 sân bóng</td><td>Khối thể thao – sự kiện xếp chồng: bể bơi trong nhà 25 m × 4 làn ở tầng 1, nhà đa năng 1 sân kiêm hội trường 600 chỗ ở tầng 2; sân thể thao trên mái; sân bóng mini 5 người</td></tr>
      <tr><td class="td-bold">Học thuật</td><td>Trung tâm STEAM 7.100 m², 3 thư viện, nhà hát</td><td>STEAM, phòng thí nghiệm, thư viện tích hợp trong khối học tập 12.000 m²; hội trường dùng chung với nhà đa năng</td></tr>
      <tr><td class="td-bold">Nội trú</td><td>—</td><td>100 giường, giai đoạn 2 (khối nhà ngủ nhóm F1.1)</td></tr>
      <tr><td class="td-bold">Tổ chức không gian</td><td>Khuôn viên rộng, thấp tầng</td><td>Khuôn viên nén, 5 tầng, 1 tầng hầm; khoảng {f0(gfa)} m² sàn nổi (khoảng {f0(gfa/r["hs"])} m² sàn/HS), mật độ xây dựng {pct(r["fp"]/a["dat_m2"])}</td></tr>
    </tbody></table></div>
  <p class="note-sm" style="font-size:13.5px;color:var(--ink-soft)">Khu đất nhỏ bằng khoảng 1/3,5 SSIS nên quy mô học sinh được giảm để giữ chất lượng không gian; phương án B cần hệ số sử dụng đất khoảng 1,1 và mật độ khoảng 32%, còn dư địa so với chỉ tiêu đề xuất (mật độ ≤ 40%, hệ số ≤ 1,6).</p></div>
  <div class="subsec"><h3 class="subsec-title">Giả định chính</h3>
  <div class="tbl-wrap"><table>
    <thead><tr><th>Giả định</th><th>Giá trị</th><th>Căn cứ</th></tr></thead><tbody>
      <tr><td class="td-bold">Đơn giá gốc</td><td>Suất vốn, suất chi phí năm 2025, mức độ 2</td><td>QĐ 425/QĐ-BXD ngày 30/03/2026 của Bộ Xây dựng</td></tr>
      <tr><td class="td-bold">Hệ số chuẩn quốc tế</td><td>{f1(a["K_qt"])} cho khối học tập, STEAM; 1,3–1,5 cho hạng mục thể thao, nội trú</td><td>Giả định của Bộ phận Đầu tư: điều hòa trung tâm, mặt dựng, hoàn thiện, âm học, hạ tầng CNTT. Chỉnh sau khi có dự toán sơ bộ</td></tr>
      <tr><td class="td-bold">Trượt giá</td><td>3,5%/năm, quy về giữa kỳ thi công (hệ số {f1(a["K_tg"])})</td><td>Giả định; độ nhạy 6%/năm ở Phần 6</td></tr>
      <tr><td class="td-bold">Giá nhận chuyển nhượng đất</td><td>10 triệu/m² × 16.500 m²</td><td><strong>Giả định</strong>. Bảng giá đất nông nghiệp 2026 tại Tân Tạo là 1,7 triệu/m²; giá thỏa thuận thực tế cần khảo sát</td></tr>
      <tr><td class="td-bold">Tiền thuê đất, chuyển mục đích</td><td>0 trong kịch bản cơ sở</td><td>Đề nghị miễn theo chính sách xã hội hóa giáo dục; nếu không được miễn sẽ phát sinh thêm</td></tr>
      <tr><td class="td-bold">Vốn vay</td><td>{pct(a["ty_le_vay_xd"])} phần xây dựng, thiết bị, chi phí khác, dự phòng; lãi {pct(a["lai_suat"])}/năm</td><td>Giải ngân theo tiến độ thi công; lãi trong thời gian xây dựng được vốn hóa</td></tr>
      <tr><td class="td-bold">Tỷ giá</td><td>{f0(USD)} đ/USD</td><td>Bình quân Q4/2025 theo QĐ 425/QĐ-BXD</td></tr>
    </tbody></table></div></div>
</section>

<section class="section" id="pa">
  <div class="sec-header"><div class="sec-num">2b</div><div><div class="sec-label">Phần 2b</div><h2 class="sec-title">Hạng Mục Phù Hợp Khu Đất 1,7 Ha</h2></div></div>
  <p>Khu đất chỉ bằng khoảng 1/3,5 khuôn viên SSIS. Nếu bố trí đủ các khối riêng như SSIS (nhà hát, nhà thi đấu 2 sân, bể bơi, sân bóng), riêng diện tích chiếm đất đã vượt xa mật độ xây dựng cho phép. Bộ phận Đầu tư so sánh ba phương án trên cùng quy mô {f0(r["hs"])} học sinh và 16.800 m² đất sử dụng:</p>
  <div class="tbl-wrap"><table class="tbl-compare">
    <thead><tr><th>Phương án</th><th class="td-right">m² sàn nổi</th><th class="td-right">m² chiếm đất</th><th class="td-right">Mật độ XD (≤ 40%)</th><th class="td-right">Hệ số SDĐ</th><th class="td-right">Đất trống m²/HS</th><th class="td-right">TMĐT (tỷ đ)</th></tr></thead>
    <tbody>{cmp_rows}</tbody></table></div>
  <div class="card-grid three">
    <div class="card coral"><div class="card-kicker">Phương án A</div><div class="card-title">Không đặt vừa khu đất</div><p>Các khối một tầng (nhà hát, nhà thi đấu 2 sân, bể bơi) chiếm khoảng 5.000 m² đất. Mật độ khoảng 57%, chỉ còn khoảng 6,8 m² đất trống cho mỗi học sinh.</p></div>
    <div class="card teal"><div class="card-kicker">Phương án B · khuyến nghị</div><div class="card-title">Giữ tiện ích cốt lõi, nén theo chiều cao</div><ul>
      <li>Bể bơi ở tầng 1, nhà đa năng kiêm hội trường ở tầng 2 trong cùng một khối</li>
      <li>STEAM, thư viện tích hợp trong khối học tập 5 tầng</li>
      <li>Sân thể thao trên mái khối học tập</li>
      <li>Nội trú 100 giường ở giai đoạn 2</li></ul></div>
    <div class="card deep"><div class="card-kicker">Phương án C</div><div class="card-title">Tinh gọn, chi phí thấp nhất</div><p>Bỏ bể bơi và nội trú, chỉ giữ nhà đa năng. Rẻ hơn B khoảng {f0(CMP[1]["total"]-CMP[2]["total"])} tỷ đồng, nhưng thiếu hai tiện ích mà phụ huynh phân khúc quốc tế thường đòi hỏi.</p></div>
  </div>
  <div class="note"><p><strong>Hướng bù đắp diện tích:</strong> phần còn lại của ô công viên II.X1 (khoảng 2,6 ha, chức năng công viên – cây xanh – thể dục thể thao) nằm liền kề. Có thể nghiên cứu phương án nhà trường đầu tư hoặc khai thác sân thể thao công cộng trong công viên theo hình thức xã hội hóa: học sinh dùng trong giờ học, cộng đồng dùng ngoài giờ. Phương án này còn hỗ trợ luận cứ “bù cây xanh, phục vụ cộng đồng” trong hồ sơ điều chỉnh quy hoạch. Cơ chế cụ thể cần làm rõ với UBND phường theo quy định hiện hành về quản lý công viên.</p></div>
</section>

<section class="section" id="s3">
  <div class="sec-header"><div class="sec-num">03</div><div><div class="sec-label">Phần 3</div><h2 class="sec-title">Tổng Mức Đầu Tư</h2></div></div>
  <div class="tbl-wrap"><table>
    <thead><tr><th>#</th><th>Khoản mục</th><th class="td-right">Tỷ đồng</th><th class="td-right">Tỷ trọng</th><th>Cách tính</th></tr></thead>
    <tbody>{tmdt_rows}<tr class="td-total-row"><td></td><td>Tổng mức đầu tư</td><td class="td-right">{f1(tot)}</td><td class="td-right">100%</td><td>≈ {f1(tot*1e9/USD/1e6)} triệu USD</td></tr></tbody></table></div>
  <div class="subsec" style="margin-top:28px"><h3 class="subsec-title">Chi tiết chi phí xây dựng</h3>
  <div class="tbl-wrap tbl-sm"><table>
    <thead><tr><th>Hạng mục</th><th class="td-right">Quy mô</th><th class="td-right">Đơn giá BXD 2025 (tr đ)</th><th>Mã hiệu</th><th class="td-right">Hệ số</th><th class="td-right">Thành tiền (tỷ đ)</th></tr></thead>
    <tbody>{item_rows}<tr class="td-total-row"><td colspan="5">Cộng chi phí xây dựng (đã nhân hệ số trượt giá {f1(a["K_tg"])})</td><td class="td-right">{f1(r["xd_total"])}</td></tr></tbody></table></div>
  <p style="font-size:13.5px;color:var(--ink-soft)">Đơn giá BXD của khối học tập, hành chính, nội trú đã gồm thiết bị công trình (thang máy, điều hòa, PCCC, cấp điện, cấp thoát nước). Hạ tầng kỹ thuật, cảnh quan là ước tính vì BXD không công bố suất riêng.</p></div>
</section>

<section class="section" id="s4">
  <div class="sec-header"><div class="sec-num">04</div><div><div class="sec-label">Phần 4</div><h2 class="sec-title">Lịch Giải Ngân Theo Tiến Độ</h2></div></div>
  <p>Giải ngân bám các mốc trong Gantt của Kế hoạch thực hiện V1: đặt cọc đất T4–T6, thanh toán đất T11–T13 sau khi điều chỉnh quy hoạch; tư vấn thiết kế từ T6; thi công giai đoạn 1 từ T22 (07/2028) đến T35, giai đoạn 2 từ T33 đến T44; thiết bị T40–T46.</p>
  <div class="chart-box">
    <div class="legend-row">{"".join(f'<span><i style="background:{c}"></i>{n}</span>' for k,n,c in SER)}</div>
    {stacked_chart()}
  </div>
  <details style="margin-top:14px"><summary style="cursor:pointer;font-size:14px;color:var(--teal);font-weight:500">Xem bảng số liệu theo quý</summary>
  <div class="tbl-wrap tbl-sm"><table>
    <thead><tr><th>Quý</th><th class="td-right">Đất, pháp lý</th><th class="td-right">Xây dựng</th><th class="td-right">Thiết bị</th><th class="td-right">Khác, DP, lãi</th><th class="td-right">Tổng</th><th class="td-right">Vốn CSH</th><th class="td-right">Vốn vay</th><th class="td-right">Lũy kế</th></tr></thead>
    <tbody>{q_rows}</tbody></table></div></details>
</section>

<section class="section" id="s5">
  <div class="sec-header"><div class="sec-num">05</div><div><div class="sec-label">Phần 5</div><h2 class="sec-title">Nguồn Vốn &amp; Kế Hoạch Góp Vốn</h2></div></div>
  <div class="pa-grid">
    <div class="tbl-wrap" style="margin:0"><table class="tbl-compare">
      <thead><tr><th>Nguồn</th><th class="td-right">Tỷ đồng</th><th class="td-right">Tỷ trọng</th></tr></thead>
      <tbody><tr><td class="td-bold">Vốn chủ sở hữu</td><td class="td-right">{f1(r["equity"])}</td><td class="td-right">{pct(r["equity"]/tot)}</td></tr>
      <tr><td class="td-bold">Vốn vay ngân hàng</td><td class="td-right">{f1(r["loan"])}</td><td class="td-right">{pct(r["loan"]/tot)}</td></tr>
      <tr class="td-total-row"><td>Tổng</td><td class="td-right">{f1(tot)}</td><td class="td-right">100%</td></tr></tbody></table></div>
    <ul class="bullet-list">
      <li><span>Vốn chủ sở hữu trả toàn bộ chi phí đất, pháp lý, tư vấn trước khởi công, phần đối ứng xây dựng và lãi vay trong thời gian xây dựng.</span></li>
      <li><span>Vốn vay chỉ giải ngân từ Q3/2028, khi đã có quyết định chấp thuận chủ trương, giấy chứng nhận quyền sử dụng đất và giấy phép xây dựng; tài sản bảo đảm là quyền sử dụng đất và công trình hình thành trong tương lai.</span></li>
      <li><span>Với mô hình không vì lợi nhuận, vốn góp là vốn dài hạn: nhà đầu tư cam kết không rút vốn và không hưởng lợi tức theo quy định hiện hành.</span></li>
    </ul>
  </div>
  <div class="chart-box" style="margin-top:14px">
    <div class="legend-row"><span><i style="background:#3a6ec0"></i>Vốn chủ sở hữu</span><span><i style="background:#16977f"></i>Vốn vay</span></div>
    {source_chart()}
  </div>
  <div class="subsec" style="margin-top:28px"><h3 class="subsec-title">Kế hoạch góp vốn theo đợt, gắn mốc pháp lý</h3>
  <div class="tbl-wrap"><table>
    <thead><tr><th>Đợt</th><th>Thời gian</th><th>Mục đích</th><th class="td-right">Tỷ đồng</th><th class="td-right">% vốn CSH</th><th>Điều kiện giải ngân</th></tr></thead>
    <tbody>{dot_rows}<tr class="td-total-row"><td colspan="3">Tổng vốn chủ sở hữu</td><td class="td-right">{f1(r["equity"])}</td><td class="td-right">100%</td><td></td></tr></tbody></table></div></div>
</section>

<section class="section" id="s6">
  <div class="sec-header"><div class="sec-num">06</div><div><div class="sec-label">Phần 6</div><h2 class="sec-title">Độ Nhạy</h2></div></div>
  <div class="tbl-wrap"><table>
    <thead><tr><th>Kịch bản</th><th class="td-right">Tổng mức đầu tư</th><th class="td-right">Chênh lệch</th><th class="td-right">Vốn CSH</th><th class="td-right">Vốn vay</th></tr></thead>
    <tbody>{sens_rows}</tbody></table></div>
  <div class="note"><p><strong>Hai biến lớn nhất</strong> là giá nhận chuyển nhượng đất và mức hoàn thiện chuẩn quốc tế: mỗi biến làm tổng mức đầu tư dao động khoảng ±80 tỷ đồng. Cần chốt sớm bằng khảo sát giá đất và dự toán sơ bộ của tư vấn thiết kế.</p></div>
</section>

<section class="section" id="s7">
  <div class="sec-header"><div class="sec-num">07</div><div><div class="sec-label">Phần 7</div><h2 class="sec-title">Ghi Chú &amp; Kiến Nghị</h2></div></div>
  <ul class="bullet-list">
    <li><span><strong>Chưa gồm:</strong> chi phí trước khai giảng (tuyển dụng, đào tạo, marketing), vốn lưu động, tiền thuê đất nếu không được miễn, chi phí đền bù ngoài giá thỏa thuận.</span></li>
    <li><span><strong>Mức chính xác:</strong> sơ bộ, khoảng ±20%. Dùng để quyết định chủ trương và kế hoạch góp vốn; thay bằng tổng mức đầu tư trong báo cáo nghiên cứu khả thi khi có thiết kế cơ sở.</span></li>
    <li><span><strong>Kiến nghị:</strong> HĐQT thông qua đợt 1 (khoảng {f1(dot(0,2))} tỷ đồng); giao Bộ phận Đầu tư khảo sát giá đất thỏa thuận và mời 2–3 đơn vị tư vấn lập ý tưởng và dự toán sơ bộ trước Q2/2027.</span></li>
  </ul>
  <footer class="doc-foot">Mô hình tính bằng mã nguồn trong thư mục source/ (fin_invest.py). Các giả định ở Phần 2 có thể thay đổi để cập nhật toàn bộ số liệu. Bộ phận Đầu tư · Phiên bản V1 · 30/09/2026.</footer>
</section>
</div></main>
<div id="tip" role="tooltip"></div>
<script>
(function(){{
  const tip=document.getElementById('tip');
  document.querySelectorAll('.chart .hit').forEach(el=>{{
    el.addEventListener('mousemove',e=>{{tip.textContent=el.dataset.tip;tip.style.display='block';
      const x=Math.min(e.clientX+14,innerWidth-330);tip.style.left=x+'px';tip.style.top=(e.clientY+14)+'px'}});
    el.addEventListener('mouseleave',()=>tip.style.display='none');
  }});
  const links=[...document.querySelectorAll('.nav-item[href^="#"]')];
  const secs=links.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
  function on(){{let cur=secs[0];for(const s of secs){{if(s.getBoundingClientRect().top<140)cur=s}}
    links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+cur.id))}}
  document.addEventListener('scroll',on,{{passive:true}});on();
}})();
</script>
</body></html>'''
open(os.path.join(ROOT, "MO_HINH_DAU_TU_V1.html"), "w", encoding="utf-8").write(html)
print("MO_HINH_DAU_TU_V1.html", len(html))
