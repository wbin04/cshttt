# Hệ thống Tích điểm Khách hàng - Tạp Hóa Management

## Tổng quan

Module tích điểm khách hàng được tích hợp vào hệ thống quản lý cửa hàng tạp hóa, cho phép:

- ✅ **Tích điểm tự động** khi khách hàng mua hàng
- ✅ **Đổi điểm giảm giá** cho đơn hàng tiếp theo
- ✅ **Quản lý chương trình** tích điểm linh hoạt
- ✅ **Tích hợp POS** và CRM
- ✅ **Hết hạn điểm tự động**

## Cài đặt nhanh

### 1. Cập nhật module

```bash
cd /home/bin04/cshttt
python3 odoo/odoo-bin -c odoo.conf -u taphoa_management -d your_database
```

### 2. Kiểm tra dependencies

Module yêu cầu:
- `crm` - Quản lý khách hàng
- `point_of_sale` - POS
- `contacts` - Danh bạ

### 3. Tạo chương trình tích điểm

Vào: **Tích điểm > Chương trình > Tạo**

Cấu hình mặc định đã có sẵn:
- **Khách hàng thân thiết**: 1 điểm/10,000đ
- **Khách hàng VIP**: 1 điểm/5,000đ (tích gấp đôi)

## Cấu trúc Models

### 1. `customer.loyalty.program`
Chương trình tích điểm với quy tắc tích/đổi điểm

**Các trường chính:**
- `points_per_amount`: Tỷ lệ tiền thành điểm
- `points_to_discount_rate`: Giá trị 1 điểm (VND)
- `min_points_to_redeem`: Điểm tối thiểu để đổi
- `max_discount_percentage`: % giảm giá tối đa
- `points_expiry_days`: Số ngày điểm hết hạn

### 2. `customer.loyalty.card`
Thẻ tích điểm của từng khách hàng

**Các trường chính:**
- `card_number`: Số thẻ (tự động: LC00000001)
- `partner_id`: Khách hàng
- `program_id`: Chương trình
- `total_points`: Điểm hiện có
- `state`: active/suspended/expired

### 3. `customer.loyalty.transaction`
Giao dịch tích/đổi điểm

**Loại giao dịch:**
- `earn`: Tích điểm từ mua hàng
- `redeem`: Đổi điểm để giảm giá
- `adjust`: Điều chỉnh thủ công
- `expire`: Hết hạn tự động

### 4. `pos.order` (Extended)
Mở rộng POS Order với tích điểm

**Thêm các trường:**
- `loyalty_card_id`: Thẻ tích điểm
- `loyalty_points_earned`: Điểm tích được
- `loyalty_points_used`: Điểm đã dùng
- `loyalty_discount_amount`: Số tiền giảm

## Workflow

```
┌─────────────────┐
│  Khách hàng     │
│  mua hàng       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Chọn thẻ       │
│  tích điểm      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│  Sử dụng điểm?  ├─Yes─▶│  Trừ điểm       │
│  để giảm giá    │      │  Tính giảm giá  │
└────────┬────────┘      └────────┬────────┘
         │ No                     │
         │◄───────────────────────┘
         ▼
┌─────────────────┐
│  Thanh toán     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tích điểm      │
│  cho đơn hàng   │
└─────────────────┘
```

## API Methods

### Program Methods

```python
# Tính điểm từ số tiền
program.calculate_points_from_amount(amount)

# Tính giảm giá từ điểm
program.calculate_discount_from_points(points, order_amount)
```

### Card Methods

```python
# Kiểm tra có thể đổi điểm
card.can_redeem_points(points)

# Xem lịch sử giao dịch
card.action_view_transactions()
```

### Partner Methods

```python
# Tạo thẻ cho khách hàng
partner.create_loyalty_card(program_id)

# Xem thẻ tích điểm
partner.action_view_loyalty_cards()
```

### POS Order Methods

```python
# Xử lý tích điểm khi thanh toán
order._process_loyalty_points()
```

## Views

