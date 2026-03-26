#!/usr/bin/env python3
"""Create and seed the Dala Succulents SQLite database."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'dala.db')


def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            scientific_name TEXT,
            description TEXT,
            price REAL NOT NULL,
            image_url TEXT,
            image_url_large TEXT,
            sold_out INTEGER DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE carousel_slides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_url TEXT NOT NULL,
            heading TEXT NOT NULL,
            subheading TEXT,
            button_text TEXT,
            button_link TEXT,
            sort_order INTEGER DEFAULT 0
        )
    ''')

    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            name TEXT,
            picture_url TEXT,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    products = [
        (
            "Echeveria 'Lola'",
            "echeveria-lola",
            "Echeveria",
            "A stunning rosette succulent with pearlescent lavender-pink leaves. "
            "Echeveria 'Lola' thrives in bright indirect light and needs watering only when the soil is completely dry. "
            "Perfect for windowsills and arrangements.",
            24.99,
            "https://picsum.photos/seed/echeveria/400/400",
            "https://picsum.photos/seed/echeveria/800/800",
            0, 1
        ),
        (
            "Haworthia cooperi",
            "haworthia-cooperi",
            "Haworthia",
            "Known for its translucent, gem-like leaf tips that glow when backlit. "
            "Haworthia cooperi prefers bright filtered light and is very forgiving of occasional neglect. "
            "A compact grower ideal for desks and small spaces.",
            18.50,
            "https://picsum.photos/seed/haworthia/400/400",
            "https://picsum.photos/seed/haworthia/800/800",
            0, 2
        ),
        (
            "Lithops karasmontana",
            "lithops-karasmontana",
            "Lithops",
            "These 'living stones' mimic pebbles in their native habitat of southern Africa. "
            "Lithops require very little water — a deep soak once a month in the growing season is plenty. "
            "They produce daisy-like flowers in autumn.",
            12.00,
            "https://picsum.photos/seed/lithops23/400/400",
            "https://picsum.photos/seed/lithops23/800/800",
            0, 3
        ),
        (
            "Adenia glauca",
            "adenia-glauca",
            "Adenia",
            "A spectacular caudiciform with a swollen grey-green trunk and delicate climbing vines. "
            "Adenia glauca stores water in its caudex and can tolerate dry periods. "
            "Provide warm temperatures and well-draining soil for best results.",
            45.00,
            "https://picsum.photos/seed/adenia7/400/400",
            "https://picsum.photos/seed/adenia7/800/800",
            1, 4
        ),
        (
            "Pachypodium lamerei",
            "pachypodium-lamerei",
            "Pachypodium",
            "Often called the Madagascar Palm, this striking plant features a thick spiny trunk topped with glossy leaves. "
            "Pachypodium lamerei loves full sun and warmth, making it a dramatic focal point. "
            "Water sparingly in winter when it drops its leaves.",
            38.00,
            "https://picsum.photos/seed/pachypod/400/400",
            "https://picsum.photos/seed/pachypod/800/800",
            0, 5
        ),
        (
            "Euphorbia obesa",
            "euphorbia-obesa",
            "Euphorbia",
            "A perfectly spherical succulent native to South Africa, sometimes called the Baseball Plant. "
            "Euphorbia obesa is slow-growing and extremely drought-tolerant. "
            "Handle with care as its sap can be irritating to skin.",
            29.99,
            "https://picsum.photos/seed/euphorbia9/400/400",
            "https://picsum.photos/seed/euphorbia9/800/800",
            0, 6
        ),
    ]

    c.executemany('''
        INSERT INTO products (name, slug, scientific_name, description, price, image_url, image_url_large, sold_out, sort_order)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', products)

    slides = [
        (
            "https://picsum.photos/seed/succulent1/1200/500",
            "Rare & Unusual Succulents",
            "Curated collection of exotic plants from around the world, delivered to your door.",
            "Shop Now",
            "#shop",
            1
        ),
        (
            "https://picsum.photos/seed/cactus42/1200/500",
            "New Arrivals Weekly",
            "Fresh shipments every Tuesday. Follow us for first access to rare finds.",
            "View New Arrivals",
            "#shop",
            2
        ),
        (
            "https://picsum.photos/seed/plant88/1200/500",
            "Expert Care Guides",
            "Every plant ships with a detailed care card. We're here to help your plants thrive.",
            "Learn More",
            "#shop",
            3
        ),
    ]

    c.executemany('''
        INSERT INTO carousel_slides (image_url, heading, subheading, button_text, button_link, sort_order)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', slides)

    conn.commit()
    conn.close()
    print(f"Database created at {os.path.abspath(DB_PATH)}")


if __name__ == '__main__':
    init_db()
