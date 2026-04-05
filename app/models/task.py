from app.extensions import db

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(60), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def complete(self):
        self.completed = True