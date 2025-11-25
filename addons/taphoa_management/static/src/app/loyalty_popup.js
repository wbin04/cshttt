/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

export class LoyaltyPopup extends AbstractAwaitablePopup {
    static template = "taphoa_management.LoyaltyPopup";
    static defaultProps = {
        confirmText: _t("OK"),
        cancelText: _t("Đóng"),
        title: _t("Thông tin tích điểm"),
        body: "",
    };

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.state = useState({
            redeemPoints: 0,
            discountAmount: 0,
        });
    }

    get currentPoints() {
        return this.props.currentPoints || 0;
    }

    get orderTotal() {
        return this.props.orderTotal || 0;
    }

    get pointsToEarn() {
        return this.props.pointsToEarn || 0;
    }

    get totalAfter() {
        return this.props.totalAfter || 0;
    }

    get explanation() {
        return this.props.explanation || "";
    }
    
    get maxRedeemPoints() {
        // Tối đa có thể đổi = min(điểm hiện có, điểm tương đương tổng đơn hàng)
        const pointsForOrderTotal = Math.floor(this.orderTotal / 10); // 100 điểm = 1000đ => 10đ = 1 điểm
        return Math.min(this.currentPoints, pointsForOrderTotal * 100);
    }
    
    get maxDiscountAmount() {
        return Math.floor(this.maxRedeemPoints / 100) * 1000;
    }
    
    get finalOrderTotal() {
        return this.orderTotal - this.state.discountAmount;
    }
    
    get pointsAfterRedeem() {
        return this.currentPoints - this.state.redeemPoints + this.pointsToEarn;
    }
    
    onRedeemPointsChange(ev) {
        let points = parseInt(ev.target.value) || 0;
        
        // Làm tròn xuống bội số của 100
        points = Math.floor(points / 100) * 100;
        
        // Không vượt quá max
        if (points > this.maxRedeemPoints) {
            points = Math.floor(this.maxRedeemPoints / 100) * 100;
        }
        
        // Không âm
        if (points < 0) {
            points = 0;
        }
        
        this.state.redeemPoints = points;
        this.state.discountAmount = Math.floor(points / 100) * 1000;
    }
    
    async confirm() {
        const { partner, earnPoints, orderTotal } = this.props;
        
        console.log("💎 User clicked OK", {
            partner_id: partner?.id,
            earnPoints,
            redeemPoints: this.state.redeemPoints,
            discountAmount: this.state.discountAmount
        });
        
        // Trả về thông tin để button xử lý
        this.props.resolve({
            confirmed: true,
            redeemPoints: this.state.redeemPoints,
            discountAmount: this.state.discountAmount
        });
        
        // Đóng popup bằng cách gọi parent method
        this.props.close();
    }
    
    cancel() {
        this.props.resolve({ confirmed: false });
        this.props.close();
    }
}
