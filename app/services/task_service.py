from app.models.task import Task


class TaskService:
    def __init__(self):
        self._tasks = []

    def add_task(self, title: str) -> Task | None:
        if self.task_exists(title):
            return None
        
        task = Task(title)
        self._tasks.append(task)
        return task
    
    def get_tasks(self):
        return self._tasks
    
    def clear_tasks(self):
        self._tasks.clear()

    def delete_task(self, index):
        if index < 0 or index >= len(self._tasks):
            return False
        
        self._tasks.pop(index)
        return True
    
    def mark_done(self, index):
        if index < 0 or index >= len(self._tasks):
            return False
        
        self._tasks[index].completed = True
        return True
    
    def mark_undo(self, index):
        if index < 0 or index >= len(self._tasks):
            return False
        
        self._tasks[index].completed = False
        return True
    
    def task_exists(self, title: str) -> bool:
        title = title.strip().lower()
        return any(t.title.strip().lower() == title for t in self._tasks)