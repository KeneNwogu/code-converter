from msport import msport_create_ticket
from sportybet import parse_ticket_to_msport

sportybet_code = input("Please input a sportybet code: ")

msport_parsed_selections = parse_ticket_to_msport(sportybet_code)

msport_ticket = msport_create_ticket(msport_parsed_selections)

print("Your msport conversion is: ", msport_ticket)