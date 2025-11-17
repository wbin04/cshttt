/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.loyalty_card_id = null;
        this.loyalty_points_used = 0;
        this.loyalty_discount_amount = 0;
        this.loyalty_points_earned = 0;
    },

    async setPartner(partner) {
        await super.setPartner(...arguments);
        if (partner) {
            await this.loadLoyaltyCard(partner);
        } else {
            this.loyalty_card_id = null;
            this.loyalty_points_used = 0;
            this.loyalty_discount_amount = 0;
        }
    },

    async loadLoyaltyCard(partner) {
        try {
            // Load thẻ tích điểm của khách hàng
            const cards = await this.env.services.orm.searchRead(
                'customer.loyalty.card',
                [['partner_id', '=', partner.id], ['state', '=', 'active']],
                ['id', 'card_number', 'total_points', 'program_id']
            );

            if (cards.length > 0) {
                this.loyalty_card_id = cards[0];
                // Load program info
                const programs = await this.env.services.orm.searchRead(
                    'customer.loyalty.program',
                    [['id', '=', cards[0].program_id[0]]],
                    ['id', 'name', 'points_per_amount', 'points_to_discount_rate', 
                     'min_points_to_redeem', 'max_discount_percentage', 'min_order_amount']
                );
                if (programs.length > 0) {
                    this.loyalty_program = programs[0];
                }
            }
        } catch (error) {
            console.error('Error loading loyalty card:', error);
        }
    },

    setLoyaltyPoints(points, discount) {
        this.loyalty_points_used = points;
        this.loyalty_discount_amount = discount;
        this.trigger('change');
    },

    calculateLoyaltyPointsEarned() {
        if (!this.loyalty_program) return 0;
        
        const total = this.get_total_with_tax();
        const eligible_amount = total - this.loyalty_discount_amount;
        
        if (eligible_amount < (this.loyalty_program.min_order_amount || 0)) {
            return 0;
        }

        return Math.floor(eligible_amount * this.loyalty_program.points_per_amount);
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.loyalty_card_id = this.loyalty_card_id ? this.loyalty_card_id.id : false;
        json.loyalty_points_used = this.loyalty_points_used || 0;
        json.loyalty_discount_amount = this.loyalty_discount_amount || 0;
        json.loyalty_points_earned = this.calculateLoyaltyPointsEarned();
        return json;
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.loyalty_card_id = json.loyalty_card_id;
        this.loyalty_points_used = json.loyalty_points_used || 0;
        this.loyalty_discount_amount = json.loyalty_discount_amount || 0;
        this.loyalty_points_earned = json.loyalty_points_earned || 0;
    },
});
