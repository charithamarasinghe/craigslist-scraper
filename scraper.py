import datetime
from typing import Union, List
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import os

from main import logger
from main import config

base_path = os.path.dirname(os.path.realpath(__file__))
web_driver_file = base_path + config["MAIN"]["web_driver_file"]


def get_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--disable-infobars')
    options.add_argument('-disable-notifications')
    options.add_argument('--no-sandbox')
    return options


def get_sel_page(url: str, page_start: int = None) -> Union[BeautifulSoup, None]:
    options = get_chrome_options()
    driver = webdriver.Chrome(web_driver_file, options=options)
    url = url + '&s={page_start}'.format(page_start=page_start) if page_start is not None else url
    driver.get(url)

    page_soup = None
    try:
        delay = 5
        wait = WebDriverWait(driver, delay)
        wait.until(ec.presence_of_element_located((By.ID, "searchform")))
        print("Page is ready")
        logger.info("Page loaded successfully")

        page = driver.page_source
        page_soup = BeautifulSoup(page, 'html.parser')

    except TimeoutException:
        print("Loading took too much time")
        logger.error("Loading took too much time")

    driver.stop_client()
    driver.close()
    driver.quit()

    return page_soup


def filter_post_based_on_date(all_post_data: List[dict]) -> List[dict]:
    filtered_posts = []
    for post in all_post_data:
        post_date = datetime.datetime.strptime(post["date_time"], '%Y-%m-%d %H:%M')
        look_back_days = int(config["MAIN"]["look_back_days"])

        day_buffer_start = datetime.datetime.now() - datetime.timedelta(days=(look_back_days + 1))
        day_buffer_end = datetime.datetime.now() - datetime.timedelta(days=(look_back_days - 1))

        day_buffer_start_val = datetime.datetime(day_buffer_start.year,
                                                 day_buffer_start.month,
                                                 day_buffer_start.day, 23, 59, 59, 0)
        day_buffer_end_val = datetime.datetime(day_buffer_end.year,
                                               day_buffer_end.month,
                                               day_buffer_end.day, 0, 0, 0, 0)

        if day_buffer_start_val < post_date < day_buffer_end_val:
            filtered_posts.append(post)
    return filtered_posts


def get_next_page_start(page_soup: BeautifulSoup) -> Union[int, None]:
    next_start = None
    try:
        buttons = page_soup.find(
            "div", {"class": "search-legend"}).find("div", {"class": "paginator"}).find("span", {"class": "buttons"})
        total_count = int(buttons.find("span", {"class": "totalcount"}).text)
        range_to = int(buttons.find("span", {"class": "range"}).find("span", {"class": "rangeTo"}).text)
        if total_count > range_to:
            next_start = range_to
            return next_start
        else:
            return next_start
    except Exception as error:
        logger.error(str(error))
        return next_start


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

        self.url = f"https://{location}.craigslist.org/search/sso?sort=date&search_distance={distance}&" \
                   f"postal={postal}&auto_make_model={auto_make_model}&min_auto_year={min_auto_year}&max_auto_year" \
                   f"={max_auto_year}&max_auto_miles={max_auto_miles}&auto_title_status={auto_title_status}"

    def collect_post_data(self, page_row_list) -> List[dict]:
        page_post_data = []
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

                page_post_data.append(post_data)
            except Exception as error:
                print(str(error))
                logger.error(str(error))

        return page_post_data

    def extract_post_data(self):
        page_soup = get_sel_page(self.url)
        page_rows = page_soup.find("ul", {"class": "rows"})
        page_row_list = page_rows.findAll("li", {"class": "result-row"})

        all_post_data = []
        post_data = self.collect_post_data(page_row_list=page_row_list)
        all_post_data.extend(post_data)

        # next_page_start = get_next_page_start(page_soup=page_soup)
        # while next_page_start is not None:
        #     page_soup = get_sel_page(self.url, page_start=next_page_start)
        #     page_rows = page_soup.find("ul", {"class": "rows"})
        #     page_row_list = page_rows.findAll("li", {"class": "result-row"})
        #     post_data = self.collect_post_data(page_row_list=page_row_list)
        #     all_post_data.extend(post_data)

        filtered_post_data = filter_post_based_on_date(all_post_data=all_post_data)

        return filtered_post_data
