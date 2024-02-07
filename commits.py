import requests
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging

# Настройки телеграм бота
TELEGRAM_TOKEN = '6585105940:AAGqHS7weZ2KVJPZScri2x4PzSeVgjtls5I'

# Настройки GitHub репозитория
GITHUB_OWNER = 'azam2802'
GITHUB_REPO = 'repository_name'

# Настройки API GitHub
GITHUB_API_URL = f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/commits'

# Настройки для последнего коммита (используются для проверки новых коммитов)
last_commit_sha = None

# Инициализация логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для отправки сообщений в телеграм
def send_message(bot: Bot, chat_id: int, message: str):
    bot.send_message(chat_id=chat_id, text=message)

# Функция для обработки команды /start
def start(update: Update, context: CallbackContext):
    send_message(update.effective_chat.id, "Привет! Я телеграм бот, который отслеживает коммиты в репозитории на GitHub.")

# Функция для проверки новых коммитов
def check_commits(context: CallbackContext):
    global last_commit_sha
    response = requests.get(GITHUB_API_URL)
    if response.status_code == 200:
        commits = response.json()
        latest_commit = commits[0]
        commit_sha = latest_commit['sha']
        if commit_sha != last_commit_sha:
            last_commit_sha = commit_sha
            commit_author = latest_commit['commit']['author']['name']
            commit_date = latest_commit['commit']['author']['date']
            commit_message = latest_commit['commit']['message']
            branch = latest_commit['commit']['tree']['url']
            send_message(context.bot, context.job.context, f"Новый коммит!\nАвтор: {commit_author}\nДата: {commit_date}\nВетка: {branch}\nСообщение: {commit_message}")
        else:
            logger.info("Нет новых коммитов")
    else:
        logger.error(f"Ошибка при получении коммитов: {response.status_code}")

def main():
    # Инициализация телеграм бота
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    # Добавление обработчика для команды /start
    dp.add_handler(CommandHandler("start", start))

    # Запуск регулярной проверки новых коммитов (каждую минуту)
    updater.job_queue.run_repeating(check_commits, interval=60, context=TELEGRAM_TOKEN)

    # Запуск телеграм бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
