from app.models.task import Task
from app.extensions import db


class TaskService:

    def add_task(self, user_id: int, title: str) -> Task | None:
        if not isinstance(title, str):
            raise TypeError("title must be a string")
        
        if self.task_exists(user_id, title):
            return None
        
        task = Task(user_id=user_id, title=title)
        db.session.add(task)
        db.session.commit()
        return task
    
    def get_tasks(self, user_id: int):
        return Task.query.filter_by(user_id=user_id).all()
    
    def clear_tasks(self, user_id):
        Task.query.filter_by(user_id=user_id).delete()
        db.session.commit()

    def delete_task(self, user_id: int, task_id: int):
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return False
        db.session.delete(task)
        db.session.commit()
        return True
    
    def mark_done(self, user_id: int, index: int):
        tasks = self.get_tasks(user_id)
        if index < 0 or index >= len(tasks):
            return False
        tasks[index].completed = True
        db.session.commit()
        return True
    
    def mark_undo(self, user_id: int, index: int):
        tasks = self.get_tasks(user_id)
        if index < 0 or index >= len(tasks):
            return False
        tasks[index].completed = False
        db.session.commit()
        return True
    
    def task_exists(self, user_id: int, title: str) -> bool:
        title = title.strip().lower()
        return Task.query.filter(
            Task.user_id == user_id,
            db.func.lower(Task.title) == title
        ).first() is not None