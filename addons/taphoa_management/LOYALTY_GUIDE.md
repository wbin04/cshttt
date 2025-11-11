# Hướng dẫn sử dụng Hệ thống Tích điểm Khách hàng

## Tổng quan

Hệ thống tích điểm giúp khuyến khích khách hàng quay lại mua sắm thường xuyên bằng cách:
- **Tích điểm**: Khách hàng nhận điểm khi mua hàng
- **Đổi điểm**: Sử dụng điểm để được giảm giá cho đơn hàng tiếp theo
- **Quản lý**: Theo dõi và quản lý điểm tích lũy của khách hàng

---

## 1. Cấu hình Chương trình Tích điểm

### Truy cập
`Tích điểm > Chương trình`

### Tạo chương trình mới

1. **Thông tin cơ bản**
   - Tên chương trình: VD: "Khách hàng thân thiết", "Khách VIP"
   - Thứ tự: Thứ tự ưu tiên khi có nhiều chương trình
   - Kích hoạt: Bật/tắt chương trình

2. **Quy tắc tích điểm**
   - **Điểm/Đồng**: Tỷ lệ quy đổi tiền thành điểm
     - VD: 0.0001 = 1 điểm cho 10,000đ
     - VD: 0.0002 = 1 điểm cho 5,000đ (tích gấp đôi)
   
   - **Giá trị đơn hàng tối thiểu**: Đơn hàng phải đạt giá trị này mới được tích điểm
     - VD: 50,000đ
   
   - **Điểm hết hạn sau (ngày)**: Số ngày điểm có hiệu lực
     - VD: 365 ngày = 1 năm
     - 0 = không hết hạn

3. **Quy tắc đổi điểm**
   - **Tỷ lệ quy đổi (Điểm -> VND)**: Giá trị của 1 điểm
     - VD: 1,000đ = 1 điểm đổi được 1,000đ giảm giá
   
   - **Số điểm tối thiểu để đổi**: Khách hàng phải có ít nhất bao nhiêu điểm
     - VD: 10 điểm
   
   - **% giảm giá tối đa**: Giới hạn giảm giá cho mỗi đơn hàng
     - VD: 50% = giảm tối đa 50% giá trị đơn hàng

### Ví dụ cấu hình

#### Chương trình "Khách hàng thân thiết"
```
Tích điểm:
- 1 điểm cho 10,000đ (points_per_amount = 0.0001)
- Đơn hàng tối thiểu: 50,000đ
- Điểm hết hạn: 365 ngày

Đổi điểm:
- 1 điểm = 1,000đ giảm giá
- Tối thiểu đổi: 10 điểm
- Giảm tối đa: 50% đơn hàng
```

#### Chương trình VIP
```
Tích điểm:
- 1 điểm cho 5,000đ (tích gấp đôi)
- Không giới hạn đơn hàng tối thiểu
- Điểm hết hạn: 730 ngày (2 năm)

Đổi điểm:
- 1 điểm = 1,500đ giảm giá
- Tối thiểu đổi: 5 điểm
- Giảm tối đa: 70% đơn hàng
```

---

## 2. Tạo Thẻ tích điểm cho Khách hàng

### Cách 1: Tạo từ danh sách Khách hàng

1. Vào `Liên hệ > Khách hàng`
2. Chọn khách hàng
3. Click nút **"Tạo thẻ tích điểm"** (nếu có)
4. Chọn chương trình tích điểm
5. Lưu

### Cách 2: Tạo trực tiếp

1. Vào `Tích điểm > Thẻ tích điểm`
2. Click **"Tạo"**
3. Chọn khách hàng
4. Chọn chương trình
5. Ngày phát hành: tự động điền ngày hiện tại
6. Lưu

**Số thẻ** sẽ được tạo tự động theo định dạng: `LC00000001`

---

## 3. Sử dụng Tích điểm tại POS (Thu ngân)

### Khi khách hàng mua hàng

1. **Tạo đơn hàng POS** như bình thường
2. **Chọn khách hàng** cho đơn hàng
3. **Xem thẻ tích điểm** của khách hàng sẽ tự động hiển thị

### Sử dụng điểm để giảm giá

