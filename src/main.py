#!/usr/bin/python3
#Author: egely1337
#Date: 10/4/2023


from util import *
from bs4 import BeautifulSoup, Tag
from requests import Session
from json import load
from dataclasses import dataclass
import secrets

config = load(open("config.json"))
dumpfile = f"./results/result_{secrets.token_hex(8)}.txt"

@dataclass
class YelpStore:
    name: str
    yelp_url: str
    website_url: str | None
    stateCode: str

    def __hash__(self) -> int:
        return hash(self.name+self.yelp_url+self.website_url+self.stateCode)

class Yelp:
    def __init__(self) -> None:
        self.session = Session() # session for get requests
        self.tagList: list[str] = config.get("tags") # return list from config.json
        self.tags = return_tags(self.tagList) # return tags as a list
        self.stores: list[YelpStore] = [] # a list that contains yelpstores
        self.states = config.get("states")

    def get_store_webpage(self, yelp_url: str):
        r = self.session.get(
            url=yelp_url
        )
        bs4 = BeautifulSoup(r.text, "html.parser")
        list: Tag = bs4.find("a", attrs={"role" : "link", "target" : "_blank", "rel" : "noopener"})
        if list:
            return list.text 

    def add_store(self, elements: list[Tag], stateCode: str):
        for element in elements:
            element: Tag
            if element.attrs.get("name"):
                name = element.attrs.get("name")
                link = "https://yelp.com" + element.attrs.get("href")
                webpage = self.get_store_webpage(yelp_url=link)
                print(f"name={name} | yelp={link} | website={webpage} | stateCode={stateCode}")
                store = YelpStore(
                    name=name,
                    yelp_url=link,
                    website_url=webpage,
                    stateCode=stateCode
                )
                
                if store not in self.stores:
                    self.stores.append(store) # add store if not in self.stores

                    if webpage:
                        open(dumpfile, "a+").write(webpage + '\n') # same as write if store not in self.stores

    def scrape(self, stateCode: str) -> None:
        for i in range(23):
            request = self.session.get(
                    url=f"https://www.yelp.com/search?find_desc={self.tags}&find_loc={stateCode}&start={i * 10}"
            ) 

            if request.status_code == 200:
                bs4 = BeautifulSoup(request.text, "html.parser")
                href_list = bs4.find_all("a") # get all <a> element from .html
                
                self.add_store(elements=href_list, stateCode=stateCode) # add stores to self.stores with their own website

    def work(self):
        for state in self.states:
            print(f"{state} is processing.")
            self.scrape(
                stateCode=state
            )




def main():
    yelp = Yelp()
    yelp.work()

main()