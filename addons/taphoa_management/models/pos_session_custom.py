# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PosSessionCustom(models.Model):
    """Mở rộng POS Session cho quản lý phiên bán hàng"""
    _inherit = 'pos.session'

    def action_pos_session_start(self):
        """Bắt đầu phiên bán hàng (chuyển từ opening_control sang opened)"""
        self.ensure_one()
        
        if self.state != 'opening_control':
            raise UserError(_('Chỉ có thể bắt đầu phiên ở trạng thái "Opening Control". Trạng thái hiện tại: %s') % self.state)
        
        # Open the session
        self.write({'state': 'opened'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Thành công!'),
                'message': _('Phiên bán hàng đã được mở. Bạn có thể vào Point of Sale để bắt đầu bán hàng.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_open_pos_ui(self):
        """Mở giao diện POS từ session đang mở"""
        self.ensure_one()
        
        if self.state == 'opening_control':
            # Tự động mở session trước
            self.write({'state': 'opened'})
        
        if self.state != 'opened':
            raise UserError(_('Phiên này chưa được mở hoặc đã đóng. Trạng thái: %s') % self.state)
        
        # Return URL action to open POS
        return {
            'type': 'ir.actions.act_url',
            'url': '/pos/web?config_id=%d' % self.config_id.id,
            'target': 'self',
        }
