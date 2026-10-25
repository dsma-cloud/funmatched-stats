import os
import json
import base64
from datetime import date, datetime, timedelta
import gspread

from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


if os.getenv("GOOGLE_CREDENTIALS_BASE64"):
    info = json.loads(
        base64.b64decode(
            os.getenv("GOOGLE_CREDENTIALS_BASE64")
        )
    )

    creds = Credentials.from_service_account_info(
        info,
        scopes=SCOPES
    )

else:
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )


client = gspread.authorize(creds)


# ID твоей Google Таблицы
spreadsheet = client.open_by_key(
    "1LbIh-8yVWH6gRdSB5kZISEqvuc5CuYiHyC6wK45OHG0"
)



# =========================
# Получение листа
# =========================

def get_sheet(name):

    return spreadsheet.worksheet(name)



# =========================
# Поиск игроков
# =========================

def search_players(query):

    sheet = get_sheet("Players")

    rows = sheet.get_all_values()

    result = []

    query = query.lower().strip()


    for row in rows[1:]:

        if len(row) > 2:

            player_name = row[2]

            if query in player_name.lower():

                result.append(player_name)


    return result



# =========================
# Поиск героев
# =========================

def search_heroes(query):

    sheet = get_sheet("Heroes")

    rows = sheet.get_all_values()

    result = []

    query = query.lower().strip()


    for row in rows[1:]:

        if len(row) > 1:

            hero_name = row[1]

            if query in hero_name.lower():

                result.append(hero_name)


    return result



# =========================
# Поиск полей
# =========================

def search_maps(query):

    sheet = get_sheet("Maps")

    rows = sheet.get_all_values()

    result = []

    query = query.lower().strip()


    for row in rows[1:]:

        if len(row) > 1:

            map_name = row[1]

            if query in map_name.lower():

                result.append(map_name)


    return result



# =========================
# Добавление матча
# =========================

def add_match(match):

    sheet = get_sheet("Matches")


    # получаем следующий ID
    last_row = len(sheet.get_all_values())

    next_id = last_row


    sheet.append_row(
        [
            next_id,

            match["date"],

            match["player1"],

            match["hero1"],

            match["player2"],

            match["hero2"],

            match["map"],

            match["winner"],

            "",   # Duration

            ""    # Notes
        ]
    )
    
def get_hero_rating():

    sheet = get_sheet("Dashboard")

    rows = sheet.get(
        "H3:L33"
    )

    rating = []


    for row in rows[1:]:

        if len(row) >= 5 and row[1]:

            rating.append(
                {
                    "hero": row[1],
                    "games": row[2],
                    "wins": row[3],
                    "winrate": row[4]
                }
            )


    return rating


# =========================
# Данные для Mini App
# Dashboard
# =========================


def dashboard_players():

    sheet = get_sheet("Dashboard")

    rows = sheet.get(
        "A4:F23"
    )

    result = []


    for row in rows[1:]:

        if len(row) >= 6 and row[1]:

            result.append({

                "place": row[0],
                "player": row[1],
                "games": row[2],
                "wins": row[3],
                "losses": row[4],
                "winrate": row[5]

            })


    return result




def dashboard_heroes():

    sheet = get_sheet("Dashboard")

    rows = sheet.get(
        "H3:L160"
    )

    result = []


    for row in rows[1:]:

        if len(row) >= 5 and row[1]:

            result.append({

                "place": row[0],
                "hero": row[1],
                "games": row[2],
                "wins": row[3],
                "winrate": row[4]

            })


    return result




def dashboard_maps():

    sheet = get_sheet("Dashboard")

    rows = sheet.get(
        "N4:P23"
    )

    result = []


    for row in rows[1:]:

        if len(row) >= 3 and row[1]:

            result.append({

                "place": row[0],
                "map": row[1],
                "games": row[2]

            })


    return result
    
# =========================
# Последний матч
# Dashboard
# =========================

# =========================
# Последний матч
# Dashboard
# =========================

