from flask import Flask, render_template, jsonify
from flask_pymongo import PyMongo
from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import pymongo
import pandas as pd

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)


@app.route("/")
def index():
    mars = mongo.db.mars.find_one()
    return render_template("index.html", mars=mars)


@app.route("/scrape")
def scrape():
    mars = mongo.db.mars

    # empty dictionary to hold all data
    payload = {}

    url = 'https://mars.nasa.gov/news'
    ex_path = {'executable_path': 'chromedriver.exe'}
    
    browser = Browser('chrome', **ex_path, headless=False)

    # URL of page 
    url = 'https://mars.nasa.gov/news'

    # ### Latest Mars News
    # Go to link in browser mode
    browser.visit(url)

    # Grab the html code
    url_html = browser.html

    # Parse 
    url_scraper = bs(url_html, 'html.parser')

    # title
    title_element = url_scraper.find('div', {'class': 'content_title'}).findChild()

    title_text = title_element.get_text()
    payload['title_text'] = title_text

    # Paragraph
    body_element = url_scraper.find('div', {'class': 'article_teaser_body'})

    body_text = body_element.get_text()
    payload['body_text'] = body_text
    
    # ### Mars Images
    #  html of that particular page
    images_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    browser.visit(images_url)

    # Capture the new html from the new page
    image_html = browser.html
    # Create and feed a new scraper the new html
    image_scraper = bs(image_html, 'html.parser')

    # Go to next image page by clicking on the "full image" button
    full_image_btn_element = image_scraper.find('a', {'class': 'button fancybox'})

    # Click the 'full image' button
    browser.click_link_by_id('full_image')

    # Click the 'more info' button
    browser.is_element_present_by_text('more info', wait_time=1)
    browser.click_link_by_partial_text('more info')

    # Scrape the image from the img element
    jpl_image_html = browser.html

    jpl_image_scraper = bs(jpl_image_html, 'html.parser')

    jpl_image = jpl_image_scraper.find('img', {'class': 'main_image'})

    jpl_image_url = 'https://www.jpl.nasa.gov' + jpl_image.get('src')
    payload['jpl_image_url'] = jpl_image_url

    # #### Mars Weather
    tweet_url = "https://twitter.com/marswxreport?lang=en"
    #browser.visit(url)
    browser.visit(tweet_url)
    html_twitter = browser.html
    twitter_soup = bs(html_twitter, 'html.parser')
    tweet_container = twitter_soup.find('div', class_="js-tweet-text-container")
    mars_text = tweet_container.get_text()
    weather = mars_text[1:76]
    payload['weather'] = weather

    ##pandas
    read = pd.read_html("http://space-facts.com/mars/")
    df = read[0]
    df = read[0]
    html_table = df.to_html()
    html_table = html_table.replace('\n', '')
    payload['html_table'] = html_table
    
    # Scrape 4 different hemisphere images 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    


    m_urls = [
        'https://astrogeology.usgs.gov/search/map/Mars/Viking/cerberus_enhanced',
        'https://astrogeology.usgs.gov/search/map/Mars/Viking/schiaparelli_enhanced',
        'https://astrogeology.usgs.gov/search/map/Mars/Viking/syrtis_major_enhanced',
        'https://astrogeology.usgs.gov/search/map/Mars/Viking/valles_marineris_enhanced'
    ]
        
    hs_image_data = []    

    # for loop through m_urls 
    for url in m_urls:
        print(url)
        # DO ALL SCRAPING LOGIC HERE
        # create empty dictionary
        album = {}
        
        # click link
        browser.visit(url)
        
        # scrape the title and image url
        # Scrape the image 
        m_html = browser.html

        m_scraper = bs(m_html, 'html.parser')

        m_title = m_scraper.find('h2', {'class': 'title'}).get_text()
        
        # add title to album
        album['title'] = m_title
        
        # repeat scraping 
        m_image_href = m_scraper.find('div', {'class': 'downloads'}).find('a').get('href')
        album['link'] = m_image_href
        
        # add album to the list
        hs_image_data.append(album)
        
        # go back a page in the browser
        browser.back()

    payload['hemisphere_data'] = hs_image_data

    # Add all scraped data to the mongo db

    mars.update({}, payload, upsert=True)
    return jsonify(payload)
    

    



if __name__ == "__main__":
    app.run(debug=True)
