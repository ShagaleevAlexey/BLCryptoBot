import logging

from app import config, logger
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from app.__services__.bittrex import Bittrex

class App(object):
    bot_updater = None  #type: Updater
    _history = {}

    def __init__(self, params: dict=None):
        self.bot_updater = Updater(config.BOT_TOKEN)

        self.configurate()

        self.bot_updater.start_polling()
        self.bot_updater.idle()

    def configurate(self):
        dp = self.bot_updater.dispatcher

        dp.add_handler(CommandHandler("start", self.command_start))
        dp.add_handler(CommandHandler("get_price", self.command_get_price, pass_args=True))

    def command_start(self, bot, update):
        if update is None or update.message is None:
            return

        uid = update.message.chat.username
        text = update.message.text

        if text is None or len(text) == 0:
            return

        if uid not in self._history:
            self._history[uid] = []

        self._history[uid].append(dict(
            text=text,
        ))

        update.message.reply_text('Start!')

    def command_get_price(self, bot, update, args):
        if update is None or update.message is None:
            return

        if len(args) != 1:
            update.message.reply_text('I need one parameter!!! FUCK!\nExample: /get_price BTC')
            return

        need_currency_name = str(args[0]).lower()
        bittrex = Bittrex()

        result = bittrex.get_markets()

        if not result['success']:
            update.message.reply_text('Error!!!')
            return

        markets = result['result']
        usdt_markets = [r for r in markets if r['BaseCurrency'] == 'USDT']

        for market in usdt_markets:
            currency_name = str(market.get('MarketCurrency', '')).lower()
            long_currency_name = str(market.get('MarketCurrencyLong', '')).lower()

            if currency_name == need_currency_name or long_currency_name == need_currency_name:
                market_name = market.get('MarketName', '')

                result = bittrex.get_marketsummary(market_name)

                if not result['success']:
                    return

                summary = result['result'][0]
                last = summary.get('Last')

                if last:
                    update.message.reply_text(f'1 {currency_name.upper()} = {last} USDT')
                else:
                    update.message.reply_text('Error!!!')

                break
        # update.message.reply_text('Start!')
