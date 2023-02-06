import requests
import time
from bs4 import BeautifulSoup
import os
import random
import json
import bs4
import pandas as pd


class Request:
    acceptEncoding = "gzip, deflate, br"
    acceptLanguage = "en-US,en;q=0.9"
    userAgents = os.listdir('UaJson/')
    
    def create_request(self, link):
        with open(os.path.join('UaJson', random.choice(self.userAgents)), 'r') as f:
            ua = random.choice(json.load(f))['ua']

        headers = {
            'User-Agent': ua,
            'Accept-Language': self.acceptLanguage,
            'Accept-Encoding': self.acceptEncoding
        }

        return requests.get(link, headers=headers, allow_redirects=True)


class RequestFailedException(Exception):
    pass


class AmazonScraper:
    categoryLinks = {
        'Men Clothing': 'https://www.amazon.com/s?i=specialty-aps&bbn=16225019011&rh=n%3A7141123011%2Cn%3A16225019011%2Cn%3A1040658&ref=nav_em__nav_desktop_sa_intl_clothing_0_2_13_2',
        'Men Shoes': 'https://www.amazon.com/s?i=specialty-aps&bbn=16225019011&rh=n%3A7141123011%2Cn%3A16225019011%2Cn%3A679255011&ref=nav_em__nav_desktop_sa_intl_shoes_0_2_13_3',
        'Women Clothing': 'https://www.amazon.com/s?i=specialty-aps&bbn=16225018011&rh=n%3A7141123011%2Cn%3A16225018011%2Cn%3A1040660&ref=nav_em__nav_desktop_sa_intl_clothing_0_2_12_2',
        'Women Shoes': 'https://www.amazon.com/s?i=specialty-aps&bbn=16225018011&rh=n%3A7141123011%2Cn%3A16225018011%2Cn%3A679337011&ref=nav_em__nav_desktop_sa_intl_shoes_0_2_12_3'
    }

    request = Request()

    page = 1

    def __init__(self, item_container, url, img_src, title, number_of_purchase, rating):
        self.item_container = item_container
        self.url = url
        self.img_src = img_src
        self.title = title
        self.number_of_purchase = number_of_purchase
        self.rating = rating
        # self.price = price
        self.current_url = None
        self.page_number = 1

    def start_request(self, link):
        response = self.request.create_request(link=link)
        self.current_url = response.url
        if response.status_code == 200:
            return response
        else:
            raise RequestFailedException('request failed with status code %d' % response.status_code)

    def get_items(self, response):
        parser = BeautifulSoup(response.content, 'html.parser')
        items = parser.find_all(self.item_container["tag"], class_=self.item_container["class"],
                                id_=self.item_container["id"])
        if len(items) == 0:
            items = parser.find_all(self.item_container["tag"], class_=self.item_container["class2"],
                                    id_=self.item_container["id"])
        return items

    def get_url(self, item: bs4.element.Tag):
        url = item.find(self.url["tag"], class_=self.url["class"], id_=self.url["id"])
        if not url:
            url = item.find(self.url["tag"], class_=self.url["class2"])
        return url["href"]

    def get_image_src(self, item: bs4.element.Tag):
        image = item.find(self.img_src['tag'], class_=self.img_src["class"], id_=self.img_src['id'])
        if not image:
            image = item.find(self.img_src['tag'], class_=self.img_src["class2"])
        return image["src"]

    def get_title(self, item: bs4.element.Tag):
        title = item.find(self.title["tag"], class_=self.title["class"], id_=self.title["id"])
        if not title:
            title = item.find(self.title["tag"], class_=self.title["class2"], id_=self.title["id"])
        return title.text

    def get_number_of_purchases(self, item: bs4.element.Tag):
        numbers = item.find(self.number_of_purchase['tag'], class_=self.number_of_purchase['class'],
                            id_=self.number_of_purchase['id'])
        if not numbers:
            numbers = item.find(self.number_of_purchase['tag'], class_=self.number_of_purchase['class2'])
        if numbers:
            return numbers.text
        else:
            return None

    def get_ratings(self, item: bs4.element.Tag):
        def get_float(string):
            for word in string.split():
                try:
                    float(word)
                    return float(word)
                except ValueError:
                    continue

        ratings = item.find(self.rating["tag"], class_=self.rating["tag"], id_=self.rating["id"])
        if not ratings:
            ratings = item.find(self.rating["tag"], class_=self.rating["class2"],)
        if ratings:
            return get_float(ratings.text)
        else:
            return None

    @staticmethod
    def time_sleep(duration: int):
        time.sleep(random.randint(duration-2, duration+2))

    def next_page(self):
        self.page_number = self.page_number + 1
        parts = self.current_url.split("&")
        if "page=" in parts[3]:
            parts[3] = f"page={self.page_number}"
            parts = parts[:4]
        else:
            parts = parts[:3]
            parts.append("page={}".format(self.page_number))
        url = '&'.join(parts)
        try:
            return self.start_request(url)
        except RequestFailedException:
            return False


