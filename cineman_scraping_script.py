import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import requests
from bs4 import BeautifulSoup

import pandas as pd
import time
from datetime import date
import re
import json


def is_time_format(string):
    try:
        time.strptime(string, '%H:%M')
        return True
    except ValueError:
        return False


# Use Selenium to scrape contents
options = FirefoxOptions()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
driver.get("https://www.cineman.ch/en/showtimes/city/")
time.sleep(15)   # have to wait for the advertisement to end

cookie_button = driver.find_element_by_class_name("cc-btn")
cookie_button.click()
time.sleep(2)

sorting_buttons = driver.find_elements_by_class_name("text-overflow-hidden")
sorting_buttons[2].click()

region_dropdown = driver.find_element_by_class_name("selectize-control")
region_dropdown.click()

input_div = driver.find_elements_by_xpath('//input[@type="text"]')
input_div[6].send_keys("Zürich")
input_div[6].send_keys(Keys.RETURN)

save_button = driver.find_element_by_class_name("select-region-save")
save_button.click()

content = BeautifulSoup(driver.page_source, features="html.parser")
driver.close()

movies = content.findAll("div", {"class": "col-xs-12 col-sm-9"})

# Now create the data frame
# Initialize the lists to store the details for each movie screening
movies_list = []
genres_list = []
cinemas_list = []
places_list = []
age_limits = []
movie_links = []
all_showtimes_lists = []
all_languages_lists = []

for movie in movies:
    # Movie title
    title = movie.find("h4").get_text()
    movies_list.append(title)

    # Movie genre
    genre = movie.find("p").get_text()
    genres_list.append(genre)

    # Cinemas and place
    cinemas = movie.findAll("h5")
    cinema_names = []
    places = []

    for cinema in cinemas:
        cinema_name = cinema.find("em").get_text()
        cinema_names.append(cinema_name)
        place = cinema.findAll("a")[1].get_text()
        places.append(place)

    cinemas_list.append(cinema_names)
    places_list.append(places)

    # Age limit
    age_links = movie.findAll("a", {"class": "link"})
    age_limit = age_links[-1].get_text()
    if age_limit == "Reservation":
        age_limit = age_links[-2].get_text()
        age_limits.append(age_limit)
    elif age_limit.find("Y.") == -1:
        age_limits.append("none")
    else:
        age_limits.append(age_limit)

    # Movie links
    movie_links_a = movie.findAll("a", href=True)
    movie_links.append(f'https://www.cineman.ch{movie_links_a[0]["href"]}')

    # Showtimes and languages
    showtimes_list_div = movie.find("div", {"class": "showtimes-list"})
    showtimes_string = showtimes_list_div.prettify().split("h5")
    showtimes_list = []
    languages_list = []

    for string in showtimes_string:
        strings = re.sub('<[^<]+?>\n', '', string).split(" ")
        showtimes = []
        languages = []

        for s in strings:
            s = s.strip("<></–)")
            s = re.sub("\t", "", s)
            s = s.strip()

            if is_time_format(s):
                showtimes.append(s)

            elif (s.find("/") != -1 and s.find("Y.") == -1) or s in ["G", "F", "O", "I", "E"]:
                languages.append(s)

        if showtimes:
            showtimes_list.append(showtimes)
        if languages:
            languages_list.append(languages)

    if showtimes_list:
        all_showtimes_lists.append(showtimes_list)
    if languages_list:
        all_languages_lists.append(languages_list)

# Initializing the dictionary to store the lists
all_info_dict = dict()

all_info_dict["movie"] = movies_list
all_info_dict["genre"] = genres_list
all_info_dict["age_limit"] = age_limits
all_info_dict["language"] = all_languages_lists
all_info_dict["movie_link"] = movie_links
all_info_dict["showtime"] = all_showtimes_lists
all_info_dict["date"] = date.today()
all_info_dict["cinema"] = cinemas_list
all_info_dict["place"] = places_list

movie_program_df = pd.DataFrame(all_info_dict).explode(["cinema", "showtime", "place", "language"]).explode(
    ["showtime", "language"])

print(movie_program_df["place"][0])

# Scraping movie ratings
umovie_links = movie_program_df["movie_link"].unique()

ratings_dict = dict()
rating_list = []
title_list = []

options = FirefoxOptions()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)

for i, movie_link in enumerate(umovie_links):
    driver.get(movie_link)
    time.sleep(3)  # have to wait for the advertisement to end

    if i == 1:
        cookie_button = driver.find_element_by_class_name("cc-btn")
        cookie_button.click()

    content2 = BeautifulSoup(driver.page_source, features="html.parser")

    # Title
    try:
        title = content2.find("span", {"itemprop": "itemreviewed"}).get_text()
        title_list.append(title)
    except AttributeError:
        title_list.append("not available")

    # Rating
    try:
        cineman_rating = content2.find("strong", {"class": "color-playstation"}).get_text()
        rating_list.append(cineman_rating)
    except AttributeError:
        rating_list.append("not available")

driver.close()

ratings_dict["movie"] = title_list
ratings_dict["rating"] = rating_list

ratings_df = pd.DataFrame(ratings_dict)
ratings_df.head()

print(ratings_df["rating"][0])
