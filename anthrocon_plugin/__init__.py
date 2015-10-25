from uber.common import *
from anthrocon_plugin._version import __version__

from anthrocon_plugin.config import *
static_overrides(join(anthrocon_config['module_root'], 'static'))
template_overrides(join(anthrocon_config['module_root'], 'templates'))
from anthrocon_plugin.models import *
from anthrocon_plugin.model_checks import *

mount_site_sections(anthrocon_config['module_root'])
