import telebot
import os
from app.services.task_service import TaskService


task_service = TaskService()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = telebot.TeleBot(BOT_TOKEN)


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
        response += f"{i}. {t.title} [{status}]\n"

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
            bot.send_message(message.chat.id, f"Задача №{index + 1} удалена")
        else:
            bot.send_message(message.chat.id, "❌ Такой задачи нет")


bot.infinity_polling()