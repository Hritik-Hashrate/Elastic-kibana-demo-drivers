from datetime import datetime
from elasticsearch import Elasticsearch
import requests
import pytz
import schedule
import time
from django.http import HttpResponse
from elasticsearch import Elasticsearch

# Elasticsearch configuration (connection setup)
es = Elasticsearch([{'host': 'localhost', 'port':9200, 'scheme':'http'}])

def get_timestamp():
    timezone_current = pytz.timezone("Asia/Kolkata")
    current_time = datetime.now(timezone_current)
    return int(current_time.timestamp() * 1000)

# function to fetch and store data for DCIM racks 
#VVIMP 
def fetch():

    #API URL
    API_URL = "http://192.168.1.31:5000/api/ea-metrics-data"
    print(API_URL)

    #Fetch data from APIs
    response = requests.get(API_URL, verify= False) # verify=False tells Python not to verify the SSL/TLS certificate
    raw_data = response.json()
    results = raw_data["results"]    
    # print("TYPE:", type(raw_data))

    #Dictionary creation
    Metrics_data = []
    timestamp = get_timestamp()

    for data in results:
            metricsdata_doc = {
              "feed_a_kw": data.get("feed_a_kw"),
              "feed_b_kw": data.get("feed_b_kw"),
              "humidity": data.get("humidity"),
            #   "id": data.get("id"),
              "kw_capacity_percent": data.get("kw_capacity_percent"),
              "location": data.get("location"),
              "max_cont_free_u_front": data.get("max_cont_free_u_front"),
              "name": data.get("name"),
              "rack_id": data.get("rack_id"),
              "rack_units_free_front": data.get("rack_units_free_front"),
              "rack_units_front": data.get("rack_units_front"),
              "status": data.get("status"),
              "temp_bottom": data.get("temp_bottom"),
              "temp_middle": data.get("temp_middle"),
              "temp_top": data.get("temp_top"),
              "total_kva": data.get("total_kva"),
              "total_kw": data.get("total_kw"),
              "current_timestamp": timestamp,
              "timestamp": data.get("timestamp")
            }


            rack_id = f"{metricsdata_doc['rack_id']}_{metricsdata_doc['current_timestamp']}"

            # check if the document already exists in the Elasticsearch 
            # if es.exists(index="ea-metrics", id=rack_id):
            #     es.update(index="ea-metrics", id=rack_id, body={"doc":metricsdata_doc})
            #     print(f"Updated the data for rack_id: {rack_id}")
            # else:
            #         es.index(index="ea-metrics", id=rack_id, document=metricsdata_doc)
            #         print(f"Created new document for rack_id: {rack_id}")

            es.index(index="ea-metrics",document=metricsdata_doc)   

            Metrics_data.append(metricsdata_doc)

fetch()

# ------------------------------------------------
# SCHEDULER
# ------------------------------------------------

schedule.every(5).minutes.do(fetch)

print("Scheduler Started. Data will be fetched every 5 minutes")

while True:
    schedule.run_pending()
    time.sleep(1)
