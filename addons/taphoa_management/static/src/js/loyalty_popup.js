/** @odoo-module **/

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useState } from "@odoo/owl";

export class LoyaltyPopup extends AbstractAwaitablePopup {
    static template = "taphoa_management.LoyaltyPopup";
    static defaultProps = {
        confirmText: _t("Apply"),
        cancelText: _t("Cancel"),
        title: _t("Use Loyalty Points"),
    };

    setup() {
        super.setup();
        this.pos = usePos();
        this.state = useState({
            pointsToUse: 0,
            discount: 0,
            maxPoints: this.props.card.total_points,
            maxDiscount: 0,
        });
        this._calculateMaxDiscount();
    }

    _calculateMaxDiscount() {
        const order = this.pos.get_order();
        if (!order) return;
        
        const orderTotal = order.get_total_with_tax();
        const program = this.props.program;
        
        // Tính giảm giá tối đa cho phép
        this.state.maxDiscount = orderTotal * (program.max_discount_percentage / 100.0);
    }

    onPointsChange(event) {
        const points = parseInt(event.target.value) || 0;
        const program = this.props.program;
        const order = this.pos.get_order();
        
        if (points < 0) {
            this.state.pointsToUse = 0;
            this.state.discount = 0;
            return;
        }

        if (points > this.state.maxPoints) {
            this.state.pointsToUse = this.state.maxPoints;
        } else {
            this.state.pointsToUse = points;
        }

        // Tính giảm giá
        let discount = this.state.pointsToUse * program.points_to_discount_rate;
        
        // Áp dụng giới hạn % giảm giá tối đa
        if (discount > this.state.maxDiscount) {
            discount = this.state.maxDiscount;
        }

        this.state.discount = discount;
    }

    useMaxPoints() {
        const program = this.props.program;
        const order = this.pos.get_order();
        const orderTotal = order.get_total_with_tax();
        
        // Tính số điểm tối đa có thể dùng dựa trên giới hạn giảm giá
        const maxDiscountAllowed = orderTotal * (program.max_discount_percentage / 100.0);
        const maxPointsByDiscount = Math.floor(maxDiscountAllowed / program.points_to_discount_rate);
        const maxPoints = Math.min(maxPointsByDiscount, this.state.maxPoints);
        
        this.state.pointsToUse = maxPoints;
        this.state.discount = maxPoints * program.points_to_discount_rate;
        
        // Update input
        const input = this.el.querySelector('input[name="points"]');
        if (input) input.value = maxPoints;
    }

    async confirm() {
        if (this.state.pointsToUse < this.props.program.min_points_to_redeem) {
            await this.pos.popup.add(ErrorPopup, {
                title: _t("Invalid Points"),
                body: _t(`Minimum points to redeem is ${this.props.program.min_points_to_redeem}`),
            });
            return;
        }

        this.props.resolve({ 
            confirmed: true, 
            payload: {
                points: this.state.pointsToUse,
                discount: this.state.discount,
            }
        });
    }

    cancel() {
        this.props.resolve({ confirmed: false });
    }
}
