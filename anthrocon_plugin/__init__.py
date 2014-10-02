from uber.common import *
from anthrocon_plugin._version import __version__

config = parse_config(__file__)
django.conf.settings.TEMPLATE_DIRS.insert(0, join(config['module_root'], 'templates'))