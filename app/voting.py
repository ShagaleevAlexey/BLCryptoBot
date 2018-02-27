class Question:
    text: str = ''

    def __init__(self, text: str):
        self.text = text

class Answer:
    text: str = ''
    ids = []
    balance = 0

    def __init__(self, text: str):
        self.text = text
        self.ids = []
        self.balance = 0


# Enum VoteStage
eVoteStageSetQuestion   = 10
eVoteStageAddAnswer     = 20
eVoteStageCreated       = 30
eVoteStageFinally       = 100

class Vote:
    question: Question
    answers: list
    owner_id: str

    vote_stage = eVoteStageSetQuestion
    total_balance = 0

    def __init__(self, owner_id):
        self.answers = []
        self.owner_id = owner_id

    def set_question(self, text):
        self.question = Question(text)
        self.vote_stage = eVoteStageAddAnswer

    def add_answer(self, text: str):
        current_answer = [a for a in self.answers if a.text == text]

        if len(current_answer) > 0:
            return

        self.answers.append(Answer(text))

    def actual_balance_message(self, answer: Answer):
        percent = answer.balance / self.total_balance
        message = ''

        if percent == 0:
            message += '▫️'
        else:
            message += ''

        message += f' {percent:.0f}'

        return message

    def actual_info_message(self):
        answers = f'*{self.question.text}*'

        answers += '\n\n'.join([self.actual_balance_message(a) for a in answers])

        answers = '\n▫️ 0%\n\n'.join([a.text for a in self.answers]) + '\n▫️ 0%\n\n'


        pass