class ScrapeItem:
    def __init__(self, img_src, url, title, number_of_purchases, ratings):
        self.img_src = img_src
        self.url = url
        self.title = title
        self.number_of_purchases = number_of_purchases
        self.ratings = ratings

    def create_dict(self):
        return {
            'url': self.url,
            'img_src': self.img_src,
            'title': self.title,
            'number_of_purchases': self.number_of_purchases,
            'ratings': self.ratings
        }

    def create_dataframe(self):
        return pd.DataFrame([self.create_dict()])


# class ScrapeElements:
#     def __init__(self, ):

categoryLinks = {
    'Men Clothing': 'https://www.amazon.com/s?i=specialty-aps&bbn=16225019011&rh=n%3A7141123011%2Cn%3A16225019011%2Cn%3A1040658&ref=nav_em__nav_desktop_sa_intl_clothing_0_2_13_2',
    'Men Shoes': 'https://www.amazon.com/s?i=specialty-aps&bbn=16225019011&rh=n%3A7141123011%2Cn%3A16225019011%2Cn%3A679255011&ref=nav_em__nav_desktop_sa_intl_shoes_0_2_13_3',
    'Women Clothing': 'https://www.amazon.com/s?i=specialty-aps&bbn=16225018011&rh=n%3A7141123011%2Cn%3A16225018011%2Cn%3A1040660&ref=nav_em__nav_desktop_sa_intl_clothing_0_2_12_2',
    'Women Shoes': 'https://www.amazon.com/s?i=specialty-aps&bbn=16225018011&rh=n%3A7141123011%2Cn%3A16225018011%2Cn%3A679337011&ref=nav_em__nav_desktop_sa_intl_shoes_0_2_12_3'
}


def start_scrape(links: dict):
    item_container = {"tag": "div", "class": "sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16"
                                             " sg-col s-widget-spacing-small sg-col-4-of-20", "class2": "s-result-item"
                                                    " s-asin sg-col s-widget-spacing-small sg-col-6-of-12", "id": ""}
    url = {"tag": "a", "class": "a-link-normal s-no-outline", "class2": "a-link-normal s-faceout-link a-text-normal",
           "id": ""}
    img_src = {"tag": "img", "class": "s-image", "id": ""}
    title = {"tag": "span", "class": "a-size-base-plus a-color-base a-text-normal",
             "class2": "a-size-small a-color-base a-text-normal", "id": ""}
    number_of_purchases = {"tag": "span", "class": "a-size-base s-underline-text",
                           "class2": "a-size-mini a-color-base puis-light-weight-text", "id": ""}
    ratings = {"tag": "span", "class": "a-icon-alt",
               "class2": "a-icon a-icon-star-small a-star-small-4-5 aok-align-bottom", "id": ""}
    for key, value in links.items():
        c = 0
        df = pd.DataFrame(columns=['url', 'img_src', 'title', 'number_of_purchases', 'ratings'])
        scraper = AmazonScraper(item_container, url, img_src, title, number_of_purchases, ratings)
        response = scraper.start_request(value)
        while True:
            items = scraper.get_items(response)
            if len(items) == 0:
                print()
            for item in items:
                item_url = scraper.get_url(item)
                item_img = scraper.get_image_src(item)
                item_title = scraper.get_title(item)
                item_number_of_purchases = scraper.get_number_of_purchases(item)
                item_ratings = scraper.get_ratings(item)
                item_object = ScrapeItem(item_img, item_url, item_title, item_number_of_purchases, item_ratings)
                df_new = item_object.create_dataframe()
                df = pd.concat([df, df_new], ignore_index=True).reset_index(drop=True)
                c += 1
            df.to_csv(f'{key}.csv')
            if scraper.page_number != c//48:
                print()
            print(f'from category {key} scraped {c} numbers of items from page {scraper.page_number}.')
            scraper.time_sleep(3)
            response = scraper.next_page()
            print(response.status_code)
            if not response:
                break


start_scrape(categoryLinks)

"""
https://www.amazon.com/s?i=specialty-aps&bbn=16225019011&rh=n%3A7141123011%2Cn%3A16225019011%2Cn%3A1040658&ref=nav_em__nav_desktop_sa_intl_clothing_0_2_13_2
https://www.amazon.com/s?i=fashion-mens-intl-ship&bbn=16225019011&rh=n%3A7141123011%2Cn%3A16225019011%2Cn%3A1040658&\
page=2&qid=1675681186&ref=sr_pg_2"""
