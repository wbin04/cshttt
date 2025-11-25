/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class LoyaltyButton extends Component {
    static template = "taphoa_management.LoyaltyButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    async onClick() {
        const order = this.pos.get_order();
        const partner = order.get_partner();
        
        console.log('🎯 Loyalty button clicked!');
        console.log('Partner:', partner);
        console.log('Loyalty card:', order.loyalty_card_id);
        
        if (!partner) {
            await this.popup.add('ErrorPopup', {
                title: 'Chưa chọn khách hàng',
                body: 'Vui lòng chọn khách hàng trước khi sử dụng tích điểm.',
            });
            return;
        }

        // Load loyalty card if not loaded yet
        if (!order.loyalty_card_id) {
            await order.loadLoyaltyCard(partner);
        }

        if (!order.loyalty_card_id) {
            await this.popup.add('ErrorPopup', {
                title: 'Không có thẻ tích điểm',
                body: `Khách hàng ${partner.name} chưa có thẻ tích điểm hoặc thẻ chưa kích hoạt.`,
            });
            return;
        }

        // Show loyalty info
        const card = order.loyalty_card_id;
        const program = order.loyalty_program;
        const pointsEarned = order.calculateLoyaltyPointsEarned();

        const message = `
<strong>Khách hàng:</strong> ${partner.name}
<strong>Thẻ:</strong> ${card.card_number}
<strong>Chương trình:</strong> ${program ? program.name : 'N/A'}

<strong>Điểm hiện tại:</strong> ${card.total_points} điểm
<strong>Điểm tích được từ đơn này:</strong> +${pointsEarned} điểm
<strong>Tổng sau giao dịch:</strong> ${card.total_points + pointsEarned} điểm

Bạn có muốn đổi điểm để giảm giá không?
        `.trim();

        const { confirmed } = await this.popup.add('ConfirmPopup', {
            title: '🎁 Thông tin tích điểm',
            body: message,
            confirmText: 'Đổi điểm',
            cancelText: 'Đóng',
        });

        if (confirmed && program) {
            // Ask how many points to use
            const maxPoints = Math.min(
                card.total_points,
                Math.floor(order.get_total_with_tax() * program.max_discount_percentage / 100 / program.points_to_discount_rate)
            );

            if (maxPoints < program.min_points_to_redeem) {
                await this.popup.add('ErrorPopup', {
                    title: 'Không đủ điểm',
                    body: `Cần tối thiểu ${program.min_points_to_redeem} điểm để đổi. Hiện tại: ${card.total_points} điểm.`,
                });
                return;
            }

            const { confirmed: confirmedPoints, payload } = await this.popup.add('NumberPopup', {
                title: 'Nhập số điểm muốn sử dụng',
                startingValue: Math.min(maxPoints, card.total_points),
            });

            if (confirmedPoints && payload) {
                const points = Math.floor(payload);
                if (points < program.min_points_to_redeem) {
                    await this.popup.add('ErrorPopup', {
                        title: 'Số điểm không hợp lệ',
                        body: `Cần tối thiểu ${program.min_points_to_redeem} điểm.`,
                    });
                    return;
                }

                if (points > card.total_points) {
                    await this.popup.add('ErrorPopup', {
                        title: 'Không đủ điểm',
                        body: `Khách hàng chỉ có ${card.total_points} điểm.`,
                    });
                    return;
                }

                const discount = points * program.points_to_discount_rate;
                order.setLoyaltyPoints(points, discount);

                await this.popup.add('ConfirmPopup', {
                    title: 'Đổi điểm thành công',
                    body: `Đã sử dụng ${points} điểm để giảm ${this.env.utils.formatCurrency(discount)}`,
                    confirmText: 'OK',
                    cancelText: '',
                });
            }
        }
    }
}

// Register as control button
ProductScreen.addControlButton({
    component: LoyaltyButton,
});

// Patch ProductScreen để thêm method onClickLoyalty cho button trong template
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
    async onClickLoyalty() {
        const order = this.pos.get_order();
        const partner = order.get_partner();
        
        console.log('🎯 Loyalty button clicked from ProductScreen!');
        console.log('Partner:', partner);
        console.log('Loyalty card:', order.loyalty_card_id);
        
        if (!partner) {
            await this.popup.add('ErrorPopup', {
                title: 'Chưa chọn khách hàng',
                body: 'Vui lòng chọn khách hàng trước khi sử dụng tích điểm.',
            });
            return;
        }

        // Load loyalty card if not loaded yet
        if (!order.loyalty_card_id) {
            await order.loadLoyaltyCard(partner);
        }

        if (!order.loyalty_card_id) {
            await this.popup.add('ErrorPopup', {
                title: 'Không có thẻ tích điểm',
                body: `Khách hàng ${partner.name} chưa có thẻ tích điểm hoặc thẻ chưa kích hoạt.`,
            });
            return;
        }

        // Show loyalty info
        const card = order.loyalty_card_id;
        const program = order.loyalty_program;
        const pointsEarned = order.calculateLoyaltyPointsEarned();

        const message = `
<strong>Khách hàng:</strong> ${partner.name}
<strong>Thẻ:</strong> ${card.card_number}
<strong>Chương trình:</strong> ${program ? program.name : 'N/A'}

<strong>Điểm hiện tại:</strong> ${card.total_points} điểm
<strong>Điểm tích được từ đơn này:</strong> +${pointsEarned} điểm
<strong>Tổng sau giao dịch:</strong> ${card.total_points + pointsEarned} điểm

Bạn có muốn đổi điểm để giảm giá không?
        `.trim();

        const { confirmed } = await this.popup.add('ConfirmPopup', {
            title: '🎁 Thông tin tích điểm',
            body: message,
            confirmText: 'Đổi điểm',
            cancelText: 'Đóng',
        });

        if (confirmed && program) {
            // Ask how many points to use
            const maxPoints = Math.min(
                card.total_points,
                Math.floor(order.get_total_with_tax() * program.max_discount_percentage / 100 / program.points_to_discount_rate)
            );

            if (maxPoints < program.min_points_to_redeem) {
                await this.popup.add('ErrorPopup', {
                    title: 'Không đủ điểm',
                    body: `Cần tối thiểu ${program.min_points_to_redeem} điểm để đổi. Hiện tại: ${card.total_points} điểm.`,
                });
                return;
            }

            const { confirmed: confirmedPoints, payload } = await this.popup.add('NumberPopup', {
                title: 'Nhập số điểm muốn sử dụng',
                startingValue: Math.min(maxPoints, card.total_points),
            });

            if (confirmedPoints && payload) {
                const points = Math.floor(payload);
                if (points < program.min_points_to_redeem) {
                    await this.popup.add('ErrorPopup', {
                        title: 'Số điểm không hợp lệ',
                        body: `Cần tối thiểu ${program.min_points_to_redeem} điểm.`,
                    });
                    return;
                }

                if (points > card.total_points) {
                    await this.popup.add('ErrorPopup', {
                        title: 'Không đủ điểm',
                        body: `Khách hàng chỉ có ${card.total_points} điểm.`,
                    });
                    return;
                }

                const discount = points * program.points_to_discount_rate;
                order.setLoyaltyPoints(points, discount);

                await this.popup.add('ConfirmPopup', {
                    title: 'Đổi điểm thành công',
                    body: `Đã sử dụng ${points} điểm để giảm ${this.env.utils.formatCurrency(discount)}`,
                    confirmText: 'OK',
                    cancelText: '',
                });
            }
        }
    }
});
