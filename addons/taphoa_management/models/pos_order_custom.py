# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PosOrderCustom(models.Model):
    """Mở rộng POS Order cho quản lý bán hàng tạp hóa"""
    _inherit = 'pos.order'

    customer_phone = fields.Char(string='Số điện thoại KH')
    customer_address = fields.Text(string='Địa chỉ KH')
    
    payment_qr_code = fields.Char(string='Mã QR thanh toán')
    
    cashier_note = fields.Text(string='Ghi chú thu ngân')
    
    is_debt = fields.Boolean(string='Bán nợ', default=False)
    debt_amount = fields.Monetary(
        string='Số tiền nợ',
        currency_field='currency_id'
    )
    debt_due_date = fields.Date(string='Hạn thanh toán')
    
    # Tích điểm
    loyalty_card_id = fields.Many2one(
        'customer.loyalty.card',
        string='Thẻ tích điểm',
        domain="[('partner_id', '=', partner_id), ('state', '=', 'active')]"
    )
    loyalty_points_earned = fields.Integer(
        string='Điểm tích được',
        compute='_compute_loyalty_points',
        store=True,
        help='Số điểm khách hàng tích được từ đơn hàng này'
    )
    loyalty_points_used = fields.Integer(
        string='Điểm đã sử dụng',
        default=0,
        help='Số điểm khách hàng dùng để giảm giá'
    )
    loyalty_discount_amount = fields.Monetary(
        string='Giảm giá từ điểm',
        currency_field='currency_id',
        compute='_compute_loyalty_discount',
        store=True,
        help='Số tiền giảm giá từ điểm tích lũy'
    )
    loyalty_transaction_id = fields.Many2one(
        'customer.loyalty.transaction',
        string='Giao dịch tích điểm',
        readonly=True,
        copy=False
    )
    
    @api.depends('amount_total', 'loyalty_card_id', 'loyalty_card_id.program_id')
    def _compute_loyalty_points(self):
        """Tính điểm tích được từ đơn hàng"""
        for order in self:
            if order.loyalty_card_id and order.loyalty_card_id.program_id:
                program = order.loyalty_card_id.program_id
                # Trừ đi số tiền giảm giá từ điểm trước khi tính điểm tích
                eligible_amount = order.amount_total - order.loyalty_discount_amount
                order.loyalty_points_earned = program.calculate_points_from_amount(
                    eligible_amount
                )
            else:
                order.loyalty_points_earned = 0
    
    @api.depends('loyalty_points_used', 'loyalty_card_id', 'loyalty_card_id.program_id', 'amount_total')
    def _compute_loyalty_discount(self):
        """Tính số tiền giảm giá từ điểm"""
        for order in self:
            if order.loyalty_points_used > 0 and order.loyalty_card_id:
                program = order.loyalty_card_id.program_id
                order.loyalty_discount_amount = program.calculate_discount_from_points(
                    order.loyalty_points_used,
                    order.amount_total
                )
            else:
                order.loyalty_discount_amount = 0.0
    
    @api.onchange('loyalty_card_id')
    def _onchange_loyalty_card(self):
        """Reset điểm sử dụng khi đổi thẻ"""
        if self.loyalty_card_id:
            self.loyalty_points_used = 0
    
    @api.onchange('loyalty_points_used')
    def _onchange_loyalty_points_used(self):
        """Kiểm tra số điểm sử dụng hợp lệ"""
        if self.loyalty_points_used > 0 and self.loyalty_card_id:
            if self.loyalty_points_used > self.loyalty_card_id.total_points:
                raise UserError(_(
                    'Khách hàng chỉ có %s điểm, không thể sử dụng %s điểm!'
                ) % (self.loyalty_card_id.total_points, self.loyalty_points_used))
            
            if self.loyalty_points_used < self.loyalty_card_id.program_id.min_points_to_redeem:
                raise UserError(_(
                    'Số điểm tối thiểu để đổi là %s điểm!'
                ) % self.loyalty_card_id.program_id.min_points_to_redeem)
    
    def _process_loyalty_points(self):
        """Xử lý tích điểm và đổi điểm sau khi thanh toán"""
        import logging
        _logger = logging.getLogger(__name__)
        
        self.ensure_one()
        
        _logger.info(f"🎁 _process_loyalty_points called for {self.name}: state={self.state}, card={self.loyalty_card_id.card_number if self.loyalty_card_id else None}, points_earned={self.loyalty_points_earned}")
        
        if not self.loyalty_card_id or self.state != 'paid':
            _logger.warning(f"❌ Skip loyalty: card={bool(self.loyalty_card_id)}, state={self.state}")
            return
        
        Transaction = self.env['customer.loyalty.transaction']
        
        # Trừ điểm nếu khách hàng đã sử dụng điểm
        if self.loyalty_points_used > 0:
            Transaction.create({
                'card_id': self.loyalty_card_id.id,
                'transaction_type': 'redeem',
                'points': -self.loyalty_points_used,
                'pos_order_id': self.id,
                'order_amount': self.amount_total,
                'note': _('Đổi điểm cho đơn hàng %s') % self.name,
                'state': 'confirmed',
            })
        
        # Tích điểm cho đơn hàng
        if self.loyalty_points_earned > 0:
            _logger.info(f"✅ Creating earn transaction: {self.loyalty_points_earned} points")
            transaction = Transaction.create({
                'card_id': self.loyalty_card_id.id,
                'transaction_type': 'earn',
                'points': self.loyalty_points_earned,
                'pos_order_id': self.id,
                'order_amount': self.amount_total,
                'note': _('Tích điểm từ đơn hàng %s') % self.name,
                'state': 'confirmed',
            })
            self.loyalty_transaction_id = transaction.id
            _logger.info(f"✅ Transaction created: {transaction.id}, card total points now: {self.loyalty_card_id.total_points}")
    
    def _prepare_invoice_vals(self):
        """Override để thêm giảm giá từ điểm vào hóa đơn"""
        vals = super()._prepare_invoice_vals()
        
        # Thêm thông tin tích điểm vào hóa đơn
        if self.loyalty_discount_amount > 0:
            vals['narration'] = (vals.get('narration') or '') + \
                _('\nGiảm giá từ điểm tích lũy: %s điểm = %s') % (
                    self.loyalty_points_used,
                    self.loyalty_discount_amount
                )
        
        return vals
    
    def action_print_receipt(self):
        """In hóa đơn"""
        return self.env.ref('point_of_sale.pos_invoice_report').report_action(self)
    
    def action_pos_order_paid(self):
        """Override để xử lý tích điểm khi thanh toán"""
        result = super().action_pos_order_paid()
        
        # Xử lý tích điểm
        for order in self:
            order._process_loyalty_points()
        
        return result
    
    @api.model
    def create(self, vals):
        """Override create để tự động tích điểm"""
        import logging
        _logger = logging.getLogger(__name__)
        
        _logger.info(f"🔵 POS Order create called: partner_id={vals.get('partner_id')}, amount_total={vals.get('amount_total')}")
        
        # Tạo order
        order = super().create(vals)
        
        _logger.info(f"🟢 Order created: {order.name}, state={order.state}, partner={order.partner_id.name if order.partner_id else None}")
        
        # Tích điểm nếu có khách hàng
        if order.partner_id and order.amount_total > 0 and order.state in ('paid', 'done', 'invoiced'):
            _logger.info(f"💰 Processing loyalty for order {order.name}")
            
            # Tự động tìm hoặc tạo loyalty card
            card = self.env['customer.loyalty.card'].search([
                ('partner_id', '=', order.partner_id.id),
                ('state', '=', 'active')
            ], limit=1)
            
            if not card:
                default_program = self.env['customer.loyalty.program'].search([
                    ('active', '=', True)
                ], order='sequence', limit=1)
                
                if default_program:
                    _logger.info(f"🆕 Creating loyalty card for {order.partner_id.name}")
                    card = self.env['customer.loyalty.card'].create({
                        'partner_id': order.partner_id.id,
                        'program_id': default_program.id,
                    })
            
            if card:
                order.loyalty_card_id = card.id
                program = card.program_id
                points_earned = program.calculate_points_from_amount(order.amount_total)
                
                if points_earned > 0:
                    _logger.info(f"💎 Earning {points_earned} points")
                    transaction = self.env['customer.loyalty.transaction'].create({
                        'card_id': card.id,
                        'transaction_type': 'earn',
                        'points': points_earned,
                        'pos_order_id': order.id,
                        'order_amount': order.amount_total,
                        'note': _('Tích điểm từ đơn hàng %s') % order.name,
                        'state': 'confirmed',
                    })
                    order.write({
                        'loyalty_points_earned': points_earned,
                        'loyalty_transaction_id': transaction.id,
                    })
                    _logger.info(f"✅ Done! Card {card.card_number} now has {card.total_points} points")
        
        return order
    
    @api.model
    def create_from_ui(self, orders, draft=False):
        """Override để tự động tích điểm khi tạo order từ POS UI"""
        import logging
        _logger = logging.getLogger(__name__)
        
        _logger.info(f"🎯 create_from_ui called with {len(orders)} orders, draft={draft}")
        
        # Gọi method gốc để tạo orders
        order_ids = super().create_from_ui(orders, draft=draft)
        
        # Xử lý tích điểm cho mỗi order vừa tạo
        created_orders = self.env['pos.order'].browse([o['id'] for o in order_ids])
        
        for order in created_orders:
            _logger.info(f"✅ Processing order {order.name}: state={order.state}, partner={order.partner_id.name if order.partner_id else None}, amount={order.amount_total}")
            
            # Tích điểm nếu có khách hàng và có tổng tiền
            if order.partner_id and order.amount_total > 0:
                # Tự động tìm hoặc tạo loyalty card cho khách hàng
                card = self.env['customer.loyalty.card'].search([
                    ('partner_id', '=', order.partner_id.id),
                    ('state', '=', 'active')
                ], limit=1)
                
                # Nếu không có card, tự động tạo mới với program mặc định
                if not card:
                    default_program = self.env['customer.loyalty.program'].search([
                        ('active', '=', True)
                    ], order='sequence', limit=1)
                    
                    if default_program:
                        _logger.info(f"🆕 Creating new loyalty card for {order.partner_id.name}")
                        card = self.env['customer.loyalty.card'].create({
                            'partner_id': order.partner_id.id,
                            'program_id': default_program.id,
                        })
                
                if card:
                    order.loyalty_card_id = card.id
                    
                    # 1. Xử lý ĐỔI ĐIỂM (REDEEM) trước - kiểm tra order lines có discount từ loyalty không
                    loyalty_discount_product = self.env['pos.config'].browse(order.session_id.config_id.id).loyalty_discount_product_id
                    redeem_points = 0
                    discount_amount = 0
                    
                    if loyalty_discount_product:
                        for line in order.lines:
                            if line.product_id.id == loyalty_discount_product.id and line.price_unit < 0:
                                discount_amount = abs(line.price_unit * line.qty)
                                # 100 điểm = 1000đ => 1 điểm = 10đ
                                redeem_points = int(discount_amount / 10)
                                _logger.info(f"🎁 Found loyalty discount line: -{discount_amount}đ = {redeem_points} points")
                                break
                    
                    # Nếu có đổi điểm, tạo redeem transaction
                    if redeem_points > 0:
                        _logger.info(f"💎 Creating redeem transaction: -{redeem_points} points for {discount_amount}đ discount")
                        redeem_transaction = self.env['customer.loyalty.transaction'].create({
                            'card_id': card.id,
                            'transaction_type': 'redeem',
                            'points': -redeem_points,  # Điểm âm = trừ điểm
                            'pos_order_id': order.id,
                            'order_amount': order.amount_total,
                            'note': _('Đổi %s điểm lấy giảm giá %s đ từ đơn hàng %s') % (redeem_points, discount_amount, order.name),
                            'state': 'confirmed',
                        })
                        order.write({
                            'loyalty_points_used': redeem_points,
                            'loyalty_discount_amount': discount_amount,
                        })
                        _logger.info(f"✅ Points redeemed! Card {card.card_number} now has {card.total_points} points")
                    
                    # 2. Tính và tạo transaction TÍCH ĐIỂM (EARN) - tính trên số tiền THỰC tế sau giảm giá
                    program = card.program_id
                    actual_amount = order.amount_total  # Tổng tiền thực tế sau khi đã trừ discount
                    points_earned = program.calculate_points_from_amount(actual_amount)
                    
                    if points_earned > 0:
                        _logger.info(f"💎 Creating earn transaction: {points_earned} points for order {order.name}")
                        earn_transaction = self.env['customer.loyalty.transaction'].create({
                            'card_id': card.id,
                            'transaction_type': 'earn',
                            'points': points_earned,
                            'pos_order_id': order.id,
                            'order_amount': actual_amount,
                            'note': _('Tích điểm từ đơn hàng %s') % order.name,
                            'state': 'confirmed',
                        })
                        order.write({
                            'loyalty_points_earned': points_earned,
                            'loyalty_transaction_id': earn_transaction.id,
                        })
                        _logger.info(f"✅ Points earned! Card {card.card_number} now has {card.total_points} points")
        
        return order_ids