def dashboard_last_match():
    """Возвращает последний заполненный матч напрямую из листа Matches."""
    rows = get_sheet("Matches").get_all_values()

    # Структура Matches: ID, Date, Player1, Hero1, Player2, Hero2, Map, Winner, Duration, Notes
    # Идём с конца, чтобы пропускать пустые строки и брать последнюю запись.
    for row in reversed(rows[1:]):
        if len(row) < 8:
            continue

        player1 = row[2].strip() if len(row) > 2 else ""
        hero1 = row[3].strip() if len(row) > 3 else ""
        player2 = row[4].strip() if len(row) > 4 else ""
        hero2 = row[5].strip() if len(row) > 5 else ""

        # Пустые/служебные строки не считаем матчами.
        if not any((row[1].strip(), player1, hero1, player2, hero2)):
            continue

        return {
            "date": row[1].strip(),
            "player1": player1,
            "hero1": hero1,
            "player2": player2,
            "hero2": hero2,
            "map": row[6].strip() if len(row) > 6 else "",
            "winner": row[7].strip() if len(row) > 7 else ""
        }

    return {
        "date": "",
        "player1": "Нет матчей",
        "hero1": "",
        "player2": "",
        "hero2": "",
        "map": "",
        "winner": ""
    }


def dashboard_stats():

    sheet = client.open(
        "Unmatched Stats"
    ).worksheet(
        "Dashboard"
    )


    rows = sheet.get(
        "U4:V7"
    )


    return {

        "matches": rows[0][1],

        "players": rows[1][1],

        "heroes": rows[2][1],

        "maps": rows[3][1]

    }

# =========================
# Отчёт по выбранному герою
# =========================

def hero_match_report(hero_name):
    """Возвращает все матчи выбранного героя и сводную статистику."""
    hero_name = (hero_name or "").strip()
    if not hero_name:
        return {"hero": "", "stats": {"games": 0, "wins": 0, "losses": 0, "winrate": 0}, "wins": [], "losses": [], "unresolved": []}

    rows = get_sheet("Matches").get_all_values()
    wins, losses, unresolved = [], [], []
    target = hero_name.casefold()

    # Matches columns: ID, Date, Player1, Hero1, Player2, Hero2, Map, Winner, Duration, Notes
    for row in rows[1:]:
        row = row + [""] * max(0, 10 - len(row))
        match_id, date, player1, hero1, player2, hero2, map_name, winner = row[:8]
        side = 1 if hero1.strip().casefold() == target else (2 if hero2.strip().casefold() == target else 0)
        if not side:
            continue

        winner_text = winner.strip().casefold()
        player1_text = player1.strip().casefold()
        player2_text = player2.strip().casefold()
        won_side = 0
        if winner_text in {"player 1", "player1", "1", player1_text} and winner_text:
            won_side = 1
        elif winner_text in {"player 2", "player2", "2", player2_text} and winner_text:
            won_side = 2

        item = {
            "id": match_id, "date": date,
            "player1": player1, "hero1": hero1,
            "player2": player2, "hero2": hero2,
            "map": map_name, "winner": winner,
            "hero_player": player1 if side == 1 else player2,
            "opponent_player": player2 if side == 1 else player1,
            "opponent_hero": hero2 if side == 1 else hero1,
        }
        if not won_side:
            unresolved.append(item)
        elif won_side == side:
            wins.append(item)
        else:
            losses.append(item)

    games = len(wins) + len(losses) + len(unresolved)
    decided = len(wins) + len(losses)
    return {
        "hero": hero_name,
        "stats": {
            "games": games, "wins": len(wins), "losses": len(losses),
            "unresolved": len(unresolved),
            "winrate": round(len(wins) / decided * 100, 1) if decided else 0
        },
        "wins": wins, "losses": losses, "unresolved": unresolved
    }


