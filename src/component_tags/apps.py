from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ComponentTagsConfig(AppConfig):
    name = 'component_tags'
    verbose_name = _('Django Component Tags')
