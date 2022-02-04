import os

import emoji
from telebot import telebot

from src.db import db
from src.keyboard import keyboards, keys, states


class Bot:
    """
    telegram bot to connect randomly to strangers... 
    """
    def __init__(self, mongodb):
        self.bot = telebot.TeleBot(os.environ['NASHENASBOT_TOKEN'], parse_mode='HTML')
        self.db = mongodb
        self.start = self.bot.message_handler(commands=['start'])(self.start)
        self.random_connect = self.bot.message_handler(regexp=emoji.emojize(keys.random_connect))(self.random_connect)
        self.exit = self.bot.message_handler(regexp=emoji.emojize(keys.exit))(self.exit)
        self.echo_all = self.bot.message_handler(func=lambda message: True)(self.echo_all)
        
    def run(self):
        print('started... ')
        self.bot.infinity_polling()

    def start(self, message):
        self.bot.send_message(message.chat.id, f"hi <strong>{message.chat.first_name}</strong>... ", reply_markup=keyboards.main)
        self.db.users.update_one({'chat.id' : message.chat.id}, {'$set' : message.json}, upsert=True)
        self.state_update(message.chat.id, states.main)


    def random_connect(self, message):
        self.bot.reply_to(message, "wait...", reply_markup=keyboards.exit)
        self.state_update(message.chat.id, states.random_connect)
        

        other_user = self.db.users.find_one(
            {   
                'state' : states.random_connect,
                'chat.id' : {'$ne' : message.chat.id}
            }
        )

        if not other_user:
             return

        # update other user state  
        self.state_update(other_user['chat']['id'], states.connected)
        self.bot.send_message(other_user['chat']['id'], f'Connected to {message.chat.id}...')
        # update curent user state  
        self.state_update(message.chat.id, states.connected)
        self.bot.send_message(message.chat.id, f'Connected to {other_user["chat"]["id"]}...')
        #store connected users 
        self.db.users.update_one(
            {"chat.id" : message.chat.id},
            {'$set' : {'connected_to' : other_user['chat']['id']}}
        )
        self.db.users.update_one(
            {"chat.id" : other_user['chat']['id']},
            {'$set' : {'connected_to' : message.chat.id}}
        )


    def echo_all(self, message):
        my_coll = self.db['users']
        user = my_coll.find_one({'chat.id' : message.chat.id})

        if ((not user) or (user['state'] != states.connected) or (user['connected_to'] is None)):
            return
        
        self.bot.send_message(user['connected_to'], message.text)


    def exit(self, message):
        self.bot.send_message(message.chat.id, emoji.emojize(keys.exit), reply_markup=keyboards.main)
        self.state_update(message.chat.id, states.main)

        connected_to = self.db.users.find_one({'chat.id' : message.chat.id})
        if not connected_to:
            return

        other_chat_id = connected_to['connected_to']

        self.state_update(other_chat_id, states.main)
        self.bot.send_message(other_chat_id, keys.exit, reply_markup=keyboards.main)

        # remove connected users
        self.db.users.update_one({'chat.id' : message.chat.id} , {'$set' : {'connected_to' : None}})
        self.db.users.update_one({'chat.id' : other_chat_id} , {'$set' : {'connected_to' : None}})


    def state_update(self, chat_id, state):
        self.db.users.update_one({'chat.id' : chat_id}, {'$set' : {'state' : state}})

tel_bot = Bot(mongodb=db)
tel_bot.run()