# =========================
# Карточка выбранного игрока
# =========================
def player_match_report(player_name):
    """Возвращает статистику игрока, наиболее частые героя/поле и его матчи."""
    player_name = (player_name or "").strip()
    if not player_name:
        return {"player": "", "stats": {"games": 0, "wins": 0, "losses": 0, "unresolved": 0, "winrate": 0}, "favorite_hero": None, "favorite_map": None, "wins": [], "losses": [], "unresolved": []}

    rows = get_sheet("Matches").get_all_values()
    wins, losses, unresolved = [], [], []
    hero_counts, map_counts = {}, {}
    target = player_name.casefold()

    # Matches columns: ID, Date, Player1, Hero1, Player2, Hero2, Map, Winner, Duration, Notes
    for row in rows[1:]:
        row = row + [""] * max(0, 10 - len(row))
        match_id, date, player1, hero1, player2, hero2, map_name, winner = row[:8]
        p1_match = player1.strip().casefold() == target
        p2_match = player2.strip().casefold() == target
        if not p1_match and not p2_match:
            continue

        # В редком случае, когда имя указано с обеих сторон, учитываем сторону Player 1.
        side = 1 if p1_match else 2
        played_hero = hero1 if side == 1 else hero2
        if played_hero.strip():
            hero_counts[played_hero.strip()] = hero_counts.get(played_hero.strip(), 0) + 1
        if map_name.strip():
            map_counts[map_name.strip()] = map_counts.get(map_name.strip(), 0) + 1

        winner_text = winner.strip().casefold()
        player1_text = player1.strip().casefold()
        player2_text = player2.strip().casefold()
        won_side = 0
        if winner_text in {"player 1", "player1", "1", player1_text} and winner_text:
            won_side = 1
        elif winner_text in {"player 2", "player2", "2", player2_text} and winner_text:
            won_side = 2

        item = {
            "id": match_id, "date": date,
            "player1": player1, "hero1": hero1,
            "player2": player2, "hero2": hero2,
            "map": map_name, "winner": winner,
            "player_hero": played_hero,
            "opponent": player2 if side == 1 else player1,
            "opponent_hero": hero2 if side == 1 else hero1,
        }
        if not won_side:
            unresolved.append(item)
        elif won_side == side:
            wins.append(item)
        else:
            losses.append(item)

    games = len(wins) + len(losses) + len(unresolved)
    decided = len(wins) + len(losses)
    favorite_hero = max(hero_counts.items(), key=lambda pair: pair[1]) if hero_counts else None
    favorite_map = max(map_counts.items(), key=lambda pair: pair[1]) if map_counts else None
    return {
        "player": player_name,
        "stats": {
            "games": games, "wins": len(wins), "losses": len(losses),
            "unresolved": len(unresolved),
            "winrate": round(len(wins) / decided * 100, 1) if decided else 0
        },
        "favorite_hero": {"name": favorite_hero[0], "games": favorite_hero[1]} if favorite_hero else None,
        "favorite_map": {"name": favorite_map[0], "games": favorite_map[1]} if favorite_map else None,
        "wins": wins, "losses": losses, "unresolved": unresolved
    }


