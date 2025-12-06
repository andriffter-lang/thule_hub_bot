import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "thulehub.db"

# === Автоматический бэкап базы ===
def backup_database(max_backups: int = 5):
    """Создаёт резервную копию базы и хранит только последние 5"""
    if not os.path.exists(DB_PATH):
        return

    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = os.path.join(backup_dir, f"backup_{timestamp}.db")

    conn = sqlite3.connect(DB_PATH)
    backup_conn = sqlite3.connect(backup_name)
    conn.backup(backup_conn)
    backup_conn.close()
    conn.close()
    print(f"💾 Создан бэкап: {backup_name}")

    backups = sorted(
        [f for f in os.listdir(backup_dir) if f.startswith("backup_") and f.endswith(".db")]
    )

    if len(backups) > max_backups:
        old_backups = backups[:-max_backups]
        for old in old_backups:
            os.remove(os.path.join(backup_dir, old))
            print(f"🗑 Удалён старый бэкап: {old}")

# === Инициализация базы ===
def init_db():
    if os.path.exists(DB_PATH):
        backup_database()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Таблица товаров
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            description TEXT,
            price REAL,
            photos TEXT
        )
    """)

    # Таблица P2P-оборудования
    cur.execute("""
        CREATE TABLE IF NOT EXISTS p2p_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER,
            category TEXT,
            title TEXT,
            description TEXT,
            price_per_day REAL,
            city TEXT,
            district TEXT,
            latitude REAL,
            longitude REAL,
            created_at TEXT,
            active INTEGER DEFAULT 1
        )
    """)

    # Таблица запросов аренды (P2P)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS p2p_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            owner_id INTEGER,
            renter_id INTEGER,
            date_from TEXT,
            date_to TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    # Таблица объявлений
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            price REAL,
            location TEXT,
            photo_url TEXT,
            approved INTEGER DEFAULT 0
        )
    """)

    # Таблица заявок на ремонт
    cur.execute("""
        CREATE TABLE IF NOT EXISTS repair_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            phone TEXT,
            photo_url TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized: thulehub.db created or verified.")


# === Работа с товарами ===
def add_product(category, name, description, price, photos):
    """Добавляет новый товар"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO products (category, name, description, price, photos)
        VALUES (?, ?, ?, ?, ?)
    """, (category, name, description, price, json.dumps(photos)))
    conn.commit()
    conn.close()
    return True


def get_products(category=None):
    """Возвращает список товаров (по категории или все)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if category:
        cur.execute("SELECT * FROM products WHERE category = ?", (category,))
    else:
        cur.execute("SELECT * FROM products")

    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def find_product_by_id(product_id):
    """Возвращает товар по его ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_product(product_id, name=None, description=None, price=None, photos=None):
    """Обновляет товар по ID"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    updates = []
    params = []

    if name:
        updates.append("name = ?")
        params.append(name)
    if description:
        updates.append("description = ?")
        params.append(description)
    if price:
        updates.append("price = ?")
        params.append(price)
    if photos is not None:
        updates.append("photos = ?")
        params.append(json.dumps(photos))

    if not updates:
        conn.close()
        return False

    params.append(product_id)
    query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
    cur.execute(query, params)
    conn.commit()
    conn.close()
    return True


def delete_product(product_id):
    """Удаляет товар по ID"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return True

from datetime import datetime

def p2p_add_item(
    owner_id: int,
    category: str,
    title: str,
    description: str,
    price_per_day: float,
    city: str,
    district: str,
    latitude: float | None,
    longitude: float | None,
) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO p2p_items (
            owner_id, category, title, description, price_per_day,
            city, district, latitude, longitude, created_at, active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            owner_id,
            category,
            title,
            description,
            price_per_day,
            city,
            district,
            latitude,
            longitude,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    item_id = cur.lastrowid
    conn.commit()
    conn.close()
    return item_id


def p2p_get_items(city: str | None = None, district: str | None = None) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if city and district:
        cur.execute(
            "SELECT * FROM p2p_items WHERE active = 1 AND city = ? AND district = ? ORDER BY id DESC",
            (city, district),
        )
    elif city:
        cur.execute(
            "SELECT * FROM p2p_items WHERE active = 1 AND city = ? ORDER BY id DESC",
            (city,),
        )
    else:
        cur.execute("SELECT * FROM p2p_items WHERE active = 1 ORDER BY id DESC")

    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def p2p_get_my_items(owner_id: int) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM p2p_items WHERE owner_id = ? ORDER BY id DESC",
        (owner_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def p2p_add_request(
    item_id: int,
    owner_id: int,
    renter_id: int,
    date_from: str,
    date_to: str,
) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO p2p_requests (item_id, owner_id, renter_id, date_from, date_to, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
        """,
        (item_id, owner_id, renter_id, date_from, date_to, datetime.now().isoformat(timespec="seconds")),
    )
    req_id = cur.lastrowid
    conn.commit()
    conn.close()
    return req_id

# === Автозапуск при первом создании ===
if __name__ == "__main__":
    init_db()
