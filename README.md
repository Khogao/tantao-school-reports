# Trường Liên cấp Tân Tạo — Kế hoạch thực hiện dự án

Báo cáo của Bộ phận Đầu tư trình HĐQT và nhà đầu tư thân hữu: hiện trạng khu đất, kiểm tra quy hoạch 1/2000, hành lang pháp lý 2021–2026, lộ trình pháp lý tới chấp thuận chủ trương đầu tư, các luồng phát triển song song và tiến độ Gantt.

- Báo cáo (GitHub Pages): `KE_HOACH_THUC_HIEN_V1.html` (bản trùng `index.html` để mở từ link gốc)
- Dữ liệu và script dựng lại: `source/`
  - `coords.py` — bảng tọa độ VN-2000 đọc từ bản scan (P1: 40 mốc, 11.617,1 m²; P2: 33 mốc, 17.356,5 m²)
  - `make_siteplan.py` — sinh `assets/site-plan.svg`
  - `report.template.html` + `build.py` — sinh `index.html` (chèn SVG và 2 bảng Gantt; dữ liệu tiến độ nằm trong `build.py`)
  - `wgs.json` — ranh đã chuyển sang WGS84 (dùng để phủ lên bản đồ quy hoạch)
- Ảnh tra cứu quy hoạch: `assets/qh-*.jpg` (cổng thongtinquyhoach.hochiminhcity.gov.vn, 30/09/2026)

## Build lại

```bash
cd source
python make_siteplan.py
python build.py
```

Yêu cầu: Python 3.10+ (chỉ dùng thư viện chuẩn). `pyproj` chỉ cần nếu muốn chuyển lại tọa độ sang WGS84.

## Lưu ý

- Bản scan gốc (`Tài liệu được quét.pdf`) **không** có trong repo vì chứa tên các chủ sử dụng đất; chép tay sang máy khác nếu cần.
- Mốc 4–5 của ranh 33 mốc bị mờ trên bản scan, đã hiệu chỉnh để khớp diện tích. Thay bằng CAD gốc khi có.
