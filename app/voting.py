import random
from app.__services__.blockchain_server import BlockchainServer

class Question:
    text: str = ''

    def __init__(self, text: str):
        self.text = text

class Answer:
    id = 0
    text: str = ''
    ids = []
    balance = 0

    def __init__(self, text: str):
        self.id = random.randint(100000, 999999)
        self.text = text
        self.ids = []
        self.balance = 0

simples = [
    {
        'q' : 'Что любят ящеры?',
        'a' : ['Насекомых', 'Траву', 'Бурито']
    },
    {
        'q': 'Фиат - это скам?',
        'a': ['Да', 'Нет', 'Bitcoin FOREVER']
    },
    {
        'q' : 'Кто сильнее всех на свете?',
        'a' : ['Человек-Паук', 'Халк', 'Тор', 'Старк', 'Монтировка']
    },
    {
        'q' : 'Какой объект Солнечной Системы стоит колонизировать в первую очередь?',
        'a' : ['Луна', 'Марс', 'Титан']
    }
]

# Enum VoteStage
eVoteStageSetQuestion   = 10
eVoteStageAddAnswer     = 20
eVoteStageCreated       = 30
eVoteStageFinally       = 100

class Vote:
    id = 0
    question: Question
    answers: list
    owner_id: str

    __vote_stage = eVoteStageSetQuestion
    total_balance = 0

    is_shared = False

    history = []

    @staticmethod
    def random_vote(owner_id):
        vote = Vote(owner_id)

        simple = simples[random.randint(0, len(simples) - 1)]

        vote.set_question(simple['q'])

        for a in simple['a']:
            vote.add_answer(a)

        vote.vote_stage = eVoteStageCreated

        return vote

    def __init__(self, owner_id):
        self.answers = []
        self.history = []
        self.owner_id = owner_id
        self.id = random.randint(100000, 999999)

    def set_question(self, text):
        self.question = Question(text)
        self.vote_stage = eVoteStageAddAnswer

    def add_answer(self, text: str):
        current_answer = [a for a in self.answers if a.text == text]

        if len(current_answer) > 0:
            return

        self.answers.append(Answer(text))

    def increase_balance(self, answer_idx, user_id, value=1):
        if answer_idx < 0 or answer_idx >= len(self.answers):
            return

        answer = self.answers[answer_idx]
        answer.balance += 1

        self.total_balance += 1

        return BlockchainServer().transaction(user_id, answer.id)

    @property
    def vote_stage(self):
        return self.__vote_stage
    
    @vote_stage.setter
    def vote_stage(self, vote_stage):
        self.__vote_stage = vote_stage

        if self.__vote_stage == eVoteStageCreated:
            self.is_shared = True
        else:
            self.is_shared = False


    def title(self):
        return self.question.text + '\n' + ' / '.join([a.text for a in self.answers])

    def actual_balance_message(self, answer: Answer):
        percent = 0

        if self.total_balance != 0:
            percent = answer.balance / self.total_balance

        message = f'{answer.text}\n'

        if percent == 0:
            message += '▫️0 %'
        else:
            message += f'👍👍👍👍👍👍 {percent:.0f} %'

        return message

    def actual_info_message(self):
        message = f'*{self.question.text}*'

        for a in self.answers:
            message += f'\n\n{self.actual_balance_message(a)}'

        message += f'\n\n👥 {self.total_balance} человек проголосовало.'

        return message
