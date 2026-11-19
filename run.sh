#!/usr/bin/env bash
# Khởi động hệ thống Web & Cơ sở dữ liệu SQLite Bánh Tráng Lâm Thanh
cd "$(dirname "$0")"

echo "=== KHỞI ĐỘNG CƠ SỞ DỮ LIỆU & WEB BÁNH TRÁNG LÂM THANH ==="
python3 init_db.py
echo ""
python3 server.py
