import logging
import traceback
from importlib import import_module

from bot.commands import help_command
from bot.commands import start_command
from bot.models import User
from data.storage.storage import StorageMixin
from telegram.bot_api import BotApi


class EvernoteBot(StorageMixin):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        telegram_token = config['telegram']['token']
        self.api = BotApi(telegram_token)

    def handle_telegram_update(self, telegram_update):
        try:
            command_name = telegram_update.get_command()
            if command_name:
                self.execute_command(command_name, telegram_update)
                return
            message = telegram_update.message or telegram_update.edited_message
            if message:
                self.handle_message(message)
            post = telegram_update.channel_post or telegram_update.edited_channel_post
            if post:
                self.handle_post(post)
        except Exception as e:
            chat_id = telegram_update.message.chat.id
            error_message = '\u274c Error. {0}'.format(e)
            self.api.sendMessage(chat_id, error_message)
            logging.getLogger().error(traceback.format_exc())


    def execute_command(self, name, telegram_update):
        if name == 'help':
            return help_command(self, telegram_update.message.chat.id)
        elif name == 'start':
            return start_command(self, telegram_update.message)
        else:
            raise Exception('Unknown command "{}"'.format(name))

    def handle_message(self, message):
        user_id = message.from_user.id
        user = self.get_storage(User).get(user_id)
        if not user:
            raise Exception('Unregistered user {0}'.format(user_id))

    def handle_post(self, post):
        # TODO:
        pass

    def _register_user(self, telegram_message):
        telegram_user = telegram_message.from_user
        user_data = {
            'id': telegram_user.id,
            'bot_mode': 'multiple_notes',
            'telegram': {
                'first_name': telegram_user.first_name,
                'last_name': telegram_user.last_name,
                'username': telegram_user.username,
                'chat_id': telegram_message.chat.id,
            }
        }
        user = self.get_storage(User).create_model(user_data)
        user.save()
        return user