1. Trong đơn hàng POS, tìm trường **"Điểm đã sử dụng"**
2. Nhập số điểm khách hàng muốn sử dụng
   - Hệ thống sẽ kiểm tra:
     - Khách hàng có đủ điểm không?
     - Số điểm có đạt mức tối thiểu không?
3. **Số tiền giảm giá** sẽ tự động tính toán
   - Ví dụ: 50 điểm × 1,000đ = 50,000đ giảm giá
   - Nhưng không vượt quá 50% giá trị đơn hàng

### Tích điểm từ đơn hàng

Sau khi **Thanh toán** đơn hàng:
1. Điểm đã sử dụng sẽ bị **trừ** khỏi thẻ
2. Điểm mới sẽ được **tích** vào thẻ dựa trên giá trị đơn hàng
   - Chỉ tính điểm trên số tiền sau khi đã trừ giảm giá từ điểm

### Ví dụ thực tế

**Tình huống:**
- Khách hàng có 100 điểm
- Đơn hàng: 200,000đ
- Chương trình: 1 điểm = 1,000đ, tích 1 điểm cho 10,000đ

**Khách hàng muốn dùng 50 điểm:**
1. Giảm giá: 50 điểm × 1,000đ = 50,000đ
2. Số tiền phải trả: 200,000đ - 50,000đ = 150,000đ
3. Điểm tích được: 150,000đ ÷ 10,000đ = 15 điểm

**Sau giao dịch:**
- Điểm còn lại: 100 - 50 + 15 = 65 điểm

---

## 4. Quản lý Giao dịch Tích điểm

### Xem lịch sử giao dịch

`Tích điểm > Giao dịch`

Bạn có thể xem:
- **Tích điểm**: Giao dịch tích điểm từ mua hàng (màu xanh)
- **Đổi điểm**: Giao dịch đổi điểm để giảm giá (màu đỏ)
- **Điều chỉnh**: Điều chỉnh điểm thủ công
- **Hết hạn**: Điểm hết hạn tự động

### Thông tin giao dịch
- Mã giao dịch: LT00000001
- Khách hàng
- Số điểm (+/-)
- Giá trị đơn hàng
- Ngày giao dịch
- Ngày hết hạn điểm
- Trạng thái: Nháp / Đã xác nhận / Đã hủy

### Điều chỉnh điểm thủ công (Chỉ Manager)

Khi cần tặng hoặc trừ điểm:

1. Vào `Tích điểm > Giao dịch`
2. Click **"Tạo"**
3. Chọn thẻ tích điểm
4. Loại giao dịch: **Điều chỉnh**
5. Nhập số điểm:
   - Dương (+): Tặng điểm
   - Âm (-): Trừ điểm
6. Ghi chú lý do
7. Xác nhận

---

## 5. Báo cáo và Thống kê

### Xem thống kê chương trình

Vào `Tích điểm > Chương trình` > Chọn chương trình

Xem được:
- **Số khách hàng tham gia**: Tổng số khách có thẻ
- **Tổng điểm đã tặng**: Tổng điểm khách hàng tích được
- **Tổng điểm đã đổi**: Tổng điểm khách hàng đã sử dụng

### Xem điểm của khách hàng

Vào `Liên hệ > Khách hàng` > Chọn khách hàng

Tab **"Tích điểm"** hiển thị:
- Tổng điểm tích lũy hiện có
- Danh sách các thẻ tích điểm
- Trạng thái thẻ

### Tìm kiếm và lọc

**Thẻ tích điểm:**
- Lọc theo: Đang hoạt động / Tạm ngưng / Hết hạn
- Nhóm theo: Chương trình / Trạng thái

**Giao dịch:**
- Lọc theo: Tích điểm / Đổi điểm / Đã xác nhận
- Lọc theo thời gian: Hôm nay / Tuần này / Tháng này
- Nhóm theo: Loại giao dịch / Khách hàng / Chương trình / Ngày

---

## 6. Hệ thống Tự động

### Hết hạn điểm tự động

Hệ thống có **Cron Job** chạy mỗi ngày để:
1. Tìm các giao dịch tích điểm đã hết hạn
2. Tự động tạo giao dịch trừ điểm
3. Đánh dấu giao dịch cũ là "Đã hết hạn"

### Tự động xác nhận giao dịch

