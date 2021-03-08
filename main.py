import json
import logging
import configparser
import os
import sys
import time

base_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, base_path)

config = configparser.ConfigParser()
config.read(base_path + "/config.ini")

logging.basicConfig(filename=config["MAIN"]["log_file"], filemode='w',
                    format="%(asctime)s %(levelname)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

import scraper
import slack_msg_sender
from email_sender import send_mail


def main():
    logger.info("job started")

    with open('filters.json') as f:
        filters = json.load(f)
    f.close()

    for filter_val in filters:
        location_val = filter_val["location_val"]
        distance_val = filter_val["distance_val"]
        postal_val = filter_val["postal_val"]
        auto_make_model_val = filter_val["auto_make_model_val"]
        min_auto_year_val = filter_val["min_auto_year_val"]
        max_auto_year_val = filter_val["max_auto_year_val"]
        max_auto_miles_val = filter_val["max_auto_miles_val"]
        auto_title_status_val = filter_val["auto_title_status_val"]

        c_scraper = scraper.CraiglistScraper(location=location_val, distance=distance_val, postal=postal_val,
                                             auto_make_model=auto_make_model_val, min_auto_year=min_auto_year_val,
                                             max_auto_year=max_auto_year_val, max_auto_miles=max_auto_miles_val,
                                             auto_title_status=auto_title_status_val)
        data = c_scraper.extract_post_data()

        sms = slack_msg_sender.SlackMsgSender(channel=auto_make_model_val)
        for post in data:
            sms.send_slack_msg(msg_text=post["post_title"])
            send_mail(email_subject=post["post_title"], body_text=post["post_url"])
            # wait 1 second before sending out emails and slack msgs
            time.sleep(1)

        # wait 5 seconds before starting next filter set
        time.sleep(5)


if __name__ == "__main__":
    main()
