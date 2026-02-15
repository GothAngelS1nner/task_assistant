from app.models.task import Task


class TaskService:
    def __init__(self):
        self._tasks = []

    def add_task(self, title: str) -> Task:
        task = Task(title)
        self._tasks.append(task)
        return task
    
    def get_tasks(self):
        return self._tasks