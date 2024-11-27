from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from app.models import RunScript
from django.utils import timezone  

class Command(BaseCommand):
    help = 'Run a script at a specified hour'

    def handle(self, *args, **kwargs):
        current_datetime = timezone.now()
        run_script = RunScript.objects.first()
        
        only_login = True
        next_run_time = run_script.last_run + timedelta(hours=run_script.datetime)
        
        if next_run_time < current_datetime:
            only_login = False
            print(f"Run script at {run_script.datetime} hours is ready to run.")
        else:
            print(f"Run script at {run_script.datetime} hours is not ready to run yet.")
        
