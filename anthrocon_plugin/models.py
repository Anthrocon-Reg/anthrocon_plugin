from anthrocon_plugin import *

@Session.model_mixin
class Attendee:
    extra_donation = Column(Integer, default=0)
    luncheon_tickets = Column(Integer, default=0)
    luncheon_going = Column(Boolean, default=False)
    coc_agree = Column(Boolean, default=False)
    free_kickin = Column(Boolean, default=False)

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

    @cost_property
    def supersponsor_discount(self):
        return -5 if c.AFTER_PREREG_TAKEDOWN and self.amount_extra >= c.SUPERSPONSOR else 0

    @property
    def total_cost(self):
        return self.default_cost if self.free_kickin else self.default_cost + self.amount_extra

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
        # "Board of Directors" doesn't fit on the badges
        badge_label = "Board" if self.badge_type == c.BOD_BADGE else self.badge_type_label

        # These are not literal badge types so we manually override the Attending badge label
        if self.badge_type == c.ATTENDEE_BADGE:
            if self.ribbon in [c.DEALER_RIBBON, c.DEALER_ASST_RIBBON]:
                return self.ribbon_label
            elif self.amount_extra == c.SPONSOR:
                return "Sponsor"
            elif self.amount_extra == c.SUPERSPONSOR:
                return "Supersponsor"

        if self.ribbon in [c.DEALER_RIBBON, c.DEALER_ASST_RIBBON]:
            if self.badge_type == c.ONE_DAY_BADGE:
                return datetime.strftime(localized_now(), "%A") + " / " + self.ribbon_label
            else:
                return badge_label + " / " + self.ribbon_label
        else:
            return datetime.strftime(localized_now(), "%A") if self.badge_type == c.ONE_DAY_BADGE else badge_label

    @property
    def extra_print_label(self):
        if self.ribbon_and_or_badge in ["Sponsor", "Supersponsor"]:
            return ''
        elif self.amount_extra == c.SPONSOR:
            return "<br />Sponsor"
        elif self.amount_extra == c.SUPERSPONSOR:
            return "<br />Supersponsor"


@Session.model_mixin
class Group:
    tax_id = Column(UnicodeText, nullable=True, default='')
    table_extras = Column(MultiChoice(c.TABLE_EXTRA_OPTS))

    @cost_property
    def table_extra_cost(self):
        return sum(map(int, self.table_extras.split(','))) if self.table_extras else 0

    @cost_property
    def table_cost(self):
        return c.TABLE_PRICES[float(self.tables)]

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
                total += c.get_attendee_price(attendee.registered) if attendee.is_dealer else c.get_group_price(attendee.registered)
        return total

    @property
    def addons(self):
        addons = []
        for amt, desc in c.TABLE_EXTRA_OPTS:
            if str(amt) in self.table_extras.split(','):
                addons.append('{} (${})'.format(desc.split(' ',2)[-1], amt) if amt else desc)
        return addons

@Session.model_mixin
class SessionMixin:
    def filter_badges_for_printing(self, badge_list, **params):
        """
        Allows batch printing by grouping badges via the passed-in parameters.

        :return:
        """

        if 'badge_type' in params:
            return badge_list.filter(Attendee.badge_type == params['badge_type'])
        elif 'dealer_only' in params:
            return badge_list.filter(Attendee.ribbon.in_([c.DEALER_RIBBON, c.DEALER_ASST_RIBBON]))
        elif 'badge_upgrade' in params:
            return badge_list.filter(Attendee.amount_extra == params['badge_upgrade'])
        else:
            return badge_list
