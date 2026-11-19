#!/usr/bin/env python3
"""
Lightweight Backend Server & REST API for Bánh Tráng Lâm Thanh
Uses only Python Standard Library (Zero external dependencies).
"""

import os
import sys
import json
import socket
import sqlite3
import mimetypes
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "banhtrang.db")
PICTURE_DIR = os.path.join(BASE_DIR, "picture")

def find_available_port(preferred_ports=[8080, 8888, 3000, 5500, 8000]):
    for port in preferred_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return 8080

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class BanhTrangRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def send_json(self, data, status_code=200):
        response_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        # Default root
        if path == '' or path == '/':
            self.path = '/index.html'
            return super().do_GET()

        # API: Get list of products
        if path == '/api/products':
            params = parse_qs(parsed.query)
            include_inactive = params.get('all', ['0'])[0] == '1'

            conn = get_db_connection()
            cursor = conn.cursor()
            if include_inactive:
                cursor.execute("SELECT * FROM products ORDER BY sort_order ASC, id DESC")
            else:
                cursor.execute("SELECT * FROM products WHERE is_active = 1 ORDER BY sort_order ASC, id DESC")
            rows = cursor.fetchall()
            products = [dict(row) for row in rows]
            conn.close()
            return self.send_json({"success": True, "data": products})

        # API: Get list of inquiries (customer contacts)
        elif path == '/api/inquiries':
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inquiries ORDER BY id DESC")
            rows = cursor.fetchall()
            inquiries = [dict(row) for row in rows]
            conn.close()
            return self.send_json({"success": True, "data": inquiries})

        # API: Get single product by ID
        elif path.startswith('/api/products/'):
            product_id = path.split('/')[-1]
            if product_id.isdigit():
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    return self.send_json({"success": True, "data": dict(row)})
                else:
                    return self.send_json({"success": False, "error": "Không tìm thấy sản phẩm"}, 404)

        # API: Get list of available image assets in picture/
        elif path == '/api/images':
            images = []
            if os.path.exists(PICTURE_DIR):
                for fname in sorted(os.listdir(PICTURE_DIR)):
                    if fname.lower().endswith(('.webp', '.jpg', '.jpeg', '.png', '.svg')):
                        images.append(f"picture/{fname}")
            return self.send_json({"success": True, "data": images})

        # Fallback to standard static file serving
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        # API: Create product
        if path == '/api/products':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
            except Exception:
                return self.send_json({"success": False, "error": "Dữ liệu JSON không hợp lệ"}, 400)

            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            image_url = data.get('image_url', '').strip()
            badge = data.get('badge', '').strip()
            badge_type = data.get('badge_type', 'normal')
            spec_tag = data.get('spec_tag', '').strip()
            delivery_note = data.get('delivery_note', 'Đóng thùng chống ẩm toàn quốc').strip()
            sort_order = int(data.get('sort_order', 0))
            is_active = 1 if data.get('is_active', True) else 0

            if not name or not description:
                return self.send_json({"success": False, "error": "Vui lòng nhập tên và mô tả sản phẩm"}, 400)

            if not image_url:
                image_url = 'picture/banhram1-500w.webp'

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO products (name, badge, badge_type, spec_tag, description, delivery_note, image_url, sort_order, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, badge, badge_type, spec_tag, description, delivery_note, image_url, sort_order, is_active))
            new_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return self.send_json({"success": True, "message": "Thêm sản phẩm thành công", "id": new_id}, 201)

        # API: Submit customer inquiry
        elif path == '/api/inquiries':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
            except Exception:
                return self.send_json({"success": False, "error": "Dữ liệu JSON không hợp lệ"}, 400)

            customer_name = data.get('customer_name', '').strip() or 'Quý khách'
            phone = data.get('phone', '').strip()
            business_type = data.get('business_type', '').strip()
            address = data.get('address', '').strip()
            note = data.get('note', '').strip()
            recipient = data.get('recipient', 'Chị Thanh (0935 746 795)').strip()

            if not phone:
                return self.send_json({"success": False, "error": "Vui lòng nhập số điện thoại"}, 400)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO inquiries (customer_name, phone, business_type, address, note, recipient)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (customer_name, phone, business_type, address, note, recipient))
            new_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return self.send_json({"success": True, "message": "Đã ghi nhận thông tin liên hệ", "id": new_id}, 201)

        # API: Upload image file
        elif path == '/api/upload':
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                return self.send_json({"success": False, "error": "Yêu cầu định dạng multipart/form-data"}, 400)

            content_length = int(self.headers.get('Content-Length', 0))
            boundary = content_type.split("boundary=")[-1].encode('utf-8')
            body_bytes = self.rfile.read(content_length)

            parts = body_bytes.split(b"--" + boundary)
            saved_file_url = None

            for part in parts:
                if b'Content-Disposition' in part and b'filename=' in part:
                    header_part, file_data = part.split(b"\r\n\r\n", 1)
                    file_data = file_data.rstrip(b"\r\n")

                    header_str = header_part.decode('latin1')
                    for line in header_str.split("\r\n"):
                        if 'filename=' in line:
                            raw_filename = line.split('filename=')[1].strip('"\'')
                            filename = os.path.basename(raw_filename).replace(' ', '_')
                            if filename:
                                target_path = os.path.join(PICTURE_DIR, filename)
                                with open(target_path, 'wb') as f:
                                    f.write(file_data)
                                saved_file_url = f"picture/{filename}"
                                break

            if saved_file_url:
                return self.send_json({"success": True, "url": saved_file_url})
            else:
                return self.send_json({"success": False, "error": "Không thể xử lý tệp tải lên"}, 400)

        return self.send_json({"success": False, "error": "Endpoint không tồn tại"}, 404)

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path.startswith('/api/products/'):
            product_id = path.split('/')[-1]
            if not product_id.isdigit():
                return self.send_json({"success": False, "error": "ID không hợp lệ"}, 400)

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
            except Exception:
                return self.send_json({"success": False, "error": "Dữ liệu JSON không hợp lệ"}, 400)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
            if not cursor.fetchone():
                conn.close()
                return self.send_json({"success": False, "error": "Sản phẩm không tồn tại"}, 404)

            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            image_url = data.get('image_url', '').strip()
            badge = data.get('badge', '').strip()
            badge_type = data.get('badge_type', 'normal')
            spec_tag = data.get('spec_tag', '').strip()
            delivery_note = data.get('delivery_note', 'Đóng thùng chống ẩm toàn quốc').strip()
            sort_order = int(data.get('sort_order', 0))
            is_active = 1 if data.get('is_active', True) else 0

            cursor.execute("""
            UPDATE products SET
                name = ?, badge = ?, badge_type = ?, spec_tag = ?, description = ?,
                delivery_note = ?, image_url = ?, sort_order = ?, is_active = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (name, badge, badge_type, spec_tag, description, delivery_note, image_url, sort_order, is_active, product_id))
            conn.commit()
            conn.close()

            return self.send_json({"success": True, "message": "Cập nhật sản phẩm thành công"})

        return self.send_json({"success": False, "error": "Endpoint không tồn tại"}, 404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path.startswith('/api/products/'):
            product_id = path.split('/')[-1]
            if not product_id.isdigit():
                return self.send_json({"success": False, "error": "ID không hợp lệ"}, 400)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()

            return self.send_json({"success": True, "message": "Đã xóa sản phẩm khỏi cơ sở dữ liệu"})

        return self.send_json({"success": False, "error": "Endpoint không tồn tại"}, 404)

def run_server():
    port = find_available_port()
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, BanhTrangRequestHandler)
    print(f"==================================================")
    print(f"  BÁNH TRÁNG LÂM THANH - LANDING PAGE SERVER")
    print(f"  Trang chủ:      http://localhost:{port}/")
    print(f"==================================================")
    print(f"Đang phục vụ tại cổng {port}. Nhấn Ctrl+C để dừng.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nĐang dừng máy chủ...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
