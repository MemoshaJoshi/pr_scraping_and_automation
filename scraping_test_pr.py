import re
import os
import yaml
import pandas as pd
from datetime import date, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from bs4 import BeautifulSoup


class CustomException(Exception):
    """Base class for all exceptions"""
    pass


class FacebookScrapeException(CustomException):
    """Raised when Facebook scraping fails"""

    def __init__(self, msg, url):
        self.msg = msg
        self.url = url

    def __str__(self):
        return f"Exception!! Failed to scrape Facebook.\n Url: {self.url}\nReason: {self.msg}"


class InstagramScrapeException(CustomException):
    """Raised when Instagram scraping fails"""

    def __init__(self, msg, url):
        self.msg = msg
        self.url = url

    def __str__(self):
        return f"Exception!! Failed to scrape Instagram.\n Url: {self.url}\nReason: {self.msg}"


class LinkedinScrapeException(CustomException):
    """Raised when LinkedIn scraping fails"""

    def __init__(self, msg, url):
        self.msg = msg
        self.url = url

    def __str__(self):
        return f"Exception!! Failed to scrape LinkedIn.\n Url: {self.url}\nReason: {self.msg}"


class TwitterScrapeException(CustomException):
    """Raised when Twitter(X) scraping fails"""

    def __init__(self, msg, url):
        self.msg = msg
        self.url = url

    def __str__(self):
        return f"Exception!! Failed to scrape Twitter(X).\n Url: {self.url}\nReason: {self.msg}"


