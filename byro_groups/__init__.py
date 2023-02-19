from django.apps import AppConfig
from django.utils.translation import ugettext_lazy


class PluginApp(AppConfig):
    name = "byro_groups"
    verbose_name = "Mitgliedergruppen"

    class ByroPluginMeta:
        name = ugettext_lazy("Mitgliedergruppen")
        author = "Lev E. Chechulin"
        description = ugettext_lazy("Plugin adds user groups to byro.")
        visible = True
        version = "0.0.1"

    def ready(self):
        from . import signals  # NOQA


default_app_config = "byro_groups.PluginApp"
