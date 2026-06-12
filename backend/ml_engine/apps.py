from django.apps import AppConfig


class MlEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml_engine'

    def ready(self):
        try:
            from .trainer import train_all_models
            from .predictor import MODEL_PATH
            if not MODEL_PATH.exists():
                train_all_models()
        except Exception:
            pass
