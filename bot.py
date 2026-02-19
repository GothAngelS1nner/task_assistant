import telebot
import os
from app.services.task_service import TaskService


task_service = TaskService()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = telebot.TeleBot(BOT_TOKEN)

MAX_TASK_LENGTH = 60

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id, 
        "Привет! Я твой Task Assistant 🤖"
    )

@bot.message_handler(commands=["add"])
def add_task(message):
    text = message.text
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        bot.send_message(message.chat.id,  "Используй: /add <название задачи>")
        return 
    
    title = parts[1]

    if len(title) > MAX_TASK_LENGTH:
        bot.send_message(message.chat.id, "❌ Задача слишком длинная (максимум 60 символов)")
        return

    task = task_service.add_task(title)
    bot.send_message(message.chat.id, f"✅ Добавлена задача: {task.title}")

@bot.message_handler(commands=["list"])
def list_tasks(message):
    tasks = task_service.get_tasks()
    if not tasks:
        bot.send_message(message.chat.id, "📭 Задач нет")
        return 
    
    response = ""
    for i, t in enumerate(tasks, 1):
        status = "✅" if t.completed else "❌"
        response += f"{i}. {t.title} {status}\n"

    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=["clear"])
def clear_tasks(message):
    parts = message.text.split()

    # /clear
    if len(parts) == 1:
        task_service.clear_tasks()
        bot.send_message(message.chat.id, "🧹 Все задачи удалены")
        return

    # /clear N
    if len(parts) == 2:
        if not parts[1].isdigit():
            bot.send_message(message.chat.id, "❌ Укажи номер задачи: /clear N")
            return
        
        index = int(parts[1]) - 1

        if task_service.delete_task(index):
            bot.send_message(message.chat.id, f"🗑️ Задача №{index + 1} удалена")
        else:
            bot.send_message(message.chat.id, "❌ Такой задачи нет")

@bot.message_handler(commands=["done"])
def done_tasks(message):
    parts = message.text.split()

    if len(parts) != 2:
        bot.send_message(message.chat.id, "Используй: /done N")
        return

    if not parts[1].isdigit():
        bot.send_message(message.chat.id, "❌ Номер задачи должен быть числом")
        return

    index = int(parts[1]) - 1
    tasks = task_service.get_tasks()

    if index < 0 or index >= len(tasks):
        bot.send_message(message.chat.id, "❌ Такой задачи нет")
        return
    
    if tasks[index].completed:
        bot.send_message(message.chat.id, f"✅ Задача №{index + 1} уже выполнена")
    else:
        task_service.mark_done(index)
        bot.send_message(message.chat.id, f"✅ Задача №{index + 1} выполнена")

@bot.message_handler(commands=["undo"])
def undo_tasks(message):
    parts = message.text.split()

    if len(parts) != 2:
        bot.send_message(message.chat.id, "Используй: /undo N")
        return
    
    if not parts[1].isdigit():
        bot.send_message(message.chat.id, "❌ Номер задачи должен быть числом")
        return
    
    index = int(parts[1]) - 1
    tasks = task_service.get_tasks()

    if index < 0 or index >= len(tasks):
        bot.send_message(message.chat.id, "❌ Такой задачи нет")
        return
    
    if not tasks[index].completed:
        bot.send_message(message.chat.id, f"⚠️ Задача №{index + 1} ещё не выполнена")
    else:
        task_service.mark_undo(index)
        bot.send_message(message.chat.id, f"↩️ Задача №{index + 1} помечена как невыполненная")

@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, 
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


bot.infinity_polling()