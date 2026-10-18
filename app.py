from flask import Flask, jsonify, send_from_directory, request


from sheets import (
    dashboard_players,
    dashboard_heroes,
    dashboard_maps,
    dashboard_last_match,
    dashboard_stats,
    add_match,
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


# =========================
# Добавление матча из Mini App
# =========================
@app.route("/api/matches", methods=["POST"])
def create_match():
    data = request.get_json(silent=True) or {}
    required = ("player1", "hero1", "player2", "hero2", "map", "winner")
    match = {key: str(data.get(key, "")).strip() for key in required}

    missing = [key for key, value in match.items() if not value]
    if missing:
        return jsonify({"error": "Заполните все поля матча."}), 400

    if match["winner"] not in ("Player 1", "Player 2"):
        return jsonify({"error": "Выберите победителя: Player 1 или Player 2."}), 400

    match["date"] = str(data.get("date", "")).strip()
    if not match["date"]:
        from datetime import date
        match["date"] = date.today().isoformat()

    try:
        add_match(match)
        return jsonify({"ok": True, "message": "Матч добавлен в таблицу Matches."}), 201
    except Exception:
        app.logger.exception("Не удалось добавить матч в Google Sheets")
        return jsonify({"error": "Не удалось сохранить матч в Google Sheets. Попробуйте позже."}), 500
