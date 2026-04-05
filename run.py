import threading
from app.main import create_app
from app.bot import TaskBot
from app.core.config import Config



app = create_app()

def run_bot():
    bot = TaskBot(Config.BOT_TOKEN, Config.MAX_TASK_LENGTH, flask_app=app)
    bot.run()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    app.run(debug=False)