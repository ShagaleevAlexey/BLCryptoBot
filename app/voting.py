class Question:
    text: str = ''

    def __init__(self, text: str):
        self.text = text

class Answer:
    text: str = ''
    ids = []

    def __init__(self, text: str):
        self.text = text
        self.ids = []

# Enum VoteStage
eVoteStageSetQuestion = 10
eVoteStageAddAnswer = 20
eVoteStageFinally = 100

class Vote:
    question: Question
    answers: list         #type: [Answer]
    owner_id: str

    is_active = True

    vote_stage = eVoteStageSetQuestion

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
