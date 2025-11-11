# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class ManagerDashboard(models.Model):
    """Dashboard cho Chủ cửa hàng"""
    _name = 'taphoa.manager.dashboard'
    _description = 'Dashboard Quản lý Tạp hóa'

    name = fields.Char(string='Tên', default='Dashboard', readonly=True)
    
    # Statistics fields - computed
    total_pos_orders_today = fields.Integer(
        string='Đơn POS hôm nay',
        compute='_compute_statistics'
    )
    total_revenue_today = fields.Monetary(
        string='Doanh thu hôm nay',
        compute='_compute_statistics',
        currency_field='currency_id'
    )
    total_pos_orders_month = fields.Integer(
        string='Đơn POS tháng này',
        compute='_compute_statistics'
    )
    total_revenue_month = fields.Monetary(
        string='Doanh thu tháng này',
        compute='_compute_statistics',
        currency_field='currency_id'
    )
    
    # Purchase orders
    total_purchase_orders = fields.Integer(
        string='Đơn mua hàng chờ',
        compute='_compute_statistics'
    )
    total_purchase_amount = fields.Monetary(
        string='Tổng giá trị đơn mua',
        compute='_compute_statistics',
        currency_field='currency_id'
    )
    
    # Warehouse receipts
    total_warehouse_receipts = fields.Integer(
        string='Phiếu nhập kho chờ',
        compute='_compute_statistics'
    )
    total_warehouse_amount = fields.Monetary(
        string='Tổng giá trị nhập kho',
        compute='_compute_statistics',
        currency_field='currency_id'
    )
    
    # Stock
    low_stock_products = fields.Integer(
        string='SP sắp hết hàng',
        compute='_compute_statistics'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    @api.depends('name')
    def _compute_statistics(self):
        """Tính toán các thống kê"""
        for record in self:
            today = fields.Date.today()
            month_start = today.replace(day=1)
            
            # POS Orders today
            pos_orders_today = self.env['pos.order'].search([
                ('date_order', '>=', fields.Datetime.now().replace(hour=0, minute=0, second=0)),
                ('state', 'in', ['paid', 'done', 'invoiced'])
            ])
            record.total_pos_orders_today = len(pos_orders_today)
            record.total_revenue_today = sum(pos_orders_today.mapped('amount_total'))
            
            # POS Orders this month
            pos_orders_month = self.env['pos.order'].search([
                ('date_order', '>=', month_start),
                ('state', 'in', ['paid', 'done', 'invoiced'])
            ])
            record.total_pos_orders_month = len(pos_orders_month)
            record.total_revenue_month = sum(pos_orders_month.mapped('amount_total'))
            
            # Purchase Orders (draft, sent, to approve)
            purchase_orders = self.env['purchase.order'].search([
                ('state', 'in', ['draft', 'sent', 'to approve'])
            ])
            record.total_purchase_orders = len(purchase_orders)
            record.total_purchase_amount = sum(purchase_orders.mapped('amount_total'))
            
            # Warehouse receipts (draft)
            warehouse_receipts = self.env['taphoa.warehouse.receipt'].search([
                ('state', '=', 'draft')
            ])
            record.total_warehouse_receipts = len(warehouse_receipts)
            record.total_warehouse_amount = sum(warehouse_receipts.mapped('total_amount'))
            
            # Low stock products (qty < 10)
            products = self.env['product.product'].search([
                ('qty_available', '<', 10),
                ('qty_available', '>', 0),
                ('type', '=', 'product')
            ])
            record.low_stock_products = len(products)

    def action_view_pos_orders_today(self):
        """Xem đơn POS hôm nay"""
        today = fields.Datetime.now().replace(hour=0, minute=0, second=0)
        return {
            'name': _('Đơn POS hôm nay'),
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order',
            'view_mode': 'tree,form',
            'domain': [
                ('date_order', '>=', today),
                ('state', 'in', ['paid', 'done', 'invoiced'])
            ],
            'context': {'create': False}
        }

    def action_view_pos_orders_month(self):
        """Xem đơn POS tháng này"""
        month_start = fields.Date.today().replace(day=1)
        return {
            'name': _('Đơn POS tháng này'),
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order',
            'view_mode': 'tree,form',
            'domain': [
                ('date_order', '>=', month_start),
                ('state', 'in', ['paid', 'done', 'invoiced'])
            ],
            'context': {'create': False}
        }

    def action_view_purchase_orders(self):
        """Xem đơn mua hàng chờ duyệt"""
        return {
            'name': _('Đơn mua hàng chờ duyệt'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('state', 'in', ['draft', 'sent', 'to approve'])],
            'context': {'create': True}
        }

    def action_view_warehouse_receipts(self):
        """Xem phiếu nhập kho chờ xử lý"""
        return {
            'name': _('Phiếu nhập kho chờ xử lý'),
            'type': 'ir.actions.act_window',
            'res_model': 'taphoa.warehouse.receipt',
            'view_mode': 'tree,form',
            'domain': [('state', '=', 'draft')],
            'context': {'create': True}
        }

    def action_view_low_stock(self):
        """Xem sản phẩm sắp hết hàng"""
        return {
            'name': _('Sản phẩm sắp hết hàng'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'tree,form',
            'domain': [
                ('qty_available', '<', 10),
                ('qty_available', '>', 0),
                ('type', '=', 'product')
            ],
            'context': {'create': False}
        }

    def action_refresh_dashboard(self):
        """Refresh dashboard data"""
        self._compute_statistics()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
