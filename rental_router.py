# rental_router.py
import asyncio
from datetime import date
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from database import (
    p2p_add_item,
    p2p_get_items,
    p2p_get_my_items,
    p2p_add_request,
)
from config import ADMIN_ID
from fsm.p2p_states import P2PAddFSM, P2PRequestFSM

rental_router = Router()

# -------------------- ОСНОВНОЕ МЕНЮ --------------------
@rental_router.message(F.text == "🚗 Аренда")
async def rental_menu(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Аренда от магазина"), KeyboardButton(text="🤝 P2P аренда")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("🚗 Раздел аренды — выберите действие:", reply_markup=kb)


# -------------------- P2P МЕНЮ --------------------
@rental_router.message(F.text == "🤝 P2P аренда")
async def p2p_menu(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📤 Сдать оборудование"), KeyboardButton(text="🔍 Найти оборудование")],
            [KeyboardButton(text="🗂 Мои P2P объявления"), KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("🤝 P2P аренда — выберите действие:", reply_markup=kb)


# -------------------- ДОБАВЛЕНИЕ P2P ОБЪЯВЛЕНИЯ --------------------
@rental_router.message(F.text == "📤 Сдать оборудование")
async def p2p_add_start(message: types.Message, state: FSMContext):
    await state.set_state(P2PAddFSM.waiting_category)
    await message.answer(
        "🗂 Введите категорию оборудования.\n"
        "Например: автобокс, багажник, велокрепление."
    )


@rental_router.message(P2PAddFSM.waiting_category)
async def p2p_add_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text.strip())
    await state.set_state(P2PAddFSM.waiting_title)
    await message.answer("📝 Укажите название / модель.")


@rental_router.message(P2PAddFSM.waiting_title)
async def p2p_add_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(P2PAddFSM.waiting_description)
    await message.answer("📄 Напишите описание состояния и комплектации.")


@rental_router.message(P2PAddFSM.waiting_description)
async def p2p_add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(P2PAddFSM.waiting_price)
    await message.answer("💰 Укажите цену аренды в сутки (руб).")


@rental_router.message(P2PAddFSM.waiting_price)
async def p2p_add_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "."))
    except ValueError:
        return await message.answer("⚠️ Укажите цену числом!")

    await state.update_data(price=price)
    await state.set_state(P2PAddFSM.waiting_city)
    await message.answer("📍 Укажите город.")


@rental_router.message(P2PAddFSM.waiting_city)
async def p2p_add_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text.strip())
    await state.set_state(P2PAddFSM.waiting_district)
    await message.answer("🏙 Укажите район / округ.")


@rental_router.message(P2PAddFSM.waiting_district)
async def p2p_add_district(message: types.Message, state: FSMContext):
    await state.update_data(district=message.text.strip())
    await state.set_state(P2PAddFSM.waiting_geo_choice)
    await message.answer("📌 Хотите указать точку на карте?\n"
                         "Отправьте геолокацию или напишите «Пропустить».")


@rental_router.message(P2PAddFSM.waiting_geo_choice, F.location)
async def p2p_add_geo(message: types.Message, state: FSMContext):
    await state.update_data(
        latitude=message.location.latitude,
        longitude=message.location.longitude,
    )
    await state.set_state(P2PAddFSM.waiting_photos)
    await message.answer("📸 Пришлите до 5 фото. Когда закончите — «Готово».") 


@rental_router.message(P2PAddFSM.waiting_geo_choice, F.text.casefold() == "пропустить")
async def p2p_skip_geo(message: types.Message, state: FSMContext):
    await state.update_data(latitude=None, longitude=None)
    await state.set_state(P2PAddFSM.waiting_photos)
    await message.answer("📸 Пришлите до 5 фото. Когда закончите — «Готово».") 


@rental_router.message(P2PAddFSM.waiting_photos, F.photo)
async def p2p_collect_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    if len(photos) >= 5:
        return await message.answer("⚠️ Можно максимум 5 фото. Напишите «Готово».")
    
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

    await message.answer(f"Фото добавлено ({len(photos)}/5).")


@rental_router.message(P2PAddFSM.waiting_photos, F.text.casefold() == "готово")
async def p2p_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    item_id = p2p_add_item(
        owner_id=message.from_user.id,
        category=data["category"],
        title=data["title"],
        description=data["description"],
        price_per_day=data["price"],
        city=data["city"],
        district=data["district"],
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
    )

    await message.answer(
        f"✅ Оборудование добавлено в P2P!\n"
        f"ID объявления: {item_id}\n"
        f"{data['title']} — {data['price']} ₽/сутки"
    )

    # уведомление администратору
    owner = message.from_user
    link = f"@{owner.username}" if owner.username else f"tg://user?id={owner.id}"

    await message.bot.send_message(
        ADMIN_ID,
        f"🤝 *Новое P2P объявление*\n\n"
        f"ID: {item_id}\n"
        f"Владелец: {link}\n"
        f"{data['title']} — {data['price']} ₽/сутки\n"
        f"{data['city']}, {data['district']}",
        parse_mode="Markdown",
    )


# -------------------- МОИ ОБЪЯВЛЕНИЯ --------------------
@rental_router.message(F.text == "🗂 Мои P2P объявления")
async def p2p_my_items(message: types.Message):
    items = p2p_get_my_items(message.from_user.id)

    if not items:
        return await message.answer("У вас нет активных объявлений.")

    for item in items:
        await message.answer(
            f"📦 *{item['title']}*\n"
            f"{item['description']}\n\n"
            f"💰 {item['price_per_day']} ₽/сутки\n"
            f"📍 {item['city']}, {item['district']}\n"
            f"ID: {item['id']}",
            parse_mode="Markdown",
        )
        await asyncio.sleep(0.2)


# -------------------- ПОИСК ОБОРУДОВАНИЯ --------------------
@rental_router.message(F.text == "🔍 Найти оборудование")
async def p2p_search(message: types.Message, state: FSMContext):
    await state.set_state(P2PRequestFSM.waiting_city)
    await message.answer("Введите город для поиска.")


@rental_router.message(P2PRequestFSM.waiting_city)
async def p2p_search_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text.strip())
    await state.set_state(P2PRequestFSM.waiting_district)
    await message.answer("Укажите район или «Любой».")
