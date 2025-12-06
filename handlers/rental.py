# handlers/rental.py
import json
import asyncio
from aiogram import Router, F, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

rental_router = Router()

# ====== МЕНЮ АРЕНДЫ ======
@rental_router.message(F.text == "🚗 Аренда")
async def rental_menu(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Аренда от магазина"), KeyboardButton(text="🤝 P2P аренда")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("🚗 Выберите раздел аренды:", reply_markup=kb)

# ====== МЕНЮ P2P ======
@rental_router.message(F.text == "🤝 P2P аренда")
async def p2p_menu(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📤 Сдать оборудование")],
            [KeyboardButton(text="🔍 Найти оборудование")],
            [KeyboardButton(text="🗂 Мои P2P объявления")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("🤝 P2P аренда — выберите действие:", reply_markup=kb)

# ====== Сдать оборудование (заглушка) ======
@rental_router.message(F.text == "📤 Сдать оборудование")
async def p2p_add_item(message: types.Message):
    await message.answer("📤 Форма добавления оборудования в P2P аренду скоро будет готова.")

# ====== Найти оборудование (заглушка) ======
@rental_router.message(F.text == "🔍 Найти оборудование")
async def p2p_search(message: types.Message):
    await message.answer("🔍 Поиск оборудования в P2P аренде находится в разработке.")

# ====== Мои объявления (заглушка) ======
@rental_router.message(F.text == "🗂 Мои P2P объявления")
async def p2p_my_items(message: types.Message):
    await message.answer("🗂 Управление вашими P2P объявлениями будет доступно позже.")
