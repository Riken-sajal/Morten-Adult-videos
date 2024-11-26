from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    def handle(self, *args, **options):

        List_of_working_commands = [
            "handjob",
            "revsharecash",
            "sexmax",
            "fivek",
        ]
        
        for command in List_of_working_commands :
            call_command(command, '--days', '7')