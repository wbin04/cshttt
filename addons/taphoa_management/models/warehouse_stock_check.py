# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WarehouseStockCheck(models.Model):
    """Kiểm kê định kỳ"""
    _name = 'taphoa.stock.check'
    _description = 'Kiểm kê kho'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'check_date desc, id desc'

    name = fields.Char(
        string='Số phiếu kiểm kê',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Mới'),
        tracking=True
    )
    
    check_date = fields.Date(
        string='Ngày kiểm kê',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Kho',
        required=True,
        tracking=True
    )
    
    location_id = fields.Many2one(
        'stock.location',
        string='Vị trí kho',
        required=True,
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('in_progress', 'Đang kiểm kê'),
        ('done', 'Hoàn thành'),
        ('cancel', 'Hủy')
    ], string='Trạng thái', default='draft', tracking=True)
    
    line_ids = fields.One2many(
        'taphoa.stock.check.line',
        'check_id',
        string='Chi tiết kiểm kê'
    )
    
    responsible_id = fields.Many2one(
        'res.users',
        string='Người chịu trách nhiệm',
        default=lambda self: self.env.user,
        tracking=True
    )
    
    notes = fields.Text(string='Ghi chú')
    
    total_difference_value = fields.Monetary(
        string='Giá trị chênh lệch',
        compute='_compute_total_difference',
        store=True,
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

    @api.model
    def create(self, vals):
        if vals.get('name', _('Mới')) == _('Mới'):
            vals['name'] = self.env['ir.sequence'].next_by_code('taphoa.stock.check') or _('Mới')
        return super(WarehouseStockCheck, self).create(vals)

    @api.depends('line_ids.difference_value')
    def _compute_total_difference(self):
        for record in self:
            record.total_difference_value = sum(record.line_ids.mapped('difference_value'))

    def action_start_check(self):
        """Bắt đầu kiểm kê - Load danh sách sản phẩm trong kho"""
        self.ensure_one()
        
        # Lấy danh sách sản phẩm có trong kho
        quants = self.env['stock.quant'].search([
            ('location_id', '=', self.location_id.id),
            ('quantity', '>', 0)
        ])
        
        lines = []
        for quant in quants:
            lines.append((0, 0, {
                'product_id': quant.product_id.id,
                'system_qty': quant.quantity,
                'actual_qty': 0,
                'unit_price': quant.product_id.standard_price,
            }))
        
        self.write({
            'line_ids': [(5, 0, 0)] + lines,
            'state': 'in_progress'
        })

    def action_done(self):
        """Hoàn thành kiểm kê - Điều chỉnh tồn kho"""
        for record in self:
            if not record.line_ids:
                raise UserError(_('Không có dữ liệu kiểm kê!'))
            
            # Tạo inventory adjustment cho các chênh lệch
            inventory_adjustment = self.env['stock.inventory'].create({
                'name': f'Kiểm kê: {record.name}',
                'location_ids': [(4, record.location_id.id)],
                'date': record.check_date,
            })
            
            for line in record.line_ids:
                if line.difference_qty != 0:
                    self.env['stock.inventory.line'].create({
                        'inventory_id': inventory_adjustment.id,
                        'product_id': line.product_id.id,
                        'location_id': record.location_id.id,
                        'theoretical_qty': line.system_qty,
                        'product_qty': line.actual_qty,
                    })
            
            if inventory_adjustment.line_ids:
                inventory_adjustment.action_validate()
            
            record.state = 'done'

    def action_cancel(self):
        """Hủy kiểm kê"""
        self.write({'state': 'cancel'})

    def action_draft(self):
        """Chuyển về nháp"""
        self.write({'state': 'draft'})


class WarehouseStockCheckLine(models.Model):
    """Chi tiết kiểm kê"""
    _name = 'taphoa.stock.check.line'
    _description = 'Chi tiết kiểm kê'

    check_id = fields.Many2one(
        'taphoa.stock.check',
        string='Phiếu kiểm kê',
        required=True,
        ondelete='cascade'
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Sản phẩm',
        required=True
    )
    
    system_qty = fields.Float(
        string='Số lượng hệ thống',
        readonly=True
    )
    
    actual_qty = fields.Float(
        string='Số lượng thực tế',
        required=True,
        default=0.0
    )
    
    difference_qty = fields.Float(
        string='Chênh lệch SL',
        compute='_compute_difference',
        store=True
    )
    
    unit_price = fields.Monetary(
        string='Đơn giá',
        currency_field='currency_id'
    )
    
    difference_value = fields.Monetary(
        string='Giá trị chênh lệch',
        compute='_compute_difference',
        store=True,
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        related='check_id.currency_id',
        readonly=True
    )
    
    notes = fields.Text(string='Ghi chú')

    @api.depends('system_qty', 'actual_qty', 'unit_price')
    def _compute_difference(self):
        for line in self:
            line.difference_qty = line.actual_qty - line.system_qty
            line.difference_value = line.difference_qty * line.unit_price
