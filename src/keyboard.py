from types import SimpleNamespace

import emoji
from telebot import types


def create_keybaord(*keys, row_width=2, resize_keyboard=True):
    """
    create a keybord from list of keys
    """
    markup = types.ReplyKeyboardMarkup(row_width=row_width , resize_keyboard=resize_keyboard)
    
    keys = map(emoji.emojize, keys)
    buttons = map(types.KeyboardButton , keys)
    markup.add(*buttons)

    return markup

keys = SimpleNamespace(
    random_connect=':bust_in_silhouette: random connect',
    settings=':gear: settings',
    exit=':cross_mark: exit',
)

states = SimpleNamespace(
    random_connect='RANDOM_CONNECT',
    main='MAIN',
    connected='connected',
)


keyboards = SimpleNamespace(
    main=create_keybaord(keys.random_connect, keys.settings),
    exit=create_keybaord(keys.exit, keys.settings),
)
