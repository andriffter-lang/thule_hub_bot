# market_router.py
import asyncio
import json
import sqlite3
from aiogram import Router, F, types
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import ADMIN_ID
from database import DB_PATH

market_router = Router()


# ---------- FSM ДЛЯ СОЗДАНИЯ ОБЪЯВЛЕНИЯ ----------
class AddAdFSM(StatesGroup):
    waiting_photos = State()
    waiting_description = State()
    waiting_price = State()
    waiting_location = State()


# ---------- МЕНЮ РЫНКА ----------
@market_router.message(F.text == "📦 Рынок оборудования Thule")
async def market_menu(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Разместить объявление"), KeyboardButton(text="🔍 Смотреть объявления")],
            [KeyboardButton(text="🗓 Мои объявления"), KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("📦 Выберите действие:", reply_markup=kb)


# ---------- СОЗДАНИЕ НОВОГО ОБЪЯВЛЕНИЯ ----------
@market_router.message(F.text == "➕ Разместить объявление")
async def market_add_start(message: types.Message, state: FSMContext):
    await state.set_state(AddAdFSM.waiting_photos)
    await state.update_data(photos=[])
    await message.answer("📸 Пришлите 1–10 фото товара. Когда закончите — напишите «Готово».")


@market_router.message(AddAdFSM.waiting_photos, F.photo)
async def market_collect_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    if len(photos) >= 10:
        return await message.answer("⚠️ Можно добавить максимум 10 фото.")

    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

    await message.answer(f"Фото добавлено ({len(photos)}/10). Добавьте ещё или напишите «Готово».")


@market_router.message(AddAdFSM.waiting_photos, F.text.casefold() == "готово")
async def market_photos_done(message: types.Message, state: FSMContext):
    await state.set_state(AddAdFSM.waiting_description)
    await message.answer("📝 Напишите название и описание объявления.")


@market_router.message(AddAdFSM.waiting_description)
async def market_add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AddAdFSM.waiting_price)
    await message.answer("💰 Укажите цену товара в рублях.")


@market_router.message(AddAdFSM.waiting_price)
async def market_add_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
    except ValueError:
        return await message.answer("⚠️ Укажите цену числом!")

    await state.update_data(price=price)
    await state.set_state(AddAdFSM.waiting_location)
    await message.answer("📍 Укажите город / локацию.")


@market_router.message(AddAdFSM.waiting_location)
async def market_add_finish(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text.strip())
    data = await state.get_data()
    await state.clear()

    # Сохраняем в базу как черновик (на модерацию)
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO ads (title, description, price, location, photo_url, approved)
            VALUES (?, ?, ?, ?, ?, 0)
        """,
        (
            data["description"].split("\n")[0],  # заголовок
            data["description"],
            data["price"],
            data["location"],
            json.dumps(data.get("photos", [])),
        ))

        ad_id = cur.lastrowid
        conn.commit()
        conn.close()

    except Exception as e:
        await message.answer("⚠️ Ошибка сохранения объявления.")
        print("DB Error:", e)
        return

    # Уведомление администратору
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_ad:{ad_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_ad:{ad_id}"),
            ]
        ]
    )

    photos = data.get("photos", [])
    caption = (
        f"🆕 *Новое объявление на модерацию*\n\n"
        f"ID: {ad_id}\n"
        f"{data['description']}\n"
        f"💰 {data['price']} ₽\n"
        f"📍 {data['location']}"
    )

    try:
        if photos:
            await message.bot.send_photo(ADMIN_ID, photos[0], caption=caption, parse_mode="Markdown", reply_markup=kb)
        else:
            await message.bot.send_message(ADMIN_ID, caption, parse_mode="Markdown", reply_markup=kb)
    except Exception as e:
        print("Admin notify error:", e)

    await message.answer("✅ Объявление отправлено на модерацию!")


# ---------- ОДОБРЕНИЕ / ОТКЛОНЕНИЕ АДМИНИСТРАТОРОМ ----------
@market_router.callback_query(F.data.startswith("approve_ad:"))
async def approve_ad(callback: types.CallbackQuery):
    ad_id = int(callback.data.split(":")[1])

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE ads SET approved = 1 WHERE id = ?", (ad_id,))
    conn.commit()
    conn.close()

    try:
        await callback.message.edit_caption(f"✅ Объявление №{ad_id} одобрено.", parse_mode="Markdown")
    except:
        await callback.message.edit_text(f"✅ Объявление №{ad_id} одобрено.", parse_mode="Markdown")

    await callback.answer("Опубликовано!")


@market_router.callback_query(F.data.startswith("reject_ad:"))
async def reject_ad(callback: types.CallbackQuery):
    ad_id = int(callback.data.split(":")[1])

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM ads WHERE id = ?", (ad_id,))
    conn.commit()
    conn.close()

    try:
        await callback.message.edit_caption(f"❌ Объявление №{ad_id} отклонено и удалено.", parse_mode="Markdown")
    except:
        await callback.message.edit_text(f"❌ Объявление №{ad_id} отклонено и удалено.", parse_mode="Markdown")

    await callback.answer("Удалено.")


# ---------- ПРОСМОТР ОДОБРЕННЫХ ОБЪЯВЛЕНИЙ ----------
@market_router.message(F.text == "🔍 Смотреть объявления")
async def view_ads(message: types.Message):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM ads WHERE approved = 1 ORDER BY id DESC LIMIT 20")
    ads = [dict(r) for r in cur.fetchall()]
    conn.close()

    if not ads:
        return await message.answer("Пока нет опубликованных объявлений 💤")

    for ad in ads:
        photos = []
        try:
            if ad["photo_url"]:
                photos = json.loads(ad["photo_url"])
        except:
            pass

        text = (
            f"📦 *{ad['title']}*\n"
            f"{ad['description']}\n\n"
            f"💰 {ad['price']} ₽\n"
            f"📍 {ad['location']}"
        )

        if photos:
            await message.answer_photo(photos[0], caption=text, parse_mode="Markdown")
        else:
            await message.answer(text, parse_mode="Markdown")

        await asyncio.sleep(0.2)


# ---------- МОИ ОБЪЯВЛЕНИЯ (будущее) ----------
@market_router.message(F.text == "🗓 Мои объявления")
async def my_ads(message: types.Message):
    await message.answer("Функция появится позже: привязка объявлений к автору.")