# =========================
# Противостояние двух героев
# =========================
def hero_head_to_head_report(hero1_name, hero2_name):
    """Все матчи между двумя героями и их результаты в очных встречах."""
    hero1_name = (hero1_name or "").strip()
    hero2_name = (hero2_name or "").strip()
    empty_stats = {"games": 0, "wins": 0, "losses": 0, "unresolved": 0, "winrate": 0}
    if not hero1_name or not hero2_name or hero1_name.casefold() == hero2_name.casefold():
        return {"hero1": hero1_name, "hero2": hero2_name, "stats1": empty_stats.copy(), "stats2": empty_stats.copy(), "matches": []}

    rows = get_sheet("Matches").get_all_values()
    matches = []
    wins1 = wins2 = unresolved = 0
    target1, target2 = hero1_name.casefold(), hero2_name.casefold()

    # Matches columns: ID, Date, Player1, Hero1, Player2, Hero2, Map, Winner, Duration, Notes
    for row in rows[1:]:
        row = row + [""] * max(0, 10 - len(row))
        match_id, date, player1, hero1, player2, hero2, map_name, winner = row[:8]
        side1_hero, side2_hero = hero1.strip().casefold(), hero2.strip().casefold()
        if not ((side1_hero == target1 and side2_hero == target2) or
                (side1_hero == target2 and side2_hero == target1)):
            continue

        winner_text = winner.strip().casefold()
        player1_text, player2_text = player1.strip().casefold(), player2.strip().casefold()
        won_side = 0
        if winner_text in {"player 1", "player1", "1", player1_text} and winner_text:
            won_side = 1
        elif winner_text in {"player 2", "player2", "2", player2_text} and winner_text:
            won_side = 2

        # Определяем, какой из выбранных героев находился на победившей стороне.
        if not won_side:
            result_for_hero1 = "unresolved"
            unresolved += 1
        else:
            winning_hero = hero1 if won_side == 1 else hero2
            if winning_hero.strip().casefold() == target1:
                result_for_hero1 = "win"
                wins1 += 1
            else:
                result_for_hero1 = "loss"
                wins2 += 1

        matches.append({
            "id": match_id, "date": date, "player1": player1, "hero1": hero1,
            "player2": player2, "hero2": hero2, "map": map_name, "winner": winner,
            "result_for_hero1": result_for_hero1,
            "result_for_hero2": ("unresolved" if result_for_hero1 == "unresolved" else "loss" if result_for_hero1 == "win" else "win")
        })

    total = len(matches)
    decided = wins1 + wins2
    stats1 = {"games": total, "wins": wins1, "losses": wins2, "unresolved": unresolved, "winrate": round(wins1 / decided * 100, 1) if decided else 0}
    stats2 = {"games": total, "wins": wins2, "losses": wins1, "unresolved": unresolved, "winrate": round(wins2 / decided * 100, 1) if decided else 0}
    return {"hero1": hero1_name, "hero2": hero2_name, "stats1": stats1, "stats2": stats2, "matches": matches}


# =========================
# Противостояние двух игроков
# =========================
def player_head_to_head_report(player1_name, player2_name):
    """Все матчи, в которых два выбранных игрока выступали друг против друга."""
    player1_name = (player1_name or "").strip()
    player2_name = (player2_name or "").strip()
    empty_stats = {"games": 0, "wins": 0, "losses": 0, "unresolved": 0, "winrate": 0}
    if not player1_name or not player2_name or player1_name.casefold() == player2_name.casefold():
        return {"player1": player1_name, "player2": player2_name, "stats1": empty_stats.copy(), "stats2": empty_stats.copy(), "matches": []}

    rows = get_sheet("Matches").get_all_values()
    matches = []
    wins1 = wins2 = unresolved = 0
    target1, target2 = player1_name.casefold(), player2_name.casefold()

    # Matches columns: ID, Date, Player1, Hero1, Player2, Hero2, Map, Winner, Duration, Notes
    for row in rows[1:]:
        row = row + [""] * max(0, 10 - len(row))
        match_id, date, player1, hero1, player2, hero2, map_name, winner = row[:8]
        side1_player, side2_player = player1.strip().casefold(), player2.strip().casefold()
        if not ((side1_player == target1 and side2_player == target2) or
                (side1_player == target2 and side2_player == target1)):
            continue

        winner_text = winner.strip().casefold()
        player1_text, player2_text = player1.strip().casefold(), player2.strip().casefold()
        won_side = 0
        if winner_text in {"player 1", "player1", "1", player1_text} and winner_text:
            won_side = 1
        elif winner_text in {"player 2", "player2", "2", player2_text} and winner_text:
            won_side = 2

        if not won_side:
            result_for_player1 = "unresolved"
            unresolved += 1
        else:
            winning_player = player1 if won_side == 1 else player2
            if winning_player.strip().casefold() == target1:
                result_for_player1 = "win"
                wins1 += 1
            else:
                result_for_player1 = "loss"
                wins2 += 1

        matches.append({
            "id": match_id, "date": date, "player1": player1, "hero1": hero1,
            "player2": player2, "hero2": hero2, "map": map_name, "winner": winner,
            "result_for_player1": result_for_player1,
            "result_for_player2": ("unresolved" if result_for_player1 == "unresolved" else "loss" if result_for_player1 == "win" else "win")
        })

    total = len(matches)
    decided = wins1 + wins2
    stats1 = {"games": total, "wins": wins1, "losses": wins2, "unresolved": unresolved, "winrate": round(wins1 / decided * 100, 1) if decided else 0}
    stats2 = {"games": total, "wins": wins2, "losses": wins1, "unresolved": unresolved, "winrate": round(wins2 / decided * 100, 1) if decided else 0}
    return {"player1": player1_name, "player2": player2_name, "stats1": stats1, "stats2": stats2, "matches": matches}


