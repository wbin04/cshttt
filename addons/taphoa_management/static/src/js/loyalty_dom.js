/** @odoo-module */

import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";

patch(ActionpadWidget.prototype, {
    setup() {
        super.setup(...arguments);
        
        console.log('🔵 ActionpadWidget setup called');
        
        onMounted(() => {
            console.log('🟢 ActionpadWidget mounted');
            // Đợi 100ms để DOM render xong
            setTimeout(() => {
                this.addLoyaltyButton();
            }, 100);
            
            // Thử lại sau 500ms nếu chưa có
            setTimeout(() => {
                if (!document.querySelector('.loyalty-btn-custom')) {
                    console.log('🔄 Retrying to add button...');
                    this.addLoyaltyButton();
                }
            }, 500);
        });
    },

    addLoyaltyButton() {
        console.log('🔍 addLoyaltyButton called');
        
        // Tìm button Customer (set-partner)
        const customerButton = document.querySelector('.actionpad .set-partner');
        
        console.log('Customer button found:', customerButton);
        console.log('Loyalty button exists:', document.querySelector('.loyalty-btn-custom'));
        
        if (customerButton && !document.querySelector('.loyalty-btn-custom')) {
            console.log('✅ Found customer button, adding loyalty button...');
            
            // Tạo button Tích điểm
            const loyaltyButton = document.createElement('button');
            loyaltyButton.className = 'button loyalty-btn-custom btn btn-light rounded-0 py-2 flex-shrink-1 fw-bolder';
            loyaltyButton.style.cssText = `
                background: linear-gradient(135deg, #9C27B0 0%, #673AB7 100%) !important;
                color: white !important;
                border-bottom: 1px solid #999;
            `;
            
            loyaltyButton.innerHTML = `
                <div class="d-flex justify-content-center align-items-center">
                    <span class="d-flex justify-content-center align-items-center rounded-circle me-2" 
                          style="background: rgba(255,255,255,0.3); width: 30px; height: 30px;">
                        <i class="fa fa-gift" style="color: white; font-size: 16px;"></i>
                    </span>
                    <div class="fw-bolder" style="font-size: 14px;">Tích điểm</div>
                </div>
            `;
            
            // Add click handler
            loyaltyButton.addEventListener('click', async () => {
                const order = this.pos.get_order();
                const partner = order.get_partner();
                
                if (!partner) {
                    await this.env.services.popup.add('ErrorPopup', {
                        title: 'Chưa chọn khách hàng',
                        body: 'Vui lòng chọn khách hàng trước khi sử dụng tích điểm.',
                    });
                } else {
                    await this.env.services.popup.add('ConfirmPopup', {
                        title: '🎁 Tích điểm - ' + partner.name,
                        body: 'Button tích điểm đã hoạt động!\n\nChức năng tích điểm đầy đủ đang được phát triển...',
                        confirmText: 'OK',
                        cancelText: '',
                    });
                }
            });
            
            // Insert button sau Customer button
            customerButton.parentNode.insertBefore(loyaltyButton, customerButton.nextSibling);
            
            console.log('✅ Loyalty button added successfully!');
        } else if (!customerButton) {
            console.log('⚠️ Customer button not found yet');
        } else {
            console.log('ℹ️ Loyalty button already exists');
        }
    }
});