class PosOrderLineCustom(models.Model):
    """Mở rộng POS Order Line"""
    _inherit = 'pos.order.line'

    discount_amount = fields.Monetary(
        string='Tiền giảm giá',
        compute='_compute_discount_amount',
        store=True,
        currency_field='currency_id'
    )

    @api.depends('price_unit', 'qty', 'discount')
    def _compute_discount_amount(self):
        for line in self:
            line.discount_amount = line.price_unit * line.qty * (line.discount / 100.0)


class PosConfig(models.Model):
    """Cấu hình POS cho tạp hóa"""
    _inherit = 'pos.config'

    enable_debt_sale = fields.Boolean(
        string='Cho phép bán nợ',
        default=False,
        help='Cho phép thu ngân bán hàng cho khách chưa thanh toán đủ'
    )
    
    enable_qr_payment = fields.Boolean(
        string='Thanh toán QR',
        default=True,
        help='Hỗ trợ thanh toán qua mã QR'
    )
    
    low_stock_warning = fields.Boolean(
        string='Cảnh báo tồn kho thấp',
        default=True,
        help='Hiển thị cảnh báo khi sản phẩm sắp hết hàng'
    )
    
    low_stock_threshold = fields.Float(
        string='Ngưỡng cảnh báo tồn kho',
        default=10.0,
        help='Số lượng tối thiểu để cảnh báo'
    )
    
    # Tích điểm
    enable_loyalty = fields.Boolean(
        string='Kích hoạt tích điểm',
        default=True,
        help='Cho phép tích điểm và đổi điểm tại POS'
    )
    
    loyalty_discount_product_id = fields.Many2one(
        'product.product',
        string='Sản phẩm giảm giá từ điểm',
        help='Sản phẩm dùng để tạo dòng giảm giá khi đổi điểm'
    )
