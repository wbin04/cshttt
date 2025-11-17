# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CustomerLoyaltyProgram(models.Model):
    """Chương trình tích điểm khách hàng"""
    _name = 'customer.loyalty.program'
    _description = 'Chương trình tích điểm'
    _order = 'sequence, id'

    name = fields.Char(string='Tên chương trình', required=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Kích hoạt', default=True)
    
    # Quy tắc tích điểm
    points_per_amount = fields.Float(
        string='Điểm/Đồng',
        default=1.0,
        help='Số điểm khách hàng nhận được cho mỗi đồng chi tiêu. VD: 1 điểm cho 10,000đ => 0.0001'
    )
    min_order_amount = fields.Monetary(
        string='Giá trị đơn hàng tối thiểu',
        currency_field='currency_id',
        default=0.0,
        help='Giá trị đơn hàng tối thiểu để được tích điểm'
    )
    
    # Quy tắc đổi điểm
    points_to_discount_rate = fields.Float(
        string='Tỷ lệ quy đổi (Điểm -> VND)',
        default=1000.0,
        help='Giá trị quy đổi 1 điểm thành tiền. VD: 1 điểm = 1,000đ'
    )
    min_points_to_redeem = fields.Integer(
        string='Số điểm tối thiểu để đổi',
        default=10,
        help='Số điểm tối thiểu khách hàng cần có để có thể đổi điểm'
    )
    max_discount_percentage = fields.Float(
        string='% giảm giá tối đa',
        default=50.0,
        help='Phần trăm giảm giá tối đa cho một đơn hàng (0-100)'
    )
    
    # Thời hạn điểm
    points_expiry_days = fields.Integer(
        string='Điểm hết hạn sau (ngày)',
        default=365,
        help='Số ngày điểm có hiệu lực. 0 = không hết hạn'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    # Thống kê
    total_points_awarded = fields.Integer(
        string='Tổng điểm đã tặng',
        compute='_compute_statistics',
        store=True
    )
    total_points_redeemed = fields.Integer(
        string='Tổng điểm đã đổi',
        compute='_compute_statistics',
        store=True
    )
    active_customers = fields.Integer(
        string='Số khách hàng tham gia',
        compute='_compute_statistics'
    )
    
    @api.depends('name')
    def _compute_statistics(self):
        """Tính toán thống kê chương trình"""
        for program in self:
            transactions = self.env['customer.loyalty.transaction'].search([
                ('program_id', '=', program.id)
            ])
            program.total_points_awarded = sum(
                t.points for t in transactions if t.transaction_type == 'earn'
            )
            program.total_points_redeemed = sum(
                abs(t.points) for t in transactions if t.transaction_type == 'redeem'
            )
            program.active_customers = len(transactions.mapped('partner_id'))
    
    @api.constrains('points_per_amount', 'points_to_discount_rate', 'max_discount_percentage')
    def _check_positive_values(self):
        """Kiểm tra giá trị dương"""
        for program in self:
            if program.points_per_amount < 0:
                raise ValidationError(_('Tỷ lệ tích điểm phải lớn hơn hoặc bằng 0'))
            if program.points_to_discount_rate < 0:
                raise ValidationError(_('Tỷ lệ quy đổi điểm phải lớn hơn 0'))
            if not (0 <= program.max_discount_percentage <= 100):
                raise ValidationError(_('Phần trăm giảm giá tối đa phải từ 0 đến 100'))
    
    def calculate_points_from_amount(self, amount):
        """
        Tính điểm từ số tiền theo bậc:
        - < 50,000: 0 điểm
        - 50,000 - < 100,000: 50 điểm
        - 100,000 - < 150,000: 100 điểm
        - Cứ thêm mỗi 50,000 thì thêm 50 điểm
        """
        self.ensure_one()
        
        # Dưới 50,000 không tích điểm
        if amount < 50000:
            return 0
        
        # Tính số bậc 50,000
        # VD: 75,000 -> 1 bậc = 50 điểm
        #     125,000 -> 2 bậc = 100 điểm
        #     200,000 -> 4 bậc = 200 điểm
        steps = int(amount // 50000)
        points = steps * 50
        
        return points
    
    def calculate_discount_from_points(self, points, order_amount):
        """Tính số tiền giảm giá từ điểm"""
        self.ensure_one()
        if points < self.min_points_to_redeem:
            return 0.0
        
        # Tính giảm giá tối đa cho phép
        max_discount = order_amount * (self.max_discount_percentage / 100.0)
        
        # Tính giảm giá từ điểm
        discount = points * self.points_to_discount_rate
        
        return min(discount, max_discount)


class CustomerLoyaltyCard(models.Model):
    """Thẻ tích điểm của khách hàng"""
    _name = 'customer.loyalty.card'
    _description = 'Thẻ tích điểm khách hàng'
    _rec_name = 'card_number'

    card_number = fields.Char(
        string='Số thẻ',
        required=True,
        copy=False,
        index=True,
        default=lambda self: _('New')
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Khách hàng',
        required=True,
        ondelete='cascade',
        index=True
    )
    program_id = fields.Many2one(
        'customer.loyalty.program',
        string='Chương trình',
        required=True,
        ondelete='restrict'
    )
    
    # Điểm tích lũy
    total_points = fields.Integer(
        string='Tổng điểm hiện có',
        compute='_compute_points',
        store=True,
        help='Tổng điểm có thể sử dụng của khách hàng'
    )
    earned_points = fields.Integer(
        string='Điểm đã tích',
        compute='_compute_points',
        store=True
    )
    redeemed_points = fields.Integer(
        string='Điểm đã đổi',
        compute='_compute_points',
        store=True
    )
    
    # Trạng thái
    state = fields.Selection([
        ('active', 'Đang hoạt động'),
        ('suspended', 'Tạm ngưng'),
        ('expired', 'Hết hạn'),
    ], string='Trạng thái', default='active', required=True)
    
    issue_date = fields.Date(
        string='Ngày phát hành',
        default=fields.Date.context_today,
        required=True
    )
    expiry_date = fields.Date(string='Ngày hết hạn')
    
    # Lịch sử giao dịch
    transaction_ids = fields.One2many(
        'customer.loyalty.transaction',
        'card_id',
        string='Lịch sử giao dịch'
    )
    
    _sql_constraints = [
        ('card_number_unique', 'unique(card_number)',
         'Số thẻ phải là duy nhất!')
    ]
    
    @api.model_create_multi
    def create(self, vals_list):
        """Tạo số thẻ tự động"""
        for vals in vals_list:
            if vals.get('card_number', _('New')) == _('New'):
                vals['card_number'] = self.env['ir.sequence'].next_by_code(
                    'customer.loyalty.card'
                ) or _('New')
        return super().create(vals_list)
    
    @api.depends('transaction_ids.points', 'transaction_ids.state')
    def _compute_points(self):
        """Tính tổng điểm"""
        for card in self:
            valid_transactions = card.transaction_ids.filtered(
                lambda t: t.state == 'confirmed'
            )
            card.earned_points = sum(
                t.points for t in valid_transactions if t.transaction_type == 'earn'
            )
            card.redeemed_points = sum(
                abs(t.points) for t in valid_transactions if t.transaction_type == 'redeem'
            )
            card.total_points = card.earned_points - card.redeemed_points
    
    def action_view_transactions(self):
        """Xem lịch sử giao dịch"""
        self.ensure_one()
        return {
            'name': _('Lịch sử tích điểm'),
            'type': 'ir.actions.act_window',
            'res_model': 'customer.loyalty.transaction',
            'view_mode': 'tree,form',
            'domain': [('card_id', '=', self.id)],
            'context': {
                'default_card_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_program_id': self.program_id.id,
            }
        }
    
    @api.model
    def add_transaction(self, partner_id, points, amount, transaction_type='earn', description=''):
        """
        Thêm giao dịch tích điểm từ POS
        @param partner_id: ID khách hàng
        @param points: Số điểm (dương: tích, âm: đổi)
        @param amount: Số tiền giao dịch
        @param transaction_type: 'earn' hoặc 'redeem'
        @param description: Mô tả giao dịch
        @return: Transaction record
        """
        import logging
        _logger = logging.getLogger(__name__)
        
        _logger.info(f"💎 add_transaction called: partner_id={partner_id}, points={points}, amount={amount}")
        
        # Tìm thẻ loyalty của khách hàng
        card = self.search([
            ('partner_id', '=', partner_id),
            ('state', '=', 'active')
        ], limit=1)
        
        if not card:
            _logger.warning(f"⚠️ No active loyalty card for partner {partner_id}")
            # Tạo thẻ mới nếu chưa có
            program = self.env['customer.loyalty.program'].search([('active', '=', True)], limit=1)
            if not program:
                raise UserError(_('Không tìm thấy chương trình tích điểm nào đang hoạt động!'))
            
            card = self.create({
                'partner_id': partner_id,
                'program_id': program.id,
            })
            _logger.info(f"✅ Created new loyalty card: {card.card_number}")
        
        # Tạo transaction
        transaction = self.env['customer.loyalty.transaction'].create({
            'card_id': card.id,
            'partner_id': partner_id,
            'program_id': card.program_id.id,
            'transaction_type': transaction_type,
            'points': points if transaction_type == 'earn' else -abs(points),
            'amount': amount,
            'description': description or f'Tích điểm từ POS: {amount}đ',
            'state': 'confirmed',
        })
        
        _logger.info(f"✅ Transaction created: {transaction.id}, points={transaction.points}")
        
        # Cập nhật loyalty_points trên partner
        partner = self.env['res.partner'].browse(partner_id)
        partner.write({'loyalty_points': card.total_points})
        
        return {
            'success': True,
            'transaction_id': transaction.id,
            'new_total_points': card.total_points,
        }
    
    def can_redeem_points(self, points):
        """Kiểm tra có thể đổi điểm không"""
        self.ensure_one()
        if self.state != 'active':
            return False
        if self.total_points < points:
            return False
        if points < self.program_id.min_points_to_redeem:
            return False
        return True


class CustomerLoyaltyTransaction(models.Model):
    """Giao dịch tích điểm"""
    _name = 'customer.loyalty.transaction'
    _description = 'Giao dịch tích điểm'
    _order = 'transaction_date desc, id desc'

    name = fields.Char(
        string='Mã giao dịch',
        required=True,
        copy=False,
        default=lambda self: _('New')
    )
    card_id = fields.Many2one(
        'customer.loyalty.card',
        string='Thẻ tích điểm',
        required=True,
        ondelete='cascade',
        index=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Khách hàng',
        related='card_id.partner_id',
        store=True,
        index=True
    )
    program_id = fields.Many2one(
        'customer.loyalty.program',
        string='Chương trình',
        related='card_id.program_id',
        store=True
    )
    
    transaction_type = fields.Selection([
        ('earn', 'Tích điểm'),
        ('redeem', 'Đổi điểm'),
        ('adjust', 'Điều chỉnh'),
        ('expire', 'Hết hạn'),
    ], string='Loại giao dịch', required=True, default='earn')
    
    points = fields.Integer(
        string='Điểm',
        required=True,
        help='Số điểm (dương = tích điểm, âm = trừ điểm)'
    )
    transaction_date = fields.Datetime(
        string='Ngày giao dịch',
        default=fields.Datetime.now,
        required=True
    )
    expiry_date = fields.Date(
        string='Ngày hết hạn điểm',
        help='Ngày điểm này hết hiệu lực'
    )
    
    # Liên kết đơn hàng
    pos_order_id = fields.Many2one(
        'pos.order',
        string='Đơn hàng POS',
        ondelete='set null'
    )
    order_amount = fields.Monetary(
        string='Giá trị đơn hàng',
        currency_field='currency_id'
    )
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('expired', 'Đã hết hạn'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='draft', required=True)
    
    note = fields.Text(string='Ghi chú')
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Tạo mã giao dịch tự động"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'customer.loyalty.transaction'
                ) or _('New')
            
            # Tự động xác nhận giao dịch tích điểm
            if vals.get('transaction_type') == 'earn' and vals.get('state') == 'draft':
                vals['state'] = 'confirmed'
                
                # Tính ngày hết hạn nếu chương trình có quy định
                if not vals.get('expiry_date'):
                    card = self.env['customer.loyalty.card'].browse(vals.get('card_id'))
                    if card and card.program_id.points_expiry_days > 0:
                        expiry_date = fields.Date.today() + \
                            fields.Timedelta(days=card.program_id.points_expiry_days)
                        vals['expiry_date'] = expiry_date
        
        return super().create(vals_list)
    
    def action_confirm(self):
        """Xác nhận giao dịch"""
        for transaction in self:
            if transaction.state != 'draft':
                raise UserError(_('Chỉ có thể xác nhận giao dịch ở trạng thái Nháp'))
            
            # Kiểm tra nếu là đổi điểm
            if transaction.transaction_type == 'redeem':
                if not transaction.card_id.can_redeem_points(abs(transaction.points)):
                    raise UserError(_(
                        'Không đủ điểm để đổi. '
                        'Điểm hiện có: %s, Cần: %s'
                    ) % (transaction.card_id.total_points, abs(transaction.points)))
            
            transaction.write({'state': 'confirmed'})
    
    def action_cancel(self):
        """Hủy giao dịch"""
        for transaction in self:
            if transaction.state == 'confirmed':
                raise UserError(_('Không thể hủy giao dịch đã xác nhận'))
            transaction.write({'state': 'cancelled'})
    
    @api.model
    def _cron_expire_points(self):
        """Cron job để hết hạn điểm tự động"""
        today = fields.Date.today()
        expired_transactions = self.search([
            ('state', '=', 'confirmed'),
            ('transaction_type', '=', 'earn'),
            ('expiry_date', '!=', False),
            ('expiry_date', '<', today),
        ])
        
        for transaction in expired_transactions:
            # Tạo giao dịch trừ điểm
            self.create({
                'card_id': transaction.card_id.id,
                'transaction_type': 'expire',
                'points': -transaction.points,
                'transaction_date': fields.Datetime.now(),
                'note': _('Điểm hết hạn từ giao dịch %s') % transaction.name,
                'state': 'confirmed',
            })
            transaction.write({'state': 'expired'})


class ResPartner(models.Model):
    """Mở rộng partner để tích hợp loyalty"""
    _inherit = 'res.partner'

    loyalty_card_ids = fields.One2many(
        'customer.loyalty.card',
        'partner_id',
        string='Thẻ tích điểm'
    )
    loyalty_card_count = fields.Integer(
        string='Số thẻ tích điểm',
        compute='_compute_loyalty_card_count'
    )
    total_loyalty_points = fields.Integer(
        string='Tổng điểm tích lũy',
        compute='_compute_total_loyalty_points',
        store=False,  # Computed field
        help='Tổng điểm từ tất cả các thẻ'
    )
    
    # Add this field for POS
    loyalty_points = fields.Integer(
        string='Điểm tích lũy (POS)',
        compute='_compute_total_loyalty_points',
        store=False,
        help='Alias for total_loyalty_points for POS compatibility'
    )
    
    @api.depends('loyalty_card_ids')
    def _compute_loyalty_card_count(self):
        for partner in self:
            partner.loyalty_card_count = len(partner.loyalty_card_ids)
    
    @api.depends('loyalty_card_ids.total_points')
    def _compute_total_loyalty_points(self):
        for partner in self:
            partner.total_loyalty_points = sum(
                card.total_points for card in partner.loyalty_card_ids 
                if card.state == 'active'
            )
    
    def action_view_loyalty_cards(self):
        """Xem thẻ tích điểm"""
        self.ensure_one()
        return {
            'name': _('Thẻ tích điểm'),
            'type': 'ir.actions.act_window',
            'res_model': 'customer.loyalty.card',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }
    
    def create_loyalty_card(self, program_id):
        """Tạo thẻ tích điểm cho khách hàng"""
        self.ensure_one()
        
        # Kiểm tra đã có thẻ chưa
        existing_card = self.env['customer.loyalty.card'].search([
            ('partner_id', '=', self.id),
            ('program_id', '=', program_id),
        ], limit=1)
        
        if existing_card:
            return existing_card
        
        return self.env['customer.loyalty.card'].create({
            'partner_id': self.id,
            'program_id': program_id,
        })
