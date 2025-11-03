from msport import msport_create_ticket, parse_ticket_to_sportybet
from sportybet import parse_ticket_to_msport, sportybet_create_ticket

# SPORTYBET TO MSPORT TEST
# sportybet_code = input("Please input a sportybet code: ")

# msport_parsed_selections = parse_ticket_to_msport(sportybet_code)

# print("Msport games to send", msport_parsed_selections)

# msport_ticket = msport_create_ticket(msport_parsed_selections)

# print("Your msport conversion is: ", msport_ticket)


# MSPORT TO SPORTYBET TEST

msport_code = input("Please input an msport code: ")

sportybet_parsed_selections = parse_ticket_to_sportybet(msport_code)

# print("SportyBet games to send", sportybet_parsed_selections)

# for game in sportybet_parsed_selections:
#     print("Validating your Event:", game.get("eventId"))
#     sportybet_ticket = sportybet_create_ticket([game])
#     print("Your SportyBet conversion is: ", sportybet_ticket)
    
#     if sportybet_ticket is None:
#         print("invalid game is:", game)
#         break

sportybet_ticket = sportybet_create_ticket(list(filter(lambda x: x['eventId'] != "sr:match:50603245", sportybet_parsed_selections)))

print("Your SportyBet conversion is: ", sportybet_ticket)

# sportybet_create_ticket([
#   {
#     "eventId": "sr:match:51271759",
#     "marketId": "18",
#     "specifier": "total=0.5",
#     "outcomeId": "12"
#   }
# ])