# Hướng dẫn Sử dụng Tích điểm tại POS

## Cấu hình ban đầu

### 1. Tạo sản phẩm giảm giá (đã có sẵn)
Module đã tự động tạo sản phẩm "Giảm giá từ điểm tích lũy" với mã `LOYALTY_DISCOUNT`.

### 2. Cấu hình POS
1. Vào **Point of Sale > Configuration > Point of Sale**
2. Chọn POS của bạn
3. Trong tab cấu hình, tìm phần **"Tích điểm khách hàng"**
4. Bật **"Kích hoạt tích điểm"**
5. Chọn **"Sản phẩm giảm giá từ điểm"** = `Giảm giá từ điểm tích lũy`
6. Lưu cấu hình

### 3. Tạo thẻ tích điểm cho khách hàng
1. Vào **Tích điểm > Thẻ tích điểm**
2. Click **Tạo**
3. Chọn khách hàng
4. Chọn chương trình (Thân thiết hoặc VIP)
5. Lưu

---

## Sử dụng tại POS

### Giao diện POS với Tích điểm

Khi mở POS, bạn sẽ thấy:

```
┌─────────────────────────────────────────┐
│  [Sản phẩm]     [Giỏ hàng]  [Tích điểm] │
│                                          │
│  • Chọn khách hàng                       │
│  • Widget tích điểm tự động hiển thị     │
│    - Thẻ số: LC00000001                  │
│    - Điểm hiện tại: 50                   │
│    - Button "Đổi điểm"                   │
│                                          │
└─────────────────────────────────────────┘
```

### Quy trình bán hàng có tích điểm

#### Bước 1: Chọn khách hàng
1. Click vào nút **"Khách hàng"** ở góc trên
2. Chọn khách hàng từ danh sách
3. **Widget tích điểm** sẽ tự động hiển thị (nếu khách có thẻ)

#### Bước 2: Thêm sản phẩm vào giỏ
- Thêm sản phẩm như bình thường
- Widget tích điểm sẽ cập nhật:
  - **Điểm tích được**: Tự động tính dựa trên tổng đơn hàng

#### Bước 3: Đổi điểm (nếu muốn)
1. Click nút **"Đổi điểm"** trên widget tích điểm
2. Popup hiển thị:
   ```
   ┌───────────────────────────────────┐
   │  Use Loyalty Points               │
   ├───────────────────────────────────┤
   │  Khách hàng: Nguyễn Văn A         │
   │  Số thẻ: LC00000001               │
   │  Điểm hiện có: 50                 │
   │  Chương trình: Khách hàng thân thiết │
   │  1 điểm = 1,000đ                  │
   │  Tối thiểu: 10 điểm               │
   │  Giảm tối đa: 50%                 │
   ├───────────────────────────────────┤
   │  Số điểm muốn sử dụng:            │
   │  [______30______] [Dùng tối đa]   │
   │                                   │
   │  Giảm giá: 30,000đ                │
   │  Điểm còn lại: 20                 │
   ├───────────────────────────────────┤
   │  [Cancel]          [Apply]        │
   └───────────────────────────────────┘
   ```

3. Nhập số điểm muốn dùng hoặc click **"Dùng tối đa"**
4. Click **"Apply"**

#### Bước 4: Xem thông tin cập nhật
Widget tích điểm sẽ hiển thị:
```
┌─────────────────────────┐
│ ⭐ Tích điểm             │
├─────────────────────────┤
│ Thẻ: LC00000001         │
│ Điểm hiện tại: 50       │
│ Điểm sử dụng: -30       │
│ Giảm giá: -30,000đ      │
│ Điểm tích được: +14     │
│ ─────────────────────── │
│ Điểm sau GD: 34         │
│                         │
│ [🎁 Đổi điểm]          │
└─────────────────────────┘
```

Giỏ hàng sẽ có dòng:
- **Giảm giá từ điểm tích lũy**: -30,000đ

#### Bước 5: Thanh toán
1. Click **"Thanh toán"**
2. Chọn phương thức thanh toán
3. Xác nhận thanh toán
4. **Hệ thống tự động**:
   - Trừ 30 điểm từ thẻ
   - Tích 14 điểm mới (từ số tiền sau giảm giá)
   - Tạo 2 giao dịch tích điểm

---

## Tính toán chi tiết

### Ví dụ: Đơn hàng 200,000đ

**Trước khi dùng điểm:**
- Tổng đơn: 200,000đ
- Khách có: 50 điểm

**Khách dùng 30 điểm:**
- Giảm giá: 30 điểm × 1,000đ = **30,000đ**
- Phải trả: 200,000đ - 30,000đ = **170,000đ**

