# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 18:23:51 2016

@author: Stephane
"""

from bs4 import BeautifulSoup
from urllib2 import urlopen


IMDB_URL = "http://www.imdb.com/search/title?sort=num_votes,desc&start=1&title_type=feature&year=2005,2014"

def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html, "html.parser")

imdb = make_soup(IMDB_URL)
#response = requests.get(IMDB_URL)
#test2 = response.content

#print imdb.prettify()
first_movie = imdb.find("div", attrs={"class": "lister-item mode-advanced"})
print first_movie.prettify()
for t in first_movie.children:
    print t
first_movie.find("img")["alt"]
first_movie.find("span", attrs={"class": "runtime"}).text
first_movie.find("span", attrs={"class": "genre"}).text
first_movie.find("span", attrs={"class": "lister-item-index unbold text-primary"}).text
first_movie.find("span", attrs={"class": "lister-item-year text-muted unbold"}).text
first_movie.find("h3").find("a").text
first_movie.h3.a.text