/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { LoyaltyPopup } from "@taphoa_management/app/loyalty_popup";

export class LoyaltyButton extends Component {
    static template = "taphoa_management.LoyaltyButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        this.orm = useService("orm");
    }

    async onClick() {
        const order = this.pos.get_order();
        const partner = order?.get_partner();
        
        console.log("🎁 Loyalty button clicked!", { order, partner });
        
        if (!partner) {
            await this.popup.add(ErrorPopup, {
                title: "Chưa chọn khách hàng",
                body: "Vui lòng chọn khách hàng trước khi tích điểm!",
            });
            return;
        }

        // Get fresh loyalty points from backend
        try {
            const partnerData = await this.orm.call('res.partner', 'read', [[partner.id], ['total_loyalty_points']]);
            const currentPoints = partnerData[0]?.total_loyalty_points || 0;
            
            console.log("💎 Current points from backend:", currentPoints);
            
            // Tính điểm sẽ tích dựa trên tổng tiền đơn hàng
            const orderTotal = order.get_total_with_tax();
            const pointsToEarn = this.calculatePoints(orderTotal);
            
            const newPoints = currentPoints + pointsToEarn;
            
            // Tạo giải thích
            let explanation = "";
            if (orderTotal < 50000) {
                explanation = "Đơn hàng < 50,000đ không được tích điểm";
            } else {
                const steps = Math.floor(orderTotal / 50000);
                explanation = `Cứ mỗi 50,000đ tích 50 điểm (${steps} bậc × 50 = ${pointsToEarn} điểm)`;
            }

            const result = await this.popup.add(LoyaltyPopup, {
                title: "Tích điểm - " + partner.name,
                currentPoints: currentPoints,
                orderTotal: orderTotal,
                pointsToEarn: pointsToEarn,
                earnPoints: pointsToEarn,
                totalAfter: newPoints,
                explanation: explanation,
                partner: partner,
            });
            
            // Nếu user chọn đổi điểm
            if (result && result.confirmed && result.redeemPoints > 0) {
                console.log("🎯 Applying discount:", result);
                
                // Áp dụng giảm giá vào order
                this.applyLoyaltyDiscount(order, partner, result.redeemPoints, result.discountAmount);
            }
        } catch (error) {
            console.error("❌ Error fetching loyalty points:", error);
            await this.popup.add(ErrorPopup, {
                title: "Lỗi",
                body: "Không thể lấy thông tin điểm tích lũy!",
            });
        }
    }
    
    applyLoyaltyDiscount(order, partner, redeemPoints, discountAmount) {
        // Tìm hoặc tạo discount product
        const discountProduct = this.pos.db.get_product_by_id(this.pos.config.loyalty_discount_product_id[0]);
        
        if (!discountProduct) {
            this.popup.add(ErrorPopup, {
                title: "Lỗi",
                body: "Chưa cấu hình sản phẩm giảm giá loyalty!",
            });
            return;
        }
        
        // Xóa discount cũ nếu có
        const existingDiscountLines = order.get_orderlines().filter(line => 
            line.product.id === discountProduct.id
        );
        existingDiscountLines.forEach(line => order.remove_orderline(line));
        
        // Thêm discount line mới
        order.add_product(discountProduct, {
            price: -discountAmount,
            quantity: 1,
            merge: false,
            extras: {
                loyalty_redeem_points: redeemPoints,
                loyalty_partner_id: partner.id,
            }
        });
        
        console.log("✅ Loyalty discount applied:", {
            redeemPoints,
            discountAmount,
            partner: partner.name
        });
    }
    
    calculatePoints(amount) {
        /**
         * Tính điểm từ số tiền theo bậc:
         * - < 50,000: 0 điểm
         * - 50,000 - < 100,000: 50 điểm
         * - 100,000 - < 150,000: 100 điểm
         * - Cứ thêm mỗi 50,000 thì thêm 50 điểm
         */
        if (amount < 50000) {
            return 0;
        }
        
        const steps = Math.floor(amount / 50000);
        return steps * 50;
    }
}

console.log("🎯 Registering LoyaltyButton to ProductScreen...");

ProductScreen.addControlButton({
    component: LoyaltyButton,
    condition: function () {
        return true; // Always show for testing
    },
});

console.log("✅ LoyaltyButton registered!");
