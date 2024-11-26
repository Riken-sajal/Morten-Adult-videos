from django.core.management.base import BaseCommand, CommandError
from Scrape.settings import BASE_DIR
from django.core.files.base import ContentFile
from app.models import videos_collection, configuration, VideosData
import requests, os, time
from driver.Bots.adultprime import Bot
from utils.mail import SendAnEmail

class Command(BaseCommand, Bot):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("--only_login", default=False, type=bool)
        
    def make_init(self):
        self.driver_type = "normal"     
        self.base_path = os.getcwd()
        
        self.download_path = os.path.join(os.getcwd(),'downloads')
        [ os.remove(os.path.join(os.getcwd(),'downloads',i)) for i in os.listdir('downloads') if i.endswith('.crdownload') or i.endswith('.mp4') ]
        
        # Configurations
        self.adultprime = configuration.objects.get(website_name='Adultprime')
        self.adultprime_category_path = self.create_or_check_path('Adultprime_category_videos')

        self.csv_folder_path = self.create_or_check_path('csv',main=True)
        self.cookies_path = self.create_or_check_path('cookies',main=True)
        self.csv_name = "Adultprime.csv"
        self.csv_path = os.path.join(self.csv_folder_path,f'{self.csv_name}')
        
    def handle(self, *args, **options):
        VideosData.delete_older_videos()
        self.make_init()
        self.driver = self.get_driver()
        if not self.driver :
            SendAnEmail('Could not open up the driver')
            return
        only_login = options["only_login"]
        if only_login :
            print('only login')
            if self.adultprime_login():
                self.adultprime.lastime_able_to_login_or_not = True
                self.adultprime.save()
            else:
                self.adultprime.lastime_able_to_login_or_not = False
                self.adultprime.save()
        else :
            print('Not only login')
            
        if self.adultprime_login():
            self.adultprime.lastime_able_to_login_or_not = True
            self.adultprime.save()
            self.download_all_adultprime_channels_video()
        else:
            self.adultprime.lastime_able_to_login_or_not = False
            self.adultprime.save()
            
    
        # self.download_and_save_file("http://208.122.217.49:8000/csv/vip4k_debt4k_videos_details.csv")