# =========================
# Рейтинг игроков за последние 7 дней
# =========================
def player_rating_last_7_days():
    """Рейтинг по матчам за последние 7 календарных дней, включая сегодня."""
    today = date.today()
    first_day = today - timedelta(days=6)
    rows = get_sheet("Matches").get_all_values()
    stats = {}

    def parse_match_date(value):
        value = (value or "").strip()
        if not value:
            return None
        # Google Sheets / HTML date input commonly use ISO; support common display formats too.
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(value[:10], fmt).date()
            except ValueError:
                pass
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None

    for row in rows[1:]:
        row = row + [""] * max(0, 8 - len(row))
        _, match_date, player1, _, player2, _, _, winner = row[:8]
        parsed_date = parse_match_date(match_date)
        if parsed_date is None or not (first_day <= parsed_date <= today):
            continue
        p1, p2 = player1.strip(), player2.strip()
        if not p1 or not p2:
            continue
        for player in {p1, p2}:
            if player not in stats:
                stats[player] = {"player": player, "games": 0, "wins": 0, "losses": 0, "unresolved": 0}
            stats[player]["games"] += 1

        winner_text = winner.strip().casefold()
        p1_won = winner_text in {"player 1", "player1", "1", p1.casefold()}
        p2_won = winner_text in {"player 2", "player2", "2", p2.casefold()}
        if p1_won and not p2_won:
            stats[p1]["wins"] += 1
            stats[p2]["losses"] += 1
        elif p2_won and not p1_won:
            stats[p2]["wins"] += 1
            stats[p1]["losses"] += 1
        else:
            stats[p1]["unresolved"] += 1
            stats[p2]["unresolved"] += 1

    result = list(stats.values())
    for item in result:
        decided = item["wins"] + item["losses"]
        item["winrate"] = round(item["wins"] / decided * 100, 1) if decided else 0
    result.sort(key=lambda item: (item["wins"], item["winrate"], item["games"], item["player"].casefold()), reverse=True)
    return {"from": first_day.isoformat(), "to": today.isoformat(), "players": result}


