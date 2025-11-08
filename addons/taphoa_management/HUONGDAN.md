# 🏪 HƯỚNG DẪN SỬ DỤNG HỆ THỐNG QUẢN LÝ TẠP HÓA

## ✅ CÀI ĐẶT THÀNH CÔNG!

Module **Quản lý Cửa hàng Tạp hóa** đã được cài đặt thành công vào database `erp_taphoa`.

Server đang chạy tại: **http://localhost:8069**

---

## 🚀 TRUY CẬP HỆ THỐNG

1. Mở trình duyệt và truy cập: http://localhost:8069
2. Đăng nhập với:
   - **Database**: erp_taphoa
   - **Email**: admin
   - **Password**: admin

---

## 📋 CÁC CHỨC NĂNG CHÍNH

### 🏭 1. THỦ KHO
**Menu**: Quản lý Tạp hóa > Thủ kho

#### a) Nhập hàng từ nhà cung cấp:
1. Vào **Phiếu nhập kho** > Tạo mới
2. Chọn nhà cung cấp
3. Thêm sản phẩm và số lượng
4. Click **Kiểm tra chất lượng**
5. Chờ chủ cửa hàng **Phê duyệt**
6. Click **Hoàn thành** để nhập kho

#### b) Kiểm kê định kỳ:
1. Vào **Kiểm kê kho** > Tạo mới
2. Chọn kho và vị trí
3. Click **Bắt đầu kiểm kê** (hệ thống tự load sản phẩm)
4. Nhập số lượng thực tế
5. Click **Hoàn thành** (hệ thống tự điều chỉnh tồn kho)

---

### 💰 2. THU NGÂN (POS)
**Menu**: Quản lý Tạp hóa > Thu ngân

#### Quy trình bán hàng:
1. Vào **Phiên bán hàng** > New Session
2. Click **Open Session** để mở ca
3. Click **New Order** để bắt đầu bán
4. Quét mã vạch hoặc chọn sản phẩm
5. Chọn phương thức thanh toán (Cash/QR)
6. Click **Validate** và in hóa đơn
7. Kết thúc ca: Click **Close** và kiểm đếm tiền

**Tính năng đặc biệt**:
- ✅ Bán nợ (nếu được kích hoạt)
- ✅ Thanh toán QR Code
- ✅ Cảnh báo tồn kho thấp

---

### 📊 3. KẾ TOÁN
**Menu**: Quản lý Tạp hóa > Kế toán

#### Tạo báo cáo:
1. Vào **Báo cáo kế toán** > Tạo mới
2. Chọn khoảng thời gian (từ ngày - đến ngày)
3. Chọn loại báo cáo:
   - Doanh thu
   - Chi phí
   - Lợi nhuận
   - Công nợ
   - Tổng hợp
4. Click **Tạo báo cáo**
5. Xem hoặc In PDF

#### Quản lý hóa đơn:
- **Hóa đơn**: Xem tất cả hóa đơn bán hàng
- **Thanh toán**: Theo dõi thanh toán từ khách hàng

---

### 👨‍💼 4. CHỦ CỬA HÀNG
**Menu**: Quản lý Tạp hóa > Chủ cửa hàng

#### Dashboard:
- Xem tổng quan doanh thu
- Xem tổng chi phí
- Lợi nhuận ròng
- Công nợ khách hàng

#### Phê duyệt đơn hàng:
1. Vào **Đơn mua hàng**
2. Xem đơn chờ duyệt
3. Click **Confirm Order** để phê duyệt

---

## ⚙️ CẤU HÌNH

### Thêm sản phẩm:
1. Vào **Cấu hình > Sản phẩm** > Tạo mới
2. Điền thông tin:
   - Tên sản phẩm
   - Mã vạch
   - Giá bán
   - Giá vốn
3. Tab **Quản lý Tạp hóa**:
   - Tồn kho tối thiểu
   - Vị trí kệ hàng
   - Nhà cung cấp

### Thêm nhà cung cấp:
1. Vào **Cấu hình > Đối tác** > Tạo mới
2. Đánh dấu **"Is a Vendor"**
3. Điền thông tin liên hệ

### Cấu hình POS:
1. Vào **Cấu hình > Cấu hình POS**
2. Chọn POS config
3. Cuộn xuống **"Cấu hình Tạp hóa"**:
   - Bật/Tắt bán nợ
   - Bật/Tắt thanh toán QR
   - Cài đặt cảnh báo tồn kho

---

## 👥 PHÂN QUYỀN

Module hỗ trợ 5 vai trò:

1. **Nhân viên**: Quyền cơ bản
2. **Thu ngân**: Sử dụng POS
3. **Thủ kho**: Quản lý nhập xuất kho
4. **Kế toán**: Xem báo cáo tài chính
5. **Chủ cửa hàng**: Toàn quyền

### Cách phân quyền:
1. Vào Settings > Users & Companies > Users
2. Chọn user > Edit
3. Tab **"Access Rights"**
4. Tìm section **"Point of Sale"**
5. Chọn vai trò phù hợp

---

## 📱 WORKFLOW MẪU

### Quy trình hoàn chỉnh:

```
1. Chủ CH tạo đơn mua hàng → Phê duyệt
                ↓
2. Thủ kho nhận hàng → Tạo phiếu nhập kho
                ↓
3. Thủ kho kiểm tra chất lượng
                ↓
4. Chủ CH phê duyệt phiếu nhập
                ↓
5. Thủ kho hoàn thành → Hàng vào kho
                ↓
6. Thu ngân bán hàng qua POS
                ↓
7. Kế toán tạo báo cáo định kỳ
                ↓
8. Chủ CH xem Dashboard và báo cáo
```

---

## 🔧 KHẮC PHỤC SỰ CỐ

### Server không khởi động:
```bash
cd /home/bin04/odoo
source venv/bin/activate
./odoo-bin -d erp_taphoa
```

### Update module sau khi sửa code:
```bash
cd /home/bin04/odoo
source venv/bin/activate
./odoo-bin -d erp_taphoa -u taphoa_management --stop-after-init
```

### Xem log lỗi:
```bash
tail -f /home/bin04/odoo/odoo.log
```

---

## 📞 HỖ TRỢ

- 📧 Email: support@taphoa.com
- 📱 Hotline: 1900-xxxx
- 🌐 Website: https://taphoa.com

---

## 🎉 CHÚC MỪNG!

Hệ thống đã sẵn sàng sử dụng. Chúc bạn kinh doanh thành công! 🚀

---

**Phát triển bởi**: Tạp hóa Management System
**Phiên bản**: 17.0.1.0.0
**Ngày**: November 8, 2025
