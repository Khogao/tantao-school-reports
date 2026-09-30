"""Mô hình đầu tư giai đoạn xây dựng — Trường Liên cấp Tân Tạo, chuẩn quốc tế (tham chiếu SSIS).
Đơn vị: tỷ đồng. Đơn giá gốc: QĐ 425/QĐ-BXD ngày 30/03/2026 (suất vốn năm 2025, mức độ 2).
Sửa giả định trong A rồi chạy:  python fin_invest.py   -> ../MO_HINH_DAU_TU_V1.html
"""
import os, re, math, json
from copy import deepcopy

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)

A = {
    # --- quy mô ---
    "hs": {"Tiểu học": 440, "THCS": 352, "THPT": 264},     # 48 lớp × ~22 HS
    "lop": 48, "giuong_kt": 200,
    "dat_m2": 16800,              # diện tích sử dụng (ranh giao–thuê trừ lộ giới, hành lang)
    # --- hệ số ---
    "K_qt": 2.0,                  # hệ số nâng từ chuẩn mức độ 2 (BXD) lên chuẩn quốc tế
    "K_tg": 1.035 ** 3.5,         # trượt giá 2025 → giữa kỳ thi công 2028–2029 (3,5%/năm)
    # --- đất ---
    "dt_nhan_cn": 16500, "gia_dat": 10.0,   # m²; triệu đ/m² (giả định — cần khảo sát giá thỏa thuận)
    "phi_ct": 0.006, "phap_ly": 4.0,        # lệ phí trước bạ, công chứng; tư vấn pháp lý, QH, đo đạc
    "tien_thue_dat": 0.0,                   # tiền thuê đất/chuyển mục đích (0: đề nghị miễn theo xã hội hóa giáo dục)
    # --- chi phí khác ---
    "khac_pct": 0.10,             # QLDA, tư vấn thiết kế–giám sát, thẩm tra, bảo hiểm, chi phí khác
    "dp_pct": 0.05,               # dự phòng khối lượng
    "tb_chuyen_dung": 60.0,       # triệu đ/HS: lab, CNTT 1:1, AV, thư viện, nội thất, sân khấu
    # --- nguồn vốn ---
    "ty_le_vay_xd": 0.55,         # vay trên phần xây dựng + thiết bị + khác + dự phòng
    "lai_suat": 0.09,
}

# Hạng mục: (tên, khối lượng, đơn vị, đơn giá BXD 2025 triệu đ, mã BXD, K áp dụng, nhóm, giai đoạn)
def items(a):
    K = a["K_qt"]
    return [
        ("Khối học tập, phòng bộ môn (4–5 tầng, 1 hầm)", 9000, "m² sàn", 9.898 + 1.104, "11213.10", K, "XD", 1),
        ("Trung tâm STEAM, thư viện, media", 3000, "m² sàn", 8.753 + 1.277, "11213.09", K, "XD", 1),
        ("Hành chính, y tế, nhà ăn – bếp", 2500, "m² sàn", 7.433 + 0.850, "11213.07", K * 0.9, "XD", 1),
        ("Hội trường – nhà hát 500 chỗ", 500, "chỗ", 35.102, "11241.01", 1.3, "XD", 2),
        ("Nhà thi đấu đa năng 2 sân", 1600, "m² sân", 6.474, "11232.03", 1.4, "XD", 2),
        ("Bể bơi trong nhà 25 m × 6 làn", 325, "m² mặt bể", 18.701, "11233.05", 1.5, "XD", 2),
        ("Khu nội trú 200 giường", 3000, "m² sàn", 9.202, "11110.01", 1.3, "XD", 2),
        ("Sân bóng mini, sân thể thao ngoài trời", 2600, "m² sân", 1.151, "11232.01", 1.5, "XD", 2),
        ("Hạ tầng kỹ thuật, cảnh quan, cổng rào", 9000, "m² đất", 1.5, "ước tính", 1.0, "XD", 3),
    ]

def month_to_q(m):  # T1 = 10/2026 → quý 1 = Q4/2026
    return (m - 1) // 3

QLAB = []
for q in range(16):
    y = 2026 + (q + 3) // 4; qq = (q + 3) % 4 + 1
    QLAB.append(f"Q{qq}/{str(y)[2:]}")

def spread(total, m0, m1, arr, key):
    n = m1 - m0 + 1
    for m in range(m0, m1 + 1):
        arr[month_to_q(m)][key] += total / n

