# -*- coding: utf-8 -*-
{
    'name': 'Quản lý Cửa hàng Tạp hóa',
    'version': '17.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Hệ thống quản lý cửa hàng tạp hóa tích hợp đầy đủ',
    'description': """
        Quản lý Cửa hàng Tạp hóa
        =========================
        
        Chức năng chính:
        
        * Thủ kho:
            - Nhập hàng từ nhà cung cấp
            - Kiểm tra số lượng và chất lượng
            - Nhập kho
            - Xuất kho khi có đơn bán
            - Kiểm kê định kỳ
            
        * Thu ngân:
            - Tiếp nhận khách hàng
            - Tạo đơn bán hàng (POS)
            - In hóa đơn
            - Xử lý thanh toán (tiền mặt/QR)
            
        * Kế toán:
            - Ghi nhận doanh thu
            - Cập nhật công nợ
            - Đối soát số cái
            - Lập báo cáo tài chính
            
        * Chủ cửa hàng:
            - Phê duyệt đơn mua hàng
            - Theo dõi doanh thu, lợi nhuận
            - Xem báo cáo tổng hợp
    """,
    'author': 'Cửa hàng Tạp hóa',
    'website': 'https://www.taphoa.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale_management',
        'purchase',
        'stock',
        'account',
        'point_of_sale',
        'sale_stock',
        'purchase_stock',
        'stock_account',
        'product',
        'contacts',
        'barcodes',
        'crm',
    ],
    'data': [
        'security/taphoa_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/dashboard_data.xml',
        'data/loyalty_data.xml',
        'views/taphoa_menu.xml',
        'views/warehouse_views.xml',
        'views/cashier_views.xml',
        'views/pos_session_views.xml',
        'views/pos_config_views.xml',
        'views/accounting_views.xml',
        'views/manager_dashboard_views.xml',
        'views/product_template_views.xml',
        'views/customer_loyalty_views.xml',
        'views/taphoa_menu_items.xml',
        'wizard/wizard_stock_import_view.xml',
        'wizard/wizard_fix_products_view.xml',
        'reports/stock_report.xml',
        'reports/sales_report.xml',
        'reports/accounting_report.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'taphoa_management/static/src/app/loyalty_button.js',
            'taphoa_management/static/src/app/loyalty_button.xml',
            'taphoa_management/static/src/app/loyalty_popup.js',
            'taphoa_management/static/src/app/loyalty_popup.xml',
            'taphoa_management/static/src/app/loyalty.css',
        ],
    },
    'demo': [
        'demo/demo_data.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
