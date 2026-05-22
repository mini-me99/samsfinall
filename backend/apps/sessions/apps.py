from django.apps import AppConfig


class SessionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sessions"
    # IMPORTANT: must differ from django.contrib.sessions ("sessions") to avoid
    # "Application labels aren't unique" on startup.
    label = "training"