Khi khách hàng mua hàng và thanh toán:
- Giao dịch đổi điểm tự động xác nhận
- Giao dịch tích điểm tự động xác nhận
- Liên kết với đơn hàng POS

---

## 7. Tích hợp với CRM

### Khi tạo khách hàng từ CRM

Module `crm` đã được thêm vào dependencies, cho phép:
- Tạo thẻ tích điểm cho Lead/Opportunity đã chuyển thành khách hàng
- Theo dõi điểm thưởng trong thông tin khách hàng
- Sử dụng điểm trong báo giá và đơn hàng

### Workflow khuyến nghị

1. **Lead/Opportunity** → Khách hàng tiềm năng
2. **Chuyển đổi thành khách hàng** → Tạo Partner
3. **Tạo thẻ tích điểm** → Gắn chương trình phù hợp
4. **Mua hàng lần đầu** → Bắt đầu tích điểm
5. **Quay lại mua tiếp** → Sử dụng điểm để giảm giá

---

## 8. Quyền truy cập

### Manager (Chủ cửa hàng)
- Toàn quyền: Tạo/Sửa/Xóa tất cả
- Quản lý chương trình
- Điều chỉnh điểm thủ công
- Xem báo cáo chi tiết

### Cashier (Thu ngân)
- Xem chương trình
- Xem/Tạo/Sửa thẻ tích điểm
- Xem/Tạo/Sửa giao dịch
- Áp dụng điểm cho đơn hàng

### Accountant (Kế toán)
- Chỉ xem
- Xem báo cáo liên quan đến tích điểm

### Warehouse (Thủ kho)
- Chỉ xem
- Không có quyền thao tác

---

## 9. Lưu ý quan trọng

### Khi thiết lập tỷ lệ tích điểm
- Tính toán kỹ để không gây lỗ
- Ví dụ tốt: 1-2% giá trị đơn hàng thành điểm
- Tránh tích quá nhiều điểm

### Khi thiết lập tỷ lệ đổi điểm
- Đặt giới hạn % giảm giá tối đa
- Đảm bảo khách vẫn phải mua với giá hợp lý
- Khuyến nghị: 30-50% tối đa

### Quản lý điểm hết hạn
- Cài đặt thời hạn hợp lý (6 tháng - 1 năm)
- Thông báo cho khách trước khi hết hạn
- Tránh để điểm tồn đọng quá lâu

### Kiểm tra định kỳ
- Xem báo cáo tích điểm hàng tháng
- Đánh giá hiệu quả chương trình
- Điều chỉnh quy tắc nếu cần

---

## 10. Ví dụ Quy trình Hoàn chỉnh

### Scenario: Khách hàng Nguyễn Văn A mua hàng

1. **Lần đầu tiên (Chưa có thẻ)**
   - Thu ngân tạo thẻ tích điểm cho anh A
   - Chọn chương trình "Khách hàng thân thiết"
   - Đơn hàng 100,000đ
   - Tích được: 10 điểm (100,000đ ÷ 10,000đ)

2. **Lần thứ hai (Đã có 10 điểm)**
   - Đơn hàng 200,000đ
   - Anh A muốn dùng 10 điểm
   - Giảm: 10,000đ
   - Phải trả: 190,000đ
   - Tích thêm: 19 điểm
   - Tổng còn: 0 - 10 + 19 = 19 điểm

3. **Lần thứ ba (Có 19 điểm)**
   - Đơn hàng 150,000đ
   - Không dùng điểm
   - Tích thêm: 15 điểm
   - Tổng: 19 + 15 = 34 điểm

4. **Lần thứ tư (Có 34 điểm, mua sắm lớn)**
   - Đơn hàng 500,000đ
   - Dùng hết 34 điểm
   - Giảm: 34,000đ (dưới 50% nên OK)
   - Phải trả: 466,000đ
   - Tích thêm: 46 điểm
   - Tổng: 46 điểm

---

## Kết luận

Hệ thống tích điểm giúp:
- ✅ Khuyến khích khách hàng quay lại
- ✅ Tăng doanh thu và lòng trung thành
- ✅ Quản lý khách hàng tốt hơn
- ✅ Tự động hóa quy trình tích/đổi điểm
- ✅ Tích hợp mượt mà với POS và CRM

**Hỗ trợ:** Liên hệ quản trị viên hệ thống nếu cần trợ giúp.
