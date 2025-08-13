import datetime
import itertools
import json
import logging
import time
from typing import Literal, Self

import logfire
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from environs import env

from settings import *
from tools import clean_text_pipe


env.read_env()
logfire.configure(token=env("LOGFIRE_TOKEN"), service_name="parser")
logging.basicConfig(handlers=[logfire.LogfireLoggingHandler()])
logger = logging.getLogger("bankiru_parser_logger")
logger.setLevel(logging.INFO)


class BankiruReviewsParser:
    """
    Parser of negative reviews posted on banki.ru.
    """

    def __init__(self) -> None:
        self.records = []

    def parse(
        self,
        product: Literal[tuple(PRODUCTS)],  # type: ignore
        *,
        start_date: datetime.datetime | None = None,
        delta: relativedelta = relativedelta(days=1),
        start_page: int = 1  # set page manually to skip irrelevant reviews
    ) -> Self:  # chain multiple parsing tasks with a fluent interface
        """
        Parse reviews tagged by the authors as `product` and posted at
        [`start_date`; `start_date` + `delta`). Interval defaults to yesterday.
        """

        # avoid using datetime object as a default value
        start_date = start_date or (today() - relativedelta(days=1))
        end_date = start_date + delta
        page_counter = itertools.count(start_page)

        while True:
            time.sleep(10)  # wait to avoid 403/429 errors
            args = (BASE_URL, product, next(page_counter))
            page = self.__class__.send_request(PAGE_URL.format(*args))
            if page is None: continue

            page = " ".join(page.text.replace("\\", "").split())
            match_factory = zip(
                REVIEW_CONTENT_PATTERN.finditer(page),
                REVIEW_URL_PATTERN.finditer(page)
            )

            for content_match, url_match in match_factory:
                time.sleep(10)
                record = json.loads("".join(content_match.groups()))
                descr = f"{product} {record["datePublished"]}"
                date_published = datetime.datetime.strptime(
                    record["datePublished"], "%Y-%m-%d %H:%M:%S"
                )
                if date_published >= end_date:
                    logger.info(f"{descr}: the right limit not yet reached")
                    continue
                if date_published < start_date:
                    logger.info(f"{descr}: the left limit has been crossed")
                    break

                review_url = BASE_URL + url_match.group(1)
                response = self.__class__.send_request(review_url)
                if response is None: continue

                record["reviewBody"] = clean_text_pipe(record["reviewBody"])
                record["bankName"] = record["itemReviewed"]["name"].strip()
                record["url"] = review_url
                record["location"] = LOC_PATTERN.search(response.text).group(1)
                record["product"] = PRODUCTS[product]

                self.records.append(record)
                logger.info(f"{descr}: successfully parsed")
            else:
                continue  # if inner loop didn't break then continue the outer
            break  # if inner loop was terminated then terminate the outer too

        return self

    @property
    def reviews(self) -> list[dict[str, str]]:
        return (
            pd.DataFrame.from_records(self.records)
            .drop_duplicates(subset=["reviewBody", "product"])
            .to_dict(orient="records")
        )

    @staticmethod
    def send_request(url: str) -> requests.Response | None:
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                logger.error(f"{url}: {response.status_code}")
                return None
            return response
        except Exception as exc:
            logger.error(f"{url}: {exc}", exc_info=False)
            return None
