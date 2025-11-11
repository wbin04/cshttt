# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountingReport(models.Model):
    """Báo cáo kế toán tổng hợp"""
    _name = 'taphoa.accounting.report'
    _description = 'Báo cáo kế toán'
    _order = 'date_from desc'

    name = fields.Char(
        string='Tên báo cáo',
        required=True,
        default='Báo cáo kế toán'
    )
    
    date_from = fields.Date(
        string='Từ ngày',
        required=True,
        default=fields.Date.context_today
    )
    
    date_to = fields.Date(
        string='Đến ngày',
        required=True,
        default=fields.Date.context_today
    )
    
    report_type = fields.Selection([
        ('revenue', 'Doanh thu'),
        ('expense', 'Chi phí'),
        ('profit', 'Lợi nhuận'),
        ('debt', 'Công nợ'),
        ('general', 'Tổng hợp')
    ], string='Loại báo cáo', required=True, default='general')
    
    total_revenue = fields.Monetary(
        string='Tổng doanh thu',
        compute='_compute_totals',
        currency_field='currency_id'
    )
    
    total_expense = fields.Monetary(
        string='Tổng chi phí',
        compute='_compute_totals',
        currency_field='currency_id'
    )
    
    total_profit = fields.Monetary(
        string='Lợi nhuận',
        compute='_compute_totals',
        currency_field='currency_id'
    )
    
    total_debt = fields.Monetary(
        string='Tổng công nợ',
        compute='_compute_totals',
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company
    )

    @api.depends('date_from', 'date_to', 'report_type')
    def _compute_totals(self):
        for record in self:
            # Tính doanh thu từ POS và Sale Order
            pos_orders = self.env['pos.order'].search([
                ('date_order', '>=', record.date_from),
                ('date_order', '<=', record.date_to),
                ('state', 'in', ['paid', 'done', 'invoiced'])
            ])
            record.total_revenue = sum(pos_orders.mapped('amount_total'))
            
            # Tính chi phí từ Purchase Order
            purchase_orders = self.env['purchase.order'].search([
                ('date_order', '>=', record.date_from),
                ('date_order', '<=', record.date_to),
                ('state', '=', 'purchase')
            ])
            record.total_expense = sum(purchase_orders.mapped('amount_total'))
            
            # Tính lợi nhuận
            record.total_profit = record.total_revenue - record.total_expense
            
            # Tính công nợ
            partners = self.env['res.partner'].search([
                ('customer_rank', '>', 0)
            ])
            record.total_debt = sum(partners.mapped('debit'))

    def action_generate_report(self):
        """Tạo báo cáo"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Báo cáo kế toán',
            'res_model': 'taphoa.accounting.report',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }


class AccountMove(models.Model):
    """Mở rộng Account Move"""
    _inherit = 'account.move'

    warehouse_receipt_id = fields.Many2one(
        'taphoa.warehouse.receipt',
        string='Phiếu nhập kho',
        readonly=True
    )
    
    is_pos_invoice = fields.Boolean(
        string='Hóa đơn POS',
        compute='_compute_is_pos_invoice',
        store=True
    )

    @api.depends('invoice_origin')
    def _compute_is_pos_invoice(self):
        for record in self:
            record.is_pos_invoice = bool(
                record.invoice_origin and 
                record.invoice_origin.startswith('POS')
            )
