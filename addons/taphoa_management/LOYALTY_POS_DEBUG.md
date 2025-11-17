# Debug: Widget Tích Điểm Không Hiển Thị

## Vấn đề
Widget tích điểm không hiển thị khi chọn customer trong POS.

## Nguyên nhân có thể:
1. ❌ Template XML kế thừa ProductScreen nhưng không có context của LoyaltyDisplay component
2. ❌ Component chưa được mount đúng cách - đang dùng `t-call` thay vì component instance
3. ✅ Cần đăng ký component vào POS và sử dụng như một control button hoặc widget

## Giải pháp
Thay vì kế thừa ProductScreen qua XML, cần:
1. Đăng ký LoyaltyDisplay như một control button
2. Hoặc patch ProductScreen để thêm component vào rightpane
3. Sử dụng `t-component` thay vì `t-call`

## Bước tiếp theo
Xem cách Odoo 17 đăng ký control button và làm theo pattern đó.

## Commands để test:
```bash
# 1. Check browser console (F12) để xem có lỗi JS không
# 2. Check POS config:
python3 odoo/odoo-bin shell -c odoo.conf -d erp_taphoa <<< "
config = env['pos.config'].search([('name', '=', 'Shop')])
print(f'enable_loyalty: {config.enable_loyalty}')
print(f'discount_product: {config.loyalty_discount_product_id.name if config.loyalty_discount_product_id else None}')
exit()
"

# 3. Check customer có loyalty card:
python3 odoo/odoo-bin shell -c odoo.conf -d erp_taphoa <<< "
cards = env['customer.loyalty.card'].search([])
for c in cards:
    print(f'{c.partner_id.name}: {c.card_number} - {c.total_points} pts')
exit()
"
```

## Note
- ProductScreen trong Odoo 17 dùng OWL framework
- Control buttons được đăng ký qua `ProductScreen.addControlButton()`
- Cần import LoyaltyDisplay trong main POS module
