import requests

url = "https://www.sportybet.com/api/ng/orders/share/"

browser_agent_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def get_games(bet_code: str):
    games_url = url + bet_code
    games_response = requests.get(games_url, headers=browser_agent_headers)
    games_object = games_response.json()

    if "invalid" in games_object.get('innerMsg', "").lower():
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


def sportybet_create_ticket(games):
    sporty_create_url = "https://www.sportybet.com/api/ng/orders/share"

    games = list(map(lambda game: {
        "eventId": game.get('eventId'),
        "marketId": str(game.get('marketId')),
        "specifier": game.get('specifier') or None,
        "outcomeId": str(game.get('outcomeId'))
    }, games))

    selections = {
      "selections": games
    }

    ticket_object = requests.post(sporty_create_url, json=selections, headers=browser_agent_headers).json()

    if ticket_object.get('innerMsg') == 'invalid':
        raise Exception(ticket_object.get('message') or "Invalid markets")

    return ticket_object.get('data', {}).get('shareCode')