def all_social_media_scraper():
    # chrome options
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--user-agent=Mozilla/5.0")
    chrome_options.add_argument("--window-size=1920,1080")

    # download the latest version of chrome driver
    chrome_service = Service(
        executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service,
                              options=chrome_options)

    # Function to get the follower and like count of two facebook accounts

    def scrape_facebook(urls):
        scraped_data = []
        for url in urls:
            driver.get(url)
            try:
                # Wait for the close_dialog element to be present
                wait = WebDriverWait(driver, 10)
                close_dialog = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'x1i10hfl') and contains(@class, 'xudhj91')]")))

                # Using JavaScript to click the close_dialog
                driver.execute_script("arguments[0].click();", close_dialog)

                # Extract account_id from URL
                account_id = re.search(r'facebook.com/([^/]+)/', url).group(1)

                # Extract follower count
                follower_elem = driver.find_element(
                    By.XPATH, '//*[contains(@id, "mount_0_0_")]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[2]/span/a[2]')
                # Keeping only the first part (e.g., 18K)
                follower_count_text = follower_elem.text.split()[0]

                # Extract like count
                like_count_elem = driver.find_element(
                    By.XPATH, '//*[contains(@id, "mount_0_0_")]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div/div[3]/div/div/div[2]/span/a[1]')
                # Keeping only the first part (e.g., 17K)
                like_count_text = like_count_elem.text.split()[0]

                scraped_data.append([datetime.now().strftime('%Y-%m-%d'),
                                     account_id, follower_count_text, like_count_text])

            except Exception as e:
                raise FacebookScrapeException(msg=e, url=url)

        # Convert the data list to a pandas DataFrame
        df = pd.DataFrame(
            scraped_data, columns=['date', 'account_id', 'follower_count', 'like_count'])

        return df

    print("************ GETTING FACEBOOK DATA *****************")
    urls = [
        'https://www.facebook.com/fusemachinesnepal/',
        'https://www.facebook.com/fusemachines/'
    ]
    facebook_df = scrape_facebook(urls=urls)
    print(facebook_df.head(5))
    print("************ RECEIVED FACEBOOK DATA *****************")

    # Function to get the follower and like count of two instagram accounts

    def scrape_instagram(urls):
        scraped_data = []
        for url in urls:
            try:
                account_id = url.split('/')[3]
                driver.get(url)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                follower_elem = soup.find(
                    'meta', attrs={'property': 'og:description'})['content']

                follower_count = int(
                    re.search(r'([\d,]+) Followers,', follower_elem).group(1).replace(',', ''))

                scraped_data.append([datetime.now().strftime('%Y-%m-%d'),
                                    account_id, follower_count])
            except Exception as e:
                raise InstagramScrapeException(msg=e, url=url)

        df = pd.DataFrame(
            scraped_data, columns=['date', 'account_id', 'follower_count'])
        return df

    print("************ GETTING INSTAGRAM DATA *****************")
    urls = [
        'https://www.instagram.com/fusemachines/',
        'https://www.instagram.com/fusemachines.nepal/'
    ]
    instagram_df = scrape_instagram(urls=urls)
    print(instagram_df.head(5))
    print("************ RECEIVED INSTAGRAM DATA *****************")

    # Function to get the follower count of two LinkedIn accounts

    def scrape_linkedin(urls):
        # Load credentials
        try:
            with open(os.path.join(os.getcwd(), 'credentials.yml'), 'r') as yaml_file:
                credentials = yaml.safe_load(yaml_file)
        except Exception as e:
            raise LinkedinScrapeException(
                msg="Error loading credentials file.", url="")
        try:
            # Login to LinkedIn
            driver.get('https://www.linkedin.com/login')
            sleep(10)
            email = driver.find_element(By.XPATH, '//*[@id="username"]')
            email.send_keys(credentials['linkedin']['username'])
            password = driver.find_element(By.XPATH, '//*[@id="password"]')
            password.send_keys(credentials['linkedin']['password'])
            password.send_keys(Keys.ENTER)
            sleep(10)
            print('Linked In login successful')
        except Exception as e:
            raise LinkedinScrapeException(
                msg='Could not login to linked in', url='https://www.linkedin.com/login')
        scraped_data = []
        for url in urls:
            try:
                driver.get(url)
                sleep(5)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                # Check if it's a company page or an individual profile
                if "/company/" in url:
                    inline_block = soup.find('div', class_='inline-block')
                    info = inline_block.find_all(
                        'div', class_='org-top-card-summary-info-list__info-item')
                    followers_str = re.sub(r'\D', '', info[1].text)
                else:
                    info = soup.find(
                        'p', class_='pvs-header__subtitle pvs-header__optional-link text-body-small')
                    followers_str = re.search(
                        r'(\d{1,3}(?:,\d{3})*) followers', info.text).group(1)

                followers = int(followers_str.replace(',', ''))
                account_id = url.split('/')[-1]
                scraped_data.append([datetime.now().strftime(
                    '%Y-%m-%d'), account_id, followers])
            except Exception as e:
                raise LinkedinScrapeException(msg=e, url=url)

        df = pd.DataFrame(
            scraped_data, columns=['date', 'account_id', 'follower_count'])
        return df

    print("************ GETTING LINKEDIN DATA *****************")
    urls = [
        'https://www.linkedin.com/company/fusemachines',
        'https://www.linkedin.com/in/sameer-maskey'
    ]
    linkedin_df = scrape_linkedin(urls=urls)
    print(linkedin_df.head(5))
    print("************ RECEIVED LINKEDIN DATA *****************")

    # Function to get the follower and following count of two Twitter accounts

    def scrape_twitter(urls):
        # Load credentials
        try:
            with open(os.path.join(os.getcwd(), 'credentials.yml'), 'r') as yaml_file:
                credentials = yaml.safe_load(yaml_file)
        except Exception as e:
            raise TwitterScrapeException(
                msg="Error loading credentials file.", url="")

        try:
            # Login to Twitter(X)
            driver.get('https://twitter.com/i/flow/login')
            print(driver.title)
            sleep(15)
            email = driver.find_element(
                By.XPATH, "//input[@class='r-30o5oe r-1dz5y72 r-13qz1uu r-1niwhzg r-17gur6a r-1yadl64 r-deolkf r-homxoj r-poiln3 r-7cikom r-1ny4l3l r-t60dpp r-fdjqy7']")
            email.send_keys(credentials['twitter']['username'])
            email.send_keys(Keys.ENTER)
            print(driver.title)
            sleep(15)
            password = driver.find_element(
                By.XPATH, "//input[@class='r-30o5oe r-1dz5y72 r-13qz1uu r-1niwhzg r-17gur6a r-1yadl64 r-deolkf r-homxoj r-poiln3 r-7cikom r-1ny4l3l r-t60dpp r-fdjqy7']")
            password.send_keys(credentials['twitter']['password'])
            password.send_keys(Keys.ENTER)
            sleep(15)
            if driver.title == 'Log in to X / X':
                email = driver.find_element(
                    By.XPATH, "//input[@class='r-30o5oe r-1dz5y72 r-13qz1uu r-1niwhzg r-17gur6a r-1yadl64 r-deolkf r-homxoj r-poiln3 r-7cikom r-1ny4l3l r-t60dpp r-fdjqy7']")
                email.send_keys(credentials['twitter']['email'])
                email.send_keys(Keys.ENTER)
                sleep(15)
            print("Twitter Login Successful")

        except Exception as e:
            raise TwitterScrapeException(
                msg='Could not login to Twitter(X)', url='https://twitter.com/i/flow/login')
        scraped_data = []

        try:
            for url in urls:
                driver.get(url)
                sleep(10)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                div_data = soup.find(
                    'div', class_='css-175oi2r r-13awgt0 r-18u37iz r-1w6e6rj')
                divs = div_data.find_all('div')

                followers_count = int(divs[1].find(
                    'a').text.replace(',', '').split(' ')[0])
                following_count = int(divs[0].find(
                    'a').text.replace(',', '').split(' ')[0])

                # Extract account_id from URL
                account_id = re.search(r'twitter.com/([^/]+)', url).group(1)

                scraped_data.append([date.today(), account_id,
                                     followers_count, following_count])
        except Exception as e:
            raise TwitterScrapeException(msg=e, url=url)

        df = pd.DataFrame(
            scraped_data, columns=['date', 'account_id', 'follower_count', 'following_count'])

        return df

    print("************ GETTING TWITTER DATA *****************")
    urls = [
        'https://www.twitter.com/fusemachines',
        'https://www.twitter.com/sameermaskey'
    ]
    twitter_df = scrape_twitter(urls=urls)
    print(twitter_df.head(5))
    print("************ RECEIVED TWITTER DATA *****************")
    # function to get the follower and following count of two Tiktok account

    # def extract_count_from_text(text):
    #     matched = re.search(r'([\d.]+[kKmM]?)', text)
    #     if matched:
    #         clean_text = matched.group(1)

    #         multiplier = 1
    #         if 'k' in clean_text:
    #             multiplier = 1000
    #             clean_text = clean_text.replace('k', '').strip()
    #         elif 'm' in clean_text:
    #             multiplier = 1000000
    #             clean_text = clean_text.replace('m', '').strip()

    #         return int(float(clean_text) * multiplier)
    #     else:
    #         return None

    # def get_tiktok_data(account_url):
    #     # Load credentials if needed
    #     with open(os.path.join(os.getcwd(), 'credentials.yml'), 'r') as yaml_file:
    #         credentials = yaml.safe_load(yaml_file)

    #     options = webdriver.ChromeOptions()
    #     options.add_argument('--ignore-ssl-errors=yes')
    #     options.add_argument('--ignore-certificate-errors')
    #     options.add_argument("--headless")

    #     driver = webdriver.Remote(
    #         command_executor='http://10.0.20.205:4444/wd/hub',
    #         options=chrome_options
    #     )

    #     # driver.find_element_by_link_text("Get started free").click()
    #     driver.get(account_url)

    #     # Extract follower count using XPath
    #     try:
    #         follower_elem = driver.find_element(
    #             By.XPATH, '//*[@id="main-content-others_homepage"]/div/div[1]/h3/div[2]')
    #         follower_count = extract_count_from_text(follower_elem.text)

    #         following_elem = driver.find_element(
    #             By.XPATH, '//*[@id="main-content-others_homepage"]/div/div[1]/h3/div[1]')
    #         following_count = extract_count_from_text(following_elem.text)

    #         likes_elem = driver.find_element(
    #             By.XPATH, '//*[@id="main-content-others_homepage"]/div/div[1]/h3/div[3]')
    #         likes_count = extract_count_from_text(likes_elem.text)
