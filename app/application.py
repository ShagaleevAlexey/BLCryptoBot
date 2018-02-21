import logging

from app import config, logger
import telegram
# from telegram import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.update import Update
from telegram.user import User
from telegram.message import Message
from app.__services__.bittrex import Bittrex

from app import voting

kLetsCreatePoll = 10
kFirstAnswer    = 11
kSecondAnswer   = 12
kUniqueAnswer   = 13

kFinishCreate   = 19

kError0         = 50


localization = {
    kLetsCreatePoll : 'Давайте создадим новое голосование. Введите ваш вопрос.', 
    kFirstAnswer    : 'Введите первый вариант ответа: ',
    kSecondAnswer   : 'Введите второй вариант ответа: ',
    kUniqueAnswer   : 'Введите следующий вариант ответа или /done',
    kError0         : 'Сначала нужно добавить варианты ответов!',
    kFinishCreate   : '👍 Голосование создано! Вы можете им поделиться с группой или с друзьями.'
}

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
        dp.add_handler(CommandHandler("done", self.command_done))

    def command_start(self, bot, update: Update):
        if update is None or update.message is None:
            return

        if update.effective_user is None:
            return

        owner_id = update.effective_user.id
        vote = voting.Vote(owner_id)

        self.votes.append(vote)

        update.message.reply_text(localization[kLetsCreatePoll])

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

        update.message.reply_text(localization[kFirstAnswer])

    def stage_add_answer(self, bot, update: Update, vote: voting.Vote):
        message = update.message

        if message is None or message.text is None:
            return

        vote.add_answer(message.text)

        if len(vote.answers) == 0:
            update.message.reply_text(localization[kFirstAnswer])
        else:
            if len(vote.answers) == 1:
                update.message.reply_text(localization[kSecondAnswer])
            else:
                if len(vote.answers) > 1:
                    update.message.reply_text(localization[kUniqueAnswer])

    def command_done(self, bot, update: Update):
        if update is None or update.message is None:
            return

        if update.effective_user is None:
            return

        owner_id = update.effective_user.id

        votes = [vote for vote in self.votes if vote.owner_id == owner_id]

        if len(votes) == 0:
            return

        vote = votes[-1]

        if len(vote.answers) == 0:
            update.message.reply_text(localization[kError0])
            return

        message: Message = update.message

        message.reply_text(localization[kFinishCreate])

        vote.vote_stage = voting.eVoteStageCreated

        answers = '\n▫️ 0%\n\n'.join([a.text for a in vote.answers]) + '\n▫️ 0%\n\n'

        message.reply_text(f'*{vote.question.text}*\n\n{answers}', parse_mode=telegram.ParseMode.MARKDOWN)
