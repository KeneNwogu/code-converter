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


def msport_create_ticket(games):
    # check if length of games exceeds 30
    if len(games) > 30:
        games = random.sample(games, 30)

    msport_create_url = "https://www.msport.com/api/ng/orders/real-sports/order/share"
    selections = {
      "selections": games
    }
    ticket_object = requests.post(msport_create_url, json=selections, headers=browser_agent_headers).json()
    print(ticket_object)

    if ticket_object.get('innerMsg') == 'invalid':
        raise Exception(ticket_object.get('message') or "Invalid markets")

    return ticket_object.get('data', {}).get('shareCode')
