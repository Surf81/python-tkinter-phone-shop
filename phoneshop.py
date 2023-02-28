# Настройки проекта
from main.router import Router
from main.settingloader import PhoneShopSettings
from main.core import PhoneShop, MainMenu
from main.settings import DATABASE, SETTINGS_FILE
from phoneshop.db.db import DB
from phoneshop.db.loadbase import load_phone_base
from phoneshop.shop.shopframe import ShopFrame



PHONE_SHOP_DB = DB(DATABASE['SQLITE'])
# Первичное наполнение базы данных
# load_phone_base()

browser = PhoneShop(PhoneShopSettings(SETTINGS_FILE))

shop_frame = ShopFrame(browser, PHONE_SHOP_DB)

router = Router(browser)
router.register_rout("shop", shop_frame.run)
router.register_rout("quit", browser.destroy)
# browser.add_router(router)

mainmenu = MainMenu(browser, router)
browser.add_menu(mainmenu.create_menu())

browser.run()