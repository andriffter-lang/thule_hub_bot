# shop_router.py
import asyncio
import json
from aiogram.filters import Command
from aiogram import Router, F, types
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from database import get_products, find_product_by_id
from config import ADMIN_ID

shop_router = Router()

@shop_router.message(Command("shop"))
async def shop_entry(message: types.Message):
    await shop_menu(message)  # вызываем существующее меню

@shop_router.message(F.text == "🏪 Магазин")
async def shop_menu(message: types.Message):
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚙 Автобоксы"), KeyboardButton(text="🚗 Автобагажники")],
            [KeyboardButton(text="🚴 Велокрепления на крышу"), KeyboardButton(text="🚚 Велокрепления на фаркоп")],
            [KeyboardButton(text="🔧 Запчасти"), KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )

    await message.answer("🏪 Выберите категорию:", reply_markup=kb)


@shop_router.message(F.text.in_(["🚙 Автобоксы", "🚗 Автобагажники",
                                 "🚴 Велокрепления на крышу", "🚚 Велокрепления на фаркоп",
                                 "🔧 Запчасти"]))
async def category_products(message: types.Message):
    category = (
        message.text.replace("🚙 ", "")
        .replace("🚗 ", "")
        .replace("🚴 ", "")
        .replace("🚚 ", "")
        .replace("🔧 ", "")
    )

    products = get_products(category)

    if not products:
        await message.answer(f"⚠️ В категории «{category}» пока нет товаров.")
        return

    for p in products:
        photos = json.loads(p["photos"]) if p.get("photos") else []
        caption = f"*{p['name']}*\n💰 {p['price']} ₽\n\n{p['description']}"

        buttons = [[InlineKeyboardButton(text="🛒 Купить", callback_data=f"buy:{p['id']}")]]
        if len(photos) > 1:
            buttons.append([InlineKeyboardButton(text="📸 Ещё фото", callback_data=f"more_photos:{p['id']}")])

        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        if photos:
            await message.answer_photo(photos[0], caption=caption, parse_mode="Markdown", reply_markup=markup)
        else:
            await message.answer(caption, parse_mode="Markdown", reply_markup=markup)

        await asyncio.sleep(0.25)


@shop_router.callback_query(F.data.startswith("more_photos:"))
async def more_photos(callback: types.CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    product = find_product_by_id(product_id)

    if not product:
        return await callback.answer("❌ Товар не найден.", show_alert=True)

    photos = json.loads(product["photos"]) if product.get("photos") else []

    if len(photos) > 1:
        media = [InputMediaPhoto(media=p) for p in photos[1:]]
        await callback.bot.send_media_group(callback.message.chat.id, media)

    await callback.answer()


@shop_router.callback_query(F.data.startswith("buy:"))
async def buy_product(callback: types.CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    product = find_product_by_id(product_id)

    if not product:
        return await callback.answer("❌ Товар не найден.", show_alert=True)

    user = callback.from_user

    user_link = f"@{user.username}" if user.username else f"[Профиль](tg://user?id={user.id})"
    admin_link = f"tg://user?id={ADMIN_ID}"

    # Сообщение покупателю
    await callback.message.answer(
        f"✅ Запрос отправлен администратору.\n"
        f"Связаться: [Открыть чат]({admin_link})",
        parse_mode="Markdown"
    )

    # Сообщение админу
    caption = (
        f"🛍 *Новая заявка на покупку*\n\n"
        f"📦 {product['name']}\n"
        f"💰 {product['price']} ₽\n"
        f"{product['description']}\n\n"
        f"👤 Покупатель: {user_link}"
    )

    photos = json.loads(product["photos"]) if product.get("photos") else []

    if photos:
        await callback.bot.send_photo(ADMIN_ID, photos[0], caption=caption, parse_mode="Markdown")
    else:
        await callback.bot.send_message(ADMIN_ID, caption, parse_mode="Markdown")

    await callback.answer()
