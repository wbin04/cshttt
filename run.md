ps aux | grep odoo-bin | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null; sleep 2 && rm -rf odoo/data/filestore/erp_taphoa/assets/* && echo "✅ Assets cleared"

cd /home/bin04/cshttt && source odoo/venv/bin/activate && python3 odoo/odoo-bin -c odoo.conf &