from uber.common import *
from anthrocon_plugin._version import __version__

anthrocon_config = parse_config(__file__)
static_overrides(join(anthrocon_config['module_root'], 'static'))
template_overrides(join(anthrocon_config['module_root'], 'templates'))

@Session.model_mixin
class Attendee:
    extra_donation = Column(Integer, default=0)

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

    @property
    def addons(self):
        return ['Extra donation of ${}'.format(self.extra_donation)] if self.extra_donation else []

mount_site_sections(anthrocon_config['module_root'])