# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WarehouseReceipt(models.Model):
    """Model quản lý phiếu nhập kho"""
    _name = 'taphoa.warehouse.receipt'
    _description = 'Phiếu nhập kho'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'receipt_date desc, id desc'
    
    # % lợi nhuận mặc định (có thể thay đổi trên từng phiếu nhập)
    profit_margin = fields.Float(
        string='% Lợi nhuận',
        default=20.0,
        help='Phần trăm lợi nhuận cộng thêm vào giá vốn để tính giá bán'
    )

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
            
            # Lấy location nguồn (từ nhà cung cấp)
            location_src_id = picking_type.default_location_src_id.id if picking_type.default_location_src_id else False
            if not location_src_id:
                # Tìm supplier location
                location_src = self.env['stock.location'].search([
                    ('usage', '=', 'supplier')
                ], limit=1)
                if not location_src:
                    raise UserError(_('Không tìm thấy địa điểm nguồn (Supplier Location)! Vui lòng cấu hình trong Kho > Cấu hình > Địa điểm'))
                location_src_id = location_src.id
            
            # Lấy location đích (kho)
            location_dest_id = picking_type.default_location_dest_id.id if picking_type.default_location_dest_id else False
            if not location_dest_id:
                # Tìm internal location của warehouse
                location_dest = self.env['stock.location'].search([
                    ('usage', '=', 'internal'),
                    ('warehouse_id', '=', record.warehouse_id.id)
                ], limit=1)
                if not location_dest:
                    raise UserError(_('Không tìm thấy địa điểm đích (kho)! Vui lòng cấu hình kho'))
                location_dest_id = location_dest.id
            
            picking_vals = {
                'partner_id': record.partner_id.id,
                'picking_type_id': picking_type.id,
                'location_id': location_src_id,
                'location_dest_id': location_dest_id,
                'origin': record.name,
                'move_ids_without_package': []
            }
            
            for line in record.line_ids:
                move_vals = {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': location_src_id,
                    'location_dest_id': location_dest_id,
                }
                picking_vals['move_ids_without_package'].append((0, 0, move_vals))
            
            picking = self.env['stock.picking'].create(picking_vals)
            _logger.info(f"Sau create, picking có {len(picking.move_ids)} moves: {picking.move_ids.ids}")
            
            picking.action_confirm()
            _logger.info(f"Sau action_confirm, picking có {len(picking.move_ids)} moves: {picking.move_ids.ids}")
            # KHÔNG gọi action_assign() để tránh tạo move_lines tự động
            
            _logger.info(f"Đã tạo picking {picking.name} với {len(picking.move_ids)} moves")
            _logger.info(f"Receipt có {len(record.line_ids)} dòng sản phẩm")
            for move in picking.move_ids:
                _logger.info(f"  - Move {move.id}: {move.product_id.display_name}, qty={move.product_uom_qty}")
            
            # Xử lý số lô/sê-ri cho các sản phẩm có tracking
            missing_lots = []
            for line in record.line_ids:
                moves = picking.move_ids.filtered(lambda m: m.product_id == line.product_id)
                if not moves:
                    _logger.warning(f"Không tìm thấy move cho sản phẩm: {line.product_id.display_name}")
                    continue
                
                # Log số lượng moves tìm thấy
                _logger.info(f"Tìm thấy {len(moves)} move(s) cho {line.product_id.display_name}: IDs={moves.ids}")
                
                # Nếu sản phẩm yêu cầu tracking
                if line.product_id.tracking != 'none':
                    if not line.lot_name:
                        missing_lots.append(f" - {line.product_id.display_name}")
                        _logger.warning(f"Sản phẩm {line.product_id.display_name} thiếu số lô!")
                        continue
                        
                    # Tìm hoặc tạo lot/serial number
                    lot = self.env['stock.lot'].search([
                        ('name', '=', line.lot_name),
                        ('product_id', '=', line.product_id.id),
                        ('company_id', '=', self.env.company.id)
                    ], limit=1)
                    
                    if not lot:
                        lot = self.env['stock.lot'].create({
                            'name': line.lot_name,
                            'product_id': line.product_id.id,
                            'company_id': self.env.company.id,
                        })
                        _logger.info(f"Đã tạo lot mới: {lot.name} (id={lot.id})")
                    else:
                        _logger.info(f"Sử dụng lot có sẵn: {lot.name} (id={lot.id})")
                    
                    # Xử lý TẤT CẢ các moves của sản phẩm này
                    for move in moves:
                        _logger.info(f"Xử lý move_id={move.id} cho {line.product_id.display_name}")
                        
                        # Tạo move line mới với lot
                        _logger.info(f"Tạo move_line mới cho move_id={move.id} với lot_id={lot.id}, quantity={line.quantity}")
                        self.env['stock.move.line'].create({
                            'move_id': move.id,
                            'product_id': line.product_id.id,
                            'lot_id': lot.id,
                            'quantity': line.quantity,
                            'picked': True,
                            'product_uom_id': line.product_id.uom_id.id,
                            'location_id': location_src_id,
                            'location_dest_id': location_dest_id,
                            'picking_id': picking.id,
                        })
                else:
                    # Không có tracking - tạo move line cho tất cả moves
                    for move in moves:
                        _logger.info(f"Tạo move_line cho sản phẩm không tracking: move_id={move.id}, quantity={line.quantity}")
                        self.env['stock.move.line'].create({
                            'move_id': move.id,
                            'product_id': line.product_id.id,
                            'quantity': line.quantity,
                            'picked': True,
                            'product_uom_id': line.product_id.uom_id.id,
                            'location_id': location_src_id,
                            'location_dest_id': location_dest_id,
                            'picking_id': picking.id,
                        })
            
            # Refresh picking để lấy dữ liệu mới nhất
            picking.invalidate_recordset()
            
            _logger.info(f"Sau khi xử lý lot, picking có {len(picking.move_ids)} moves: IDs={picking.move_ids.ids}")
            
            # Kiểm tra lại xem tất cả move lines có lot chưa
            for move in picking.move_ids:
                _logger.info(f"Kiểm tra move {move.id}: product={move.product_id.display_name}, tracking={move.product_id.tracking}, move_lines={len(move.move_line_ids)}")
                if move.product_id.tracking != 'none':
                    if not move.move_line_ids or not any(ml.lot_id for ml in move.move_line_ids):
                        if move.product_id.display_name not in [ml.split(' - ')[1] for ml in missing_lots]:
                            missing_lots.append(f" - {move.product_id.display_name}")
                            _logger.error(f"Move {move.id} cho {move.product_id.display_name} vẫn thiếu lot sau khi xử lý!")
                    else:
                        _logger.info(f"Move {move.id} đã có lot: {[ml.lot_id.name for ml in move.move_line_ids if ml.lot_id]}")
            
            # Kiểm tra nếu có sản phẩm thiếu lot
            if missing_lots:
                raise UserError(_('Bạn cần cung cấp Số lô/sê-ri cho sản phẩm: \n%s') % '\n'.join(missing_lots))
            
            # Validate picking trực tiếp thay vì dùng button_validate để tránh tạo thêm moves
            _logger.info(f"Đang validate picking {picking.name}...")
            
            # Đảm bảo tất cả move lines có picked=True
            for move in picking.move_ids:
                _logger.info(f"Kiểm tra move {move.id}: product={move.product_id.display_name}, quantity={move.product_uom_qty}, tracking={move.product_id.tracking}")
                for move_line in move.move_line_ids:
                    _logger.info(f"  - move_line {move_line.id}: quantity={move_line.quantity}, picked={move_line.picked}, lot={move_line.lot_id.name if move_line.lot_id else 'None'}")
            
            # Dùng với context skip_backorder và skip_sms để validate trực tiếp
            picking_with_context = picking.with_context(skip_backorder=True, skip_sms=True)
            res = picking_with_context.button_validate()
            
            # Nếu vẫn trả về wizard, bỏ qua
            if not isinstance(res, dict):
                _logger.info(f"Đã validate picking {picking.name} thành công!")
            
            # Lấy % lợi nhuận từ phiếu nhập (mặc định 20%)
            profit_margin = record.profit_margin or 20.0
            
            # Cập nhật cost (standard_price) và sales price của sản phẩm
            for line in record.line_ids:
                if line.unit_price > 0:
                    # Tính sales price = cost + % lợi nhuận
                    sale_price = line.unit_price * (1 + profit_margin / 100.0)
                    
                    line.product_id.write({
                        'standard_price': line.unit_price,  # Cost
                        'list_price': sale_price  # Sales Price
                    })
                    
                    _logger.info(
                        f"Cập nhật giá {line.product_id.name}: "
                        f"Cost=${line.unit_price:.2f}, "
                        f"Sales Price=${sale_price:.2f} "
                        f"(+{profit_margin}%)"
                    )
            
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
