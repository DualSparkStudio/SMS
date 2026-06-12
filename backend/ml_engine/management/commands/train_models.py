from django.core.management.base import BaseCommand

from ml_engine.trainer import train_all_models


class Command(BaseCommand):
    help = 'Train ML models and save comparison metrics'

    def add_arguments(self, parser):
        parser.add_argument('--feedback', action='store_true', help='Include user feedback data')

    def handle(self, *args, **options):
        result = train_all_models(include_feedback=options['feedback'])
        self.stdout.write(self.style.SUCCESS(f'Trained on {result["samples_used"]} samples'))
        for m in result['comparison']:
            self.stdout.write(f'  {m["model"]}: Acc={m["accuracy"]}% F1={m["f1_score"]}%')
