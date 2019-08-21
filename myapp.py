from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_nasa

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/nasa_app"
mongo = PyMongo(app)

@app.route('/')
def index():
    # find one document from our mongo db and return it.
    mars_headlines = mongo.db.listings.find_one()
    # pass that listing to render_template
    return render_template("index.html", mars_headlines=mars_headlines)

@app.route("/scrape")
def scraper():
    # create a listings database
    mars_headlines = mongo.db.mars_headlines
    # call the scrape function in our scrape_craigslist file. This will scrape and save to mongo.
    mars_headline_data = scrape_nasa.scrape()
    # update our listings with the data that is being scraped.
    mars_headlines.update({}, mars_headline_data, upsert=True)
    # return a message to our page so we know iscrapet was successful.
    return redirect("/", code=302)

if __name__ == "main":
    app.run(debug=True)