# Hướng dẫn chạy Odoo Server

## Lệnh khởi động server cơ bản

### 1. Khởi động server thông thường
```bash
cd /home/bin04/odoo
source venv/bin/activate
python3 odoo-bin -c odoo.conf
```

### 2. Khởi động với database cụ thể
```bash
cd /home/bin04/odoo
source venv/bin/activate
python3 ./odoo-bin -d erp_taphoa
python3 odoo-bin -c odoo.conf -d odoo
```

### 3. Khởi động không có demo data (Khuyến nghị)
```bash
cd /home/bin04/odoo
source venv/bin/activate
python3 odoo-bin -c odoo.conf --without-demo=all
```

### 4. Lệnh một dòng để khởi động nhanh
```bash
cd /home/bin04/odoo && source venv/bin/activate && python3 odoo-bin -c odoo.conf --without-demo=all
```

## Lệnh quản lý database

### 5. Khởi tạo database với module base
```bash
cd /home/bin04/odoo
source venv/bin/activate
python3 odoo-bin -c odoo.conf -d odoo -i base --stop-after-init
```

### 6. Cập nhật tất cả module
```bash
cd /home/bin04/odoo
source venv/bin/activate
python3 odoo-bin -c odoo.conf -d odoo -u all
```

### 7. Cài đặt module cụ thể
```bash
cd /home/bin04/odoo
source venv/bin/activate
python3 odoo-bin -c odoo.conf -d odoo -i sale,purchase,stock
```

## Lệnh debug và maintenance

### 8. Khởi động với log level debug
```bash
cd /home/bin04/odoo
source venv/bin/activate
python3 odoo-bin -c odoo.conf --log-level=debug
```

### 9. Khởi động ở background (chạy nền)
```bash
cd /home/bin04/odoo
source venv/bin/activate
nohup python3 odoo-bin -c odoo.conf --without-demo=all > /dev/null 2>&1 &
```

### 10. Kiểm tra server có đang chạy không
```bash
ps aux | grep python3.*odoo-bin | grep -v grep
ss -tlnp | grep :8069
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069
```

### 11. Dừng server
```bash
# Nếu chạy trong terminal: Ctrl+C
# Nếu chạy background: 
ps aux | grep python3.*odoo-bin | grep -v grep
kill <process_id>
```

## Thông tin kết nối

- **URL**: http://localhost:8069
- **Database**: odoo
- **Admin Username**: admin
- **Admin Password**: admin
- **Master Password**: admin

## File cấu hình quan trọng

- **Config file**: `/home/bin04/odoo/odoo.conf`
- **Log file**: `/home/bin04/odoo/odoo.log`
- **Data directory**: `/home/bin04/odoo/data`
- **Addons path**: `/home/bin04/odoo/addons`

## Lệnh thường dùng nhất

```bash
# Khởi động server
cd /home/bin04/odoo && source venv/bin/activate && python3 odoo-bin -c odoo.conf --without-demo=all

# Kiểm tra trạng thái
ss -tlnp | grep :8069

# Truy cập web
# Mở browser: http://localhost:8069
```