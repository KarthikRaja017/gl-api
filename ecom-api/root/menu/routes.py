from root.menu.models import AddMenu, DeleteMenu, GetMenu
from . import menu_api

menu_api.add_resource(AddMenu, "/add/menu")
menu_api.add_resource(GetMenu, "/get/menus")
menu_api.add_resource(DeleteMenu, "/delete/menu")