# DAGs
#     account_id = account_url.split('tiktok.com/')[-1].strip('/')
#     df = pd.DataFrame({
#         'date': [datetime.now().strftime('%Y-%m-%d')],
#         'account_id': [account_id],
#         'follower_count': [followescraping_social_media_count


all_social_media_scraper()
# ## Function to write the DataFrame to s3

# with open(os.path.join(os.getcwd(), 'config.yml'), 'r') as yaml_file:
#     config = yaml.safe_load(yaml_file)

# s3_client = boto3.client('s3', aws_access_key_id=config['Credentials']['AccessKeyId'], aws_secret_access_key=config['Credentials']['SecretAccessKey'])

# def get_s3_subdirs(bucket_name, prefix):
#     '''
#     Returns a list of sub-directories within given prefix directory upto depth level 1. Returns full path of sub-directories from bucket root. Does not return files.
#     '''
#     try:
#         # try to get the sub directories
#         response = s3_client.list_objects_v2(
#             Bucket=bucket_name, Prefix=prefix, Delimiter='/')
#     except:
#         print(
#             f'Error!! Could not get sub-directories from: s3://{bucket_name}/{prefix}')
#         raise
#     else:
#         subdirectories = [prefix.get('Prefix')
#                         for prefix in response.get('CommonPrefixes', [])]
#         # print(f"List of subdirectories: {subdirectories}")
#         return subdirectories

