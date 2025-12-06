from aiogram.fsm.state import StatesGroup, State


# ====== P2P: Добавление оборудования ======
class P2PAddFSM(StatesGroup):
    waiting_category = State()
    waiting_title = State()
    waiting_description = State()
    waiting_price = State()
    waiting_city = State()
    waiting_district = State()
    waiting_geo_choice = State()
    waiting_photos = State()


# ====== P2P: Поиск и аренда ======
class P2PRequestFSM(StatesGroup):
    waiting_city = State()
    waiting_district = State()
    choosing_item = State()
    choosing_dates = State()
