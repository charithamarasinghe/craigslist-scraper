import logging
import configparser
import os
import sys

base_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, base_path)

import scraper

config = configparser.ConfigParser()
config.read(base_path + "/config.ini")

logging.basicConfig(filename=config["MAIN"]["log_file"], filemode='w',
                    format="%(asctime)s %(levelname)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def main():
    logger.info("job started")

    location_val = "losangeles"
    distance_val = "50"
    postal_val = 90069
    auto_make_model_val = "BMW"
    min_auto_year_val = "2013"
    max_auto_year_val = "2018"
    max_auto_miles_val = "80000"
    auto_title_status_val = "1"

    c_scraper = scraper.CraiglistScraper(location=location_val, distance=distance_val, postal=postal_val,
                                         auto_make_model=auto_make_model_val, min_auto_year=min_auto_year_val,
                                         max_auto_year=max_auto_year_val, max_auto_miles=max_auto_miles_val,
                                         auto_title_status=auto_title_status_val)
    data = c_scraper.extract_post_data()

    return data


if __name__ == "__main__":
    main()
