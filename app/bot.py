import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.core.config import Config
from app.services.task_service import TaskService


class TaskBot:

    def __init__(self, token: str, max_task_length: int, flask_app=None):
        if not token:
            raise ValueError("BOT_TOKEN is not set")
        
        self.bot = telebot.TeleBot(token)
        self.task_service = TaskService()
        self.MAX_TASK_LENGTH = max_task_length
        self.flask_app = flask_app
        self._register_handlers()

    def with_context(self, func, *args, **kwargs):
        if self.flask_app:
            with self.flask_app.app_context():
                return func(*args, **kwargs)
        return func(*args, **kwargs)

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
        self.bot.callback_query_handler(func=lambda call: True)(self.handle_callback)


    # =========================
    # Helpers
    # =========================
    def get_task_buttons(self, task, index):
        buttons = []

        if not task.completed:
            buttons.append(
                InlineKeyboardButton(
                    text=f"✅ Выполнить №{index}",
                    callback_data=f"done:{index - 1}"
                )
            )
        else:
            buttons.append(
                InlineKeyboardButton(
                    text=f"↩️ Отменить №{index}",
                    callback_data=f"undo:{index - 1}"
                )
            )

        return buttons
    
    def get_global_buttons(self, tasks):
        buttons = []

        # Кнопка "Выполнить все" если есть хоть одна невыполненная задача
        if any(not task.completed for task in tasks):
            buttons.append(
                InlineKeyboardButton(
                    text="✅ Выполнить все",
                    callback_data="done_all:0"
                )
            )
        # Кнопка "Отменить все" только если все задачи выполнены
        if tasks and all(task.completed for task in tasks):
            buttons.append(
                InlineKeyboardButton(
                    text="❌ Отменить все",
                    callback_data="undo_all:0"
                )
            )

        return buttons
    
    
    def build_task_view(self):
        tasks = self.with_context(self.task_service.get_tasks)
        markup = InlineKeyboardMarkup(row_width=2)

        if not tasks:
            return "📭 Задач нет", None
        
        response = ""
        row = []
        MAX_IN_ROW = 2

        for i, t in enumerate(tasks, 1):
            status = "✅" if t.completed else "❌"
            response += f"{i}. {t.title} {status}\n"
            row.extend(self.get_task_buttons(t, i))
            if len(row) >= MAX_IN_ROW:
                markup.add(*row[:MAX_IN_ROW])
                row = row[MAX_IN_ROW:]

        if row:
            markup.add(*row)

        global_buttons = self.get_global_buttons(tasks)
        if global_buttons:
            markup.add(*global_buttons)
            
        return f"Текущий список задач:\n{response}", markup

    def show_tasks(self, chat_id: int):
        text, markup = self.build_task_view()
        self.bot.send_message(chat_id, text, reply_markup=markup)
    

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

        task = self.with_context(self.task_service.add_task, title)

        if task is None:
            self.bot.send_message(message.chat.id, "⚠️ Такая задача уже существует")
            return
        
        self.bot.send_message(message.chat.id, f"✅ Добавлена задача: {title}")


    def list_tasks(self, message):
        self.show_tasks(message.chat.id)


    def clear_tasks(self, message):
        parts = message.text.split()

        # /clear
        if len(parts) == 1:
            self.with_context(self.task_service.clear_tasks)
            self.bot.send_message(message.chat.id, "🧹 Все задачи удалены")
            return

        # /clear N
        if len(parts) == 2:
            if not parts[1].isdigit():
                self.bot.send_message(message.chat.id, "❌ Укажи номер задачи: /clear N")
                return
            
            index = int(parts[1]) - 1
            tasks = self.with_context(self.task_service.get_tasks)

            if index < 0 or index >= len(tasks):
                self.bot.send_message(message.chat.id, "❌ Такой задачи нет")
                return
            
            task_id = tasks[index].id
            if self.with_context(self.task_service.delete_task, task_id):
                self.bot.send_message(message.chat.id, f"🗑️ Задача №{index + 1} удалена")
                self.show_tasks(message.chat.id)

                


    def done_tasks(self, message):
        parts = message.text.split()

        if len(parts) != 2:
            self.bot.send_message(message.chat.id, "Используй: /done N")
            return

        if not parts[1].isdigit():
            self.bot.send_message(message.chat.id, "❌ Номер задачи должен быть числом")
            return

        index = int(parts[1]) - 1
        tasks = self.with_context(self.task_service.get_tasks)

        if index < 0 or index >= len(tasks):
            self.bot.send_message(message.chat.id, "❌ Такой задачи нет")
            return
        
        if tasks[index].completed:
            self.bot.send_message(message.chat.id, f"✅ Задача №{index + 1} уже выполнена")
        else:
            self.with_context(self.task_service.mark_done, index)
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
        tasks = self.with_context(self.task_service.get_tasks)

        if index < 0 or index >= len(tasks):
            self.bot.send_message(message.chat.id, "❌ Такой задачи нет")
            return
        
        if not tasks[index].completed:
            self.bot.send_message(message.chat.id, f"⚠️ Задача №{index + 1} ещё не выполнена")
        else:
            self.with_context(self.task_service.mark_undo, index)
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

    
    def handle_callback(self, call):
        action, index_str = call.data.split(":")
        index = int(index_str)
        tasks = self.with_context(self.task_service.get_tasks)

        if index < 0 or index >= len(tasks):
            self.bot.answer_callback_query(call.id, "❌ Такой задачи нет")
            return

        task = tasks[index]

        if action == "done":
            if task.completed:
                self.bot.answer_callback_query(call.id, f"✅ Задача №{index + 1} уже выполнена")
            else:
                self.with_context(self.task_service.mark_done, index)
                self.bot.answer_callback_query(call.id, f"✅ Задача №{index + 1} выполнена")

        elif action == "undo":
            if not task.completed:
                self.bot.answer_callback_query(call.id, f"⚠️ Задача №{index + 1} ещё не выполнена")
            else:
                self.with_context(self.task_service.mark_undo, index)
                self.bot.answer_callback_query(call.id, f"↩️ Задача №{index + 1} помечена как невыполненная")

        elif action == "done_all":
            for i in range(len(tasks)):
                self.with_context(self.task_service.mark_done, i)
            self.bot.answer_callback_query(call.id, "✅ Все задачи выполнены")
        
        elif action == "undo_all":
            for i in range(len(tasks)):
                self.with_context(self.task_service.mark_undo, i)
            self.bot.answer_callback_query(call.id, "❌ Все задачи отменены")

        text, markup = self.build_task_view()

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup
        )
        

    # =========================
    # Run
    # =========================
    def run(self, app=None):
        print("Бот запущен...")
        self.flask_app = app or self.flask_app
        self.bot.infinity_polling()


if __name__ == "__main__":
    app = TaskBot(Config.BOT_TOKEN, Config.MAX_TASK_LENGTH)
    app.run()
    