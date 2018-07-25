import json
import logging
from datetime import datetime

from util.http import HTTPFound
from telegram.models import TelegramUpdate


def welcome(request):
    return b'Welcome!'


def telegram_hook(request):
    logger = logging.getLogger()
    logger.info('Telegram update: {}'.format(request.body))
    data = request.json()
    telegram_update = TelegramUpdate(data)
    bot = request.app.bot
    bot.handle_telegram_update(telegram_update)


def evernote_oauth(request):
    callback_key = request.GET['key']
    oauth_verifier = request.GET.get('oauth_verifier')
    bot = request.app.bot
    bot.oauth_callback(callback_key, oauth_verifier, access='basic')
    return HTTPFound(bot.url)


def error(request):
    raise Exception('Some application error')
