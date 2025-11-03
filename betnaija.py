import logging
import requests

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BET9JA_GET_BASE = "https://coupon.bet9ja.com/desktop/feapi/CouponAjax/GetBookABetCoupon"
BET9JA_CREATE_BASE = "https://apigw.bet9ja.com/sportsbook/placebet/BookABetV2"

BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://coupon.bet9ja.com/',
    'Origin': 'https://coupon.bet9ja.com',
}


def get_games(bet_code: str):
    """Fetch games from Bet9ja booking code"""
    url = f"{BET9JA_GET_BASE}?couponCode={bet_code}&v_cache_version=1.295.4.219"
    logger.info(f"Fetching: {url}")

    try:
        resp = requests.get(url, headers=BROWSER_HEADERS, timeout=15)
        data = resp.json()
        logger.info(f"Status: {resp.status_code}, Response R: {data.get('R')}")
    except Exception as e:
        raise ValueError(f'Network error: {str(e)}')

    if data.get('R') != 'OK':
        raise ValueError('Invalid Bet9ja Code')

    games_dict = data.get('D', {}).get('O', {})
    if not games_dict:
        raise ValueError('No games found in this booking code')

    games_details = []
    for sel_id, game in games_dict.items():
        games_details.append({
            'id': sel_id,
            'E_ID': int(game.get('E_ID', 0)),
            'E_C': game.get('E_C', ''),
            'E_NAME': game.get('E_NAME', 'Unknown'),
            'SGN': game.get('SGN', 'Unknown'),
            'M_NAME': game.get('M_NAME', 'Unknown'),
            'V': game.get('V', '1.0'),
            'GID': game.get('GID', ''),
            'SGID': game.get('SGID', ''),
            'SPORT_ID': game.get('SPORT_ID', 1),
            'odds_display': float(game.get('V', 1.0))
        })

    logger.info(f"Found {len(games_details)} games")
    return games_details


def bet9ja_create_ticket(games):
    """Create new Bet9ja booking code"""
    import json

    logger.info(f"Creating ticket with {len(games)} games")

    # Build BETLINES exactly like the response structure
    betlines = {}
    odds_dict = {}
    bets = []

    odds_min = 1

    for game in games:
        game_id = game.get('id')
        betlines[game_id] = {
            "eventId": str(game.get('E_ID')),
            "eventName": game.get('E_NAME'),
            "market": "S_1X2",
            "marketName": f"1X2 {game.get('SGN')}",
            "marketNameNoSign": "1X2",
            "sign": game.get('SGN'),
            "sid": f"S_1X2_{game.get('SGN')}",
            "sportId": game.get('SPORT_ID', 1),
            "id": game_id
        }
        odds_dict[game_id] = float(game.get('V'))
        odds_min *= float(game.get('V'))

    bets.append({
        "BSTYPE": 0,
        "TAB": 0,
        "NUMLINES": len(games),
        "COMB": 1,
        "TYPE": len(games),
        "STAKE": 0,
        "POTWINMIN": 0,
        "POTWINMAX": 0,
        "BONUSMIN": 0,
        "BONUSMAX": 0,
        "ODDMIN": odds_min,
        "ODDMAX": odds_min,
        "ODDS": odds_dict,
        "FIXED": {}
    })

    betslip_data = {
        # "BETLINES": betlines,
        # "SUBBETS": [{
        #     "TYPE": len(games),
        #     "COMB": 1,
        #     "ODDS": odds_dict
        # }],
        "BETS": bets,
        "EVS": betlines,
        "IMPERSONIZE": 0
    }

    url = f"{BET9JA_CREATE_BASE}?source=desktop&v_cache_version=1.295.4.219"

    # CRITICAL: Send as form data with BETSLIP parameter
    form_data = {
        'BETSLIP': json.dumps(betslip_data)
    }

    headers = BROWSER_HEADERS.copy()
    headers['Content-Type'] = 'application/x-www-form-urlencoded'

    logger.info(f"POST URL: {url}")
    logger.info(f"Sending BETSLIP with {len(games)} games")

    try:
        resp = requests.post(url, data=form_data, headers=headers, timeout=20)
        logger.info(f"Response Status: {resp.status_code}")

        data = resp.json()
        logger.info(f"Create Response status: {data.get('status')}")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        raise Exception(f'Network error: {str(e)}')

    # Check if successful (status = 1)
    if data.get('status') != 1:
        error = data.get('error', {}).get(
            'message', 'Failed to create booking code')
        logger.error(f"Create failed: {error}")
        logger.error(f"Full response: {data}")
        raise Exception(f'Bet9ja Error: {error}')

    # Extract RIS (booking code)
    response_data = data.get('data', [])
    if response_data and len(response_data) > 0:
        code = response_data[0].get('RIS')
    else:
        code = None

    if not code:
        logger.error(f"No RIS in response: {data}")
        raise Exception("No booking code in response")

    logger.info(f"✅ SUCCESS! New booking code: {code}")
    return str(code)


if __name__ == "__main__":
    # Example runner / demo usage
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description='Demo runner for betnaija helpers')
    parser.add_argument(
        '--code', '-c', help='A Bet9ja booking code to fetch games for')
    parser.add_argument('--create', action='store_true',
                        help='If set, create a new booking code from the sample games (will POST)')
    args = parser.parse_args()

    if args.code:
        # Fetch and display games for a real booking code
        try:
            games = get_games(args.code)
            print('\nFetched games:')
            print(json.dumps(games, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Failed to fetch games for code {args.code}: {e}")

    else:
        # Show a safe example with sample games. This does not perform network I/O by default.
        sample_games = [
            {
                "id": "669990094$S_1X2_1",
                "E_ID": 669990094,
                "E_C": "2312",
                "E_NAME": "Atl. Madrid - Union St. Gilloise",
                "SGN": "1",
                "M_NAME": "1X2",
                "V": "1.28",
                "GID": 5468459,
                "SGID": 11418,
                "SPORT_ID": 1,
                "odds_display": 1.28
            },
            {
                "id": "670431291$S_1X2_2",
                "E_ID": 670431291,
                "E_C": "3035",
                "E_NAME": "Slavia Prague - Arsenal",
                "SGN": "2",
                "M_NAME": "1X2",
                "V": "1.28",
                "GID": 5468459,
                "SGID": 11418,
                "SPORT_ID": 1,
                "odds_display": 1.28
            },
            {
                "id": "670487424$S_1X2_1",
                "E_ID": 670487424,
                "E_C": "2470",
                "E_NAME": "Napoli - Eintracht Frankfurt",
                "SGN": "1",
                "M_NAME": "1X2",
                "V": "1.62",
                "GID": 5468459,
                "SGID": 11418,
                "SPORT_ID": 1,
                "odds_display": 1.62
            }
        ]

        # print('\nSample games (no network calls):')
        # print(json.dumps(sample_games, indent=2, ensure_ascii=False))

        if args.create:
            # Ask user for explicit confirmation before performing a POST
            proceed = input(
                '\n--create requested. This will POST to Bet9ja to attempt creating a booking code. Proceed? (y/N): ').strip().lower()
            if proceed == 'y':
                try:
                    code = bet9ja_create_ticket(sample_games)
                    print(f"\nCreated booking code: {code}")
                except Exception as e:
                    logger.error(f"Failed to create booking code: {e}")
            else:
                print('Create action cancelled by user. No network requests made.')
        else:
            print('\nTo try creating a real booking code from these sample games, re-run with the --create flag and confirm when prompted.')
