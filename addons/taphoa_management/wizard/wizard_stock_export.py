# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class WizardStockExport(models.TransientModel):
    """Wizard để xuất báo cáo tồn kho"""
    _name = 'wizard.stock.export'
    _description = 'Xuất báo cáo tồn kho'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Kho',
        required=True
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
        ('summary', 'Tổng hợp'),
        ('detail', 'Chi tiết'),
        ('low_stock', 'Sắp hết hàng')
    ], string='Loại báo cáo', default='summary', required=True)

    def action_export_excel(self):
        """Xuất báo cáo ra Excel"""
        # Placeholder for Excel export functionality
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/export/stock_report',
            'target': 'new',
        }

    def action_print_pdf(self):
        """In báo cáo PDF"""
        return self.env.ref('taphoa_management.action_report_stock').report_action(self)
