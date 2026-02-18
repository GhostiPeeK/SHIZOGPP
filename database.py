import aiosqlite
import os
from datetime import datetime

DB_NAME = os.getenv('DB_NAME', 'shizogp.db')

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Пользователи
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                balance_coins INTEGER DEFAULT 0,
                balance_crypto REAL DEFAULT 0,
                vip_status INTEGER DEFAULT 0,
                vip_until DATETIME,
                referrer_id INTEGER,
                steam_id TEXT,
                steam_username TEXT,
                steam_avatar TEXT,
                steam_profile_url TEXT,
                telegram_avatar TEXT,
                rating REAL DEFAULT 5.0,
                rating_count INTEGER DEFAULT 0,
                total_sales INTEGER DEFAULT 0,
                total_purchases INTEGER DEFAULT 0,
                registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_visit DATETIME,
                is_admin INTEGER DEFAULT 0,
                is_verified INTEGER DEFAULT 0,
                FOREIGN KEY (referrer_id) REFERENCES users (user_id)
            )
        ''')
        
        # Steam авторизация
        await db.execute('''
            CREATE TABLE IF NOT EXISTS steam_auth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                steam_id TEXT UNIQUE,
                steam_username TEXT,
                steam_avatar TEXT,
                profile_url TEXT,
                auth_token TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Объявления
        await db.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER,
                skin_name TEXT,
                quality TEXT,
                price_usd REAL,
                price_rub INTEGER,
                price_btc REAL,
                price_eth REAL,
                steam_link TEXT,
                image_url TEXT,
                float_value REAL,
                pattern TEXT,
                status TEXT DEFAULT 'active',
                views INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                FOREIGN KEY (seller_id) REFERENCES users (user_id)
            )
        ''')
        
        # Сделки
        await db.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER,
                buyer_id INTEGER,
                seller_id INTEGER,
                amount_usd REAL,
                amount_rub INTEGER,
                amount_btc REAL,
                amount_eth REAL,
                currency TEXT DEFAULT 'usd',
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                payment_id TEXT,
                crypto_tx_hash TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                buyer_rating INTEGER,
                seller_rating INTEGER,
                buyer_review TEXT,
                seller_review TEXT,
                FOREIGN KEY (listing_id) REFERENCES listings (id),
                FOREIGN KEY (buyer_id) REFERENCES users (user_id),
                FOREIGN KEY (seller_id) REFERENCES users (user_id)
            )
        ''')
        
        # Крипто-платежи
        await db.execute('''
            CREATE TABLE IF NOT EXISTS crypto_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER,
                user_id INTEGER,
                amount_usd REAL,
                amount_crypto REAL,
                currency TEXT,
                payment_address TEXT,
                payment_id TEXT,
                status TEXT DEFAULT 'pending',
                confirmations INTEGER DEFAULT 0,
                tx_hash TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expired_at DATETIME,
                completed_at DATETIME,
                FOREIGN KEY (transaction_id) REFERENCES transactions (id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Комментарии
        await db.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER,
                user_id INTEGER,
                comment TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES listings (id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Избранное
        await db.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER,
                listing_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, listing_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (listing_id) REFERENCES listings (id)
            )
        ''')
        
        # Уведомления
        await db.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                title TEXT,
                message TEXT,
                data TEXT,
                is_read INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Отзывы
        await db.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER,
                to_user_id INTEGER,
                transaction_id INTEGER,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_user_id) REFERENCES users (user_id),
                FOREIGN KEY (to_user_id) REFERENCES users (user_id),
                FOREIGN KEY (transaction_id) REFERENCES transactions (id)
            )
        ''')
        
        await db.commit()