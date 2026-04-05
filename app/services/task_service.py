from app.models.task import Task
from app.extensions import db


class TaskService:

    def add_task(self, title: str) -> Task | None:
        if not isinstance(title, str):
            raise TypeError("title must be a string")
        
        if self.task_exists(title):
            return None
        
        task = Task(title=title)
        db.session.add(task)
        db.session.commit()
        return task
    
    def get_tasks(self):
        return Task.query.all()
    
    def clear_tasks(self):
        Task.query.delete()
        db.session.commit()

    def delete_task(self, task_id: int):
        task = Task.query.get(task_id)
        if not task:
            return False
        db.session.delete(task)
        db.session.commit()
        return True
    
    def mark_done(self, index: int):
        tasks = self.get_tasks()
        if index < 0 or index > len(tasks):
            return False
        tasks[index].completed = True
        db.session.commit()
        return True
    
    def mark_undo(self, index: int):
        tasks = self.get_tasks()
        if index < 0 or index >= len(tasks):
            return False
        tasks[index].completed = False
        db.session.commit()
        return True
    
    def task_exists(self, title: str) -> bool:
        title = title.strip().lower()
        return Task.query.filter(
            db.func.lower(Task.title) == title
        ).first() is not None