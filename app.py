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
    hero_match_report,
    player_match_report,
    hero_head_to_head_report,
    player_head_to_head_report,
    player_rating_last_7_days,
    hero_development_report,
    heroes_not_in_rating_report,
    matches_period_report
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
# Поиск игрока для карточки игрока
# =========================
@app.route("/api/player_search")
def player_search():
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return jsonify([])
    return jsonify(search_players(query)[:20])


# =========================
# Карточка игрока
# =========================
@app.route("/api/player_report")
def player_report():
    player = request.args.get("player", "").strip()
    if not player:
        return jsonify({"error": "Укажите игрока"}), 400
    return jsonify(player_match_report(player))


# =========================
# Противостояние двух героев
# =========================
@app.route("/api/hero_head_to_head")
def hero_head_to_head():
    hero1 = request.args.get("hero1", "").strip()
    hero2 = request.args.get("hero2", "").strip()
    if not hero1 or not hero2:
        return jsonify({"error": "Выберите обоих героев."}), 400
    if hero1.casefold() == hero2.casefold():
        return jsonify({"error": "Выберите двух разных героев."}), 400
    try:
        # Не принимаем произвольные значения: оба героя должны быть в справочнике Heroes.
        known_heroes = search_heroes(hero1)
        if not any(str(item).strip().casefold() == hero1.casefold() for item in known_heroes):
            return jsonify({"error": f"Герой «{hero1}» не найден в таблице Heroes."}), 400
        known_heroes = search_heroes(hero2)
        if not any(str(item).strip().casefold() == hero2.casefold() for item in known_heroes):
            return jsonify({"error": f"Герой «{hero2}» не найден в таблице Heroes."}), 400
        return jsonify(hero_head_to_head_report(hero1, hero2))
    except Exception:
        app.logger.exception("Ошибка формирования отчёта противостояния героев")
        return jsonify({"error": "Не удалось загрузить отчёт. Попробуйте позже."}), 500


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


# =========================
# Противостояние двух игроков
# =========================
@app.route("/api/player_head_to_head")
def player_head_to_head():
    player1 = request.args.get("player1", "").strip()
    player2 = request.args.get("player2", "").strip()
    if not player1 or not player2:
        return jsonify({"error": "Выберите обоих игроков."}), 400
    if player1.casefold() == player2.casefold():
        return jsonify({"error": "Выберите двух разных игроков."}), 400
    try:
        known_players = search_players(player1)
        if not any(str(item).strip().casefold() == player1.casefold() for item in known_players):
            return jsonify({"error": f"Игрок «{player1}» не найден в таблице Players."}), 400
        known_players = search_players(player2)
        if not any(str(item).strip().casefold() == player2.casefold() for item in known_players):
            return jsonify({"error": f"Игрок «{player2}» не найден в таблице Players."}), 400
        return jsonify(player_head_to_head_report(player1, player2))
    except Exception:
        app.logger.exception("Ошибка формирования отчёта противостояния игроков")
        return jsonify({"error": "Не удалось загрузить отчёт. Попробуйте позже."}), 500


@app.route("/api/player_rating_last_7_days")
def player_rating_last_7_days_api():
    try:
        return jsonify(player_rating_last_7_days())
    except Exception:
        app.logger.exception("Ошибка формирования рейтинга игроков за 7 дней")
        return jsonify({"error": "Не удалось загрузить рейтинг игроков."}), 500


@app.route("/api/hero_development")
def hero_development_api():
    try:
        start_value = (request.args.get("start_date") or "").strip()
        end_value = (request.args.get("end_date") or "").strip()
        if not start_value or not end_value:
            return jsonify({"error": "Укажите начало и конец периода."}), 400
        return jsonify(hero_development_report(start_value, end_value))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        app.logger.exception("Ошибка формирования отчёта развития героя")
        return jsonify({"error": "Не удалось загрузить отчёт развития героя."}), 500


@app.route("/api/heroes_not_in_rating")
def heroes_not_in_rating_api():
    try:
        return jsonify(heroes_not_in_rating_report())
    except Exception:
        app.logger.exception("Ошибка формирования отчёта героев вне рейтинга")
        return jsonify({"error": "Не удалось загрузить список героев вне рейтинга."}), 500


@app.route("/api/matches_period")
def matches_period_api():
    try:
        start_value = (request.args.get("start_date") or "").strip()
        end_value = (request.args.get("end_date") or "").strip()
        if not start_value or not end_value:
            return jsonify({"error": "Укажите начало и конец периода."}), 400
        return jsonify(matches_period_report(start_value, end_value))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        app.logger.exception("Ошибка формирования отчёта матчей за период")
        return jsonify({"error": "Не удалось загрузить матчи за период."}), 500
