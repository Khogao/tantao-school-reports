"""Build báo cáo: chèn sơ đồ ranh (SVG) + bảng Gantt vào template -> ../index.html
Chạy:  python make_siteplan.py && python build.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
M = 48                      # T1 = 10/2026 ... T48 = 9/2030
START_Y, START_M = 2026, 10

C = {"crit": "var(--coral)", "edu": "var(--deep-light)", "build": "var(--teal)",
     "team": "var(--amber)", "prep": "var(--border-str)", "doc": "var(--deep-light)",
     "land": "var(--teal)", "opt": "var(--border-str)"}

LEGAL = [
    ("1 · Pháp nhân", [
        ("Thỏa thuận thành viên, điều lệ, cam kết không vì lợi nhuận", "Nhà đầu tư, luật sư", 1, 1, "doc"),
        ("Đăng ký doanh nghiệp", "Sở Tài chính", 2, 2, "crit"),
    ]),
    ("2 · Thông tin quy hoạch & pháp lý đất", [
        ("Xin văn bản cung cấp thông tin quy hoạch", "Sở QH-KT", 1, 2, "crit"),
        ("Bàn giao CAD gốc, trích lục tờ 196, đo chỉnh lý", "Đo đạc, VPĐKĐĐ", 1, 2, "land"),
        ("Kiểm tra pháp lý từng thửa, xác định đất công", "Luật sư", 1, 3, "land"),
    ]),
    ("3 · Chủ trương điều chỉnh quy hoạch", [
        ("Báo cáo luận cứ, phương án bù cây xanh, ý tưởng QH", "Bộ phận ĐT, tư vấn", 2, 3, "doc"),
        ("Nộp đề xuất; làm việc UBND phường, Sở QH-KT", "Phường, Sở QH-KT", 3, 4, "crit"),
        ("UBND TP có ý kiến chủ trương điều chỉnh", "UBND TP", 4, 4, "ms"),
    ]),
    ("4 · Điều chỉnh cục bộ quy hoạch phân khu 1/2000", [
        ("Báo cáo rà soát quy hoạch; lập hồ sơ điều chỉnh cục bộ", "UBND phường, tư vấn QH", 5, 6, "doc"),
        ("Lấy ý kiến cơ quan (15 ngày) và cộng đồng (20–30 ngày)", "UBND phường", 7, 8, "crit"),
        ("Ý kiến Sở QH-KT; thẩm định hồ sơ (≈20 ngày)", "Sở QH-KT, phòng chuyên môn", 8, 9, "crit"),
        ("Phê duyệt (≈10 ngày), công bố (≤15 ngày)", "UBND phường", 10, 10, "ms"),
        ("Cập nhật kế hoạch sử dụng đất hằng năm", "Sở NN&MT", 10, 12, "land"),
    ]),
    ("5 · Quyền sử dụng đất", [
        ("Đàm phán, đặt cọc có điều kiện với chủ đất", "Bộ phận ĐT", 3, 6, "land"),
        ("Văn bản cho phép TCKT nhận chuyển nhượng đất NN", "UBND TP", 10, 12, "crit"),
        ("Ký chuyển nhượng, công chứng, đăng ký biến động", "VPĐKĐĐ", 11, 13, "crit"),
        ("Dự phòng: đề nghị thu hồi phần còn lại (NQ 254)", "HĐND TP", 13, 17, "opt"),
    ]),
    ("6 · Chấp thuận chủ trương đầu tư", [
        ("Lập hồ sơ đề xuất dự án", "Bộ phận ĐT", 9, 11, "doc"),
        ("Nộp hồ sơ; lấy ý kiến sở ngành; thẩm định", "Sở Tài chính", 12, 14, "crit"),
        ("Quyết định chấp thuận chủ trương và nhà đầu tư", "Chủ tịch UBND TP", 14, 14, "ms"),
    ]),
    ("7 · Sau chủ trương", [
        ("Chuyển mục đích (đất lúa không phải trình HĐND), cho thuê đất", "Sở NN&MT, UBND TP", 15, 18, "crit"),
        ("Xác định tiền thuê đất, ưu đãi; ký hợp đồng thuê", "Sở NN&MT, Thuế", 17, 19, "land"),
        ("Cấp giấy chứng nhận quyền sử dụng đất", "VPĐKĐĐ", 20, 20, "ms"),
        ("Hồ sơ cho phép thành lập trường", "Sở GD&ĐT", 20, 24, "edu"),
    ]),
]

# (tên, bên thực hiện, tháng bắt đầu, tháng kết thúc, loại)  — loại "ms" = mốc
LANES = [
    ("A · Pháp lý đất – đầu tư (đường găng)", [
        ("Thành lập pháp nhân dự án", "NĐT, luật sư", 1, 2, "prep"),
        ("Thẩm định đất, thông tin quy hoạch", "Bộ phận ĐT", 1, 3, "crit"),
        ("Đề xuất chủ trương điều chỉnh QH 1/2000", "Sở QH-KT", 2, 4, "crit"),
        ("Ý kiến chủ trương điều chỉnh QH", "UBND TP", 4, 4, "ms"),
        ("Lập, lấy ý kiến, phê duyệt điều chỉnh QH", "Tư vấn QH", 5, 10, "crit"),
        ("Thỏa thuận chủ đất (cọc có điều kiện)", "Bộ phận ĐT", 3, 12, "crit"),
        ("Hồ sơ chấp thuận chủ trương đầu tư", "Sở Tài chính", 10, 13, "crit"),
        ("Quyết định chấp thuận chủ trương", "Chủ tịch UBND TP", 14, 14, "ms"),
        ("Chuyển mục đích, thuê đất, cấp GCN", "Sở NN&MT", 15, 20, "crit"),
    ]),
    ("B · Mô hình trường & giấy phép giáo dục", [
        ("Định vị, chương trình, mô hình quản trị", "Tư vấn GD", 1, 6, "edu"),
        ("Quyết định cho phép thành lập trường", "Sở GD&ĐT", 20, 24, "edu"),
        ("Cho phép hoạt động giáo dục", "Sở GD&ĐT", 42, 45, "edu"),
    ]),
    ("C · Thiết kế & cấp phép xây dựng", [
        ("Tuyển chọn ý tưởng kiến trúc", "Kiến trúc sư", 6, 10, "prep"),
        ("Tổng mặt bằng, TKCS, nghiên cứu khả thi", "Tư vấn TK", 14, 19, "build"),
        ("Thẩm định PCCC, môi trường, GPXD", "Sở XD, PC07", 18, 22, "build"),
    ]),
    ("D · Lựa chọn nhà thầu & thi công", [
        ("Tư vấn QLDA, tư vấn giám sát", "Chủ đầu tư", 16, 20, "build"),
        ("Chào thầu, chọn tổng thầu", "Chủ đầu tư", 19, 22, "build"),
        ("Thi công giai đoạn 1 (TH, THCS, khối chung)", "Tổng thầu", 22, 35, "build"),
        ("Thi công giai đoạn 2 (THPT, nhà thi đấu)", "Tổng thầu", 33, 44, "build"),
    ]),
    ("E · Đội ngũ", [
        ("Tuyển hiệu trưởng dự kiến", "HĐ trường", 18, 24, "team"),
        ("Tổ chuyên môn nòng cốt", "Hiệu trưởng", 30, 36, "team"),
        ("Tuyển và đào tạo giáo viên", "Hiệu trưởng", 38, 47, "team"),
    ]),
    ("F · Tuyển sinh & vận hành", [
        ("Thương hiệu, cộng đồng phụ huynh", "Marketing", 24, 47, "prep"),
        ("Tuyển sinh năm học đầu", "Nhà trường", 36, 47, "team"),
        ("Khai giảng năm học 2030 – 2031", "Nhà trường", 48, 48, "ms"),
    ]),
]


def months(M):
    y, m = START_Y, START_M
    for i in range(1, M + 1):
        yield i, y, m
        m += 1
        if m > 12:
            y, m = y + 1, 1


def gantt(LANES, M):
    ms = list(months(M))
    h = ['<table class="gantt"><colgroup><col class="c-name"><col class="c-who">']
    h += ['<col>' for _ in ms]
    h.append('</colgroup><thead><tr class="yr"><th class="gname" colspan="2">Hạng mục</th>')
    years = {}
    for _, y, _m in ms:
        years[y] = years.get(y, 0) + 1
    for y, n in years.items():
        h.append(f'<th colspan="{n}">{y}</th>')
    h.append('</tr><tr><th class="gname">Công việc</th><th class="gname" style="padding-left:6px">Đầu mối</th>')
    for i, y, m in ms:
        h.append(f'<th title="T{i}">{m}</th>')
    h.append('</tr></thead><tbody>')
    for lane, tasks in LANES:
        h.append(f'<tr class="lane"><td colspan="{M + 2}">{lane}</td></tr>')
        for name, who, s, e, k in tasks:
            span = f"T{s}" if s == e else f"T{s}–T{e}"
            h.append(f'<tr><td class="gname">{name} <span style="color:var(--ink-soft);font-size:11px">· {span}</span></td>'
                     f'<td class="gwho">{who}</td>')
            for i, y, m in ms:
                cls = ["m"]
                if m == 1: cls.append("y")
                elif m in (4, 7, 10): cls.append("q")
                style = ""
                if k == "ms" and i == s:
                    cls.append("ms")
                elif k != "ms" and s <= i <= e:
                    cls.append("on")
                    if i == s: cls.append("s")
                    if i == e: cls.append("e")
                    if k == "opt": cls.append("opt")
                    style = f' style="--bar:{C[k]}"'
                h.append(f'<td class="{" ".join(cls)}"{style}></td>')
            h.append('</tr>')
    h.append('</tbody></table>')
    return "".join(h)


tpl = open(os.path.join(HERE, "report.template.html"), encoding="utf-8").read()
svg = open(os.path.join(ROOT, "assets", "site-plan.svg"), encoding="utf-8").read()
out = (tpl.replace("{{SITEPLAN}}", svg).replace("{{GANTT}}", gantt(LANES, 48))
       .replace("{{GANTT_LEGAL}}", gantt(LEGAL, 24)))
for name in ("index.html", "KE_HOACH_THUC_HIEN_V1.html"):
    open(os.path.join(ROOT, name), "w", encoding="utf-8").write(out)
print("index.html", len(out), "bytes")
