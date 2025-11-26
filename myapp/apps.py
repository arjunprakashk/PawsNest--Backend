from django.apps import AppConfig

class MyAppConfig(AppConfig):  # use your app name
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'  # your app folder name

    def ready(self):
        import myapp.signals  # ensures signals are loaded
