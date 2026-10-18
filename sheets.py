import os
import json
import base64
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

    sheet = get_sheet("Dashboard")

    rows = sheet.get(
        "R3:S13"
    )


    return {

        "date": rows[1][1],


        "player1": rows[3][0],
        "hero1": rows[3][1],


        "player2": rows[5][0],
        "hero2": rows[5][1],


        "map": rows[7][1],


        "winner": rows[9][1]

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
