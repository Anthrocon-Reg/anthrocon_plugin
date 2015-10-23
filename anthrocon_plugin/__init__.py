from uber.common import *
from anthrocon_plugin._version import __version__

anthrocon_config = parse_config(__file__)
c.include_plugin_config(anthrocon_config)
static_overrides(join(anthrocon_config['module_root'], 'static'))
template_overrides(join(anthrocon_config['module_root'], 'templates'))

@Session.model_mixin
class Attendee:
    extra_donation = Column(Integer, default=0)
    luncheon_tickets = Column(Integer, default=0)
    luncheon_going = Column(Boolean, default=False)

    @cost_property
    def donation_cost(self):
        return self.extra_donation or 0

    @presave_adjustment
    def set_empty_donation(self):
        if not self.extra_donation:
            self.extra_donation = 0

    @validation.Attendee
    def only_positive_donation(self):
        if self.extra_donation and self.extra_donation < 0:
            return "You cannot donate negative money."

    @cost_property
    def luncheon_cost(self):
        return self.luncheon_tickets * c.LUNCHEON_PRICE or 0

    @presave_adjustment
    def set_empty_tickets(self):
        if not self.luncheon_tickets:
            self.luncheon_tickets = 0

    @validation.Attendee
    def only_positive_tickets(self):
        if self.luncheon_tickets and self.luncheon_tickets < 0:
            return "You cannot buy negative tickets."

    @validation.Attendee
    def only_tickets_for_supersponsors(self):
        if self.luncheon_tickets and not self.amount_extra >= c.SUPERSPONSOR:
            return "Only Supersponsors may buy luncheon tickets."

    @property
    def addons(self):
        addons = []
        if self.extra_donation:
            addons.append('Extra donation of ${}'.format(self.extra_donation))
        if self.luncheon_tickets:
            addons.append('{} extra luncheon tickets (${})'.format(self.luncheon_tickets, self.luncheon_cost))
        return addons

    @property
    def ribbon_and_or_badge(self):
        if self.ribbon in [c.DEALER_RIBBON, c.DEALER_ASST_RIBBON] and self.badge_type != c.ATTENDEE_BADGE:
            if self.badge_type == c.ONE_DAY_BADGE:
                return datetime.strftime(localized_now(), "%A") + " / " + self.ribbon_label
            else:
                return self.badge_type_label + " / " + self.ribbon_label
        elif self.ribbon in [c.DEALER_RIBBON, c.DEALER_ASST_RIBBON]:
             return self.ribbon_label
        else:
            return datetime.strftime(localized_now(), "%A") if self.badge_type == c.ONE_DAY_BADGE else self.badge_type_label


mount_site_sections(anthrocon_config['module_root'])