import time
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


def find_competition_info_by_country_id(competition_name: str, country_id: int) -> dict:
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


def get_current_league_standings(tournament_id: int, season_id: int) -> dict:
    url = f"{BASE_URL}/unique-tournament/{tournament_id}/season/{season_id}/standings/total"
    try:
        response = get(url)
        return response['standings'][0]['rows']
    except Exception:
        return []


def get_tournament_info_by_season_id(tournament_id: int, season_id: int) -> dict:
    url = f"{BASE_URL}/unique-tournament/{tournament_id}/season/{season_id}/statistics/info"
    return get(url)


def get_team_info(team_id: int) -> dict:
    url = f"{BASE_URL}/team/{team_id}"
    return get(url)


def get_team_stats_by_competition(team_id: int, tournament_id: int, season_id: int) -> dict:
    url = f"{BASE_URL}/team/{team_id}/unique-tournament/{tournament_id}/season/{season_id}/statistics/overall"
    try:
        response = get(url)
        return response['statistics']
    except Exception:
        return []