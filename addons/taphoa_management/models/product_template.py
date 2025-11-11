# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    """Mở rộng Product Template"""
    _inherit = 'product.template'

    min_stock_qty = fields.Float(
        string='Tồn kho tối thiểu',
        default=10.0,
        help='Số lượng tồn kho tối thiểu, dưới mức này sẽ cảnh báo'
    )
    
    max_stock_qty = fields.Float(
        string='Tồn kho tối đa',
        default=1000.0,
        help='Số lượng tồn kho tối đa'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Tự động bật sản phẩm cho POS và bán hàng khi tạo mới"""
        for vals in vals_list:
            # BẮT BUỘC bật các tùy chọn quan trọng (override nếu có)
            vals['available_in_pos'] = True
            vals['sale_ok'] = True
            
            # Chỉ set type nếu chưa có hoặc là 'consu'
            if 'type' not in vals or vals.get('type') == 'consu':
                vals['type'] = 'product'
        return super(ProductTemplate, self).create(vals_list)
    
    is_fast_moving = fields.Boolean(
        string='Hàng bán chạy',
        compute='_compute_is_fast_moving',
        store=True,
        help='Sản phẩm được đánh dấu là hàng bán chạy'
    )
    
    total_sold_qty = fields.Float(
        string='Tổng số lượng đã bán',
        compute='_compute_total_sold',
        store=True
    )
    
    supplier_ids = fields.Many2many(
        'res.partner',
        'product_supplier_rel',
        'product_id',
        'partner_id',
        string='Nhà cung cấp',
        domain=[('supplier_rank', '>', 0)]
    )
    
    shelf_location = fields.Char(
        string='Vị trí kệ hàng',
        help='Vị trí của sản phẩm trên kệ hàng'
    )
    
    expiry_days = fields.Integer(
        string='Số ngày hết hạn',
        help='Số ngày từ ngày sản xuất đến hết hạn sử dụng'
    )

    @api.depends('product_variant_ids.sales_count')
    def _compute_total_sold(self):
        for template in self:
            template.total_sold_qty = sum(
                template.product_variant_ids.mapped('sales_count')
            )

    @api.depends('total_sold_qty')
    def _compute_is_fast_moving(self):
        for template in self:
            # Sản phẩm bán trên 100 đơn vị được coi là hàng bán chạy
            template.is_fast_moving = template.total_sold_qty > 100


class ProductProduct(models.Model):
    """Mở rộng Product Product"""
    _inherit = 'product.product'

    current_stock = fields.Float(
        string='Tồn kho hiện tại',
        compute='_compute_current_stock',
        search='_search_current_stock'
    )
    
    stock_status = fields.Selection([
        ('in_stock', 'Còn hàng'),
        ('low_stock', 'Sắp hết'),
        ('out_of_stock', 'Hết hàng')
    ], string='Trạng thái tồn kho', compute='_compute_stock_status')

    @api.depends('qty_available')
    def _compute_current_stock(self):
        for product in self:
            product.current_stock = product.qty_available

    def _search_current_stock(self, operator, value):
        products = self.search([])
        product_ids = []
        for product in products:
            if operator == '>' and product.qty_available > value:
                product_ids.append(product.id)
            elif operator == '<' and product.qty_available < value:
                product_ids.append(product.id)
            elif operator == '=' and product.qty_available == value:
                product_ids.append(product.id)
        return [('id', 'in', product_ids)]

    @api.depends('qty_available', 'product_tmpl_id.min_stock_qty')
    def _compute_stock_status(self):
        for product in self:
            if product.qty_available <= 0:
                product.stock_status = 'out_of_stock'
            elif product.qty_available < product.product_tmpl_id.min_stock_qty:
                product.stock_status = 'low_stock'
            else:
                product.stock_status = 'in_stock'