# =========================
# Развитие героя: переход между группами рейтинга за выбранный период
# =========================
def hero_development_report(start_value, end_value):
    """Сравнивает all-time win rate до начала периода и после его окончания."""
    start_day = datetime.strptime(start_value, "%Y-%m-%d").date()
    end_day = datetime.strptime(end_value, "%Y-%m-%d").date()
    if end_day < start_day:
        raise ValueError("Дата окончания периода должна быть не раньше даты начала.")

    rows = get_sheet("Matches").get_all_values()
    stats = {}

    def parse_match_date(value):
        value = (value or "").strip()
        if not value:
            return None
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(value[:10], fmt).date()
            except ValueError:
                pass
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None

    def ensure(hero):
        if hero and hero not in stats:
            stats[hero] = {
                "hero": hero, "before_wins": 0, "before_losses": 0,
                "after_wins": 0, "after_losses": 0, "period_games": 0,
                "period_wins": 0, "period_losses": 0
            }
        return stats.get(hero)

    for row in rows[1:]:
        row = row + [""] * max(0, 8 - len(row))
        _, match_date, player1, hero1, player2, hero2, _, winner = row[:8]
        match_day = parse_match_date(match_date)
        if match_day is None or match_day > end_day:
            continue
        hero1, hero2 = hero1.strip(), hero2.strip()
        winner_text = winner.strip().casefold()
        p1_won = winner_text in {"player 1", "player1", "1", player1.strip().casefold()}
        p2_won = winner_text in {"player 2", "player2", "2", player2.strip().casefold()}
        if p1_won == p2_won:
            continue  # матч без однозначного победителя не влияет на win rate
        for hero, won in ((hero1, p1_won), (hero2, p2_won)):
            item = ensure(hero)
            if not item:
                continue
            if match_day < start_day:
                item["before_wins" if won else "before_losses"] += 1
                item["after_wins" if won else "after_losses"] += 1
            else:
                item["after_wins" if won else "after_losses"] += 1
                item["period_games"] += 1
                item["period_wins" if won else "period_losses"] += 1

    def group(rate):
        if rate >= 75: return "Мета"
        if rate >= 60: return "Сильные"
        if rate >= 45: return "Стабильные"
        return "Остальные"

    result = []
    for item in stats.values():
        before_decided = item["before_wins"] + item["before_losses"]
        after_decided = item["after_wins"] + item["after_losses"]
        if not item["period_games"] or not before_decided or not after_decided:
            continue
        before_rate = round(item["before_wins"] / before_decided * 100, 1)
        after_rate = round(item["after_wins"] / after_decided * 100, 1)
        before_group, after_group = group(before_rate), group(after_rate)
        if before_group == after_group:
            continue
        result.append({
            "hero": item["hero"], "from_group": before_group, "to_group": after_group,
            "before_winrate": before_rate, "after_winrate": after_rate,
            "change": round(after_rate - before_rate, 1),
            "period_games": item["period_games"], "period_wins": item["period_wins"],
            "period_losses": item["period_losses"]
        })
    result.sort(key=lambda item: (abs(item["change"]), item["period_games"]), reverse=True)
    return {"from": start_day.isoformat(), "to": end_day.isoformat(), "heroes": result}


def heroes_not_in_rating_report():
    """Список героев, сыгравших менее 30 матчей, по группам в 10 игр."""
    heroes_rows = get_sheet("Heroes").get_all_values()
    matches_rows = get_sheet("Matches").get_all_values()

    # Каталог героев: название хранится во втором столбце листа Heroes.
    names = {}
    for row in heroes_rows[1:]:
        if len(row) > 1 and row[1].strip():
            name = row[1].strip()
            names.setdefault(name.casefold(), name)

    counts = {key: 0 for key in names}
    # Matches columns: ID, Date, Player1, Hero1, Player2, Hero2, Map, Winner, ...
    for row in matches_rows[1:]:
        row = row + [""] * max(0, 6 - len(row))
        for index in (3, 5):
            hero = row[index].strip()
            if hero:
                key = hero.casefold()
                if key not in names:
                    names[key] = hero
                    counts[key] = 0
                counts[key] = counts.get(key, 0) + 1

    heroes = [
        {"hero": names[key], "games": games}
        for key, games in counts.items() if games < 30
    ]
    heroes.sort(key=lambda item: (-item["games"], item["hero"].casefold()))

    groups = []
    for lower in (0, 10, 20):
        upper = lower + 9
        items = [hero for hero in heroes if lower <= hero["games"] <= upper]
        groups.append({"min_games": lower, "max_games": upper, "count": len(items), "heroes": items})
    return {"total": len(heroes), "groups": groups}



