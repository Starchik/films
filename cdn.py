from flask import Flask, render_template_string, request
import requests
import webbrowser
import socket

app = Flask(__name__)


# Функция для поиска фильмов
def search_movie_by_title(title, api_token):
    url = "https://portal.lumex.host/api/short"
    params = {
        "api_token": api_token,
        "title": title
    }

    # Отправляем GET-запрос
    response = requests.get(url, params=params)

    # Проверяем успешность запроса
    if response.status_code == 200:
        data = response.json()
        if data.get("result"):
            # Получаем список фильмов
            movies = data.get("data", [])
            # Сортируем фильмы по релевантности
            sorted_movies = sorted(movies,
                                   key=lambda x: get_relevance_score(title, x['title'], x.get('orig_title', '')),
                                   reverse=True)
            return sorted_movies
    return []


# Функция для подсчета релевантности совпадений
def get_relevance_score(query, title, orig_title):
    # Преобразуем в нижний регистр для поиска без учета регистра
    query = query.lower()
    title = title.lower()
    orig_title = orig_title.lower() if orig_title else ""

    # Если название фильма точно совпадает с запросом, присваиваем наивысший приоритет
    if query == title:
        return float('inf')

    # Считаем количество совпадений символов в названии фильма
    title_score = sum(1 for char in query if char in title)

    # Считаем количество совпадений символов в оригинальном названии, если оно есть
    orig_title_score = sum(1 for char in query if char in orig_title) if orig_title else 0

    # Возвращаем суммарную релевантность (объединяем оба показателя)
    return title_score + orig_title_score


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form["title"]
        api_token = "7KRyeRqk77NXXRRQ99R0JDhpvzWesA4L"  # Ваш токен
        movies = search_movie_by_title(title, api_token)
        return render_template_string("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Film</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #171a21;
                        color: #fff;
                    }
                    #container {
                        max-width: 800px;
                        margin: 20px auto;
                        padding: 20px;
                        background-color: #2c2f35;
                        border-radius: 8px;
                    }
                    h1 {
                        text-align: center;
                        color: #66c0f4;
                    }
                    #search-container {
                        margin-bottom: 20px;
                        text-align: center;
                    }
                    #search-input, #category-select {
                        padding: 10px;
                        border: none;
                        border-radius: 4px;
                        margin: 5px;
                    }
                    #search-input {
                        width: 50%;
                    }
                    #category-select {
                        width: 20%;
                    }
                    #search-button {
                        padding: 10px 20px;
                        background-color: #4b5263;
                        color: #fff;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                    #movie-list {
                        list-style-type: none;
                        padding: 0;
                    }
                    .movie-item {
                        margin-bottom: 10px;
                        padding: 10px;
                        background-color: #3e4251;
                        border-radius: 4px;
                    }
                    .movie-name {
                        font-size: 18px;
                        color: #66c0f4;
                        cursor: pointer;
                        text-decoration: none;
                    }
                    .movie-details {
                        font-size: 14px;
                    }
                    .movie-details a {
                        color: #b0b0b0;
                        text-decoration: none;
                    }
                    .movie-details a:hover {
                        color: #66c0f4;
                    }
                    .download-button {
                        padding: 8px 16px;
                        background-color: #66c0f4;
                        color: #fff;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                    .iframe-container {
                        display: none;
                        margin-top: 10px;
                    }
                    .iframe-container iframe {
                        width: 100%;
                        height: 400px;
                    }
                    #footer {
                        text-align: center;
                        margin-top: 20px;
                    }
                    #footer a {
                        color: #66c0f4;
                        text-decoration: none;
                        font-size: 14px;
                    }
                    #logo {
                        width: 50px;
                        height: auto;
                        margin-right: 10px;
                        vertical-align: middle;
                    }
                    #header {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 20px;
                    }
                    a {
                        color: inherit;
                        text-decoration: none;
                    }
                </style>
                <script>
                    function toggleIframe(movieId) {
                        var iframeContainer = document.getElementById("iframe-" + movieId);
                        if (iframeContainer.style.display === "none" || iframeContainer.style.display === "") {
                            iframeContainer.style.display = "block";
                        } else {
                            iframeContainer.style.display = "none";
                        }
                    }
                </script>
            </head>
            <body>
                <div id="container">
                    <div id="header">
                        <img id="logo" src="static/icon.png" alt="Logo">
                        <h1>Film</h1>
                    </div>
                    <div id="search-container">
                        <form method="POST">
                            <input type="text" id="search-input" name="title" placeholder="Enter keyword" required>
                            <button id="search-button" type="submit">Search</button>
                        </form>
                    </div>
                    <ul id="movie-list">
                        {% if movies %}
                            {% for movie in movies %}
                                <li class="movie-item">
                                    <div class="movie-name">
                                        <a href="https://{{ movie['iframe'].split('src="')[1].split('"')[0] }}" target="_blank">
                                            {{ movie['title'] }}
                                        </a>
                                    </div>
                                    <div class="movie-details">
                                        {% if movie['orig_title'] %}
                                            Original Title: {{ movie['orig_title'] }}<br>
                                        {% endif %}
                                        {% if movie['imdb_id'] %}
                                            IMDB ID: <a href="https://www.imdb.com/title/{{ movie['imdb_id'] }}" target="_blank">{{ movie['imdb_id'] }}</a><br>
                                        {% else %}
                                            IMDB ID: Not available<br>
                                        {% endif %}
                                        Type: {{ movie['content_type'] or 'Not specified' }}<br>
                                        Translations: {{ movie['translations'][0] if movie['translations'] else 'None' }}
                                    </div>
                                </li>
                            {% endfor %}
                        {% else %}
                            <p>No results found.</p>
                        {% endif %}
                    </ul>
                    <div id="footer">
                        <a href="https://t.me/Starchik_1" target="_blank">Starchik</a>
                    </div>
                </div>
            </body>
            </html>
        """, movies=movies)

    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Film</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #171a21;
                    color: #fff;
                }
                #container {
                    max-width: 800px;
                    margin: 20px auto;
                    padding: 20px;
                    background-color: #2c2f35;
                    border-radius: 8px;
                }
                h1 {
                    text-align: center;
                    color: #66c0f4;
                }
                #search-container {
                    margin-bottom: 20px;
                    text-align: center;
                }
                #search-input, #category-select {
                    padding: 10px;
                    border: none;
                    border-radius: 4px;
                    margin: 5px;
                }
                #search-input {
                    width: 50%;
                }
                #category-select {
                    width: 20%;
                }
                #search-button {
                    padding: 10px 20px;
                    background-color: #4b5263;
                    color: #fff;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                #footer {
                    text-align: center;
                    margin-top: 20px;
                }
                #footer a {
                    color: #66c0f4;
                    text-decoration: none;
                    font-size: 14px;
                }
                #logo {
                    width: 50px;
                    height: auto;
                    margin-right: 10px;
                    vertical-align: middle;
                }
                #header {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <div id="container">
                <div id="header">
                    <img id="logo" src="static/icon.png" alt="Logo">
                    <h1>Film</h1>
                </div>
                <div id="search-container">
                    <form method="POST">
                        <input type="text" id="search-input" name="title" placeholder="Enter keyword" required>
                        <button id="search-button" type="submit">Search</button>
                    </form>
                </div>
                <div id="footer">
                    <a href="https://t.me/Starchik_1" target="_blank">Starchik</a>
                </div>
            </div>
        </body>
        </html>
    """)


if __name__ == '__main__':
    host_ip = socket.gethostbyname(socket.gethostname())
    port = 5000
    url = f"http://{host_ip}:{port}/"
    webbrowser.open(url)
    app.run(host=host_ip, port=port, debug=False)
