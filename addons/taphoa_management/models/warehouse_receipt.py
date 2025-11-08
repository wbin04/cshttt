# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WarehouseReceipt(models.Model):
    """Phiếu nhập kho - Quản lý nhập hàng từ nhà cung cấp"""
    _name = 'taphoa.warehouse.receipt'
    _description = 'Phiếu nhập kho'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'receipt_date desc, id desc'

    name = fields.Char(
        string='Số phiếu nhập',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Mới'),
        tracking=True
    )
    
    receipt_date = fields.Datetime(
        string='Ngày nhập kho',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Nhà cung cấp',
        required=True,
        domain=[('supplier_rank', '>', 0)],
        tracking=True
    )
    
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Kho',
        required=True,
        default=lambda self: self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1),
        tracking=True
    )
    
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Đơn mua hàng',
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('quality_check', 'Kiểm tra chất lượng'),
        ('approved', 'Đã duyệt'),
        ('done', 'Hoàn thành'),
        ('cancel', 'Hủy')
    ], string='Trạng thái', default='draft', tracking=True)
    
    line_ids = fields.One2many(
        'taphoa.warehouse.receipt.line',
        'receipt_id',
        string='Chi tiết sản phẩm'
    )
    
    total_amount = fields.Monetary(
        string='Tổng tiền',
        compute='_compute_total_amount',
        store=True,
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    notes = fields.Text(string='Ghi chú')
    
    quality_check_note = fields.Text(string='Ghi chú kiểm tra chất lượng')
    
    checked_by = fields.Many2one('res.users', string='Người kiểm tra')
    checked_date = fields.Datetime(string='Ngày kiểm tra')
    
    approved_by = fields.Many2one('res.users', string='Người duyệt')
    approved_date = fields.Datetime(string='Ngày duyệt')
    
    company_id = fields.Many2one(
        'res.company',
        string='Công ty',
        default=lambda self: self.env.company
    )
    
    picking_id = fields.Many2one(
        'stock.picking',
        string='Phiếu nhập kho',
        readonly=True
    )

    @api.model
    def create(self, vals):
        if vals.get('name', _('Mới')) == _('Mới'):
            vals['name'] = self.env['ir.sequence'].next_by_code('taphoa.warehouse.receipt') or _('Mới')
        return super(WarehouseReceipt, self).create(vals)

    @api.depends('line_ids.subtotal')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('subtotal'))

    def action_quality_check(self):
        """Chuyển sang trạng thái kiểm tra chất lượng"""
        self.write({
            'state': 'quality_check',
            'checked_by': self.env.user.id,
            'checked_date': fields.Datetime.now()
        })

    def action_approve(self):
        """Phê duyệt phiếu nhập kho"""
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now()
        })

    def action_done(self):
        """Hoàn thành nhập kho - Tạo phiếu nhập kho thực tế"""
        for record in self:
            if not record.line_ids:
                raise UserError(_('Vui lòng thêm sản phẩm vào phiếu nhập kho!'))
            
            # Tạo picking để nhập kho
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'incoming'),
                ('warehouse_id', '=', record.warehouse_id.id)
            ], limit=1)
            
            if not picking_type:
                raise UserError(_('Không tìm thấy loại phiếu nhập kho!'))
            
            picking_vals = {
                'partner_id': record.partner_id.id,
                'picking_type_id': picking_type.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': picking_type.default_location_dest_id.id,
                'origin': record.name,
                'move_ids_without_package': []
            }
            
            for line in record.line_ids:
                move_vals = {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': picking_type.default_location_dest_id.id,
                }
                picking_vals['move_ids_without_package'].append((0, 0, move_vals))
            
            picking = self.env['stock.picking'].create(picking_vals)
            picking.action_confirm()
            picking.action_assign()
            
            # Tự động xác nhận số lượng
            for move in picking.move_ids:
                move.quantity = move.product_uom_qty
            
            picking.button_validate()
            
            record.write({
                'state': 'done',
                'picking_id': picking.id
            })

    def action_cancel(self):
        """Hủy phiếu nhập kho"""
        self.write({'state': 'cancel'})

    def action_draft(self):
        """Chuyển về nháp"""
        self.write({'state': 'draft'})


class WarehouseReceiptLine(models.Model):
    """Chi tiết phiếu nhập kho"""
    _name = 'taphoa.warehouse.receipt.line'
    _description = 'Chi tiết phiếu nhập kho'

    receipt_id = fields.Many2one(
        'taphoa.warehouse.receipt',
        string='Phiếu nhập kho',
        required=True,
        ondelete='cascade'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Sản phẩm',
        required=True,
        domain=[('type', 'in', ['product', 'consu'])]
    )
    
    quantity = fields.Float(
        string='Số lượng',
        required=True,
        default=1.0
    )
    
    uom_id = fields.Many2one(
        'uom.uom',
        string='Đơn vị',
        related='product_id.uom_id',
        readonly=True
    )
    
    unit_price = fields.Monetary(
        string='Đơn giá',
        required=True,
        currency_field='currency_id'
    )
    
    subtotal = fields.Monetary(
        string='Thành tiền',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        related='receipt_id.currency_id',
        readonly=True
    )
    
    expiry_date = fields.Date(string='Hạn sử dụng')
    
    lot_name = fields.Char(string='Lô sản xuất')
    
    quality_status = fields.Selection([
        ('good', 'Tốt'),
        ('acceptable', 'Chấp nhận'),
        ('reject', 'Từ chối')
    ], string='Chất lượng', default='good')
    
    notes = fields.Text(string='Ghi chú')

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.standard_price
