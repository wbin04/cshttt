# Quản lý Cửa hàng Tạp hóa - Odoo Module

Module quản lý cửa hàng tạp hóa tích hợp đầy đủ cho Odoo 17.

## Tính năng chính

### 1. Thủ kho
- ✅ Nhập hàng từ nhà cung cấp
- ✅ Kiểm tra số lượng và chất lượng hàng hóa
- ✅ Nhập kho tự động tạo phiếu stock picking
- ✅ Xuất kho khi có đơn bán
- ✅ Kiểm kê định kỳ với điều chỉnh tồn kho

### 2. Thu ngân (POS)
- ✅ Tiếp nhận khách hàng
- ✅ Tạo đơn bán hàng qua POS
- ✅ In hóa đơn tùy chỉnh
- ✅ Xử lý thanh toán (tiền mặt/QR)
- ✅ Hỗ trợ bán nợ

### 3. Kế toán
- ✅ Ghi nhận doanh thu tự động
- ✅ Cập nhật công nợ
- ✅ Đối soát số cái
- ✅ Lập báo cáo tài chính

### 4. Chủ cửa hàng
- ✅ Dashboard tổng quan
- ✅ Phê duyệt đơn mua hàng
- ✅ Theo dõi doanh thu, lợi nhuận
- ✅ Xem báo cáo tổng hợp

## Cài đặt

1. Copy module vào thư mục addons:
```bash
cp -r taphoa_management /path/to/odoo/addons/
```

2. Cập nhật danh sách module:
   - Vào Settings > Apps > Update Apps List

3. Cài đặt module:
   - Tìm "Quản lý Cửa hàng Tạp hóa"
   - Click Install

## Cấu hình

### Bước 1: Cấu hình POS
1. Vào **Quản lý Tạp hóa > Cấu hình > Cấu hình POS**
2. Tạo hoặc chỉnh sửa POS config
3. Bật các tùy chọn:
   - Thanh toán QR
   - Cảnh báo tồn kho thấp
   - Cho phép bán nợ (nếu cần)

### Bước 2: Thêm sản phẩm
1. Vào **Quản lý Tạp hóa > Cấu hình > Sản phẩm**
2. Tạo sản phẩm mới hoặc import từ Excel
3. Cấu hình:
   - Tồn kho tối thiểu/tối đa
   - Vị trí kệ hàng
   - Nhà cung cấp
   - Hạn sử dụng

### Bước 3: Thêm nhà cung cấp
1. Vào **Quản lý Tạp hóa > Cấu hình > Đối tác**
2. Tạo đối tác mới
3. Đánh dấu là "Nhà cung cấp"

### Bước 4: Phân quyền người dùng
1. Vào **Settings > Users & Companies > Users**
2. Chọn user và phân quyền:
   - **Nhân viên**: Quyền cơ bản
   - **Thu ngân**: Sử dụng POS
   - **Thủ kho**: Quản lý kho
   - **Kế toán**: Xem báo cáo tài chính
   - **Chủ cửa hàng**: Toàn quyền

## Quy trình sử dụng

### Quy trình nhập hàng (Thủ kho)
1. **Tạo phiếu nhập kho**
   - Vào: Thủ kho > Phiếu nhập kho > Tạo mới
   - Chọn nhà cung cấp
   - Thêm sản phẩm và số lượng

2. **Kiểm tra chất lượng**
   - Click "Kiểm tra chất lượng"
   - Ghi chú về chất lượng hàng
   - Đánh dấu trạng thái từng sản phẩm

3. **Phê duyệt** (Chủ cửa hàng)
   - Review và click "Phê duyệt"

4. **Hoàn thành nhập kho**
   - Click "Hoàn thành"
   - Hệ thống tự động tạo stock picking và cập nhật tồn kho

### Quy trình bán hàng (Thu ngân)
1. **Mở phiên POS**
   - Vào: Thu ngân > Phiên bán hàng
   - Click "New Session"

2. **Bán hàng**
   - Quét mã vạch hoặc chọn sản phẩm
   - Nhập số lượng
   - Chọn phương thức thanh toán

3. **In hóa đơn**
   - Click "Print Receipt"

4. **Đóng phiên**
   - Kiểm đếm tiền
   - Close Session

### Quy trình kiểm kê (Thủ kho)
1. **Tạo phiếu kiểm kê**
   - Vào: Thủ kho > Kiểm kê kho
   - Chọn kho và vị trí

2. **Bắt đầu kiểm kê**
   - Click "Bắt đầu kiểm kê"
   - Hệ thống load danh sách sản phẩm

3. **Nhập số lượng thực tế**
   - Kiểm đếm và nhập số liệu

4. **Hoàn thành**
   - Click "Hoàn thành"
   - Hệ thống tự động điều chỉnh tồn kho

### Báo cáo (Kế toán/Chủ cửa hàng)
1. **Dashboard**
   - Vào: Chủ cửa hàng > Dashboard
   - Xem tổng quan doanh thu, chi phí, lợi nhuận

2. **Báo cáo chi tiết**
   - Vào: Kế toán > Báo cáo kế toán
   - Chọn khoảng thời gian
   - Chọn loại báo cáo
   - Generate và Export PDF/Excel

## Cấu trúc Module

```
taphoa_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── warehouse_receipt.py      # Phiếu nhập kho
│   ├── warehouse_stock_check.py  # Kiểm kê
│   ├── pos_order_custom.py       # Mở rộng POS
│   ├── accounting_report.py      # Báo cáo kế toán
│   └── product_template.py       # Mở rộng sản phẩm
├── views/
│   ├── taphoa_menu.xml           # Menu chính
│   ├── warehouse_views.xml       # Giao diện thủ kho
│   ├── cashier_views.xml         # Giao diện thu ngân
│   ├── accounting_views.xml      # Giao diện kế toán
│   ├── manager_dashboard_views.xml # Dashboard
│   └── product_template_views.xml
├── reports/
│   ├── stock_report.xml          # Báo cáo tồn kho
│   ├── sales_report.xml          # Báo cáo bán hàng
│   └── accounting_report.xml     # Báo cáo tài chính
├── security/
│   ├── taphoa_security.xml       # Nhóm quyền
│   └── ir.model.access.csv       # Access rights
├── data/
│   └── sequence_data.xml         # Sequence
├── demo/
│   └── demo_data.xml             # Dữ liệu demo
└── wizard/
    ├── __init__.py
    └── wizard_stock_export.py    # Wizard xuất báo cáo
```

## Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log file: `/var/log/odoo/odoo.log`
2. Kiểm tra quyền truy cập của user
3. Đảm bảo các module dependencies đã được cài đặt

## Tác giả

Phát triển bởi Cửa hàng Tạp hóa Team

## License

LGPL-3
