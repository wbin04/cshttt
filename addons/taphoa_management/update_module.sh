#!/bin/bash

# Script cập nhật module Taphoa Management

echo "==================================================="
echo "  SCRIPT CẬP NHẬT MODULE TAPHOA MANAGEMENT"
echo "==================================================="
echo ""

# Dừng Odoo đang chạy
echo "1. Đang dừng Odoo..."
pkill -f "odoo-bin -d erp_taphoa"
sleep 2
echo "   ✓ Đã dừng Odoo"
echo ""

# Cập nhật module
echo "2. Đang cập nhật module taphoa_management..."
cd /home/bin04/odoo
python3 ./odoo-bin -d erp_taphoa -u taphoa_management --stop-after-init
echo "   ✓ Đã cập nhật module"
echo ""

# Khởi động lại Odoo
echo "3. Đang khởi động lại Odoo..."
nohup python3 ./odoo-bin -d erp_taphoa > /tmp/odoo.log 2>&1 &
sleep 3
echo "   ✓ Đã khởi động Odoo"
echo ""

echo "==================================================="
echo "  HOÀN THÀNH!"
echo "==================================================="
echo ""
echo "Thông tin đăng nhập Thu Ngân:"
echo "  - URL: http://localhost:8069"
echo "  - Login: thungan"
echo "  - Password: thungan123"
echo ""
echo "Các user khác:"
echo "  - Thủ kho:        thukho / thukho123"
echo "  - Kế toán:        ketoan / ketoan123"
echo "  - Chủ cửa hàng:  quanly / quanly123"
echo ""
echo "Xem log tại: /tmp/odoo.log"
echo "==================================================="
