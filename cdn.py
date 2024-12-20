import telebot
from flask import Flask, request
import requests

# Создаём бота
API_TOKEN = '6958777588:AAGD8N_z0Jc-jjO46SF8DPb7ROo-laa3LeI'
bot = telebot.TeleBot(API_TOKEN)

# Токен API для поиска фильмов
MOVIE_API_TOKEN = "7KRyeRqk77NXXRRQ99R0JDhpvzWesA4L"

# Flask приложение
app = Flask(__name__)

# Функция для поиска фильмов
def search_movie_by_title(title, api_token):
    url = "https://portal.lumex.host/api/short"
    params = {
        "api_token": api_token,
        "title": title
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("result"):
            movies = data.get("data", [])
            sorted_movies = sorted(
                movies,
                key=lambda x: get_relevance_score(title, x['title'], x.get('orig_title', '')),
                reverse=True
            )
            return sorted_movies
    return []


# Функция для подсчёта релевантности совпадений
def get_relevance_score(query, title, orig_title):
    query = query.lower()
    title = title.lower()
    orig_title = orig_title.lower() if orig_title else ""

    if query == title:
        return float('inf')

    title_score = sum(1 for char in query if char in title)
    orig_title_score = sum(1 for char in query if char in orig_title) if orig_title else 0

    return title_score + orig_title_score


# Функция для форматирования URL
def format_url(iframe_url):
    if iframe_url.startswith('/'):
        return f"https:{iframe_url}"
    elif not iframe_url.startswith(('http://', 'https://')):
        return None
    return iframe_url


# Обработка команд в боте
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне название фильма, чтобы найти его.")


@bot.message_handler(func=lambda message: True)
def search_and_send_movies(message):
    title = message.text.strip()
    movies = search_movie_by_title(title, MOVIE_API_TOKEN)

    if movies:
        response_text = "Вот что я нашёл:\n\n"
        for movie in movies:
            title = movie.get('title', 'Без названия')
            orig_title = movie.get('orig_title', 'Без оригинального названия')
            imdb_id = movie.get('imdb_id', None)
            kp_id = movie.get('kp_id', None)
            content_type = movie.get('content_type', 'Не указано')
            iframe_url = movie.get('iframe', '').split('src="')[1].split('"')[0] if 'iframe' in movie else ''
            formatted_url = format_url(iframe_url)

            # Формирование ссылок на IMDb и Кинопоиск
            imdb_link = f"https://www.imdb.com/title/{imdb_id}" if imdb_id else 'Нет IMDb ссылки'
            kp_link = f"https://www.kinopoisk.ru/film/{kp_id}/" if kp_id else 'Нет Кинопоиск ссылки'

            response_text += f"🎥 Название: {title}\n"
            response_text += f"📜 Оригинальное название: {orig_title}\n"
            if imdb_id:
                response_text += f"🎬 IMDB ID: [{imdb_id}]({imdb_link})\n"
            else:
                response_text += "🎬 IMDB ID: Нет данных\n"
            response_text += f"📁 Тип: {content_type}\n"
            if kp_id:
                response_text += f"🎬 KP ID: [{kp_id}]({kp_link})\n"
            else:
                response_text += "🎬 KP ID: Нет данных\n"
            if formatted_url:
                response_text += f"🔗 [Перейти]({formatted_url})\n\n"
            else:
                response_text += "🔗 Ссылка недоступна\n\n"

        bot.send_message(message.chat.id, response_text, parse_mode="Markdown", disable_web_page_preview=True)
    else:
        bot.reply_to(message, "Ничего не найдено по вашему запросу.")


# Вебхук для получения обновлений
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200


# Установка webhook
def set_webhook():
    url = 'https://54.226.101.68/webhook'  # Укажите URL для вашего webhook
    bot.remove_webhook()
    bot.set_webhook(url=url)


# Запуск Flask сервера
if __name__ == '__main__':
    set_webhook()  # Устанавливаем webhook
    app.run(host='0.0.0.0', port=5000)  # Запускаем сервер на порту 5000
