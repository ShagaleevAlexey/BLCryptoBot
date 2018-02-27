import logging

from app import config, logger
import telegram
# from telegram import ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
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

kButtonCreateVote = 10
kButtonCreateSimpleVote = 11

localization_buttons = {
    kButtonCreateVote   : '✍ Создать голосование',
    kButtonCreateSimpleVote   : '🔥 Случайное голосование'
}

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

        dp.add_handler(CommandHandler("help", self.command_help))
        dp.add_handler(CommandHandler("start", self.command_start))

        dp.add_handler(CommandHandler("create_vote", self.command_start))
        dp.add_handler(MessageHandler(Filters.text, self.command_echo))
        dp.add_handler(CommandHandler("done", self.command_done))
        dp.add_handler(CallbackQueryHandler(self.command_button))

    def command_help(self, bot, update: Update):
        keyboard = [[KeyboardButton(localization_buttons[kButtonCreateVote], callback_data='callback_data', resize_keyboard=True)],
                    [KeyboardButton(localization_buttons[kButtonCreateSimpleVote], callback_data='2', resize_keyboard=True)]]

        # reply_markup = InlineKeyboardMarkup(keyboard)
        reply_markup = ReplyKeyboardMarkup(keyboard)

        message: Message = update.message
        message.reply_text('Выбери что ты хочешь сделать 👇', reply_markup=reply_markup)

    def command_start(self, bot, update: Update):
        self.command_help()


    def command_create_vote(self, bot, update: Update):
        if update is None or update.message is None:
            return

        if update.effective_user is None:
            return

        owner_id = update.effective_user.id
        vote = voting.Vote(owner_id)

        self.votes.append(vote)

        update.message.reply_text(localization[kLetsCreatePoll], reply_markup=ReplyKeyboardRemove())

    def command_echo(self, bot, update: Update):
        if update is None or update.message is None:
            return

        if update.effective_user is None:
            return

        if update.message.text == localization_buttons[kButtonCreateVote]:
            self.command_create_vote(bot, update)
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

        actual_answers = vote.actual_info_message()

        message.reply_text(f'*{vote.question.text}*\n\n{answers}', parse_mode=telegram.ParseMode.MARKDOWN)

        keyboard = [
            [InlineKeyboardButton('Выслать голосование', callback_data='1', switch_inline_query_current_chat='siqcc')]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('Please choose:', reply_markup=reply_markup)

    def command_button(self, bot, update: Update):
        query = update.callback_query

        pass
