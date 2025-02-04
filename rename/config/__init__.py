from .base import *
from .iso import config_iso
from .media import config_media
from .other import config_other
from .phone import config_phone
from .python import config_python
from .software import config_software
from .temp import config_temp

_config_temp = [] if not config_temp else config_temp

config = [] \
         + config_iso \
         + config_media \
         + config_other \
         + config_phone \
         + config_python \
         + config_software \
         + _config_temp