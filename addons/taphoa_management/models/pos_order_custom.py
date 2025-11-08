# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


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
    
    def action_print_receipt(self):
        """In hóa đơn"""
        return self.env.ref('point_of_sale.pos_invoice_report').report_action(self)


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
