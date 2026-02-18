from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import aiosqlite
import os
from datetime import datetime

app = FastAPI()

# Монтируем статику
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Конфиг
WEBSITE_URL = os.getenv('WEBSITE_URL', 'http://localhost:8000')
VIP_CHAT_LINK = os.getenv('VIP_CHAT_LINK', 'https://t.me/+r3rxYlBjbTYyMDY6')

# ========== РОУТЫ ==========
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница"""
    async with aiosqlite.connect('../shizogp.db') as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT l.*, u.username as seller_name 
            FROM listings l
            JOIN users u ON l.seller_id = u.user_id
            WHERE l.status = 'active'
            ORDER BY l.created_at DESC
            LIMIT 8
        ''')
        listings = await cursor.fetchall()
    
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "listings": listings,
            "vip_chat_link": VIP_CHAT_LINK
        }
    )

@app.get("/webapp", response_class=HTMLResponse)
async def webapp(request: Request):
    """Telegram Mini App страница"""
    return templates.TemplateResponse("webapp.html", {"request": request})

@app.get("/api/listings")
async def get_listings():
    """API для получения списка скинов"""
    async with aiosqlite.connect('../shizogp.db') as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT l.*, u.username as seller_name, u.rating
            FROM listings l
            JOIN users u ON l.seller_id = u.user_id
            WHERE l.status = 'active'
            ORDER BY l.created_at DESC
            LIMIT 50
        ''')
        listings = await cursor.fetchall()
    
    return JSONResponse([dict(l) for l in listings])

@app.post("/api/user/deals")
async def get_user_deals(data: dict):
    """Получение сделок пользователя"""
    user_id = data.get('userId')
    
    async with aiosqlite.connect('../shizogp.db') as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT t.*, l.skin_name, l.quality,
                   u1.username as buyer_name,
                   u2.username as seller_name
            FROM transactions t
            JOIN listings l ON t.listing_id = l.id
            JOIN users u1 ON t.buyer_id = u1.user_id
            JOIN users u2 ON t.seller_id = u2.user_id
            WHERE t.buyer_id = ? OR t.seller_id = ?
            ORDER BY t.created_at DESC
        ''', (user_id, user_id))
        deals = await cursor.fetchall()
    
    return JSONResponse([dict(d) for d in deals])