**Sau thanh toán:**
- Trừ điểm: -30
- Tích điểm mới: 170,000đ ÷ 10,000đ = +17
- **Tổng điểm còn**: 50 - 30 + 17 = **37 điểm**

### Giới hạn giảm giá tối đa

Chương trình "Thân thiết" giới hạn 50%:
- Đơn 100,000đ → Giảm tối đa 50,000đ
- Nếu dùng 100 điểm (= 100,000đ) → Chỉ giảm 50,000đ

**Ví dụ:**
```
Đơn hàng: 100,000đ
Khách có: 100 điểm
Dùng: 100 điểm

❌ KHÔNG giảm 100,000đ (100%)
✅ CHỈ giảm 50,000đ (50%)

Phải trả: 50,000đ
Tích được: 5 điểm (từ 50,000đ)
Điểm sau: 100 - 100 + 5 = 5 điểm
```

---

## Xem báo cáo

### 1. Lịch sử giao dịch của khách hàng
- Vào **Liên hệ > Khách hàng**
- Chọn khách hàng
- Tab **"Tích điểm"**
- Click vào thẻ → Button **"Xem giao dịch"**

### 2. Tất cả giao dịch
- Vào **Tích điểm > Giao dịch**
- Lọc theo:
  - Hôm nay / Tuần này / Tháng này
  - Tích điểm / Đổi điểm
  - Khách hàng
  - POS Order

### 3. Thống kê đơn hàng POS
- Vào **Point of Sale > Orders > Orders**
- Xem các trường:
  - **Điểm tích được**
  - **Điểm đã sử dụng**
  - **Giảm giá từ điểm**

---

## Xử lý tình huống

### Khách hàng không có thẻ
→ Widget tích điểm không hiển thị
→ Tạo thẻ từ backend trước

### Khách muốn hủy việc dùng điểm
1. Click lại nút **"Đổi điểm"**
2. Nhập 0 điểm
3. Apply
→ Dòng giảm giá sẽ bị xóa

### Thay đổi giỏ hàng sau khi đã dùng điểm
- Widget tự động cập nhật điểm tích được
- Giảm giá từ điểm **không tự động thay đổi**
- Cần click lại **"Đổi điểm"** để điều chỉnh

### Khách hủy đơn
- Giao dịch chỉ được tạo **sau khi thanh toán**
- Nếu hủy trước thanh toán → Không ảnh hưởng gì

---

## Lưu ý quan trọng

### 1. Chọn đúng sản phẩm giảm giá
- Phải cấu hình trong POS Config
- Sản phẩm phải có `available_in_pos = True`
- Không được đánh thuế

### 2. Quyền truy cập
- Thu ngân có thể xem và dùng điểm
- Không thể sửa điểm thủ công
- Chỉ Manager mới điều chỉnh được

### 3. Performance
- Widget load thông tin khi chọn khách hàng
- Có thể hơi chậm nếu khách có nhiều giao dịch
- Cân nhắc archiving old transactions

### 4. Offline mode
- POS Odoo hỗ trợ offline
- Tính năng tích điểm cần kết nối server
- Không thể dùng điểm khi offline

---

## Troubleshooting

### Widget không hiển thị?
✓ Kiểm tra khách hàng có thẻ không
✓ Thẻ phải ở trạng thái "active"
✓ Đã bật "Kích hoạt tích điểm" trong POS Config
✓ Clear cache trình duyệt

### Không click được "Đổi điểm"?
✓ Khách có ít nhất min_points_to_redeem
✓ Đơn hàng phải có sản phẩm
✓ Check console browser có lỗi JS không

### Điểm không được tích?
✓ Đơn hàng phải thanh toán xong
✓ Giá trị đơn ≥ min_order_amount
✓ Check log server Odoo

### Giảm giá không đúng?
✓ Kiểm tra max_discount_percentage
✓ Kiểm tra points_to_discount_rate
✓ Tính toán lại thủ công để verify

---

## FAQ

**Q: Có thể dùng điểm từ nhiều thẻ?**  
A: Không, mỗi đơn chỉ dùng 1 thẻ (của khách hàng được chọn).

**Q: Khách có thể tích điểm từ phần giảm giá không?**  
A: Không, chỉ tích điểm trên số tiền thực tế phải trả.

**Q: Điểm có hết hạn không?**  
A: Có, theo cấu hình `points_expiry_days` (mặc định 365 ngày).

**Q: Có thể chuyển điểm giữa các khách hàng?**  
A: Không, điểm gắn với từng thẻ riêng biệt.

**Q: Làm sao tạo thẻ hàng loạt?**  
A: Dùng import CSV hoặc viết script Python.

---

**Tài liệu chi tiết**: Xem `LOYALTY_GUIDE.md`  
**Hỗ trợ kỹ thuật**: Liên hệ admin hệ thống
