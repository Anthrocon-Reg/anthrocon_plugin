from anthrocon_plugin import *

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

    @cost_property
    def luncheon_cost(self):
        return self.luncheon_tickets * c.LUNCHEON_PRICE or 0

    @presave_adjustment
    def set_empty_tickets(self):
        if not self.luncheon_tickets:
            self.luncheon_tickets = 0

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


@Session.model_mixin
class Group:
    tax_id = Column(UnicodeText, nullable=True, default='')
    table_extras = Column(MultiChoice(c.TABLE_EXTRA_OPTS))

    @cost_property
    def table_extra_cost(self):
        total_cost = 0
        return sum(map(int, self.table_extras.split(',')))
        return total_cost

    @property
    def new_ribbon(self):
        return c.DEALER_ASST_RIBBON if self.is_dealer else c.NO_RIBBON

    @property
    def new_badge_cost(self):
        return c.BADGE_PRICE if self.tables else c.get_group_price(sa.localized_now())

    @cost_property
    def badge_cost(self):
        total = 0
        for attendee in self.attendees:
            if attendee.paid == c.PAID_BY_GROUP:
                total += c.BADGE_PRICE if attendee.is_dealer else c.get_group_price(attendee.registered)
        return total
