from splinter import Browser
from bs4 import BeautifulSoup 
import time
from selenium import webdriver
import pandas as pd

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver.exe"}

    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    
    #set empty dict for mars_headlines
    mars_headlines = {}

    # URL we want to scrape
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    
    # Call visit on browser and pass url
    browser.visit(url)
    
    #1 sec. sleep time
    time.sleep(1)

    # #return all html on page
    html = browser.html
    
    # Create a BeautifulSoup object, pass in our HTML, and call 'html.parser'
    soup = BeautifulSoup(html, "html.parser")
    
    # Build our dictionary for headline, price and neighborhood from our scraped data.
    mars_headlines["news_title"] = soup.find("div", class_="content_title").get_text()
    mars_headlines["paragraph"] = soup.find("div", class_="article_teaser_body").get_text()
    
    browser.quit()
    return mars_headlines