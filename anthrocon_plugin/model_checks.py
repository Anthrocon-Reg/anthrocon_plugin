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

@prereg_validation.Attendee
def accept_coc(attendee):
    if not attendee.coc_agree:
        return "You must agree to the standards of conduct."

@prereg_validation.Attendee
def cellphone_required(attendee):
    if not attendee.cellphone:
        return "Please enter your phone number."

@prereg_validation.Group
def dealer_website(group):
    pass

@prereg_validation.Group
def dealer_tax_id(group):
    if group.tables and not group.tax_id:
        return "You must enter your Pennsylvania tax id."

@validation.Attendee
def zip_code(attendee):
    pass