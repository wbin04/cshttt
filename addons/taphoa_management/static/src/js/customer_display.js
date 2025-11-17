/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

export class LoyaltyDisplay extends Component {
    static template = "taphoa_management.LoyaltyDisplay";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        this.state = useState({
            dummy: 0
        });
    }

    get currentOrder() {
        this.state.dummy;
        return this.pos.get_order();
    }

    get partner() {
        return this.currentOrder?.get_partner();
    }

    get loyaltyCard() {
        return this.currentOrder?.loyalty_card_id;
    }

    get currentPoints() {
        return this.loyaltyCard?.total_points || 0;
    }

    get pointsUsed() {
        return this.currentOrder?.loyalty_points_used || 0;
    }

    get discountAmount() {
        return this.currentOrder?.loyalty_discount_amount || 0;
    }

    get pointsToEarn() {
        return this.currentOrder?.calculateLoyaltyPointsEarned() || 0;
    }

    get pointsAfterTransaction() {
        return this.currentPoints - this.pointsUsed + this.pointsToEarn;
    }

    async useLoyaltyPoints() {
        if (!this.loyaltyCard) {
            this.popup.add('ErrorPopup', {
                title: 'Không có thẻ tích điểm',
                body: 'Khách hàng này chưa có thẻ tích điểm.',
            });
            return;
        }

        const { confirmed, payload } = await this.popup.add('LoyaltyPopup', {
            title: 'Đổi điểm tích lũy',
            loyaltyCard: this.loyaltyCard,
            loyaltyProgram: this.currentOrder.loyalty_program,
        });

        if (confirmed) {
            this.currentOrder.setLoyaltyPoints(payload.points, payload.discount);
            this.state.dummy++;
        }
    }
}

// Patch ActionpadWidget để thêm loyalty button handler
patch(ActionpadWidget.prototype, {
    async onClickLoyalty() {
        console.log('🎯 Loyalty button clicked!');
        const order = this.pos.get_order();
        const partner = order.get_partner();
        
        console.log('Order:', order);
        console.log('Partner:', partner);
        console.log('Loyalty card:', order.loyalty_card_id);
        
        if (!partner) {
            await this.popup.add('ErrorPopup', {
                title: 'Chưa chọn khách hàng',
                body: 'Vui lòng chọn khách hàng trước.',
            });
            return;
        }

        if (!order.loyalty_card_id) {
            await this.popup.add('ErrorPopup', {
                title: 'Không có thẻ tích điểm',
                body: 'Khách hàng này chưa có thẻ tích điểm.',
            });
            return;
        }

        // Show loyalty info
        const card = order.loyalty_card_id;
        const program = order.loyalty_program;

        await this.popup.add('ConfirmPopup', {
            title: 'Thông tin tích điểm',
            body: `
                Khách hàng: ${partner.name}
                Thẻ: ${card.card_number}
                Điểm hiện tại: ${card.total_points}
                Chương trình: ${program ? program.name : 'N/A'}
            `,
        });
    }
});

// Patch ProductScreen để hiển thị loyalty widget
patch(ProductScreen.prototype, {
    get showLoyaltyDisplay() {
        return this.pos.config.enable_loyalty && this.pos.get_order()?.get_partner();
    }
});
