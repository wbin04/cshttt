# HƯỚNG DẪN ĐĂNG NHẬP THU NGÂN

## Thông tin đăng nhập

### User Thu Ngân Demo
- **Tên đăng nhập:** `thungan`
- **Mật khẩu:** `thungan123`
- **Email:** thungan@taphoa.com
- **Vai trò:** Thu ngân
- **Quyền:** 
  - Truy cập Point of Sale (POS)
  - Tạo đơn hàng
  - Xử lý thanh toán
  - In hóa đơn
  - Xem báo cáo bán hàng của mình

## Các bước đăng nhập

### 1. Khởi động lại Odoo
```bash
# Dừng Odoo hiện tại
pkill -f odoo-bin

# Khởi động Odoo với database
cd /home/bin04/odoo
python3 ./odoo-bin -d erp_taphoa
```

### 2. Truy cập hệ thống
- Mở trình duyệt web
- Truy cập: `http://localhost:8069`

### 3. Đăng nhập
1. Nhập tên đăng nhập: **thungan**
2. Nhập mật khẩu: **thungan123**
3. Nhấn nút "Đăng nhập"

### 4. Truy cập Point of Sale
Sau khi đăng nhập thành công:
1. Vào menu **Point of Sale** > **Phiên mới**
2. Hoặc chọn **Tạp hóa** > **Thu ngân** > **Point of Sale**

## Chức năng của Thu Ngân

### 1. Tạo đơn hàng bán (POS)
- Chọn sản phẩm từ danh sách
- Quét mã vạch (nếu có)
- Nhập số lượng
- Áp dụng giảm giá (nếu có)

### 2. Xử lý thanh toán
- **Tiền mặt:** Nhập số tiền khách đưa, hệ thống tự tính tiền thừa
- **Chuyển khoản/QR:** Chọn phương thức thanh toán QR
- **Công nợ:** Chọn khách hàng và ghi nhận công nợ

### 3. In hóa đơn
- Sau khi thanh toán, in hóa đơn cho khách
- Hóa đơn bao gồm: Tên cửa hàng, danh sách sản phẩm, tổng tiền, phương thức thanh toán

### 4. Quản lý phiên làm việc
- **Mở phiên:** Nhập số tiền đầu ca
- **Đóng phiên:** Kiểm đếm tiền, in báo cáo ca
- **Xem lịch sử:** Xem các đơn hàng đã bán trong ca

### 5. Tra cứu đơn hàng
- Menu **Point of Sale** > **Đơn hàng**
- Tìm kiếm theo mã đơn, khách hàng, ngày
- Xem chi tiết đơn hàng
- In lại hóa đơn (nếu cần)

## Các user demo khác

### Thủ kho
- **Login:** `thukho`
- **Password:** `thukho123`
- **Chức năng:** Nhập kho, xuất kho, kiểm kê

### Kế toán
- **Login:** `ketoan`
- **Password:** `ketoan123`
- **Chức năng:** Ghi sổ, đối soát, báo cáo tài chính

### Chủ cửa hàng
- **Login:** `quanly`
- **Password:** `quanly123`
- **Chức năng:** Toàn quyền, xem dashboard, phê duyệt

## Lưu ý quan trọng

1. **Bảo mật:**
   - Đổi mật khẩu sau lần đăng nhập đầu tiên
   - Không chia sẻ thông tin đăng nhập

2. **Thao tác:**
   - Luôn kiểm tra kỹ đơn hàng trước khi thanh toán
   - Xác nhận số tiền với khách hàng
   - In hóa đơn cho mọi giao dịch

3. **Kết thúc ca:**
   - Đóng phiên POS trước khi kết thúc ca
   - Kiểm đếm tiền trong két
   - Đối chiếu với báo cáo hệ thống

4. **Sự cố:**
   - Không tự ý xóa đơn hàng
   - Báo ngay cho quản lý nếu có sai lệch
   - Ghi chép rõ ràng các giao dịch đặc biệt

## Các phím tắt POS

- **Enter:** Thanh toán
- **Esc:** Hủy/Quay lại
- **+/-:** Tăng/Giảm số lượng
- **Del/Backspace:** Xóa sản phẩm khỏi đơn
- **Ctrl+K:** Tìm kiếm khách hàng
- **Ctrl+P:** Tìm kiếm sản phẩm

## Hỗ trợ

Nếu gặp vấn đề:
1. Liên hệ Chủ cửa hàng (quanly)
2. Xem HUONGDAN.md để biết thêm chi tiết
3. Kiểm tra log hệ thống nếu có lỗi kỹ thuật
