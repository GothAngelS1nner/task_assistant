class Task:
    def __init__(self, title: str):
        self.ttile = title
        self.completed = False

    def complete(self):
        self.completed = True