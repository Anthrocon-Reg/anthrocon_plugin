from uber.common import *
from anthrocon_plugin._version import __version__

config = parse_config(__file__)
mount_site_sections(config['module_root'])
static_overrides(join(config['module_root'], 'static'))
template_overrides(join(config['module_root'], 'templates'))

@Config.mixin
class ExtraConfig:
    c.TABLE_OPTS = [
        (0.5, 'Half Table'),
        (1.0, 'Full Table'),
        (2.0, 'Double Table'),
        (3.0, 'Triple Table'),
        (4.0, 'Island/Quad Table')
    ]

    c.ADMIN_TABLE_OPTS = [(0.0, 'No Table')] + c.TABLE_OPTS + [(float(i), str(i)) for i in range(5, 11)]

    c.TABLE_PRICES = {0: 0, 0.5: 40, 1: 100, 2: 350, 3: 600, 4: 999}

    c.TABLE_OPTS = [(count, '{}: ${}'.format(desc, c.TABLE_PRICES[count])) for count, desc in c.TABLE_OPTS]

    c.TABLE_EXTRA_PRICES = {c.POWER_TABLE: 60, c.WALL_TABLE: 10}

    c.MAX_DEALER_BADGES = {0: 1, 0.5: 2, 1: 2, 2: 3, 3: 4, 4: 5}


class AgeGroup(MagModel):
    desc          = Column(UnicodeText)
    min_age       = Column(Integer)
    max_age       = Column(Integer)
    discount      = Column(Integer)
    can_register  = Column(Boolean, default=True)
    can_volunteer = Column(Boolean, default=True)
    consent_form  = Column(Boolean, default=False)


@Session.model_mixin
class Group:
    table_extras  = Column(MultiChoice(c.TABLE_EXTRA_OPTS))

    @cost_property
    def table_cost(self):
        total = 0

        total += c.TABLE_PRICES.get(self.tables, 999)

        for extra, amount in c.TABLE_EXTRA_PRICES.items():
            if extra in self.table_extras_ints:
                total += amount
        return total

    @property
    def default_cost(self):
        return self.table_cost + self.badge_cost + self.amount_extra

@Session.model_mixin
class Attendee:
    status        = Column(Choice(c.BADGE_STATUS_OPTS), default=c.NEW_STATUS)
    age_group_id  = Column(UUID, ForeignKey('age_group.id', ondelete='SET NULL'), nullable=True)
    age_group     = relationship(AgeGroup, backref='attendees', foreign_keys=age_group_id, single_parent=True)
    ec_name       = Column(UnicodeText, default='')

    @property
    def age_group_conf(self):
        return None

    @property
    def can_volunteer(self):
        if self.age_group: return self.age_group.can_volunteer
        with Session() as session:
            return session.age_group_from_birthdate(self.birthdate).can_volunteer

    @property
    def can_register(self):
        if self.age_group: return self.age_group.can_register
        with Session() as session:
            return session.age_group_from_birthdate(self.birthdate).can_register

    @property
    def age_discount(self):
        if self.age_group: return self.age_group.discount
        with Session() as session:
            return session.age_group_from_birthdate(self.birthdate).discount

    @property
    def consent_form(self):
        if self.age_group: return self.age_group.consent_form
        with Session() as session:
            return session.age_group_from_birthdate(self.birthdate).consent_form

    @property
    def age_group_desc(self):
        if self.age_group: return self.age_group.desc
        with Session() as session:
            return session.age_group_from_birthdate(self.birthdate).desc

    def age_group_from_birthdate(self, birthdate):
        if not birthdate: return None
        calc_date = c.EPOCH.date() if date.today() <= c.EPOCH.date() else date.today()
        attendee_age = int((calc_date - birthdate).days / 365.2425)

        age_groups = self.query(AgeGroup)
        for current_age_group in age_groups:
            if current_age_group.min_age <= attendee_age <= current_age_group.max_age:
                return current_age_group
        return None

    @presave_adjustment
    def status_adjustments(self):
        old_status = self.orig_value_of('status')
        old_amount_paid = self.orig_value_of('amount_paid')
        if old_status == self.status and old_amount_paid != self.amount_paid:
            if self.paid == NOT_PAID or self.placeholder:
                self.status = NEW_STATUS
            elif self.paid == HAS_PAID or self.paid == NEED_NOT_PAY:
                self.status = COMPLETED_STATUS

    @presave_adjustment
    def _staffing_adjustments(self):
        if self.ribbon == c.DEPT_HEAD_RIBBON:
            self.staffing = self.trusted = True
            self.badge_type = c.STAFF_BADGE
            if self.paid == c.NOT_PAID:
                self.paid = c.NEED_NOT_PAY

        if not self.is_new:
            old_ribbon = self.orig_value_of('ribbon')
            old_staffing = self.orig_value_of('staffing')
            if self.staffing and not old_staffing or self.ribbon == c.VOLUNTEER_RIBBON and old_ribbon != c.VOLUNTEER_RIBBON:
                self.staffing = True
                if self.ribbon == c.NO_RIBBON:
                    self.ribbon = c.VOLUNTEER_RIBBON

        if self.badge_type == c.STAFF_BADGE and self.ribbon == c.VOLUNTEER_RIBBON:
            self.ribbon = c.NO_RIBBON

        if self.badge_type == c.STAFF_BADGE:
            self.staffing = True


@validation.Attendee
def emergency_contact(attendee):
    pass

@validation.Attendee
def allowed_to_volunteer(attendee):
    if attendee.staffing and not attendee.can_volunteer and attendee.badge_type != c.STAFF_BADGE and c.PRE_CON:
        return 'Volunteers cannot be ' + attendee.age_group_desc

@validation.Attendee
def allowed_to_register(attendee):
    if not attendee.can_register:
        return 'Attendees ' + attendee.age_group_desc + ' years of age do not need to register, but MUST be accompanied by a parent at all times!'

Session.initialize_db()

from anthrocon_plugin import ac_sep