def matches_period_report(start_value, end_value):
    """Матчи за указанный период, сгруппированные по героям."""
    start_day = datetime.strptime(start_value, "%Y-%m-%d").date()
    end_day = datetime.strptime(end_value, "%Y-%m-%d").date()
    if end_day < start_day:
        raise ValueError("Дата окончания периода должна быть не раньше даты начала.")

    rows = get_sheet("Matches").get_all_values()
    grouped = {}

    def parse_date(value):
        value = (value or "").strip()
        if not value:
            return None
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(value[:10], fmt).date()
            except ValueError:
                pass
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None

    total_match_keys = set()
    for row in rows[1:]:
        row = row + [""] * max(0, 8 - len(row))
        match_id, date_value, player1, hero1, player2, hero2, map_name, winner = row[:8]
        day = parse_date(date_value)
        if day is None or not (start_day <= day <= end_day):
            continue
        match = {
            "id": match_id.strip(), "date": day.strftime("%d.%m.%Y"),
            "player1": player1.strip(), "hero1": hero1.strip(),
            "player2": player2.strip(), "hero2": hero2.strip(),
            "map": map_name.strip(), "winner": winner.strip()
        }
        total_match_keys.add(match_id.strip() or f"{date_value}|{player1}|{hero1}|{player2}|{hero2}")
        for hero in {hero1.strip(), hero2.strip()}:
            if hero:
                grouped.setdefault(hero.casefold(), {"hero": hero.strip(), "matches": []})["matches"].append(match)

    groups = list(grouped.values())
    for group in groups:
        group["matches"].sort(key=lambda item: (item["date"], item["id"]), reverse=True)
        group["count"] = len(group["matches"])
    groups.sort(key=lambda item: item["hero"].casefold())
    return {"from": start_day.isoformat(), "to": end_day.isoformat(), "total": len(total_match_keys), "groups": groups}



