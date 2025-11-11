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
        self.ensure_one()
        
        if not self.loyalty_card_id or self.state != 'paid':
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
