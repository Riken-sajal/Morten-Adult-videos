from driver.get_driver import StartDriver
import json, random, os, time, requests, urllib, shutil
from utils.mail import SendAnEmail
from bs4 import BeautifulSoup
from app.models import cetegory, configuration, videos_collection, VideosData
from dateutil import parser
from datetime import datetime, timedelta
import pandas as pd

# selenium imports
from selenium.common.exceptions import NoSuchElementException, TimeoutException,ElementNotInteractableException,NoSuchElementException,WebDriverException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver


class Bot(StartDriver):
    

    def get_main_handjob_category(self): 
        return random.choice([i.category for i in self.handjob.category.all()])
    
    def login_Handjob_TV(self):
        url = "https://handjob.tv/login"
        self.driver.get(url)
        self.click_element('agree btn','verify-age', By.ID, timeout=3)
        self.input_text(self.handjob.username,'username','//input[@id="username"]')
        self.input_text(self.handjob.password,'password','//input[@id="password"]')
        self.click_element('Submit btn','//button[@id="login"]')
        if self.find_element('Logout btn','//a[@class="logout"]') :
            self.get_cookies(self.handjob.website_name)
            return True
        else : return False
        
        self.cookies_dict = ''
        cookies_file = f'{self.cookies_path}/{self.handjob.website_name}_cookietest.json'
        if os.path.isfile(cookies_file):
            with open(cookies_file, 'r') as file: 
                self.cookies_dict = json.load(file)
            response = requests.request("GET", url, cookies=self.cookies_dict)
            soup = BeautifulSoup(response.content, 'html.parser')
            logout = soup.find('a', class_="logout")
            if logout:
                return True
            
        headers = {'Cookies':'_ga=GA1.1.1004529152.1702469470; PHPSESSID=rugc1hlu0itorhumpom12pk59q; _ga_HK7FVQ1HVZ=GS1.1.1702982456.7.1.1702982470.0.0.0'}
        response = requests.request("GET", url, headers=headers)
        hidden_input = soup.find('input', {'name': 'nocsrf_login_popup'})
        if hidden_input:
            value = hidden_input.get('value')
            payload = {'u': 'romeostream', 'p' : 'tub3S3bm1t', 'nocsrf_login_popup' : f'{value}'}
            print('value found')
        else:
            payload = {'u': 'romeostream', 'p' : 'tub3S3bm1t'}

        url = "https://handjob.tv/api/verifying"
        headers =   {
                        'Content-Type' :  'application/x-www-form-urlencoded'
                    }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            self.cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
            with open(cookies_file, 'w') as file:
                json.dump(self.cookies_dict, file)
            print("Cookies saved to cookies.json file.")
            soup = BeautifulSoup(response.content, 'html.parser')
            logout = soup.find('a', class_="logout")
            if logout:
                return True
        return False
    
    def download_from_main_category(self):
        search_ele = self.input_text(self.handjob.main_category,'search input','//input[@id="search"]')
        search_ele.submit()
        csv_name = "Handjob.csv"
        self.check_csv_exist(csv_name)
        collection_path = self.create_or_check_path(self.handjob_category_path,sub_folder_=self.handjob.main_category)
        
        # download from main category
        self.driver.get(f"https://handjob.tv/search/{self.handjob.main_category}/")
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        numbers_of_download_videos = self.handjob.numbers_of_download_videos
        video_links = soup.find_all('a', href=lambda value: value and '/video/' in value)
        
        df_url = [i.Url for i in VideosData.objects.filter(configuration=self.handjob)]
        for link in video_links: 
            video_url = link['href']
            
            img_tag = link.find('img', alt='', src=True)
            if not img_tag or not video_url : continue
            
            video_date_ele = link.select_one('span.bio-videos-date')
            if not video_date_ele : continue
            
            date_string = video_date_ele.get_text(strip=True)
            if not self.date_older_or_not(date_string, self.handjob.more_than_old_days_download) : continue

            video_url = 'https://handjob.tv' + video_url
            img_src = 'https:'+img_tag['src']
            if video_url in df_url : continue
            print("Video URL:", video_url)
            print("Image Source:", img_src)
            self.driver.get(video_url)
            
            video_ele = self.find_element('Video Link','video',By.TAG_NAME)
            video_title_ele = self.find_element('Video Title','h1',By.TAG_NAME)
            if not video_ele or not video_title_ele: continue
            
            video_title = video_title_ele.text
            self.handjob_category_path
            video_link = self.driver.find_elements(By.XPATH,'//*[@class="download-full-movie"]/div/*')[-2].get_attribute('href')
            video_name = f"handjob_{self.handjob.main_category.replace('videos', '')}_{self.sanitize_title(video_title)}"
            
            # VideoDdownloaded = False
            # try :VideoDdownloaded = urllib.request.urlretrieve(video_link, os.path.join(collection_path, f'{video_name}.mp4'))
            # except Exception as e : print('Error : Videos downloading in handjob :',e)
            
            # try :ImgDownloaded = urllib.request.urlretrieve(img_src, os.path.join(collection_path, f'{video_name}.jpg'))
            # except Exception as e : print('Error : image downloading in handjob :',e)
            # if not VideoDdownloaded or not ImgDownloaded : 
            #     print('error : Video or Image could not download in hand job')
            #     continue
            
            tmp = {"Likes" : "","Disclike" :"","Url" : video_url,"Category" : self.handjob.main_category,"video_download_url" : '',"Title" : '',"Discription" : "","Release-Date" : "","Poster-Image_uri" : img_src,"poster_download_uri" : '',"Video-name" : '',"Photo-name" : '',"Pornstarts" : '',"Username" : self.handjob.website_name}
            
            model_name_ele = self.find_element('models name','//div[@class="model-tags"]')
            if model_name_ele :
                model_name = model_name_ele.text.replace('Model:','').strip()
            else : model_name

            self.base_path
            
            v_url = f'http://208.122.217.49:8000/API{collection_path.replace(self.base_path,"")}/{video_name}.mp4'
            p_url = f'http://208.122.217.49:8000/API{collection_path.replace(self.base_path,"")}/{video_name}.jpg'
            
            discription = ''
            All_Ptag = self.driver.find_elements(By.TAG_NAME,'p')
            for Ptag in All_Ptag : 
                PtagText = Ptag.text.strip()
                if not PtagText or PtagText.startswith('Lenght') or PtagText.startswith('Photos') or  PtagText.startswith('Added on: '):continue
                discription += PtagText
                
            tmp['Title'] = video_title
            tmp['Discription'] = discription
            tmp['Release-Date'] = date_string
            tmp['Video-name'] = f'{video_name}.mp4'
            tmp['Photo-name'] = f'{video_name}.jpg'
            tmp['poster_download_uri'] = p_url
            tmp['video_download_url'] = v_url
            tmp['Pornstarts'] = model_name    
            
            cetegory_obj, _ = cetegory.objects.get_or_create(category = self.handjob.main_category)

            videos_data_obj = VideosData.objects.create(
                video = f'{collection_path.replace(self.base_path,"")}/{video_name}.mp4',
                image = f'{collection_path.replace(self.base_path,"")}/{video_name}.jpg',
                Username = self.handjob.username,
                Likes = 0,
                Disclike = 0,
                Url = video_url,
                Title = video_title,
                Discription = discription,
                Release_Date = date_string,
                Poster_Image_url = p_url,
                video_download_url = v_url,
                Video_name = f'{video_name}.mp4',
                Photo_name = f'{video_name}.jpg',
                Pornstarts = model_name,
                configuration = self.handjob,
                cetegory = cetegory_obj
            )
            numbers_of_download_videos -= 1
            
            if numbers_of_download_videos <= 0 :
                break
            
    def other_sites_of_handjob(self):
        
        # for other catefories
        for category in self.handjob.category.all() : 
            numbers_of_download_videos = self.handjob.numbers_of_download_videos
            print(category)
            
            link = f"https://handjob.tv/videos/{category.category}/"
            self.driver.get(link)

            handjob_not_used_links = []
            hand_job_category_name = category
            details_csv_path = self.handjob.website_name
            self.check_csv_exist(details_csv_path)
            
            if self.find_element("Age verify","age-verify-overlay",By.ID):
                self.click_element("I'm older","verify-age", By.ID)
                
            find_last_pag_num = 0
            
            last_page_ele = self.driver.find_elements(By.XPATH,'//*[@id="pagination"]/div/*')[-1]
            if last_page_ele.find_elements(By.TAG_NAME,'a'):
                find_last_pag_num = last_page_ele.find_elements(By.TAG_NAME,'a')[0].get_attribute('href').split('/')[-1].replace('page','')
            
            if not find_last_pag_num :
                print("cound not found the find_last_pag_num for hand job other sites of category")
                continue
            
            all_used_link = [i.Url for i in VideosData.objects.filter( configuration = self.handjob )]
            for pages in range(int(find_last_pag_num)): 
                
                if pages == 0:
                    self.driver.get(link)
                else:
                    self.driver.get(link+'page'+str(pages))
                    
                all_videos_thumbs = self.driver.find_elements(By.CLASS_NAME,'thumb-all')
                for i in all_videos_thumbs : 
                    vd_link = i.find_element(By.TAG_NAME,'a').get_attribute('href')
                    if not vd_link in all_used_link :
                        handjob_not_used_links.append([vd_link,i.find_element(By.TAG_NAME,'img').get_attribute('src')])
                        
                    if len(handjob_not_used_links) > self.handjob.numbers_of_download_videos : break
                if len(handjob_not_used_links) > self.handjob.numbers_of_download_videos : break
            
            for vd_link in handjob_not_used_links: 

                self.driver.get(vd_link[0])
                self.random_sleep(5,7)

                self.driver.find_elements(By.XPATH,'//*[@class="download-full-movie"]/div/*')[-2].click()
                self.random_sleep(3,5)

                file_name = self.wait_for_file_download()
                self.random_sleep(3,5)

                video_infor = self.genrate_handjob_a_data_dict(vd_link,category)
                name_of_file = os.path.join(self.download_path, video_infor['Video-name'])

                os.rename(os.path.join(self.download_path,file_name), name_of_file)
                self.random_sleep(3,5)
                
                collection_path = os.path.join(self.download_path,'handjob_category_videos',f'{hand_job_category_name}')
                shutil.move(name_of_file,f'{collection_path}/{video_infor["Video-name"]}')
                
                if not os.path.exists(collection_path):
                    os.mkdir(collection_path)
                
                response = requests.get(vd_link[1])
                if response.status_code == 200:
                    with open(f'{collection_path}/{video_infor["Video-name"]}.jpg', 'wb') as file: 
                        file.write(response.content)

                
                cetegory_obj, _ = cetegory.objects.get_or_create(category = category)
                video_file = f'{collection_path.replace(self.base_path,"")}/{video_infor["Video-name"]}'
                
                if os.path.exists(video_file) :
                    video_file = self.copy_files_in_media_folder(video_file)
                    
                image_file = f'{collection_path}/{video_infor["Photo-name"]}'
                if os.path.exists(image_file) :
                    image_file = self.copy_files_in_media_folder(image_file)
                    
                videos_data_obj = VideosData.objects.create(
                    video = video_file,
                    image = image_file,
                    Username = self.handjob.username,
                    Likes = 0,
                    Disclike = 0,
                    Url = self.driver.current_url,
                    Title = video_infor["Title"],
                    Discription = video_infor["Discription"],
                    Release_Date = video_infor["Release-Date"],
                    Poster_Image_url = video_infor["Poster-Image_uri"],
                    video_download_url = video_infor["poster_download_uri"],
                    Video_name = video_infor["Video-name"],
                    Photo_name = video_infor["Photo-name"],
                    Pornstarts = video_infor["Pornstarts"],
                    configuration = self.handjob,
                    cetegory = cetegory_obj
                )
                
                numbers_of_download_videos -= 1
            
                if numbers_of_download_videos <= 0 :
                    break
            if numbers_of_download_videos <= 0 :
                break
                
    def genrate_handjob_a_data_dict(self,video_li : list,hand_job_category_name : str):
        
        video_info = self.find_element('Video0info','video-info',By.CLASS_NAME)
        vd_title = self.find_element('Video title','video-title',By.CLASS_NAME).text if self.find_element('Video title','video-title',By.CLASS_NAME) else None

        video_name = f"{self.handjob.website_name}_{hand_job_category_name}_{self.sanitize_title(vd_title)}"
        data = {       
        "Likes" : 0,
        "Disclike" : 0,
        "Url" : self.driver.current_url,
        "Title" : self.find_element('Video title','video-title',By.CLASS_NAME).text if self.find_element('Video title','video-title',By.CLASS_NAME) else "could not found the title" ,
        "Discription" : self.find_element('Video title','//div[@style="color: white;"]',By.XPATH).text if self.find_element('Video title','//div[@style="color: white;"]',By.XPATH) else "could not found the description" , #color: white;
        "Release-Date" : video_info.find_element(By.TAG_NAME,'div').find_elements(By.TAG_NAME,'p')[-1].text.removeprefix('Added on: ') if video_info else "could not found the added date time", #/html/body/div[4]/div[1]/div
        "Poster-Image_uri" : video_li[-1] if video_li[-1] else "video post img link could not found",
        "poster_download_uri" : f'http://208.122.217.49:8000/API/downloads/handjob_category_videos/{hand_job_category_name}/{video_name}.jpg',
        "Video-name" : video_name+".mp4",
        "video_download_url" : f'http://208.122.217.49:8000/API/downloads/handjob_category_videos/{hand_job_category_name}/{video_name}.mp4',
        "Photo-name" : video_name + ".jpg",
        "Pornstarts" : self.find_element('Pornstar name','model-tags',By.CLASS_NAME).text.replace("Model: ",'') if self.find_element('Pornstar name','model-tags',By.CLASS_NAME) else "Not found porn star",
        "Category" : hand_job_category_name,
        "Username" : self.handjob.username,
        "downloaded_time" : datetime.now()
        }
                
        return data
                
    
        
    def date_older_or_not(self,video_data='', old_days : int = 30):
        
        if video_data and old_days:
            today = datetime.now()
            old_date = today - timedelta(days=old_days)
            date_obj = parser.parse(video_data)
            return date_obj < old_date 
        return False
    
    def sanitize_title(self,title : str): 
        formatted_title = ''.join(c.lower() if c.isalnum() else '_' for c in title)
        formatted_title = '_'.join(filter(None, formatted_title.split('_')))
        return formatted_title
    
    def set_data_of_csv(self, videos_data_obj):
        
        df = self.check_csv_exist(videos_data_obj.configuration.website_name)
        
        new_data = {
            "image": videos_data_obj.image,
            "Username": videos_data_obj.Username,
            "Likes": videos_data_obj.Likes,
            "Disclike": videos_data_obj.Disclike,
            "Url": videos_data_obj.Url,
            "Title": videos_data_obj.Title,
            "Discription": videos_data_obj.Discription,
            "Release_Date": videos_data_obj.Release_Date,
            "Poster_Image_url": videos_data_obj.Poster_Image_url,
            "video_download_url": videos_data_obj.video_download_url,
            "Video_name": videos_data_obj.Video_name,
            "Photo_name": videos_data_obj.Photo_name,
            "Pornstarts": videos_data_obj.Pornstarts,
            "configuration": videos_data_obj.configuration.website_name,
            "cetegory": videos_data_obj.cetegory.category
        }
        # df = df.append(new_data, ignore_index=True)
        new_row = pd.DataFrame([new_data])

        df = pd.concat([df, new_row], ignore_index=True)
        csv_path = f"{os.path.join(os.getcwd(),'csv', videos_data_obj.configuration.website_name)}.csv"
        df.to_csv(csv_path, index=False)
        
        pass