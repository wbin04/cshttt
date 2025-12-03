# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, timedelta


class StockLot(models.Model):
    """Mở rộng stock.lot để thêm tính năng cảnh báo hết hạn"""
    _inherit = 'stock.lot'
    
    is_expired = fields.Boolean(
        string='Đã hết hạn',
        compute='_compute_expiry_status',
        store=False
    )
    
    is_expiring_soon = fields.Boolean(
        string='Sắp hết hạn',
        compute='_compute_expiry_status',
        store=False
    )
    
    @api.depends('expiration_date')
    def _compute_expiry_status(self):
        """Tính toán trạng thái hết hạn"""
        today = fields.Date.today()
        warning_days = 7  # Cảnh báo trước 7 ngày
        
        for lot in self:
            if lot.expiration_date:
                # Chuyển expiration_date về date để so sánh
                expiry_date = lot.expiration_date
                if hasattr(expiry_date, 'date'):
                    # Nếu là datetime, chuyển về date
                    expiry_date = expiry_date.date()
                elif isinstance(expiry_date, str):
                    expiry_date = fields.Date.from_string(expiry_date)
                
                # Đã hết hạn
                lot.is_expired = expiry_date < today
                
                # Sắp hết hạn (trong vòng 7 ngày)
                days_until_expiry = (expiry_date - today).days
                lot.is_expiring_soon = (0 < days_until_expiry <= warning_days)
            else:
                lot.is_expired = False
                lot.is_expiring_soon = False
