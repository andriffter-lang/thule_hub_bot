import asyncio
import logging
import json
from aiogram import types, F
from aiogram import Bot, Dispatcher, F, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# 🔧 Глобальные настройки
BOT_TOKEN = "8444074524:AAE9u8KIpkVynFihXeqjHnorMvgF7xGeKdk"
ADMIN_ID = 230325201

# 🔧 Импортируем роутеры
from shop_router import shop_router, shop_menu
from rental_router import rental_router, rental_menu
from market_router import market_router
from repair_router import repair_router
from admin_router import admin_router

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =======================================================
#                 ИНИЦИАЛИЗАЦИЯ БОТА
# =======================================================

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# =======================================================
#                 ГЛАВНОЕ МЕНЮ
# =======================================================

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

def main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🏪 Магазин"), KeyboardButton(text="🚗 Аренда")],
        [KeyboardButton(text="📦 Рынок оборудования Thule"), KeyboardButton(text="🧰 Ремонт")],
        [KeyboardButton(text="❓ FAQ"), KeyboardButton(text="💬 Сообщество")],
    ]

    # 🔹 Кнопка Mini App
    webapp_button = KeyboardButton(
        text="🌐 Mini App",
        web_app=WebAppInfo(
            url="https://andriffter-lang.github.io/thule_hub_bot/"   # ← заменишь на свой GitHub Pages URL
        ),
    )

    rows.append([webapp_button])

    if is_admin:
        rows.append([KeyboardButton(text="⚙️ Админ-панель")])

    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


# =======================================================
#                ОБРАБОТЧИК /start
# =======================================================

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в Thule Hub!\n"
        "Здесь вы можете купить, арендовать или разместить оборудование Thule, "
        "оформить ремонт и общаться с сообществом.",
        reply_markup=main_menu(is_admin=(message.from_user.id == ADMIN_ID)),
    )


# =======================================================
#                ОБРАБОТЧИК НАЗАД
# =======================================================

@dp.message(F.text == "⬅️ Назад")
async def back_to_main(message: types.Message):
    await message.answer(
        "🔙 Главное меню",
        reply_markup=main_menu(is_admin=(message.from_user.id == ADMIN_ID)),
    )
import json

@dp.message(F.web_app_data)
async def webapp_data_handler(message: types.Message):
    """
    Обработка данных, которые отправляет React Mini App через WebApp.sendData()
    """
    raw_data = message.web_app_data.data

    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError:
        await message.answer("❗ Не удалось обработать данные из Mini App")
        return

    # 👉 ВАЖНО: мини-апп шлёт type, а не action
    msg_type = data.get("type")
    section = data.get("section")

    # На будущее — если захочешь другие типы сообщений
    if msg_type != "open_section":
        await message.answer(f"📨 Данные из Mini App: {data}")
        return

    # 🔹 Маршрутизация по разделам
    if section == "shop":
        await shop_menu(message)          # вызываем настоящее меню магазина

    elif section == "rental":
        await rental_menu(message)        # вызываем меню аренды

    elif section == "market":
        await message.answer("📦 Открываю рынок оборудования…")

    elif section == "repair":
        await message.answer("🧰 Открываю ремонт…")

    elif section == "faq":
        await message.answer("❓ Открываю FAQ…")

    elif section == "community":
        await message.answer("💬 Открываю сообщество…")

    elif section == "admin":
        await message.answer("⚙️ Открываю админ-панель…")

    else:
        await message.answer(f"🤔 Неизвестный раздел из Mini App: {section}")

        return

    await message.answer(f"📨 Данные из Mini App: {data}")

# =======================================================
#                ПОДКЛЮЧЕНИЕ ROUTERS
# =======================================================
@dp.message(F.web_app_data)
async def debug_webapp(message: types.Message):
    await message.answer("DEBUG:\n" + str(message.web_app_data.data))

dp.include_router(shop_router)
dp.include_router(rental_router)
dp.include_router(market_router)
dp.include_router(repair_router)
dp.include_router(admin_router)


# =======================================================
#                    ЗАПУСК БОТА
# =======================================================

async def main():
    logger.info("🚀 Бот запущен и ожидает события...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

            