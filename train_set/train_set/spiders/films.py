import json

import scrapy

from train_set.items import FilmItem


BASE_URL = "https://allocine.fr"


# Loading file with ids of films to scrape.
with open("box_office.json", "r") as file:
    id_entries = json.load(file)


class FilmsSpider(scrapy.Spider):
    name = "films"

    custom_settings = {
        'ITEM_PIPELINES': {"train_set.pipelines.CleanPipeline": 100}
    }    

    def start_requests(self):        
        for elem in id_entries:
            item = FilmItem()
            item["film_id"] = elem["film_id"]
            item["entries"] = elem["entries"]
            film_page_url = f"{BASE_URL}/film/fichefilm_gen_cfilm={item['film_id']}.html"

            # Follow the film page
            yield scrapy.Request(url = film_page_url,
                                 callback = self.parse_film_page,
                                 meta = {"item": item})
    
    def parse_film_page(self, response):
        item = response.meta["item"]
        item["title"] = response.css("div.titlebar-title::text").get()
        item["img_src"] = response.css("[title^='Bande-'] > img::attr(src)").get()

        # release, duration, genres
        raw_info = response.css('div.meta-body-info ::text').getall()
        info = [item.strip('\n') for item in raw_info
                if item not in ('\nen VOD\n', '\nen DVD\n', '\nen salle\n', '|', '\n', ',\n')]
        try:
            item["release"] = info[0]
        except BaseException:
            item["release"] = None
        try:
            item["duration"] = info[1]
        except BaseException:
            item["duration"] = None
        item["genres"] = info[2:]  # A slice never raises an exception

        # Ratings press & viewers
        ratings = response.css("span.stareval-note::text").getall()
        try:
            item["press_ratings"] = ratings[0]
        except BaseException:
            item["press_ratings"] = None
        try:
            item["viewers_ratings"] = ratings[1]
        except BaseException:
            item["viewers_ratings"] = None

        item["synopsis"] = response.css("section#synopsis-details div.content-txt p::text").get()

        # Follow the casting page
        casting_page_url = f"{BASE_URL}/film/fichefilm-{item['film_id']}/casting/"

        yield scrapy.Request(url = casting_page_url,
                             callback = self.parse_casting_page,
                             meta = {"item": item})

    def parse_casting_page(self, response):
        item = response.meta["item"]
        item["director"] = response.css('section.casting-director a::text').getall()
        item["casting"] = response.css('section.casting-actor *.meta-title-link::text').getall()
        societies_fields = response.css('div.gd-col-left div.casting-list-gql')[-1]
        item["societies"] = societies_fields.css("div.md-table-row span.link::text").getall()
        
        yield item
