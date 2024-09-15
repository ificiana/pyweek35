from time import sleep
from typing import Union

import arcade.gui
from pyglet.math import Vec2

import assets

item_functionality = {
    "knife": "equip",
    "torch": "equip",
    "letter": "read",
    "key": "use",
}


class Door(arcade.Sprite):
    def __init__(self, sprite_file: str, pos: Vec2, angle: float, name_color: str):
        super().__init__(assets.sprites.resolve(sprite_file))
        self.name, self.item_color = name_color.split("-")
        self.center_x, self.center_y = pos
        self.angle = angle

    def try_open(self, key: "Item", game):
        if key is not None and key.name == "key" and key.item_color == self.item_color:
            self.kill()
        else:
            game.player.game_view.set_display_text(f"You need a {self.item_color} key")
            sleep(3)
            game.player.game_view.set_display_text("")


class Item(arcade.Sprite):
    def __init__(
        self, sprite_file: str, pos: Vec2, angle: float, name_color: str = None
    ):
        super().__init__(assets.items.resolve(sprite_file))
        # self.name, self.item_color = name_color.split("_")
        self.center_x, self.center_y = pos
        self.angle = angle
        # self.functionality = item_functionality[self.name]

    # pylint: disable=E1101
    def use(self, game: arcade.View):
        # TODO : Replace with Match Case
        if self.functionality == "equip":
            game.player.holding_item = self
        elif self.functionality == "read":
            # TODO Display the letter on screen
            pass
        elif self.name == "key":
            game.player.near_door.try_open(self, game)

    def get_position(self):
        return Vec2(self.center_x, self.center_y)


class Inventory:
    def __init__(self):
        self.items = {}
        self.quantities = {}

    def add_item(self, item: Item):
        self.items[item.name] = item
        self.quantities[item.name] = self.quantities.get(item.name, 0) + 1
        item.remove_from_sprite_lists()
        print(f"added {item.name} to the inventory")

    def remove_item(self, item_name):
        self.quantities[item_name] = max(self.quantities.get(item_name, 0) - 1, 0)
        if self.quantities[item_name] == 0:
            return self.items.pop(item_name)
        return self.items[item_name]

    def clear(self):
        self.items.clear()
        self.quantities.clear()


def get_inventory_ui(
    window: arcade.Window,
) -> Union[arcade.gui.UIWidget, list[arcade.gui.UIWidget]]:
    text_area0 = arcade.gui.UITextArea(
        x=270,
        y=220,
        width=600,
        height=300,
        text="INVENTORY",
        text_color=arcade.csscolor.WHITE,
        font_size=30,
        font_name="Melted Monster",
    )
    text_area = arcade.gui.UITextArea(
        x=195,
        y=200,
        width=600,
        height=250,
        text="Press ESC to return to Game",
        text_color=arcade.csscolor.WHITE,
        font_size=18,
    )
    no_item = arcade.gui.UITextArea(
        x=0,
        y=220,
        width=600,
        height=80,
        text="Inventory is empty.",
        text_color=arcade.csscolor.WHITE,
        font_size=43,
        font_name="Melted Monster",
    )

    inventory: Inventory = window.inventory
    items_view = arcade.gui.UIBoxLayout(vertical=True)
    if inventory.items:
        for item in inventory.items:
            item_view = arcade.gui.UISpriteWidget(
                x=10, y=200, width=120, height=120, sprite=inventory.items[item]
            )
            v_box = arcade.gui.UIBoxLayout(vertical=True)
            h_box = arcade.gui.UIBoxLayout(vertical=False, space_between=100)

            use_button = arcade.gui.UIFlatButton(
                text=inventory.items[item].functionality.upper(), width=80
            )
            v_box.add(use_button.with_space_around(bottom=10))

            drop_button = arcade.gui.UIFlatButton(text="DROP", width=80)
            v_box.add(drop_button.with_space_around(bottom=30))

            item_name = arcade.gui.UITextArea(
                x=0,
                y=0,
                width=100,
                height=80,
                text=inventory.items[item].name,
                text_color=arcade.csscolor.WHITE,
                font_size=30,
                font_name="Melted Monster",
            )

            h_box.add(item_view)
            h_box.add(item_name)
            h_box.add(v_box)
            items_view.add(h_box)

            # pylint: disable=W0640
            # noinspection PyUnusedLocal
            @use_button.event("on_click")
            def on_click_use(event):
                assets.sounds.click.play()
                inventory.items[item].use(window)

            # pylint: disable=W0640
            # noinspection PyUnusedLocal
            @drop_button.event("on_click")
            def on_click_drop(event):
                assets.sounds.click.play()

    return [
        arcade.gui.UIAnchorWidget(
            anchor_x="left",
            anchor_y="center",
            align_x=100,
            align_y=-50,
            child=items_view if inventory.items else no_item,
        ),
        text_area0,
        text_area,
    ]
