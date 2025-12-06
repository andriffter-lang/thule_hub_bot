# admin_router.py
import json
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
from database import (
    get_products,
    find_product_by_id,
    delete_product,
    update_product,
    p2p_get_items,
)

admin_router = Router()


# ========= ЗАЩИТА =========
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ========= ГЛАВНОЕ МЕНЮ АДМИНА =========
@admin_router.message(F.text == "⚙️ Админ-панель")
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("🚫 У вас нет доступа.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Товары магазина", callback_data="adm_products")],
        [InlineKeyboardButton(text="📦 Объявления рынка", callback_data="adm_market_ads")],
        [InlineKeyboardButton(text="🤝 P2P объявления", callback_data="adm_p2p")],
        [InlineKeyboardButton(text="🧰 Заявки на ремонт", callback_data="adm_repairs")],
        [InlineKeyboardButton(text="❓ Справка", callback_data="adm_help")],
    ])

    await message.answer("⚙️ *Панель администратора*", parse_mode="Markdown", reply_markup=kb)


# ========= СПИСОК ТОВАРОВ МАГАЗИНА =========
@admin_router.callback_query(F.data == "adm_products")
async def adm_products(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)

    items = get_products(None)
    if not items:
        await callback.message.answer("📦 Товаров в магазине пока нет.")
        return await callback.answer()

    for p in items:
        text = (
            f"🆔 ID: {p['id']}\n"
            f"Категория: {p['category']}\n"
            f"Название: *{p['name']}*\n"
            f"Цена: {p['price']} ₽"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"adm_edit:{p['id']}")],
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"adm_delete:{p['id']}")],
        ])

        photos = []
        try:
            if p.get("photos"):
                photos = json.loads(p["photos"])
        except:
            pass

        if photos:
            await callback.message.answer_photo(photos[0], caption=text, parse_mode="Markdown", reply_markup=kb)
        else:
            await callback.message.answer(text, parse_mode="Markdown", reply_markup=kb)

    await callback.answer()


# ========= УДАЛЕНИЕ ТОВАРА =========
@admin_router.callback_query(F.data.startswith("adm_delete:"))
async def adm_delete(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)

    product_id = int(callback.data.split(":")[1])
    delete_product(product_id)

    await callback.message.answer(f"🗑 Товар ID {product_id} удалён.")
    await callback.answer("Удалено")


# ========= РЕДАКТИРОВАНИЕ ТОВАРА =========
class EditState:
    waiting_new_name = {}
    waiting_new_price = {}
    waiting_new_description = {}
    waiting_new_photos = {}


@admin_router.callback_query(F.data.startswith("adm_edit:"))
async def adm_edit(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)

    product_id = int(callback.data.split(":")[1])
    product = find_product_by_id(product_id)

    if not product:
        return await callback.answer("Товар не найден")

    EditState.waiting_new_name[callback.from_user.id] = product_id

    await callback.message.answer(
        f"✏️ *Редактирование товара ID {product_id}.*\n"
        f"Текущее название: *{product['name']}*\n\n"
        "Введите новое название:",
        parse_mode="Markdown"
    )
    await callback.answer()


@admin_router.message(lambda msg: msg.from_user.id in EditState.waiting_new_name)
async def edit_name(message: types.Message):
    admin = message.from_user.id
    product_id = EditState.waiting_new_name.pop(admin)
    new_name = message.text

    update_product(product_id, name=new_name)
    await message.answer(f"Название обновлено: *{new_name}*", parse_mode="Markdown")

    EditState.waiting_new_price[admin] = product_id
    await message.answer("Введите новую цену:")


@admin_router.message(lambda msg: msg.from_user.id in EditState.waiting_new_price)
async def edit_price(message: types.Message):
    admin = message.from_user.id
    product_id = EditState.waiting_new_price.pop(admin)

    try:
        price = float(message.text.replace(",", "."))
    except ValueError:
        return await message.answer("⚠️ Введите корректное число.")

    update_product(product_id, price=price)
    await message.answer(f"Цена обновлена: {price} ₽")

    EditState.waiting_new_description[admin] = product_id
    await message.answer("Введите новое описание товара:")


@admin_router.message(lambda msg: msg.from_user.id in EditState.waiting_new_description)
async def edit_description(message: types.Message):
    admin = message.from_user.id
    product_id = EditState.waiting_new_description.pop(admin)

    new_desc = message.text
    update_product(product_id, description=new_desc)

    await message.answer("Описание обновлено.")

    EditState.waiting_new_photos[admin] = product_id
    await message.answer(
        "📸 Теперь отправьте *новые фото* товара (1–5 шт.)\n"
        "Когда закончите — напишите «Готово».",
        parse_mode="Markdown"
    )


@admin_router.message(lambda msg: msg.from_user.id in EditState.waiting_new_photos, F.photo)
async def edit_photos_collect(message: types.Message):
    admin = message.from_user.id
    product_id = EditState.waiting_new_photos[admin]

    # временный список фото
    if not hasattr(EditState, "photos_buffer"):
        EditState.photos_buffer = {}

    photos = EditState.photos_buffer.get(admin, [])
    if len(photos) >= 5:
        return await message.answer("Максимум 5 фото.")

    photos.append(message.photo[-1].file_id)
    EditState.photos_buffer[admin] = photos

    await message.answer(f"Фото добавлено ({len(photos)}/5).")


@admin_router.message(lambda msg: msg.from_user.id in EditState.waiting_new_photos, F.text.casefold() == "готово")
async def edit_photos_finish(message: types.Message):
    admin = message.from_user.id
    product_id = EditState.waiting_new_photos.pop(admin)

    photos = EditState.photos_buffer.pop(admin, [])

    update_product(product_id, photos=json.dumps(photos))

    await message.answer("📸 Фото обновлены. Редактирование завершено!")


# ========= ОБЪЯВЛЕНИЯ РЫНКА =========
@admin_router.callback_query(F.data == "adm_market_ads")
async def adm_market_ads(callback: types.CallbackQuery):
    await callback.message.answer("📦 Управление объявлениями рынка Thule появится позже.")
    await callback.answer()


# ========= P2P =========
@admin_router.callback_query(F.data == "adm_p2p")
async def adm_p2p_list(callback: types.CallbackQuery):
    items = p2p_get_items(city=None, district=None)

    if not items:
        await callback.message.answer("🤝 P2P объявлений пока нет.")
        return await callback.answer()

    txt = "🤝 *Список P2P объявлений:*\n\n"
    for it in items:
        txt += f"ID {it['id']} — {it['title']} — {it['city']}/{it['district']}\n"

    await callback.message.answer(txt, parse_mode="Markdown")
    await callback.answer()


# ========= РЕМОНТНЫЕ ЗАЯВКИ =========
@admin_router.callback_query(F.data == "adm_repairs")
async def adm_repairs(callback: types.CallbackQuery):
    await callback.message.answer("🧰 Управление ремонтными заявками появится позже.")
    await callback.answer()


# ========= СПРАВКА =========
@admin_router.callback_query(F.data == "adm_help")
async def adm_help(callback: types.CallbackQuery):
    txt = (
        "ℹ️ *Раздел помощи администратора*\n\n"
        "Доступные функции:\n"
        "• управление товарами\n"
        "• удаление и редактирование\n"
        "• контроль рынка Thule\n"
        "• обработка P2P\n"
        "• просмотр ремонтов\n\n"
        "Скоро появится больше функций."
    )
    await callback.message.answer(txt, parse_mode="Markdown")
    await callback.answer()
