#!/usr/bin/env python3
"""
Initialize SQLite Database for Bánh Tráng Lâm Thanh
Database file: data/banhtrang.db
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "banhtrang.db")

def init_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        badge TEXT DEFAULT '',
        badge_type TEXT DEFAULT 'normal',
        spec_tag TEXT DEFAULT '',
        description TEXT NOT NULL,
        delivery_note TEXT DEFAULT 'Đóng thùng chống ẩm toàn quốc',
        image_url TEXT NOT NULL,
        stars INTEGER DEFAULT 5,
        sort_order INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create inquiries / contacts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        business_type TEXT,
        address TEXT,
        note TEXT,
        recipient TEXT DEFAULT 'Chị Thanh (0935 746 795)',
        status TEXT DEFAULT 'Mới',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Check if table already has rows
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count == 0:
        initial_products = [
            (
                "Bánh Ram Ống Chiên Giòn",
                "Bán Chạy Nhất",
                "accent",
                "✓ Chuyên Quán Nem Nướng",
                "Cuộn ống chuẩn size, khi chiên phồng xốp vàng ruộm, đặc biệt giữ độ giòn suốt 8 tiếng mà không hề ngấm dầu hay bị ỉu.",
                "Đóng thùng chống ẩm toàn quốc",
                "picture/banhram1-500w.webp",
                5,
                1,
                1
            ),
            (
                "Bánh Ram Vuông Cuốn Nem",
                "Gạo Thuần Khiết",
                "normal",
                "✓ Dẻo Dai Không Rách",
                "Độ mỏng đồng đều, mềm mịn tự nhiên từ hạt gạo quê; không cần nhúng nhiều nước, dễ dàng cuộn chặt tay với rau sống và nem nướng.",
                "Đóng gói theo yêu cầu đối tác",
                "picture/banhcuon1-500w.webp",
                5,
                2,
                1
            ),
            (
                "Bánh Mè Nhúng Liếp Tre",
                "Hạt Mè Rang Thơm",
                "normal",
                "✓ Đậm Vị Truyền Thống",
                "Bánh dày vừa vặn điểm xuyết hạt mè rang thơm béo ngậy; nhúng nước mềm mại cuốn cá hấp, thịt luộc hoặc nướng giòn ăn vặt.",
                "Phơi nẹp tre mộc thơm lúa mới",
                "picture/banhme2-500w.webp",
                5,
                3,
                1
            ),
            (
                "Bánh Tráng Theo Quy Cách",
                "Cung Ứng Lớn",
                "accent",
                "✓ Đơn Hàng Sỉ & Chuỗi Quán",
                "Nhận đặt hàng số lượng lớn theo độ dày, kích thước vuông/tròn và quy cách đóng gói riêng cho các hệ thống nhà hàng khắp cả nước.",
                "Chính sách ưu đãi giá gốc tận xưởng",
                "picture/banhcuon2-500w.webp",
                5,
                4,
                1
            )
        ]

        cursor.executemany("""
        INSERT INTO products (
            name, badge, badge_type, spec_tag, description, delivery_note, image_url, stars, sort_order, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, initial_products)
        print(f"Initialized database with {len(initial_products)} sample products.")
    else:
        print(f"Database already contains {count} products.")

    conn.commit()
    conn.close()
    print(f"Database ready at: {DB_PATH}")

if __name__ == "__main__":
    init_database()

