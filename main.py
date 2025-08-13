import time

import requests
import schedule
from environs import env

from parser import BankiruReviewsParser
from settings import PRODUCTS


def job() -> None:
    """
    Parse reviews and upload to the database.
    """

    parser = BankiruReviewsParser()

    for product in PRODUCTS:
        parser.parse(product)

    requests.post(
        url=env("CREATE_REVIEWS_ENDPOINT"),
        headers={"API-Token": env("API_TOKEN")},
        json=parser.reviews
    )


if __name__ == "__main__":
    schedule.every().day.at("00:05", "Europe/Moscow").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
