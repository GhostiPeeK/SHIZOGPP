import asyncio
import logging
import json
import hmac
import hashlib
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiosqlite
from datetime import datetime, timedelta
import os

# ========== КОНФИГ ==========
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
WEBSITE_URL = os.getenv('WEBSITE_URL', 'https://your-site.com')
VIP_CHAT_LINK = os.getenv('VIP_CHAT_LINK', 'https://t.me/+r3rxYlBjbTYyMDY6')
VIP_PRICE_COINS = 550

# ========== ИНИЦИАЛИЗАЦИЯ ==========
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

# ========== ФУНКЦИИ БД ==========
async def get_user(user_id):
    async with aiosqlite.connect('../shizogp.db') as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return await cursor.fetchone()

async def create_user(user_id, username, full_name, referrer_id=None):
    async with aiosqlite.connect('../shizogp.db') as db:
        cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if await cursor.fetchone():
            return
        await db.execute('''
            INSERT INTO users (user_id, username, full_name, referrer_id, last_visit)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, username, full_name, referrer_id))
        if referrer_id:
            await db.execute('''
                UPDATE users SET balance_coins = balance_coins + 50 
                WHERE user_id = ?
            ''', (referrer_id,))
        await db.commit()

# ========== КЛАВИАТУРЫ ==========
def get_main_keyboard():
    buttons = [
        [InlineKeyboardButton(
            text="🛒 Открыть магазин", 
            web_app=WebAppInfo(url=f"{WEBSITE_URL}/webapp")
        )],
        [InlineKeyboardButton(text="💸 Продать скин", callback_data="sell_start")],
        [InlineKeyboardButton(text="📦 Мои сделки", callback_data="my_deals")],
        [InlineKeyboardButton(text="👑 VIP чат", url=VIP_CHAT_LINK)],
        [InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
        [InlineKeyboardButton(text="🤝 Рефералы", callback_data="referral")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ========== СОСТОЯНИЯ ==========
class SellStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_quality = State()
    waiting_for_price = State()
    waiting_for_link = State()

# ========== ХЕНДЛЕРЫ ==========
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name
    
    args = message.text.split()
    referrer_id = None
    if len(args) > 1:
        ref_arg = args[1]
        if ref_arg.startswith("ref_"):
            try:
                referrer_id = int(ref_arg.replace("ref_", ""))
                if referrer_id == user_id:
                    referrer_id = None
            except:
                pass
    
    await create_user(user_id, username, full_name, referrer_id)
    
    text = (
        f"👋 Добро пожаловать в SHIZOGP!\n\n"
        f"🔥 Здесь ты можешь покупать и продавать скины CS2\n"
        f"💎 Плати как хочешь: карта, крипта, баланс\n"
        f"👑 VIP чат для избранных\n\n"
        f"⬇️ Жми кнопку ниже, чтобы открыть магазин прямо в Telegram!"
    )
    
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.callback_query(F.data == "balance")
async def show_balance(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    
    if not user:
        await callback.message.edit_text("Пользователь не найден")
        return
    
    text = (
        f"💰 ТВОЙ БАЛАНС\n\n"
        f"Монеты: {user['balance_coins']} 🪙\n"
        f"Крипта: {user['balance_crypto']:.6f} BTC\n\n"
        f"Рейтинг: {user['rating']:.1f} ⭐ ({user['rating_count']} отзывов)\n"
        f"Продаж: {user['total_sales']}\n"
        f"Покупок: {user['total_purchases']}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀ Назад", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("Главное меню:", reply_markup=get_main_keyboard())

# ========== ЗАПУСК ==========
async def main():
    print("🔥 SHIZOGP Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())