def period_summary_report(start_value, end_value):
    """Комплексный отчёт за период: игроки, лидеры, изменение рейтинга героев и близкие к рейтингу."""
    start_day = datetime.strptime(start_value, "%Y-%m-%d").date()
    end_day = datetime.strptime(end_value, "%Y-%m-%d").date()
    if end_day < start_day:
        raise ValueError("Дата окончания периода должна быть не раньше даты начала.")

    rows = get_sheet("Matches").get_all_values()
    matches = []

    def parse_date(value):
        value = (value or "").strip()
        if not value:
            return None
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(value[:10], fmt).date()
            except ValueError:
                pass
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None

    for row in rows[1:]:
        row = row + [""] * max(0, 8 - len(row))
        match_id, date_value, p1, h1, p2, h2, map_name, winner = row[:8]
        day = parse_date(date_value)
        if day is None:
            continue
        winner_text = winner.strip().casefold()
        p1_won = winner_text in {"player 1", "player1", "1", p1.strip().casefold()}
        p2_won = winner_text in {"player 2", "player2", "2", p2.strip().casefold()}
        matches.append({"day": day, "p1": p1.strip(), "h1": h1.strip(), "p2": p2.strip(), "h2": h2.strip(),
                        "map": map_name.strip(), "winner": winner.strip(), "p1_won": p1_won, "p2_won": p2_won,
                        "decided": p1_won != p2_won})

    # 1. Player rating for the selected period.
    player_stats = {}
    favorite_hero = {}
    favorite_map = {}
    for m in matches:
        if not (start_day <= m["day"] <= end_day):
            continue
        for player, hero, won, lost in ((m["p1"], m["h1"], m["p1_won"], m["p2_won"]),
                                        (m["p2"], m["h2"], m["p2_won"], m["p1_won"])):
            if not player:
                continue
            st = player_stats.setdefault(player, {"player": player, "games": 0, "wins": 0, "losses": 0, "unresolved": 0})
            st["games"] += 1
            if m["decided"]:
                st["wins"] += int(won)
                st["losses"] += int(lost)
            else:
                st["unresolved"] += 1
            if hero:
                favorite_hero.setdefault(player, {})[hero] = favorite_hero.setdefault(player, {}).get(hero, 0) + 1
            if m["map"]:
                favorite_map.setdefault(player, {})[m["map"]] = favorite_map.setdefault(player, {}).get(m["map"], 0) + 1

    players = list(player_stats.values())
    for player in players:
        decided = player["wins"] + player["losses"]
        player["winrate"] = round(player["wins"] / decided * 100, 1) if decided else 0
        player["favorite_hero"] = max(favorite_hero.get(player["player"], {}).items(), key=lambda x: (x[1], x[0].casefold()))[0] if favorite_hero.get(player["player"]) else "—"
        player["favorite_map"] = max(favorite_map.get(player["player"], {}).items(), key=lambda x: (x[1], x[0].casefold()))[0] if favorite_map.get(player["player"]) else "—"
    players.sort(key=lambda x: (-x["wins"], -x["winrate"], -x["games"], x["player"].casefold()))

    # 2. Top three leaders.
    leaders = players[:3]

    # 3. Compare hero rank and win rate before the period vs at period end.
    hero_names = {}
    hero_stats_before = {}
    hero_stats_after = {}
    hero_total_counts = {}
    for m in matches:
        for hero in (m["h1"], m["h2"]):
            if hero:
                hero_names.setdefault(hero.casefold(), hero)
                hero_total_counts[hero.casefold()] = hero_total_counts.get(hero.casefold(), 0) + 1
        if m["day"] > end_day:
            continue
        for hero, won, played in ((m["h1"], m["p1_won"], m["p1_won"] or m["p2_won"]),
                                  (m["h2"], m["p2_won"], m["p1_won"] or m["p2_won"])):
            if not hero:
                continue
            key = hero.casefold()
            if m["day"] < start_day:
                st = hero_stats_before.setdefault(key, {"games": 0, "decided": 0, "wins": 0})
                st["games"] += 1
                if played:
                    st["decided"] += 1; st["wins"] += int(won)
            st = hero_stats_after.setdefault(key, {"games": 0, "decided": 0, "wins": 0})
            st["games"] += 1
            if played:
                st["decided"] += 1; st["wins"] += int(won)

    def ranked(stats):
        eligible = []
        for key, st in stats.items():
            if st["games"] >= 30 and st["decided"]:
                rate = st["wins"] / st["decided"] * 100
                eligible.append({"key": key, "hero": hero_names.get(key, key), "games": st["games"], "winrate": round(rate, 1)})
        eligible.sort(key=lambda x: (-x["winrate"], -x["games"], x["hero"].casefold()))
        for i, item in enumerate(eligible, 1): item["rank"] = i
        return {x["key"]: x for x in eligible}

    before_rank, after_rank = ranked(hero_stats_before), ranked(hero_stats_after)
    hero_changes = []
    for key in set(before_rank) & set(after_rank):
        old, new = before_rank[key], after_rank[key]
        rank_change = old["rank"] - new["rank"]
        rate_change = round(new["winrate"] - old["winrate"], 1)
        if rank_change or rate_change:
            hero_changes.append({"hero": new["hero"], "rank_before": old["rank"], "rank_after": new["rank"],
                                 "rank_change": rank_change, "winrate_before": old["winrate"],
                                 "winrate_after": new["winrate"], "winrate_change": rate_change,
                                 "games_before": old["games"], "games_after": new["games"]})
    hero_changes.sort(key=lambda x: (-abs(x["rank_change"]), -abs(x["winrate_change"]), x["hero"].casefold()))

    # 4. Heroes with 25–29 games as of the selected end date.
    near_rating = [{"hero": hero_names[key], "games": count} for key, count in hero_total_counts.items()
                   if count < 30 and count >= 25 and any(m["day"] <= end_day and key in {m["h1"].casefold(), m["h2"].casefold()} for m in matches)]
    # Recount strictly through the selected end date (including heroes not seen later).
    counts_at_end = {}
    for m in matches:
        if m["day"] <= end_day:
            for hero in (m["h1"], m["h2"]):
                if hero: counts_at_end[hero.casefold()] = counts_at_end.get(hero.casefold(), 0) + 1
    near_rating = [{"hero": hero_names.get(key, key), "games": count} for key, count in counts_at_end.items() if 25 <= count <= 29]
    near_rating.sort(key=lambda x: (-x["games"], x["hero"].casefold()))

    return {"from": start_day.isoformat(), "to": end_day.isoformat(), "players": players,
            "leaders": leaders, "hero_changes": hero_changes, "near_rating": near_rating}
