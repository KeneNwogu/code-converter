import requests
import random
# msport_create = [
#     {
#         "eventId": "sr:match:43458917",
#         "marketId": 1,
#         "specifier": "",
#         "outcomeId": "1"
#     },
#     {
#         "eventId": "sr:match:43458597",
#         "marketId": 1,
#         "specifier": "",
#         "outcomeId": "1"
#     },
#     {
#         "eventId": "sr:match:43458599",
#         "marketId": 1,
#         "specifier": "",
#         "outcomeId": "1"
#     }
# ]

browser_agent_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
msport_ticket_url = "https://www.msport.com/api/ng/orders/real-sports/order/share"



def msport_create_ticket(games):
    # check if length of games exceeds 30
    if len(games) > 30:
        games = random.sample(games, 30)

    msport_create_url = "https://www.msport.com/api/ng/orders/real-sports/order/share"
    selections = {
      "selections": games
    }
    ticket_object = requests.post(msport_create_url, json=selections, headers=browser_agent_headers).json()
    # print(ticket_object)

    if ticket_object.get('innerMsg') == 'invalid':
        raise Exception(ticket_object.get('message') or "Invalid markets")

    return ticket_object.get('data', {}).get('shareCode')


def get_msport_games(ticket: str):
    games_url = f"{msport_ticket_url}/{ticket}"
    games_object = requests.get(games_url, headers=browser_agent_headers).json()
    
    if games_object.get('innerMsg') != "success":
        raise ValueError('Invalid Game Code')

    outcomes = games_object['data']['bettableBetSlip']
    game_details = []
    
    for outcome in outcomes:
        data = {
            'eventId': outcome.get('event').get('eventId'),
            'marketId': outcome.get('market').get('id'),
            'specifier': outcome.get('market').get('specifiers') or "",
            'outcomeId': outcome.get('outcome').get('id')
        }
        
        game_details.append(data)
    
    return game_details
    

def parse_ticket_to_sportybet(ticket):
    games = get_msport_games(ticket)
    
    # TODO: check if valid game and remove
    
    return list(map(lambda game: {
        "eventId": game.get('eventId'),
        "marketId": str(game.get('marketId')),
        "specifier": game.get('specifier') or None,
        "outcomeId": str(game.get('outcomeId'))
    }, games))
