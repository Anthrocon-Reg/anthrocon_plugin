from anthrocon_plugin import *

@validation.Attendee
def only_positive_donation(attendee):
    if attendee.extra_donation and attendee.extra_donation < 0:
        return "You cannot donate negative money."

@validation.Attendee
def only_positive_tickets(attendee):
    if attendee.luncheon_tickets and attendee.luncheon_tickets < 0:
        return "You cannot buy negative tickets."

@validation.Attendee
def only_tickets_for_supersponsors(attendee):
    if attendee.luncheon_tickets and not attendee.amount_extra >= c.SUPERSPONSOR:
        return "Only Supersponsors may buy luncheon tickets."

@validation.Attendee
def emergency_contact(attendee):
    pass

@validation.Attendee
def cellphone_required(attendee):
    if not attendee.cellphone:
        return "Please enter your phone number."

@validation.Group
def dealer_website(group):
    pass

@validation.Group
def dealer_tax_id(group):
    if dealer.tables and not dealer.tax_id:
        return "You must enter your Pennsylvania tax id."