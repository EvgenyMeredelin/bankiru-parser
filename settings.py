import re

import requests


PRODUCTS: dict[str, str] = {
    # услуги для физических лиц
    "autocredits"        : "Автокредит",
    "deposits"           : "Вклад",
    "debitcards"         : "Дебетовая карта",
    "transfers"          : "Денежный перевод",
    "remote"             : "Дистанционное обслуживание физических лиц",
    "hypothec"           : "Ипотека",
    "creditcards"        : "Кредитная карта",
    "mobile_app"         : "Мобильное приложение",
    "individual"         : "Обслуживание физических лиц",
    "credits"            : "Потребительский кредит",
    "restructing"        : "Реструктуризация/рефинансирование",
    "other"              : "Другое (физические лица)",

    # услуги для юридических лиц
    "bank_guarantee"     : "Банковская гарантия",
    "businessdeposits"   : "Депозит",
    "business_remote"    : "Дистанционное обслуживание юридических лиц",
    "salary_project"     : "Зарплатный проект",
    "businesscredits"    : "Кредитование бизнеса",
    "leasing"            : "Лизинг",
    "business_mobile_app": "Мобильное приложение для бизнеса",
    "corporate"          : "Обслуживание юридических лиц",
    "legal"              : "Обслуживание юридических лиц",
    "rko"                : "Расчетно-кассовое обслуживание",
    "acquiring"          : "Эквайринг",
    "business_other"     : "Другое (юридические лица)"
}

BASE_URL: str = "https://www.banki.ru"

# example
# https://www.banki.ru/services/responses/list/product/deposits/?page=1&type=all&rate[]=1&rate[]=2
PAGE_URL: str = (
    "{}/services/responses/list/product/{}/"
    "?page={}&type=all&rate[]=1&rate[]=2"
)

REVIEW_URL_PATTERN: re.Pattern = re.compile(
    r"(?:<a href=\")(/services/responses/bank/response/\d+)(?:/\" data)"
)

REVIEW_CONTENT_PATTERN: re.Pattern = re.compile(
    r"(\{)(?: \"@type\":\"Review\", "             # opening curly brace
    r"\"author\":\"[^\"]*\", )"
    r"(\"datePublished\":\"[^\"]*\", "            # keep this field
    r"\"reviewBody\":\"[^\"]*\", )"               # keep this field
    r"(?:\"name\":\"[^\"]*\", "
    r"\"reviewRating\": "
    r"\{ \"@type\":\"Rating\", "
    r"\"bestRating\":\"[^\"]*\", "
    r"\"ratingValue\":\"[^\"]*\", "
    r"\"worstRating\":\"[^\"]*\" \}, )"
    r"(\"itemReviewed\": "                        # keep this field
    r"\{)(?: \"@type\":\"BankOrCreditUnion\", )"  # opening curly brace
    r"(\"name\":\"[^\"]*\")(?:, "                 # keep this field
    r"\"telephone\":\"[^\"]*\", "
    r"\"address\": "
    r"\{ \"@type\":\"PostalAddress\", "
    r"\"streetAddress\":\"[^\"]*\", "
    r"\"addressCountry\":\"[^\"]*\", "
    r"\"postalCode\":\"[^\"]*\" \})( \} \})"      # closing curly braces
)

LOC_PATTERN: re.Pattern = re.compile(
    r"(?:<span class=\"l3a372298\">)([^<]+)(?:</span>)"
)

HEADERS = requests.utils.default_headers()
headers_update = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
        "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    ),
    "Accept-Language": "ru,en;q=0.9"
}
HEADERS.update(headers_update)