def run(a=None):
    a = deepcopy(a or A)
    hs = sum(a["hs"].values())
    rows = []
    for n, qty, unit, dg, code, k, grp, ph in items(a):
        base = qty * dg / 1000
        val = base * k * a["K_tg"]
        rows.append(dict(ten=n, qty=qty, unit=unit, dg=dg, code=code, k=k, base=base, val=val, ph=ph))
    xd = {1: 0, 2: 0, 3: 0}
    for r in rows: xd[r["ph"]] += r["val"]
    xd_total = sum(xd.values())
    tb = hs * a["tb_chuyen_dung"] / 1000 * a["K_tg"]
    khac = (xd_total + tb) * a["khac_pct"]
    dp = (xd_total + tb + khac) * a["dp_pct"]
    dat = a["dt_nhan_cn"] * a["gia_dat"] / 1000
    dat_phi = dat * a["phi_ct"]
    # --- giải ngân theo quý, khớp Gantt (T1 = 10/2026) ---
    Q = [dict(dat=0.0, xd=0.0, tb=0.0, khac=0.0) for _ in range(16)]
    spread(a["phap_ly"], 1, 14, Q, "dat")
    spread((dat + dat_phi) * 0.10, 4, 6, Q, "dat")           # đặt cọc có điều kiện
    spread((dat + dat_phi) * 0.90, 11, 13, Q, "dat")         # thanh toán khi QH đã điều chỉnh
    spread(xd[1], 22, 35, Q, "xd"); spread(xd[2], 33, 44, Q, "xd"); spread(xd[3], 40, 46, Q, "xd")
    spread(tb, 40, 46, Q, "tb")
    spread(khac * 0.35, 6, 22, Q, "khac")                     # tư vấn thiết kế, thẩm tra
    spread(khac * 0.65, 22, 46, Q, "khac")                    # QLDA, giám sát, bảo hiểm
    spread(dp, 22, 46, Q, "khac")
    # --- nguồn vốn ---
    loan_total = (xd_total + tb + khac + dp) * a["ty_le_vay_xd"]
    cons_q = [q["xd"] + q["tb"] + q["khac"] for q in Q]
    cons_from = 7                                             # từ quý 8 (T22) mới giải ngân vay
    cons_tot = sum(cons_q[cons_from:])
    bal, idc = 0.0, 0.0
    for i, q in enumerate(Q):
        draw = loan_total * cons_q[i] / cons_tot if i >= cons_from else 0.0
        q["vay"] = draw
        q["lai"] = (bal + draw / 2) * a["lai_suat"] / 4
        idc += q["lai"]; bal += draw
        q["csh"] = q["dat"] + q["xd"] + q["tb"] + q["khac"] + q["lai"] - draw
    for q in Q: q["khac"] += q["lai"]
    total = sum(q["dat"] + q["xd"] + q["tb"] + q["khac"] for q in Q)
    equity = total - loan_total
    cum = 0
    for q in Q:
        q["tong"] = q["dat"] + q["xd"] + q["tb"] + q["khac"]; cum += q["tong"]; q["luy_ke"] = cum
    return dict(a=a, hs=hs, rows=rows, xd=xd, xd_total=xd_total, tb=tb, khac=khac, dp=dp, dat=dat,
                dat_phi=dat_phi, lai=idc, loan=loan_total, equity=equity, total=total, Q=Q,
                gfa=sum(r["qty"] for r in rows if r["unit"] == "m² sàn") + 1800 + 2000 + 1200)

def sens():
    out = []
    def case(name, **kw):
        b = deepcopy(A); b.update(kw); r = run(b); out.append((name, r["total"], r["equity"], r["loan"]))
    case("Kịch bản cơ sở")
    case("Giá đất 6 triệu/m²", gia_dat=6.0)
    case("Giá đất 15 triệu/m²", gia_dat=15.0)
    case("Hệ số chuẩn quốc tế 1,6", K_qt=1.6)
    case("Hệ số chuẩn quốc tế 2,4", K_qt=2.4)
    case("Trượt giá 6%/năm", K_tg=1.06 ** 3.5)
    case("Lãi suất 11%/năm", lai_suat=0.11)
    case("Tỷ lệ vay 40%", ty_le_vay_xd=0.40)
    return out

if __name__ == "__main__":
    r = run()
    print(f"HS {r['hs']} | XD {r['xd_total']:.1f} TB {r['tb']:.1f} khác {r['khac']:.1f} DP {r['dp']:.1f} "
          f"đất {r['dat']+r['dat_phi']+r['a']['phap_ly']:.1f} lãi {r['lai']:.1f} | TỔNG {r['total']:.1f} | vay {r['loan']:.1f} CSH {r['equity']:.1f}")
    for x in r["rows"]: print(f"  {x['ten']}: {x['val']:.1f}")
    for i, q in enumerate(r["Q"]): print(QLAB[i], round(q["tong"], 1), round(q["csh"], 1), round(q["vay"], 1), round(q["luy_ke"], 1))
    for s in sens(): print(s[0], round(s[1], 1), round(s[2], 1), round(s[3], 1))
