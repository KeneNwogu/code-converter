import requests

url = "https://www.sportybet.com/api/ng/orders/share/"

browser_agent_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def get_games(bet_code: str):
    games_url = url + bet_code
    games_object = requests.get(games_url, headers=browser_agent_headers).json()

    if games_object.get('innerMsg') == "Invalid":
        raise ValueError('Invalid Game Code')

    outcomes = games_object['data']['outcomes']
    games_details = []

    for outcome in outcomes:
        data = {'eventId': outcome.get('eventId')}
        # set events to db
        try:
            data['marketId'] = outcome["markets"][0]["id"]
            data['specifier'] = outcome["markets"][0].get("specifier") or ""
            data['outcomeId'] = outcome["markets"][0]["outcomes"][0]["id"]
        except IndexError:
            raise ValueError('Invalid Game. Error occurred')
        else:
            games_details.append(data)

    return games_details


def parse_ticket_to_msport(sporty_bet_code: str):
    games = get_games(sporty_bet_code)
    return list(map(lambda game: {
        "eventId": game.get('eventId'),
        "marketId": str(game.get('marketId')),
        "specifier": game.get('specifier'),
        "outcomeId": str(game.get('outcomeId'))
    }, games))
