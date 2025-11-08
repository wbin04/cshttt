# Hướng Dẫn Cài Đặt và Triển Khai Odoo 17.0

## 📋 Mục Lục
1. [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
2. [Chuẩn Bị Git Repository](#chuẩn-bị-git-repository)
3. [Các Thư Mục Cần Đưa Lên Git](#các-thư-mục-cần-đưa-lên-git)
4. [Các Thư Mục Cần Ignore](#các-thư-mục-cần-ignore)
5. [Hướng Dẫn Push Code Lên Git](#hướng-dẫn-push-code-lên-git)
6. [Hướng Dẫn Cài Đặt Hoàn Chỉnh](#hướng-dẫn-cài-đặt-hoàn-chỉnh)
7. [Cấu Hình Odoo](#cấu-hình-odoo)
8. [Chạy Odoo](#chạy-odoo)
9. [Xử Lý Lỗi Thường Gặp](#xử-lý-lỗi-thường-gặp)

---

## 🗂️ Cấu Trúc Thư Mục

```
odoo/
├── addons/                 # Các module chính thức của Odoo
├── odoo/                   # Core framework của Odoo
├── setup/                  # Setup scripts
├── doc/                    # Tài liệu
├── debian/                 # Package cho Debian
├── data/                   # Data templates
├── odoo-bin               # File thực thi chính
├── requirements.txt       # Python dependencies
├── setup.py               # Setup configuration
├── odoo.conf              # File cấu hình (không push lên git)
├── .gitignore            # Danh sách file/folder ignore
└── README.md             # Tài liệu dự án
```

---

## 🚀 Chuẩn Bị Git Repository

### 1. Kiểm tra Git đã được cài đặt
```bash
git --version
```

### 2. Cấu hình Git (nếu chưa có)
```bash
git config --global user.name "Tên của bạn"
git config --global user.email "email@example.com"
```

### 3. Khởi tạo Git repository (nếu chưa có)
```bash
cd /home/bin04/odoo
git init
```

---

## ✅ Các Thư Mục Cần Đưa Lên Git

### Bắt buộc:
- ✅ `addons/` - Các module Odoo
- ✅ `odoo/` - Core framework
- ✅ `setup/` - Setup scripts
- ✅ `doc/` - Documentation
- ✅ `debian/` - Package files
- ✅ `data/` - Data templates
- ✅ `odoo-bin` - Main executable
- ✅ `requirements.txt` - Python dependencies
- ✅ `setup.py` - Setup configuration
- ✅ `setup.cfg` - Setup config
- ✅ `README.md` - Documentation
- ✅ `LICENSE` - License file
- ✅ `COPYRIGHT` - Copyright info
- ✅ `MANIFEST.in` - Manifest file
- ✅ `CONTRIBUTING.md` - Contributing guidelines
- ✅ `SECURITY.md` - Security policy
- ✅ `SERVER_COMMANDS.md` - Server commands
- ✅ `.gitignore` - Git ignore file

### Tùy chọn (nếu có custom modules):
- ✅ `custom_addons/` - Custom modules của bạn (nếu có)
- ✅ `themes/` - Custom themes (nếu có)

---

## ❌ Các Thư Mục/File Cần Ignore

File `.gitignore` đã được cấu hình để ignore các thư mục/file sau:

### 1. **File cấu hình cá nhân:**
- `odoo.conf` - Chứa thông tin database, password
- `*.pyc`, `*.pyo` - Python compiled files
- `__pycache__/` - Python cache
- `*.egg-info` - Python egg info

### 2. **Thư mục môi trường ảo:**
- `bin/`
- `lib/`
- `include/`
- `share/`
- `build/`
- `dist/`
- `venv/` (nếu có)
- `env/` (nếu có)

### 3. **Thư mục dữ liệu:**
- `odoo/filestore/` - File uploads của users
- `odoo/addons/base/maintenance/` - Migration scripts

### 4. **File tạm và backup:**
- `*~` - Emacs backup files
- `*.orig` - Merge conflict files
- `*.log` - Log files
- `.DS_Store` - MacOS files

### 5. **Node modules và JS:**
- `node_modules/`
- `package-lock.json`
- `jsconfig.json`
- `tsconfig.json`

### 6. **File ẩn khác:**
- Tất cả dotfiles (`.something`) trừ `.gitignore`, `.github`, `.mailmap`

---

## 📤 Hướng Dẫn Push Code Lên Git

### Bước 1: Kiểm tra trạng thái
```bash
cd /home/bin04/odoo
git status
```

### Bước 2: Thêm tất cả file cần thiết
```bash
# Thêm tất cả file (sẽ tự động ignore theo .gitignore)
git add .

# Hoặc thêm từng file/folder cụ thể
git add addons/
git add odoo/
git add requirements.txt
git add setup.py
git add README.md
```

### Bước 3: Commit changes
```bash
git commit -m "Initial commit: Odoo 17.0 setup"
```

### Bước 4: Thêm remote repository
```bash
# Với GitHub
git remote add origin https://github.com/username/repository-name.git

# Với GitLab
git remote add origin https://gitlab.com/username/repository-name.git

# Với Bitbucket
git remote add origin https://bitbucket.org/username/repository-name.git
```

### Bước 5: Push lên remote
```bash
# Push lên branch main/master
git push -u origin main

# Hoặc nếu dùng branch master
git push -u origin master

# Hoặc branch 17.0 (theo current branch của bạn)
git push -u origin 17.0
```

### Bước 6: Push các lần sau
```bash
# Kiểm tra thay đổi
git status

# Thêm file thay đổi
git add .

# Commit
git commit -m "Mô tả thay đổi"

# Push
git push
```

---

## 🔧 Hướng Dẫn Cài Đặt Hoàn Chỉnh

### Yêu Cầu Hệ Thống

#### 1. **Python**
- Python 3.10 trở lên
- pip (Python package manager)

#### 2. **PostgreSQL**
- PostgreSQL 12 trở lên
- Database user với quyền tạo database

#### 3. **System Dependencies** (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    libxml2-dev \
    libxslt1-dev \
    libevent-dev \
    libsasl2-dev \
    libldap2-dev \
    libpq-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    zlib1g-dev \
    libwebp-dev \
    liblcms2-dev \
    libtiff5-dev \
    libopenjp2-7-dev \
    build-essential \
    git \
    curl \
    node-less \
    npm
```

#### 4. **wkhtmltopdf** (cho PDF reports)
```bash
# Ubuntu/Debian
sudo apt-get install -y wkhtmltopdf

# Hoặc tải phiên bản chính thức từ:
# https://wkhtmltopdf.org/downloads.html
```

---

### Các Bước Cài Đặt

#### Bước 1: Clone Repository
```bash
# Clone từ Git
git clone https://github.com/username/repository-name.git
cd repository-name

# Hoặc nếu đã có source code
cd /home/bin04/odoo
```

#### Bước 2: Tạo Virtual Environment
```bash
# Tạo virtual environment
python3 -m venv venv

# Kích hoạt virtual environment
source venv/bin/activate
```

#### Bước 3: Cài Đặt Python Dependencies
```bash
# Update pip
pip install --upgrade pip setuptools wheel

# Cài đặt dependencies từ requirements.txt
pip install -r requirements.txt

# Hoặc cài đặt từ setup.py
pip install -e .
```

#### Bước 4: Cài Đặt PostgreSQL
```bash
# Cài đặt PostgreSQL
sudo apt-get install -y postgresql postgresql-client

# Khởi động service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Tạo PostgreSQL user
sudo -u postgres createuser -s $USER

# Hoặc tạo user cụ thể cho Odoo
sudo -u postgres createuser -d -R -S odoo
sudo -u postgres psql -c "ALTER USER odoo WITH PASSWORD 'your_password';"
```

#### Bước 5: Tạo File Cấu Hình
```bash
# Tạo file odoo.conf
nano odoo.conf
```

**Nội dung file `odoo.conf`:**
```ini
[options]
; Database settings
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your_password
db_name = False

; Server settings
http_port = 8069
; http_interface = 0.0.0.0
workers = 2
max_cron_threads = 1

; Addons paths
addons_path = /home/bin04/odoo/addons,/home/bin04/odoo/odoo/addons

; Log settings
logfile = /home/bin04/odoo/odoo.log
log_level = info

; Admin settings
admin_passwd = admin_master_password

; Data directory
data_dir = /home/bin04/.local/share/Odoo

; Session settings
; limit_time_cpu = 60
; limit_time_real = 120
; limit_memory_hard = 2684354560
; limit_memory_soft = 2147483648
```

⚠️ **LƯU Ý:** File `odoo.conf` chứa thông tin nhạy cảm, không push lên Git!

#### Bước 6: Tạo Thư Mục Data
```bash
# Tạo thư mục lưu data
mkdir -p ~/.local/share/Odoo

# Set quyền
chmod 755 ~/.local/share/Odoo
```

---

## 🏃 Chạy Odoo

### 1. Chạy Odoo Development Mode
```bash
# Kích hoạt virtual environment (nếu chưa)
source venv/bin/activate

# Chạy Odoo
./odoo-bin -c odoo.conf

# Hoặc chạy với parameters
./odoo-bin -c odoo.conf -d database_name -i base --log-level=debug
```

### 2. Các Option Quan Trọng

#### Tạo database mới và cài modules:
```bash
./odoo-bin -c odoo.conf -d mydb -i base,sale,crm
```

#### Update modules:
```bash
./odoo-bin -c odoo.conf -d mydb -u all
```

#### Chạy không có config file:
```bash
./odoo-bin --addons-path=addons,odoo/addons -d mydb
```

#### Chạy với debug mode:
```bash
./odoo-bin -c odoo.conf --dev=all
```

### 3. Truy Cập Odoo
Mở trình duyệt và truy cập:
```
http://localhost:8069
```

### 4. Tạo Database Qua Web Interface
1. Truy cập `http://localhost:8069/web/database/manager`
2. Click "Create Database"
3. Nhập thông tin:
   - Master Password: (từ admin_passwd trong odoo.conf)
   - Database Name: mydb
   - Email: admin@example.com
   - Password: admin
   - Language: Vietnamese
4. Click "Create Database"

---

## 🔄 Setup Script Tự Động

Tạo file `install.sh` để tự động hóa cài đặt:

```bash
#!/bin/bash

echo "=== Bắt đầu cài đặt Odoo 17.0 ==="

# 1. Update system
echo "1. Updating system..."
sudo apt-get update -y

# 2. Cài đặt dependencies
echo "2. Installing system dependencies..."
sudo apt-get install -y \
    python3-dev python3-pip python3-venv \
    libxml2-dev libxslt1-dev libevent-dev \
    libsasl2-dev libldap2-dev libpq-dev \
    libjpeg-dev libpng-dev libfreetype6-dev \
    zlib1g-dev libwebp-dev liblcms2-dev \
    libtiff5-dev libopenjp2-7-dev \
    build-essential git curl node-less npm \
    postgresql postgresql-client wkhtmltopdf

# 3. Tạo virtual environment
echo "3. Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 4. Cài đặt Python packages
echo "4. Installing Python packages..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 5. Setup PostgreSQL
echo "5. Setting up PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres createuser -d -R -S $USER 2>/dev/null || echo "User already exists"

# 6. Tạo thư mục data
echo "6. Creating data directory..."
mkdir -p ~/.local/share/Odoo
chmod 755 ~/.local/share/Odoo

echo "=== Cài đặt hoàn tất! ==="
echo "Chạy lệnh sau để khởi động Odoo:"
echo "  source venv/bin/activate"
echo "  ./odoo-bin -c odoo.conf"
```

Cấp quyền và chạy:
```bash
chmod +x install.sh
./install.sh
```

---

## 🐛 Xử Lý Lỗi Thường Gặp

### 1. **Lỗi: Cannot import name 'etree'**
```bash
pip install --upgrade lxml
```

### 2. **Lỗi: psycopg2 installation failed**
```bash
sudo apt-get install -y libpq-dev python3-dev
pip install psycopg2-binary
```

### 3. **Lỗi: Pillow installation failed**
```bash
sudo apt-get install -y libjpeg-dev zlib1g-dev libpng-dev
pip install --upgrade Pillow
```

### 4. **Lỗi: Permission denied on port 8069**
```bash
# Đổi port trong odoo.conf
http_port = 8070

# Hoặc chạy với sudo (không khuyến khích)
sudo ./odoo-bin -c odoo.conf
```

### 5. **Lỗi: Database connection failed**
- Kiểm tra PostgreSQL đang chạy:
  ```bash
  sudo systemctl status postgresql
  ```
- Kiểm tra user/password trong odoo.conf
- Kiểm tra PostgreSQL user tồn tại:
  ```bash
  sudo -u postgres psql -c "\du"
  ```

### 6. **Lỗi: Module not found**
- Kiểm tra addons_path trong odoo.conf
- Restart Odoo sau khi thêm custom modules
- Update module list trong Settings

### 7. **Lỗi: Memory/Performance issues**
- Tăng workers trong odoo.conf:
  ```ini
  workers = 4
  max_cron_threads = 2
  ```
- Tăng memory limits:
  ```ini
  limit_memory_hard = 4294967296
  limit_memory_soft = 3221225472
  ```

---

## 📦 Deploy Production

### 1. Sử dụng Systemd Service

Tạo file `/etc/systemd/system/odoo.service`:

```ini
[Unit]
Description=Odoo 17.0
After=network.target postgresql.service

[Service]
Type=simple
User=odoo
Group=odoo
WorkingDirectory=/opt/odoo
Environment="PATH=/opt/odoo/venv/bin"
ExecStart=/opt/odoo/venv/bin/python3 /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf
StandardOutput=journal+console

[Install]
WantedBy=multi-user.target
```

Enable và start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo
sudo systemctl status odoo
```

### 2. Sử dụng Nginx Reverse Proxy

Cài đặt Nginx:
```bash
sudo apt-get install -y nginx
```

Tạo config `/etc/nginx/sites-available/odoo`:
```nginx
upstream odoo {
    server 127.0.0.1:8069;
}

server {
    listen 80;
    server_name your-domain.com;

    access_log /var/log/nginx/odoo.access.log;
    error_log /var/log/nginx/odoo.error.log;

    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    location / {
        proxy_pass http://odoo;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ~* /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📚 Tài Liệu Tham Khảo

- [Odoo Documentation](https://www.odoo.com/documentation/17.0/)
- [Odoo Developer Documentation](https://www.odoo.com/documentation/17.0/developer.html)
- [Odoo GitHub Repository](https://github.com/odoo/odoo)
- [Odoo Community Forum](https://www.odoo.com/forum)

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log file: `tail -f odoo.log`
2. Tham khảo documentation
3. Tìm kiếm trên Odoo Forum
4. Báo cáo issue trên GitHub

---

**Chúc bạn thành công! 🚀**
