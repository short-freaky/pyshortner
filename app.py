from flask import Flask, request, redirect, render_template
from pymongo import MongoClient
import shortuuid
import os

app = Flask(__name__)

# MongoDB Connection
client = MongoClient("mongodb://freakyshortner:73ocJcK55717514JkA5fAD4fKDmpL3VJFxLvf7t0wQnP4WkaT9j0hDNemu2g1Io3hVzG1wixqDXVACDbs6r4OA==@freakyshortner.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&maxIdleTimeMS=120000&appName=@freakyshortner@")
db = client["url_shortener_db"]
collection = db["urls"]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        protocol = request.form.get('protocol')
        original_url = request.form.get('url')
        if not original_url.startswith(('http://', 'https://')):
            original_url = protocol + '://' + original_url

        # Generate short ID
        short_id = shortuuid.ShortUUID().random(length=6)
        
        # Store in MongoDB
        collection.insert_one({
            "_id": short_id,
            "original_url": original_url,
            "clicks": 0
        })

        short_url = request.host_url + short_id
        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<short_id>')
def redirect_url(short_id):
    url_data = collection.find_one({"_id": short_id})
    
    if url_data:
        original_url = url_data['original_url']
        clicks = url_data['clicks']
        
        # Increment click count
        collection.update_one({"_id": short_id}, {"$set": {"clicks": clicks + 1}})
        return redirect(original_url)
    else:
        return "URL not found", 404

if __name__ == '__main__':
    app.run(debug=True)