# def create_directory_structure_s3(bucket_name, prefix, date_dict,subdir):
#     '''
#     This creates a directory structure in the destination of the following format, it the directory structure does not exist.

#     Format:
#         prefix/subdir/year=year/month=month/day=day

#     Here, subdir is equivalent to table-name. subdir does not have / at its end. However, prefix has / at its end.
#     '''
#     # full sub directory path is obtained by reading adding prefix to subdir path
#     full_subdir = f'{prefix}{subdir}'

#     # tuples of (parent folder, current folder)
#     list_of_directories = [
#         (prefix, '{}/'.format(full_subdir)),
#         ('{}/'.format(full_subdir),
#         '{}/year={}/'.format(full_subdir, date_dict['year'])),
#         ('{}/year={}/'.format(full_subdir, date_dict['year']), '{}/year={}/month={}/'.format(
#             full_subdir, date_dict['year'], date_dict['month'])),
#         ('{}/year={}/month={}/'.format(full_subdir, date_dict['year'], date_dict['month']), '{}/year={}/month={}/day={}/'.format(
#             full_subdir, date_dict['year'], date_dict['month'], date_dict['day']))
#     ]

#     # check if the directories already exist, if not create them
#     for (parent_directory, directory) in list_of_directories:
#         # list the directories that are in its parent folder, use get_s3_subdirs function
#         parent_subdir_list = get_s3_subdirs(
#             bucket_name=bucket_name, prefix=parent_directory)
#         if directory not in parent_subdir_list:
#             # create the directory in destination directory
#             try:
#                 s3_client.put_object(Bucket=bucket_name, Key=directory)
#             except:
#                 print(
#                     f'Error !! Could not create diretory structure: s3://{bucket_name}/{directory}')
#                 raise
#             else:
#                 print(f'Created directory: s3://{bucket_name}/{directory}')

# def write_dataframe_to_s3(s3_client, bucket_name: str, date_dict: dict, df: DataFrame, platform: str) -> None:
#     try:
#         with io.StringIO() as csv_buffer:
#             df.to_csv(csv_buffer, index=False)
#             response = s3_client.put_object(
#                 Bucket=bucket_name,
#                 Key=f"pr/{platform}_followers_count/year={date_dict['year']}/month={date_dict['month']}/day={date_dict['day']}/{platform}.csv",
#                 Body=csv_buffer.getvalue()
#             )
#             status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
#             if status == 200:
#                 print(f"Successful S3 put_object response for {platform}. Status - {status}")
#             else:
#                 print(f"Unsuccessful S3 put_object response for {platform}. Status - {status}")
#     except Exception as e:
#         print(f'Exception: {e}')

# # if __name__ == '__main__':
# date_today = str(datetime.now().date())
# date_dict = {
#     'year': date_today.split('-')[0],
#     'month': date_today.split('-')[1],
#     'day': date_today.split('-')[2]
# }

# platforms = ['instagram', 'facebook', 'linkedin', 'twitter', 'tiktok']

# for platform in platforms:
#     create_directory_structure_s3(
#         bucket_name='fuse-ia-pr-bronze-dev',
#         prefix='pr/',
#         date_dict=date_dict,
#         subdir=f'{platform}_followers_count',
#     )
#     if platform == 'instagram':
#         write_dataframe_to_s3(
#             s3_client=s3_client,
#             bucket_name='fuse-ia-pr-bronze-dev',
#             date_dict=date_dict,
#             df=instagram_df,
#             platform=platform
#         )
#     elif platform == 'facebook':
#         write_dataframe_to_s3(
#             s3_client=s3_client,
#             bucket_name='fuse-ia-pr-bronze-dev',
#             date_dict=date_dict,
#             df=facebook_df,
#             platform=platform
#         )
#     elif platform == 'linkedin':
#         write_dataframe_to_s3(
#             s3_client=s3_client,
#             bucket_name='fuse-ia-pr-bronze-dev',
#             date_dict=date_dict,
#             df=linkedin_df,
#             platform=platform
#         )
#     elif platform == 'twitter':
#         write_dataframe_to_s3(
#             s3_client=s3_client,
#             bucket_name='fuse-ia-pr-bronze-dev',
#             date_dict=date_dict,
#             df=linkedin_df,
#             platform=platform
#         )
#     elif platform == 'tiktok':
#         write_dataframe_to_s3(
#             s3_client=s3_client,
#             bucket_name='fuse-ia-pr-bronze-dev',
#             date_dict=date_dict,
#             df=linkedin_df,
#             platform=platform
#         )
