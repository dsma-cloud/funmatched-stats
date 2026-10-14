from flask import Flask, jsonify, send_from_directory


from sheets import (
    dashboard_players,
    dashboard_heroes,
    dashboard_maps,
    dashboard_last_match,
    dashboard_stats
)





app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)





# =========================
# Главная страница
# =========================

@app.route("/")
def index():

    return send_from_directory(
        "static",
        "index.html"
    )





# =========================
# Игроки
# =========================

@app.route("/api/players")
def players():

    return jsonify(
        dashboard_players()
    )





# =========================
# Герои
# =========================

@app.route("/api/heroes")
def heroes():

    return jsonify(
        dashboard_heroes()
    )





# =========================
# Поля
# =========================

@app.route("/api/maps")
def maps():

    return jsonify(
        dashboard_maps()
    )





# =========================
# Последний матч
# =========================

@app.route("/api/last_match")
def last_match():

    return jsonify(
        dashboard_last_match()
    )





# =========================
# Общая статистика
# =========================

@app.route("/api/stats")
def stats():

    return jsonify(
        dashboard_stats()
    )

