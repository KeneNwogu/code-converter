import requests

from sportybet import sportybet_create_ticket

browser_agent_headers = {'User-Agent':
                             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                         }

api_to_model_map = {}


def predict_game(home: str, away: str):
    return 0.4, 0.1, 0.5


# Draw no bet type
def generate_sporty_bet_predictions():
    request_data = [
        {
            "sportId": "sr:sport:1",
            "marketId": "1,18,10,29,11,26,36,14",
            "tournamentId": [
                [
                    "sr:tournament:17"
                ]
            ]
        }
    ]
    epl_games_url = "https://www.sportybet.com/api/ng/factsCenter/pcEvents"
    games_object = requests.post(epl_games_url, json=request_data, headers=browser_agent_headers).json()

    if games_object.get('innerMsg') == "Invalid":
        pass

    games = games_object['data'][0]['events'][:10]

    game_parser = []
    for game in games:
        home = game['homeTeamName']
        away = game['awayTeamName']
        home_win_probability, draw_probability, away_win_probability = predict_game(home, away)

        # Market id is constant "11" for Draw no bet
        # Specifier is ""

        # get outcome IDs from event data
        # find draw no bet market
        draw_no_bet_market = list(filter(lambda x: x['id'] == "11", game['markets']))[0]
        home_outcome_id, away_outcome_id = map(lambda x: x['id'], draw_no_bet_market['outcomes'])
        outcome_id = home_outcome_id if home_win_probability > away_win_probability else away_outcome_id

        data = {
            'eventId': game['eventId'],
            "marketId": "11",
            'specifier': "",
            'outcomeId': outcome_id
        }

        game_parser.append(data)
    return game_parser


print(sportybet_create_ticket(generate_sporty_bet_predictions()))
