# -*- coding: utf-8 -*-


import sys
import logging
import telegram
from collections import defaultdict, Counter

from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
    Message,
    ParseMode,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)


kartinka = r'''<code>
           ___
    ,_    '---'    _,
    \ `-._|\_/|_.-' /
     |   =)'T'(=   |
      \   /`"`\   /
hello, '._\) (/_.'   wanna
user       | |       know
this      /\ /\      the
is        \ T /      rules?
word      (/ \)\ 
in word        ))
game          ((
               \)
</code>'''
kartinka1 = '~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

#kartinka = '<3'
logger = logging.getLogger(__name__)
MAIN = 0
GAME = 1
ASKWORD = 2
CHOICE = 3
FINISH = 4


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(kartinka, parse_mode=telegram.ParseMode.HTML)
    start_button(update, context)
    return MAIN


def start_button(update: Update, context: CallbackContext):
    context.user_data['hey'] = update.message.reply_text(
        kartinka1,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Начать игру', callback_data='1')]]
        ),
    )


def start_game(update: Update, context: CallbackContext):
    ud = context.user_data
    (ud['hey'].edit_text if ud.get('edit', True) else ud['hey'].reply_text)(
        kartinka1,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Ввести слово', callback_data='2')]]
        ),
    )
    return CHOICE


def ask_word(update: Update, context: CallbackContext):
    return ASKWORD


def askword(update: Update, context: CallbackContext):
    logger.info('Word has been written.')
    s = update.message.text.lower()
    context.user_data['word'] = Counter(s)
    context.user_data['words'] = set()
    context.job_queue.run_once(callback_300, 10, context=context.user_data)
    update.message.reply_text('удачи до дачи')
    return GAME


def is_okay(update: Update, context: CallbackContext):
    s = update.message.text.lower()
    for elem in Counter(s):
        if elem not in context.user_data['word'] or context.user_data['word'][elem] < Counter(s)[elem]:
            return
    context.user_data['words'].add(s)
    return


def callback_300(context: CallbackContext):
    context.job.context['hey'].reply_text(
        'Результат: ' + str(len(context.job.context['words'])),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Новая игра', callback_data='3')]]
        ),
    )
    context.job.context['edit'] = False


def main():
    updater = Updater(token=sys.argv[1])
    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            MAIN: [CallbackQueryHandler(start_game, pattern='1')],

            CHOICE: [CallbackQueryHandler(ask_word, pattern='2')],

            ASKWORD: [MessageHandler(Filters.text, askword)],

            GAME: [CallbackQueryHandler(start_game, pattern='3'), MessageHandler(Filters.text, is_okay)]
        },

        fallbacks=[]
    )

    dispatcher.add_handler(conversation_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
