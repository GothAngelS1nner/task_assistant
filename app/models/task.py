class Task:
    def __init__(self, title: str):
        self.title = title
        self.completed = False

    def complete(self):
        self.completed = True