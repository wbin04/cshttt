# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardFixProducts(models.TransientModel):
    """Wizard để sửa sản phẩm hiện có - bật POS và đổi type"""
    _name = 'wizard.fix.products'
    _description = 'Sửa cấu hình sản phẩm cho POS'

    product_ids = fields.Many2many(
        'product.template',
        string='Sản phẩm cần sửa',
        help='Chọn sản phẩm cần bật POS và đổi thành Storable Product'
    )
    
    enable_pos = fields.Boolean(
        string='Bật hiển thị trong POS',
        default=True,
        help='Tự động bật "Available in POS" cho các sản phẩm đã chọn'
    )
    
    enable_sale = fields.Boolean(
        string='Bật có thể bán',
        default=True,
        help='Tự động bật "Can be Sold" cho các sản phẩm đã chọn'
    )
    
    set_storable = fields.Boolean(
        string='Đổi thành sản phẩm tồn kho',
        default=True,
        help='Đổi Product Type thành "Storable Product" để quản lý tồn kho'
    )

    @api.model
    def default_get(self, fields_list):
        """Lấy sản phẩm từ context"""
        res = super(WizardFixProducts, self).default_get(fields_list)
        
        # Nếu được gọi từ list view với active_ids
        if self._context.get('active_model') == 'product.template' and self._context.get('active_ids'):
            res['product_ids'] = [(6, 0, self._context.get('active_ids'))]
        else:
            # Tự động tìm sản phẩm chưa bật POS hoặc type không phải 'product'
            products = self.env['product.template'].search([
                '|',
                ('available_in_pos', '=', False),
                ('type', '!=', 'product')
            ])
            if products:
                res['product_ids'] = [(6, 0, products.ids)]
                
        return res

    def action_fix_products(self):
        """Thực hiện sửa sản phẩm"""
        self.ensure_one()
        
        if not self.product_ids:
            raise UserError(_('Vui lòng chọn ít nhất 1 sản phẩm!'))
        
        vals = {}
        
        if self.enable_pos:
            vals['available_in_pos'] = True
            
        if self.enable_sale:
            vals['sale_ok'] = True
            
        if self.set_storable:
            vals['type'] = 'product'
        
        if vals:
            self.product_ids.write(vals)
        
        message = _('Đã cập nhật %s sản phẩm thành công!') % len(self.product_ids)
        
        if self.enable_pos:
            message += _('\n✓ Bật hiển thị trong POS')
        if self.enable_sale:
            message += _('\n✓ Bật có thể bán')
        if self.set_storable:
            message += _('\n✓ Đổi thành Storable Product')
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Thành công!'),
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }
