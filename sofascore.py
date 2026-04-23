import time
import pandas as pd
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.sofascore.com/api/v1"

_playwright = None
_browser = None
_context = None
_page = None

def _init_browser():
    global _playwright, _browser, _context, _page

    if _page is not None:
        return _page

    _playwright = sync_playwright().start()

    _browser = _playwright.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ]
    )

    _context = _browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0"
    )

    _page = _context.new_page()

    return _page


def close_browser():
    global _playwright, _browser, _context, _page

    if _browser:
        _browser.close()
    if _playwright:
        _playwright.stop()

    _playwright = _browser = _context = _page = None


def get(url, retries=2):
    if retries == 0:
        return None

    page = _init_browser()

    try:
        response = page.goto(url, wait_until="networkidle", timeout=10000)

        if not response:
            return get(url, retries - 1)

        if response.status == 200:
            return response.json()

        if response.status == 403:
            time.sleep(1)
            return get(url, retries - 1)

        raise Exception(f"Failed to fetch {url}: {response.status}")

    except Exception as e:
        print(f"Error performing request: {e}")
        time.sleep(1)
        return get(url, retries - 1)


def search_all_by_keyword(keyword: str)-> list:
    url = f'https://www.sofascore.com/api/v1/search/all?q={keyword}&page=0'
    try:
        response = get(url)
        return response.get('results', []) if response else []
    except Exception:
        return []


def search_team_by_keyword(keyword: str)-> list:
    url = f'https://www.sofascore.com/api/v1/search/teams?q={keyword}&page=0'
    try:
        response = get(url)
        return response.get('results', []) if response else []
    except Exception:
        return []


def search_competition_by_keyword(keyword: str)-> list:
    url = f'https://www.sofascore.com/api/v1/search/unique-tournaments?q={keyword}&page=0'
    try:
        response = get(url)
        return response.get('results', []) if response else []
    except Exception:
        return []


def get_all_countries_by_sport(sport: str) -> list:
    url = f"{BASE_URL}/sport/{sport}/categories/all"
    try:
        response = get(url)
        return response.get('categories', []) if response else []
    except Exception:
        return []
    

def get_country_info_by_sport(country_name: str, sport: str) -> dict:
    countries = get_all_countries_by_sport(sport)
    for country in countries:
        name = country.get('name')
        if name.lower() == country_name.lower():
            return country
        
    return None


def get_all_competitions_by_country_id(country_id: int) -> list:
    url = f"{BASE_URL}/category/{country_id}/unique-tournaments"
    try:
        response = get(url)
        return response['groups'][0]['uniqueTournaments'] if response else []
    except Exception:
        return []


def get_competition_info_by_country_id(competition_name: str, country_id: int) -> dict:
    comps = get_all_competitions_by_country_id(country_id)
    for tournament in comps:
        name = tournament.get('name')
        if name.lower() == competition_name.lower():
            return tournament
        
    return None


def get_seasons_by_tournament_id(tournament_id: int) -> list:
    url = f"{BASE_URL}/unique-tournament/{tournament_id}/seasons"
    try:
        response = get(url)
        return response.get('seasons', []) if response else []
    except Exception:
        return []


def get_current_league_standings_by_id(tournament_id: int, season_id: int) -> dict:
    url = f"{BASE_URL}/unique-tournament/{tournament_id}/season/{season_id}/standings/total"
    try:
        response = get(url)
        return response['standings'][0]['rows']
    except Exception:
        return []
    

def get_country_competition_season_ids(sport: str, country_name: str, competition_name: str, seasons_ago: int = 0) -> tuple:
    country_entry = get_country_info_by_sport(country_name, sport)
    country_id = country_entry.get('id')

    comp_entry = get_competition_info_by_country_id(competition_name, country_id)
    comp_id = comp_entry.get('id')

    seasons = get_seasons_by_tournament_id(comp_id)
    season_id = seasons[seasons_ago].get('id')

    return (country_id, comp_id, season_id)
    
    
def get_league_standings_by_name(sport: str, country_name: str, competition_name: str, seasons_ago: int = 0) -> dict:
    country_id, comp_id, season_id = get_country_competition_season_ids(sport, country_name, competition_name, seasons_ago)
    return get_current_league_standings_by_id(comp_id, season_id)


def get_tournament_info_by_season_id(tournament_id: int, season_id: int) -> dict:
    url = f"{BASE_URL}/unique-tournament/{tournament_id}/season/{season_id}/info"
    try:
        response = get(url)
        return response['info']
    except Exception:
        return {}


