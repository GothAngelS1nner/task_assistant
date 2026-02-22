import os
import telebot
from app.services.task_service import TaskService


class TaskBot:
    MAX_TASK_LENGTH = 60

    def __init__(self, token: str):
        if not token:
            raise ValueError("BOT_TOKEN is not set")
        
        self.bot = telebot.TeleBot(token)
        self.task_service = TaskService()

        self._register_handlers()

    # =========================
    # Handlers registration
    # =========================
    def _register_handlers(self):
        self.bot.message_handler(commands=["start"])(self.start)
        self.bot.message_handler(commands=["add"])(self.add_task)
        self.bot.message_handler(commands=["list"])(self.list_tasks)
        self.bot.message_handler(commands=["clear"])(self.clear_tasks)
        self.bot.message_handler(commands=["done"])(self.done_tasks)
        self.bot.message_handler(commands=["undo"])(self.undo_tasks)
        self.bot.message_handler(commands=["help"])(self.help_command)
        self.bot.message_handler(func=lambda message: True)(self.unknown_command)


    # =========================
    # Helpers
    # =========================
    def show_tasks(self, chat_id: int):
        tasks = self.task_service.get_tasks()
        if not tasks:
            self.bot.send_message(chat_id, "📭 Задач нет")
            return 
        
        response = ""
        for i, t in enumerate(tasks, 1):
            status = "✅" if t.completed else "❌"
            response += f"{i}. {t.title} {status}\n"

        self.bot.send_message(chat_id, f"Текущий список задач:\n{response}")

    # =========================
    # Commands
    # =========================
    def start(self, message):
        self.bot.send_message(
            message.chat.id, 
            "Привет! Я твой Task Assistant 🤖"
        )


    def add_task(self, message):
        text = message.text
        parts = text.split(maxsplit=1)

        if len(parts) < 2:
            self.bot.send_message(message.chat.id,  "Используй: /add <название задачи>")
            return 
        
        title = parts[1]

        if len(title) > self.MAX_TASK_LENGTH:
            self.bot.send_message(message.chat.id, "❌ Задача слишком длинная (максимум 60 символов)")
            return

        task = self.task_service.add_task(title)

        if task is None:
            self.bot.send_message(message.chat.id, "⚠️ Такая задача уже существует")
            return
        
        self.bot.send_message(message.chat.id, f"✅ Добавлена задача: {task.title}")


    def list_tasks(self, message):
        self.show_tasks(message.chat.id)


    def clear_tasks(self, message):
        parts = message.text.split()

        # /clear
        if len(parts) == 1:
            self.task_service.clear_tasks()
            self.bot.send_message(message.chat.id, "🧹 Все задачи удалены")
            return

        # /clear N
        if len(parts) == 2:
            if not parts[1].isdigit():
                self.bot.send_message(message.chat.id, "❌ Укажи номер задачи: /clear N")
                return
            
            index = int(parts[1]) - 1

            if self.task_service.delete_task(index):
                self.bot.send_message(message.chat.id, f"🗑️ Задача №{index + 1} удалена")
                self.show_tasks(message.chat.id)
            else:
                self.bot.send_message(message.chat.id, "❌ Такой задачи нет")


    def done_tasks(self, message):
        parts = message.text.split()

        if len(parts) != 2:
            self.bot.send_message(message.chat.id, "Используй: /done N")
            return

        if not parts[1].isdigit():
            self.bot.send_message(message.chat.id, "❌ Номер задачи должен быть числом")
            return

        index = int(parts[1]) - 1
        tasks = self.task_service.get_tasks()

        if index < 0 or index >= len(tasks):
            self.bot.send_message(message.chat.id, "❌ Такой задачи нет")
            return
        
        if tasks[index].completed:
            self.bot.send_message(message.chat.id, f"✅ Задача №{index + 1} уже выполнена")
        else:
            self.task_service.mark_done(index)
            self.bot.send_message(message.chat.id, f"✅ Задача №{index + 1} выполнена")
            self.show_tasks(message.chat.id)


    def undo_tasks(self, message):
        parts = message.text.split()

        if len(parts) != 2:
            self.bot.send_message(message.chat.id, "Используй: /undo N")
            return
        
        if not parts[1].isdigit():
            self.bot.send_message(message.chat.id, "❌ Номер задачи должен быть числом")
            return
        
        index = int(parts[1]) - 1
        tasks = self.task_service.get_tasks()

        if index < 0 or index >= len(tasks):
            self.bot.send_message(message.chat.id, "❌ Такой задачи нет")
            return
        
        if not tasks[index].completed:
            self.bot.send_message(message.chat.id, f"⚠️ Задача №{index + 1} ещё не выполнена")
        else:
            self.task_service.mark_undo(index)
            self.bot.send_message(message.chat.id, f"↩️ Задача №{index + 1} помечена как невыполненная")
            self.show_tasks(message.chat.id)


    def help_command(self, message):
        self.bot.send_message(message.chat.id, 
                        "Список команд Task Assistant 🤖:\n"
                        "/start — Приветствие и краткое описание бота\n"
                        "/add <текст> — Добавить новую задачу (максимум 60 символов)\n"
                        "/list — Показать все задачи с их статусом (✅ выполнена, ❌ не выполнена)\n" 
                        "/clear — Удалить все задачи\n"
                        "/clear N — Удалить задачу с номером N\n"
                        "/done N — Отметить задачу с номером N как выполненную\n"
                        "/undo N — Снять отметку о выполнении задачи для номера N\n"
                        "/help — Показать этот список команд"
                        )
        

    def unknown_command(self, message):
        self.bot.send_message(message.chat.id, "❌ Я не знаю такую команду. Используй /help для списка команд.")

    # =========================
    # Run
    # =========================
    def run(self):
        print("Бот запущен...")
        self.bot.infinity_polling()


if __name__ == "__main__":
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    app = TaskBot(BOT_TOKEN)
    app.run()
    