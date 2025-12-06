# repair_router.py
import json
import sqlite3
from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from database import DB_PATH

repair_router = Router()


# ---------- FSM ----------
class RepairFSM(StatesGroup):
    waiting_photos = State()
    waiting_description = State()
    waiting_phone = State()


# ---------- Старт ----------
@repair_router.message(F.text == "🧰 Ремонт")
async def repair_start(message: types.Message, state: FSMContext):
    await state.set_state(RepairFSM.waiting_photos)
    await state.update_data(photos=[])

    await message.answer(
        "🧰 *Оформление заявки на ремонт*\n\n"
        "Пришлите **1–10 фото поломки**.\n"
        "Когда закончите — напишите «Готово».",
        parse_mode="Markdown"
    )


# ---------- Получение фото ----------
@repair_router.message(RepairFSM.waiting_photos, F.photo)
async def repair_collect_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    if len(photos) >= 10:
        return await message.answer("⚠️ Можно добавить максимум 10 фото. Напишите «Готово».")

    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

    await message.answer(f"📸 Фото добавлено ({len(photos)}/10). Вы можете добавить ещё или написать «Готово».")


# ---------- Конец загрузки фото ----------
@repair_router.message(RepairFSM.waiting_photos, F.text.casefold() == "готово")
async def repair_photos_done(message: types.Message, state: FSMContext):
    await state.set_state(RepairFSM.waiting_description)
    await message.answer("📝 Теперь опишите проблему. Можно в нескольких предложениях.")


# ---------- Описание ----------
@repair_router.message(RepairFSM.waiting_description)
async def repair_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(RepairFSM.waiting_phone)
    await message.answer("📞 Укажите контактный номер телефона.")


# ---------- Телефон и завершение ----------
@repair_router.message(RepairFSM.waiting_phone)
async def repair_finish(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    data = await state.get_data()
    await state.clear()

    photos = data.get("photos", [])
    description = data.get("description", "")
    phone = data.get("phone", "")

    # ------- Сохраняем в базу -------
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO repair_requests (description, phone, photo_url)
            VALUES (?, ?, ?)
        """, (description, phone, json.dumps(photos)))
        conn.commit()
        conn.close()
    except Exception as e:
        print("DB Error:", e)
        await message.answer("⚠️ Ошибка при сохранении заявки. Попробуйте позже.")
        return

    # ------- Отправляем админу -------
    caption = (
        "🧰 *Новая заявка на ремонт*\n\n"
        f"📝 Описание:\n{description}\n\n"
        f"📞 Телефон: {phone}"
    )

    try:
        if photos:
            await message.bot.send_photo(
                ADMIN_ID,
                photos[0],
                caption=caption,
                parse_mode="Markdown"
            )
        else:
            await message.bot.send_message(ADMIN_ID, caption, parse_mode="Markdown")
    except Exception as e:
        print("Admin notify error:", e)

    await message.answer("✅ Заявка отправлена.\nАдминистратор свяжется с вами в ближайшее время.")