def get_tournament_stats_info_by_season_id(tournament_id: int, season_id: int) -> dict:
    url = f"{BASE_URL}/unique-tournament/{tournament_id}/season/{season_id}/statistics/info"
    try:
        response = get(url)
        return response
    except Exception:
        return {}


def get_team_info(team_id: int) -> dict:
    url = f"{BASE_URL}/team/{team_id}"
    try:
        response = get(url)
        return response
    except Exception:
        return {}


def get_team_stats_by_competition(team_id: int, tournament_id: int, season_id: int) -> dict:
    url = f"{BASE_URL}/team/{team_id}/unique-tournament/{tournament_id}/season/{season_id}/statistics/overall"
    try:
        response = get(url)
        return response['statistics']
    except Exception:
        return {}
    

def get_scheduled_rounds_by_competition_season_id(competition_id: int, season_id: int) -> dict:
    url = f'{BASE_URL}/unique-tournament/{competition_id}/season/{season_id}/rounds'
    try:
        response = get(url)
        return response
    except Exception:
        return {}
    

def get_current_round_number_by_competition_season_id(competition_id: int, season_id: int) -> int:
    rounds = get_scheduled_rounds_by_competition_season_id(competition_id, season_id)
    try:
        return rounds['currentRound']['round']
    except Exception:
        return -1


def get_all_matches_by_competition_season_id(competition_id: int, season_id: int) -> list:
    url = f'{BASE_URL}/unique-tournament/{competition_id}/season/{season_id}/events/round'
    matches = []
    try:
        rounds = get_scheduled_rounds_by_competition_season_id(competition_id, season_id)['rounds']
        highest = 0
        for round in rounds:
            number = round['round']
            if number > highest:
                highest = number
        for i in range(highest):
            response = get(f'{url}/{i + 1}')
            matches += response['events']
        return matches
    except Exception:
        return []
    

def get_all_matches_by_competition_name(sport: str, country_name: str, competition_name: str, seasons_ago: int = 0) -> list:
    country_id, comp_id, season_id = get_country_competition_season_ids(sport, country_name, competition_name, seasons_ago)
    return get_all_matches_by_competition_season_id(comp_id, season_id)


def get_incidents_by_match_id(match_id: int) -> list:
    url = f'{BASE_URL}/event/{match_id}/incidents'
    try:
        response = get(url)
        return response['incidents']
    except Exception:
        return []
    

def stats_dataframe_by_competition(sport: str, country_name: str, competition_name: str, seasons_ago: int = 0) -> dict:
    country_id, comp_id, season_id = get_country_competition_season_ids(sport, country_name, competition_name, seasons_ago)

    current_standings = get_current_league_standings_by_id(comp_id, season_id)

    df_cols = None
    rows = []
    index = []

    for entry in current_standings:
        team_info = entry.get('team')
        team_id = team_info.get('id')
        team_name = team_info.get('name')
        team_stats = get_team_stats_by_competition(team_id, comp_id, season_id)
        team_stats.pop('statisticsType')

        if df_cols is None:
            df_cols = ['points', 'wins', 'losses', 'draws'] + list(team_stats.keys())

        team_stats.update(entry)
        row = [team_stats[field] for field in df_cols]
        index.append(team_name)
        rows.append(row)

    df = pd.DataFrame(rows, columns=df_cols, index=index)
    return df


def team_stats_dataframe_by_competition(sport: str, country_name: str, competition_name: str, team_id: int, seasons_ago: int = 0) -> dict:
    df_cols = None
    dicts = []

    for i in range(seasons_ago + 1):
        country_id, comp_id, season_id = get_country_competition_season_ids(sport, country_name, competition_name, i)
        current_standings = get_current_league_standings_by_id(comp_id, season_id)

        entry = None
        for team in current_standings:
            if team_id == team['team']['id']:
                entry = team
        if entry is None:
            return {}

        team_stats = get_team_stats_by_competition(team_id, comp_id, season_id)
        
        current_cols = set(['points', 'wins', 'losses', 'draws'] + list(team_stats.keys()))
        if df_cols == None:
            df_cols = current_cols
        else:
            df_cols = df_cols.intersection(current_cols)

        team_stats.update(entry)
        dicts.append(team_stats)
    
    df_cols = list(df_cols)
    rows = []
    for dict in dicts:
        row = [dict[col] for col in df_cols]
        rows.append(row)

    return pd.DataFrame(rows, columns=df_cols)