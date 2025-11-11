# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardStockImport(models.TransientModel):
    """Wizard đơn giản để nhập hàng vào kho"""
    _name = 'wizard.stock.import'
    _description = 'Nhập hàng vào kho nhanh'

    product_id = fields.Many2one(
        'product.product',
        string='Sản phẩm',
        required=True,
        domain=[('type', '=', 'product')]
    )
    
    quantity = fields.Float(
        string='Số lượng nhập',
        required=True,
        default=1.0
    )
    
    location_id = fields.Many2one(
        'stock.location',
        string='Kho nhập',
        required=True,
        domain=[('usage', '=', 'internal')]
    )
    
    reference = fields.Char(
        string='Tham chiếu',
        help='Số phiếu nhập hoặc ghi chú'
    )

    @api.model
    def default_get(self, fields_list):
        """Lấy giá trị mặc định"""
        res = super(WizardStockImport, self).default_get(fields_list)
        
        # Tự động chọn kho mặc định
        if 'location_id' in fields_list:
            location = self.env['stock.location'].search([
                ('usage', '=', 'internal'),
                ('company_id', '=', self.env.company.id)
            ], limit=1)
            if location:
                res['location_id'] = location.id
        
        # Nếu có product_id từ context (mở từ form sản phẩm)
        if self._context.get('active_model') == 'product.product':
            res['product_id'] = self._context.get('active_id')
        elif self._context.get('active_model') == 'product.template':
            template_id = self._context.get('active_id')
            product = self.env['product.product'].search([
                ('product_tmpl_id', '=', template_id)
            ], limit=1)
            if product:
                res['product_id'] = product.id
                
        return res

    def action_import_stock(self):
        """Thực hiện nhập hàng vào kho"""
        self.ensure_one()
        
        if self.quantity <= 0:
            raise UserError(_('Số lượng nhập phải lớn hơn 0!'))
        
        # Tìm location nguồn (Supplier/Vendor)
        location_src = self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False)
        if not location_src:
            location_src = self.env['stock.location'].search([
                ('usage', '=', 'supplier')
            ], limit=1)
        
        if not location_src:
            raise UserError(_('Không tìm thấy kho nguồn (Supplier Location)!'))
        
        # Tạo stock move để nhập hàng
        stock_move = self.env['stock.move'].create({
            'name': self.reference or _('Nhập hàng: %s') % self.product_id.name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': self.product_id.uom_id.id,
            'location_id': location_src.id,
            'location_dest_id': self.location_id.id,
            'state': 'draft',
        })
        
        # Xác nhận và thực hiện move
        stock_move._action_confirm()
        stock_move._action_assign()
        stock_move._action_done()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Thành công!'),
                'message': _('Đã nhập %s %s vào kho %s') % (
                    self.quantity,
                    self.product_id.name,
                    self.location_id.name
                ),
                'type': 'success',
                'sticky': False,
            }
        }
