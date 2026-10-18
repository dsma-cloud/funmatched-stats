from flask import Flask, jsonify, send_from_directory, request


from sheets import (
    dashboard_players,
    dashboard_heroes,
    dashboard_maps,
    dashboard_last_match,
    dashboard_stats,
    search_heroes,
    hero_match_report
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



# =========================
# Поиск героя для отчёта
# =========================
@app.route("/api/hero_search")
def hero_search():
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return jsonify([])
    return jsonify(search_heroes(query)[:20])


# =========================
# Отчёт по герою
# =========================
@app.route("/api/hero_report")
def hero_report():
    hero = request.args.get("hero", "").strip()
    if not hero:
        return jsonify({"error": "Укажите героя"}), 400
    return jsonify(hero_match_report(hero))
