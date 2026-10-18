from flask import Flask, jsonify, send_from_directory, request


from sheets import (
    dashboard_players,
    dashboard_heroes,
    dashboard_maps,
    dashboard_last_match,
    dashboard_stats,
    add_match,
    search_players,
    search_heroes,
    search_maps,
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
# Подсказки для формы добавления матча
# Источник — только соответствующие справочники Google Sheets
# =========================
@app.route("/api/match_lookup")
def match_lookup():
    lookup_type = request.args.get("type", "").strip().lower()
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return jsonify([])

    lookup_functions = {
        "players": search_players,
        "heroes": search_heroes,
        "maps": search_maps,
    }
    lookup = lookup_functions.get(lookup_type)
    if lookup is None:
        return jsonify({"error": "Неизвестный тип поиска."}), 400

    try:
        return jsonify(lookup(query)[:20])
    except Exception:
        app.logger.exception("Ошибка поиска значений для формы матча")
        return jsonify({"error": "Не удалось загрузить варианты из таблицы."}), 500


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

    # Проверяем значения по справочникам до записи. Нельзя создать нового
    # игрока, героя или поле через форму Mini App.
    directories = (
        ("player1", search_players, "игроков", "Players"),
        ("player2", search_players, "игроков", "Players"),
        ("hero1", search_heroes, "героев", "Heroes"),
        ("hero2", search_heroes, "героев", "Heroes"),
        ("map", search_maps, "полей", "Maps"),
    )
    for field, lookup, label, sheet_name in directories:
        try:
            matches = lookup(match[field])
        except Exception:
            app.logger.exception("Не удалось проверить значение в справочнике %s", sheet_name)
            return jsonify({"error": f"Не удалось проверить {label[:-1]} в таблице {sheet_name}. Попробуйте позже."}), 500
        if not any(str(item).strip().casefold() == match[field].casefold() for item in matches):
            return jsonify({
                "error": f"Значение «{match[field]}» не найдено в таблице {sheet_name}. Выберите вариант из подсказок; новые записи через эту форму не создаются."
            }), 400

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
