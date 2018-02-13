import logging

from app import config, logger
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.update import Update
from telegram.user import User
from app.__services__.bittrex import Bittrex

from app import voting

class App(object):
    bot_updater = None  #type: Updater
    votes = []

    def __init__(self, params: dict=None):
        self.bot_updater = Updater(config.BOT_TOKEN)

        self.configurate()

        self.bot_updater.start_polling()
        self.bot_updater.idle()

    def configurate(self):
        dp = self.bot_updater.dispatcher

        dp.add_handler(CommandHandler("start", self.command_start))
        dp.add_handler(CommandHandler("list", self.command_list))
        dp.add_handler(MessageHandler(Filters.text, self.command_echo))

    def command_start(self, bot, update: Update):
        if update is None or update.message is None:
            return

        if update.effective_user is None:
            return

        owner_id = update.effective_user.id
        vote = voting.Vote(owner_id)

        self.votes.append(vote)

        update.message.reply_text('Let\'s create a new poll. First, send me the question.')

    def command_list(self, bot, update: Update):
        if update is None or update.message is None:
            return

        if update.effective_user is None:
            return

        owner_id = update.effective_user.id

        votes = [vote for vote in self.votes if vote.owner_id == owner_id]

        if len(votes) == 0:
            return

        vote = votes[-1]

        update.message.reply_text('\n'.join([a.text for a in vote.answers]))

    def command_echo(self, bot, update: Update):
        if update is None or update.message is None:
            return

        if update.effective_user is None:
            return

        owner_id = update.effective_user.id

        votes = [vote for vote in self.votes if vote.owner_id == owner_id]

        if len(votes) == 0:
            return

        vote = votes[-1]

        if vote.vote_stage == voting.eVoteStageSetQuestion:
            self.stage_set_question(bot, update, vote)
        else:
            if vote.vote_stage == voting.eVoteStageAddAnswer:
                self.stage_add_answer(bot, update, vote)

    def stage_set_question(self, bot, update: Update, vote: voting.Vote):
        message = update.message

        if message is None or message.text is None:
            return

        vote.set_question(message.text)

        update.message.reply_text(f'Creating a new poll: \'{vote.question.text}\'\n\nPlease send me the first answer option.')

    def stage_add_answer(self, bot, update: Update, vote: voting.Vote):
        message = update.message

        if message is None or message.text is None:
            return

        vote.add_answer(message.text)