### Menu Structure
```
Tích điểm
├── Chương trình
├── Thẻ tích điểm
└── Giao dịch
```

### Forms
- `customer_loyalty_views.xml`: Tất cả views cho tích điểm
- Tích hợp vào `res.partner`: Tab "Tích điểm"
- Tích hợp vào `pos.order`: Fields tích điểm

## Security

### Groups
- **Manager**: Toàn quyền
- **Cashier**: Tạo/Sửa thẻ và giao dịch
- **Accountant/Warehouse**: Chỉ xem

### Access Rights
Xem: `security/ir.model.access.csv`

## Cron Jobs

### Hết hạn điểm tự động
- **Model**: `customer.loyalty.transaction`
- **Method**: `_cron_expire_points()`
- **Frequency**: Chạy mỗi ngày
- **Function**: Tìm và hết hạn điểm đã quá hạn

## Ví dụ sử dụng

### 1. Tạo chương trình

```xml
<record id="my_loyalty_program" model="customer.loyalty.program">
    <field name="name">Khách hàng mới</field>
    <field name="points_per_amount">0.0002</field> <!-- 1 điểm / 5,000đ -->
    <field name="points_to_discount_rate">1000</field> <!-- 1 điểm = 1,000đ -->
    <field name="min_points_to_redeem">5</field>
    <field name="max_discount_percentage">30</field>
    <field name="points_expiry_days">180</field> <!-- 6 tháng -->
</record>
```

### 2. Python: Tạo thẻ cho khách hàng

```python
partner = self.env['res.partner'].browse(partner_id)
program = self.env['customer.loyalty.program'].browse(program_id)

card = self.env['customer.loyalty.card'].create({
    'partner_id': partner.id,
    'program_id': program.id,
})
```

### 3. Python: Tích điểm thủ công

```python
card = self.env['customer.loyalty.card'].browse(card_id)

transaction = self.env['customer.loyalty.transaction'].create({
    'card_id': card.id,
    'transaction_type': 'earn',
    'points': 50,
    'note': 'Khuyến mãi đặc biệt',
})
transaction.action_confirm()
```

### 4. Python: Đổi điểm

```python
# Kiểm tra
if card.can_redeem_points(30):
    transaction = self.env['customer.loyalty.transaction'].create({
        'card_id': card.id,
        'transaction_type': 'redeem',
        'points': -30,
        'note': 'Đổi điểm giảm giá',
    })
    transaction.action_confirm()
```

## Testing

### Test Cases

1. **Tích điểm**
   - Đơn hàng 100,000đ → 10 điểm (với tỷ lệ 0.0001)
   - Đơn hàng dưới min_order_amount → 0 điểm

2. **Đổi điểm**
   - 50 điểm × 1,000đ = 50,000đ giảm
   - Giảm tối đa 50% × 100,000đ = 50,000đ

3. **Hết hạn**
   - Điểm quá 365 ngày → Tự động trừ điểm

## Troubleshooting

### Không thấy menu Tích điểm?
- Kiểm tra user có quyền truy cập không
- Restart Odoo server
- Clear browser cache

### Không tích được điểm?
- Kiểm tra chương trình đang active
- Kiểm tra đơn hàng đạt min_order_amount
- Kiểm tra thẻ ở trạng thái active

### Không đổi được điểm?
- Kiểm tra số điểm còn lại
- Kiểm tra min_points_to_redeem
- Kiểm tra thẻ còn hiệu lực

## Changelog

### Version 1.0.0
- ✅ Thêm models: Program, Card, Transaction
- ✅ Tích hợp POS Order
- ✅ Views và menu
- ✅ Security rules
- ✅ Cron job hết hạn điểm
- ✅ Demo data
- ✅ Documentation

## Tài liệu tham khảo

- **Hướng dẫn chi tiết**: `LOYALTY_GUIDE.md`
- **Odoo Documentation**: https://www.odoo.com/documentation/17.0/

## Support

Liên hệ: team@taphoa.com

---

**License**: LGPL-3  
**Author**: Cửa hàng Tạp hóa  
**Version**: 17.0.1.0.0
