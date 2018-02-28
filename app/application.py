import logging

from app import config, logger

from uuid import uuid4
import json

import telegram
# from telegram import ParseMode
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InlineQuery, InlineQueryResultArticle, InputMessageContent, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, InlineQueryHandler
from telegram.update import Update
from telegram.user import User
from telegram.message import Message, Chat
from telegram.bot import Bot
from telegram.utils.helpers import escape_markdown

from app import voting

kLetsCreatePoll = 10
kFirstAnswer    = 11
kSecondAnswer   = 12
kUniqueAnswer   = 13

kFinishCreate   = 19

kError0         = 500
kError1         = 501

kMainMenuState0 = 100
kVoteAccept     = 200

kButtonCreateVote = 10
kButtonCreateSimpleVote = 11

localization_buttons = {
    kButtonCreateVote   : '✍ Создать голосование',
    kButtonCreateSimpleVote   : '🔥 Случайное голосование'
}

localization = {
    kMainMenuState0 : 'Выбери что ты хочешь сделать 👇',
    kLetsCreatePoll : 'Давайте создадим новое голосование. Введите ваш вопрос.❔',
    kFirstAnswer    : 'Введите первый вариант ответа: ',
    kSecondAnswer   : 'Введите второй вариант ответа: ',
    kUniqueAnswer   : 'Введите следующий вариант ответа или /done',
    kError0         : 'Сначала нужно добавить варианты ответов!',
    kFinishCreate   : '👍 Голосование создано! Вы можете им поделиться с группой или с друзьями.',
    kError1         : 'Произошла ошибка транзакции. Обратитесь к разработчику: alexey.shagaleev@yandex.ru',
    kVoteAccept     : 'Ваш голос был учтен. Можете посмотреть свою транзакцию: [EtherScan]({url})'
}

kCommandTypeKey     = 'type'
kCommandTypeData    = 'data'
kCommandTypeParams    = 'params'

eCommandTypeNone    = ''
eCommandTypeCommand = 'command'
eCommandTypeVote    = 'vote'

class Command:
    type    :str = eCommandTypeNone
    command :str = ''
    params  :str = []

    # @staticmethod
    # def from_json(json: dict):

    def __init__(self, command):
        self.command = command
        self.type = ''
        self.params = []

    def dict(self):
        return {
            'type' : self.type,
            'data' : self.command
        }

    def json(self):
        return json.dumps(self.dict)


class App(object):
    bot_updater = None  #type: Updater
    votes = []

    _commands = {}

    def __init__(self, params: dict=None):
        self.bot_updater = Updater(config.BOT_TOKEN)

        self.configurate()

        self.bot_updater.start_polling()
        self.bot_updater.idle()

    def configurate(self):
        self._commands = {
            'start'         : self.command_help,
            'help'          : self.command_help,
            'create_vote'   : self.command_create_vote,
            'simple_vote'   : self.command_simple_vote,
            'done'          : self.command_done
        }

        dp = self.bot_updater.dispatcher

        for command in self._commands.keys():
            dp.add_handler(CommandHandler(command, self._commands[command]))

        dp.add_handler(MessageHandler(Filters.text, self.command_echo))
        dp.add_handler(CallbackQueryHandler(self.command_button))
        dp.add_handler(InlineQueryHandler(self.command_inline_query))

    def command_help(self, bot, update: Update):
        keyboard = [[InlineKeyboardButton(localization_buttons[kButtonCreateVote], callback_data='create_vote')],
                    [InlineKeyboardButton(localization_buttons[kButtonCreateSimpleVote], callback_data='simple_vote')]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        message: Message = update.message
        message.reply_text(localization[kMainMenuState0], reply_markup=reply_markup)

    def command_create_vote(self, bot: Bot, update: Update):
        # if update is None or update.message is None:
        #     return

        if update.effective_user is None:
            return

        owner_id = update.effective_user.id
        vote = voting.Vote(owner_id)

        self.votes.append(vote)

        message: Message = update.message
        text = localization[kLetsCreatePoll]

        if message is None:
            chat: Chat = update.effective_chat
            chat_id = chat.id
            bot.send_message(chat_id=chat_id, text=text)
        else:
            update.message.reply_text(text)


    def command_simple_vote(self, bot: Bot, update: Update):
        # if update is None or update.message is None:
        #     return

        if update.effective_user is None:
            return

        owner_id = update.effective_user.id
        vote = voting.Vote.random_vote(owner_id)

        self.votes.append(vote)

        self.command_done(bot, update)

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
        # if update is None or update.message is None:
        #     return

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
        text = localization[kFinishCreate]

        if message is None:
            chat: Chat = update.effective_chat
            chat_id = chat.id
            bot.send_message(chat_id=chat_id, text=text)
        else:
            update.message.reply_text(text)

        vote.vote_stage = voting.eVoteStageCreated

        actual_answers = vote.actual_info_message()

        keyboard = [
            [InlineKeyboardButton('Выслать голосование', switch_inline_query=f'{vote.question.text}')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        if message is None:
            chat: Chat = update.effective_chat
            chat_id = chat.id
            m = bot.send_message(chat_id=chat_id, text=actual_answers, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)
            vote.history.append((m.chat_id, m.message_id))
        else:
            m = update.message.reply_text(actual_answers, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)
            vote.history.append((m.chat_id, m.message_id))

        pass

    def command_button(self, bot: Bot, update: Update):
        query = update.callback_query
        data = query.data
        command = None

        try:
            command = json.loads(data)
        except:
            pass

        if command is not None:
            if command['type'] == 'vote':
                vote_id = command['id']
                index = command['data']

                votes = [vote for vote in self.votes if vote.id == vote_id]

                if len(votes) == 0:
                    return

                vote = votes[0]

                user:User = update.effective_user

                tx_id = vote.increase_balance(index, user.id)

                user: User = update.effective_user
                chat_id = user.id

                if tx_id is None:
                    bot.send_message(chat_id, localization[kError1])
                else:
                    bot.send_message(chat_id, localization[kVoteAccept].format(url=config.ETH_EXPLORER_URL + tx_id), parse_mode=telegram.ParseMode.MARKDOWN)

                info = vote.actual_info_message()

                for h in vote.history:
                    chat_id = h[0]

                    if len(h) == 1:
                        message_id = chat_id
                        bot.edit_message_text(info, parse_mode=telegram.ParseMode.MARKDOWN, message_id=message_id)
                        continue

                    message_id = h[1]
                    bot.edit_message_text(info, parse_mode=telegram.ParseMode.MARKDOWN, chat_id=chat_id, message_id=message_id)

            return


        for command in self._commands.keys():
            if data == command:
                self._commands[command](bot, update)
                break

    def command_inline_query(self, bot: Bot, update: Update):
        if update.effective_user is None:
            return

        owner_id = update.effective_user.id

        votes = [vote for vote in self.votes if vote.owner_id == owner_id and vote.is_shared == True]

        if len(votes) == 0:
            return

        results = []

        for vote in votes:
            input_message = InputTextMessageContent(message_text=vote.actual_info_message(), parse_mode=telegram.ParseMode.MARKDOWN)
            keyboard = [[InlineKeyboardButton(a.text, callback_data=json.dumps({'type':'vote', 'data':idx, 'id':vote.id}))] for idx, a in enumerate(vote.answers)]

            article_id = uuid4()
            article = InlineQueryResultArticle(id=article_id,
                                               title=vote.title(),
                                               input_message_content=input_message,
                                               reply_markup=InlineKeyboardMarkup(keyboard))

            vote.history.append((article_id))

            results.append(article)

        update.inline_query.answer(results)

        pass
