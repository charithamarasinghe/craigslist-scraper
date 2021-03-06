from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup
import os
import configparser

base_path = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(base_path + "/config.ini")

web_driver_file = base_path + config["MAIN"]["web_driver_file"]


def get_sel_page(url: str) -> BeautifulSoup:
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--disable-infobars')
    options.add_argument('-disable-notifications')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(web_driver_file, options=options)
    driver.get(url)
    try:
        delay = 5
        wait = WebDriverWait(driver, delay)
        wait.until(ec.presence_of_element_located((By.ID, "searchform")))
        print("Page is ready")
    except TimeoutException:
        print("Loading took too much time")

    page = driver.page_source
    page_soup = BeautifulSoup(page, 'html.parser')
    driver.stop_client()
    driver.close()
    driver.quit()

    return page_soup


def get_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--disable-infobars')
    options.add_argument('-disable-notifications')
    options.add_argument('--no-sandbox')
    return options


class CraiglistScraper(object):
    def __init__(self, location, distance, postal, auto_make_model, min_auto_year, max_auto_year, max_auto_miles,
                 auto_title_status):
        self.location = location
        self.distance = distance
        self.postal = postal
        self.auto_make_model = auto_make_model
        self.min_auto_year = min_auto_year
        self.max_auto_year = max_auto_year
        self.max_auto_miles = max_auto_miles
        self.auto_title_status = auto_title_status

        self.url = f"https://{location}.craigslist.org/search/cta?purveyor-input=all&search_distance={distance}&" \
                   f"postal={postal}&auto_make_model={auto_make_model}&min_auto_year={min_auto_year}&max_auto_year" \
                   f"={max_auto_year}&max_auto_miles={max_auto_miles}&auto_title_status={auto_title_status}"

    def extract_post_data(self):
        page_soup = get_sel_page(self.url)
        page_rows = page_soup.find("ul", {"class": "rows"})
        page_row_list = page_rows.findAll("li", {"class": "result-row"})

        all_post_data = []
        for post in page_row_list:
            try:
                post_data = dict()
                post_data["price"] = post.find("span", {"class": "result-price"}).text

                basic_info = post.find("div", {"class": "result-info"})
                post_data["date_time"] = basic_info.find("time", {"class": "result-date"})['datetime']
                post_data["post_url"] = basic_info.find("a", {"class": "result-title hdrlnk"})['href']
                post_data["post_title"] = basic_info.find("a", {"class": "result-title hdrlnk"}).text
                post_data["location"] = self.location
                post_data["distance"] = self.distance
                post_data["postal"] = self.postal
                post_data["auto_make_model"] = self.auto_make_model
                post_data["min_auto_year"] = self.min_auto_year
                post_data["max_auto_year"] = self.max_auto_year
                post_data["max_auto_miles"] = self.max_auto_miles
                post_data["auto_title_status"] = self.auto_title_status

                all_post_data.append(post_data)
            except Exception as error:
                print(str(error))

        return all_post_data
