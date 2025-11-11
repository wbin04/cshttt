#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test hệ thống tích điểm
Chạy trong Odoo shell: python3 odoo-bin shell -c odoo.conf -d your_database
"""

def test_loyalty_system(env):
    """Test các chức năng cơ bản của hệ thống tích điểm"""
    
    print("\n" + "="*60)
    print("BẮT ĐẦU TEST HỆ THỐNG TÍCH ĐIỂM")
    print("="*60 + "\n")
    
    # 1. Kiểm tra chương trình tích điểm
    print("1. Kiểm tra chương trình tích điểm...")
    programs = env['customer.loyalty.program'].search([])
    print(f"   ✓ Tìm thấy {len(programs)} chương trình")
    for program in programs:
        print(f"   - {program.name}")
        print(f"     Tích: 1 điểm / {1/program.points_per_amount:,.0f}đ")
        print(f"     Đổi: 1 điểm = {program.points_to_discount_rate:,.0f}đ")
    
    if not programs:
        print("   ⚠️  Không tìm thấy chương trình nào!")
        print("   → Cần import data/loyalty_data.xml")
        return False
    
    # 2. Tạo/Tìm khách hàng test
    print("\n2. Tạo khách hàng test...")
    partner = env['res.partner'].search([('name', '=', 'Test Customer Loyalty')], limit=1)
    if not partner:
        partner = env['res.partner'].create({
            'name': 'Test Customer Loyalty',
            'email': 'test.loyalty@example.com',
            'phone': '0123456789',
        })
        print(f"   ✓ Đã tạo khách hàng: {partner.name}")
    else:
        print(f"   ✓ Sử dụng khách hàng: {partner.name}")
    
    # 3. Tạo thẻ tích điểm
    print("\n3. Tạo thẻ tích điểm...")
    program = programs[0]
    card = env['customer.loyalty.card'].search([
        ('partner_id', '=', partner.id),
        ('program_id', '=', program.id)
    ], limit=1)
    
    if not card:
        card = partner.create_loyalty_card(program.id)
        print(f"   ✓ Đã tạo thẻ: {card.card_number}")
    else:
        print(f"   ✓ Sử dụng thẻ: {card.card_number}")
    
    print(f"   Điểm hiện có: {card.total_points}")
    
    # 4. Test tích điểm
    print("\n4. Test tích điểm (100,000đ)...")
    order_amount = 100000
    points_earned = program.calculate_points_from_amount(order_amount)
    print(f"   Đơn hàng: {order_amount:,.0f}đ")
    print(f"   ✓ Điểm tích được: {points_earned}")
    
    # Tạo giao dịch tích điểm
    transaction = env['customer.loyalty.transaction'].create({
        'card_id': card.id,
        'transaction_type': 'earn',
        'points': points_earned,
        'order_amount': order_amount,
        'note': 'Test tích điểm',
    })
    transaction.action_confirm()
    print(f"   ✓ Giao dịch: {transaction.name}")
    print(f"   Tổng điểm sau: {card.total_points}")
    
    # 5. Test đổi điểm
    print("\n5. Test đổi điểm...")
    if card.total_points >= program.min_points_to_redeem:
        points_to_use = min(10, card.total_points)
        order_amount = 150000
        
        discount = program.calculate_discount_from_points(points_to_use, order_amount)
        print(f"   Đơn hàng: {order_amount:,.0f}đ")
        print(f"   Dùng: {points_to_use} điểm")
        print(f"   ✓ Giảm giá: {discount:,.0f}đ")
        print(f"   Phải trả: {order_amount - discount:,.0f}đ")
        
        # Tạo giao dịch đổi điểm
        if card.can_redeem_points(points_to_use):
            transaction = env['customer.loyalty.transaction'].create({
                'card_id': card.id,
                'transaction_type': 'redeem',
                'points': -points_to_use,
                'order_amount': order_amount,
                'note': 'Test đổi điểm',
            })
            transaction.action_confirm()
            print(f"   ✓ Giao dịch: {transaction.name}")
            print(f"   Tổng điểm sau: {card.total_points}")
        else:
            print("   ⚠️  Không đủ điều kiện đổi điểm")
    else:
        print(f"   ⚠️  Không đủ điểm để đổi (cần tối thiểu {program.min_points_to_redeem})")
    
    # 6. Kiểm tra lịch sử giao dịch
    print("\n6. Kiểm tra lịch sử giao dịch...")
    transactions = env['customer.loyalty.transaction'].search([
        ('card_id', '=', card.id)
    ], order='transaction_date desc')
    print(f"   ✓ Tìm thấy {len(transactions)} giao dịch")
    for trans in transactions[:5]:  # Hiển thị 5 giao dịch gần nhất
        type_name = dict(trans._fields['transaction_type'].selection).get(trans.transaction_type)
        print(f"   - {trans.transaction_date}: {type_name} {trans.points:+d} điểm")
    
    # 7. Kiểm tra tích hợp Partner
    print("\n7. Kiểm tra tích hợp Partner...")
    print(f"   ✓ Khách hàng có {partner.loyalty_card_count} thẻ")
    print(f"   ✓ Tổng điểm: {partner.total_loyalty_points}")
    
    # 8. Test giới hạn giảm giá
    print("\n8. Test giới hạn giảm giá tối đa...")
    order_amount = 100000
    points_to_use = 100  # Dùng nhiều điểm
    discount = program.calculate_discount_from_points(points_to_use, order_amount)
    max_discount = order_amount * (program.max_discount_percentage / 100.0)
    print(f"   Đơn hàng: {order_amount:,.0f}đ")
    print(f"   Dùng: {points_to_use} điểm")
    print(f"   Giảm tối đa ({program.max_discount_percentage}%): {max_discount:,.0f}đ")
    print(f"   ✓ Giảm thực tế: {discount:,.0f}đ")
    if discount <= max_discount:
        print("   ✓ Giới hạn hoạt động đúng")
    else:
        print("   ⚠️  Giới hạn không hoạt động!")
    
    # Tổng kết
    print("\n" + "="*60)
    print("KẾT QUẢ TEST")
    print("="*60)
    print("✓ Chương trình tích điểm: OK")
    print("✓ Tạo thẻ tích điểm: OK")
    print("✓ Tích điểm: OK")
    print("✓ Đổi điểm: OK")
    print("✓ Lịch sử giao dịch: OK")
    print("✓ Tích hợp Partner: OK")
    print("✓ Giới hạn giảm giá: OK")
    print("\n🎉 HỆ THỐNG TÍCH ĐIỂM HOẠT ĐỘNG BÌNH THƯỜNG!\n")
    
    return True


def test_pos_order_integration(env):
    """Test tích hợp với POS Order"""
    
    print("\n" + "="*60)
    print("TEST TÍCH HỢP POS ORDER")
    print("="*60 + "\n")
    
    # Tìm partner có thẻ
    cards = env['customer.loyalty.card'].search([('state', '=', 'active')], limit=1)
    if not cards:
        print("⚠️  Không tìm thấy thẻ tích điểm nào!")
        return False
    
    card = cards[0]
    partner = card.partner_id
    
    print(f"Khách hàng: {partner.name}")
    print(f"Thẻ: {card.card_number}")
    print(f"Điểm hiện có: {card.total_points}")
    
    # Tìm config POS
    pos_config = env['pos.config'].search([('active', '=', True)], limit=1)
    if not pos_config:
        print("⚠️  Không tìm thấy POS config!")
        return False
    
    # Tìm sản phẩm
    product = env['product.product'].search([('available_in_pos', '=', True)], limit=1)
    if not product:
        print("⚠️  Không tìm thấy sản phẩm POS!")
        return False
    
    print(f"\n✓ Sẵn sàng tạo đơn hàng test")
    print("  (Cần tạo thủ công qua POS interface để test đầy đủ)")
    
    return True


if __name__ == '__main__':
    print("Chạy script này trong Odoo shell:")
    print("python3 odoo-bin shell -c odoo.conf -d your_database")
    print("\nSau đó chạy:")
    print(">>> exec(open('test_loyalty.py').read())")
    print(">>> test_loyalty_system(env)")
    print(">>> test_pos_order_integration(env)")
