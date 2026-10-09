from datetime import datetime
from elasticsearch import Elasticsearch
import requests
import pytz
import schedule
import time

# Elasticsearch configuration (connection setup)
es = Elasticsearch([{'host': 'localhost', 'port':9200, 'scheme':'http'}]) #update host and port as needed
# es = Elasticsearch("http://localhost:9200")

# es = Elasticsearch(
#     "http://localhost:9200",
#     basic_auth=("elastic", "kRDBQ_TVoMYM9cvpULtg"),
#     verify_certs=False
# )

# print("Connected:", es.ping())

# print(es.info())

# print("Elasticsearch connected:", es.ping())
# es = Elasticsearch(
#     "http://localhost:9200",
#     request_timeout=30
# )

#Function to clean numbers and handle invalid data
# def clean_number(value):
#     if value in (None,"-", ""):
#         return 0
#     try:
#         return int(value)
#     except (ValueError,TypeError): # "42.6"
#          return 0

# Function to get the current timestamp in Asia/Kolkata timezone
def get_timestamp():

    timezone_current = pytz.timezone("Asia/Kolkata")
    return datetime.now(timezone_current).strftime("%Y-%m-%d %H:%M:%S")
    
# function to fetch and store data for DCIM racks 
#VVIMP 
def fetch():

    #API URL
    API_URL = "http://192.168.1.31:5000/api/rack-data"
    print(API_URL)

    #Fetch data from APIs
    response = requests.get(API_URL, verify= False) # verify=False tells Python not to verify the SSL/TLS certificate
    raw_data = response.json()
    results = raw_data["results"]
    
    # print("TYPE:", type(raw_data))

    #Dictionary creation
    Rack_data = []
    timestamp = get_timestamp()
    
    for data in results:
        rackdata_doc = {
          "Address ID": data.get("Address ID"),
          "Consumed U": data.get("Consumed U"),
          "Created By": data.get("Created By"),
          "Free U": data.get("Free U"),
          "Gateway ID": data.get("Gateway ID"),
          "IP Address": data.get("IP Address"),
          "Location": data.get("Location"),
          "Module ID": data.get("Module ID"),
          "Rack Make": data.get("Rack Make"),
          "Rack Name": data.get("Rack Name"),
          "Rack Type": data.get("Rack Type"),
          "Rack U Size": data.get("Rack U Size"),
          "Row": data.get("Row"),
          "SR No.": data.get("SR No."),
          "rack_id": data.get("id"),
          "timestamp": timestamp
        }

        rack_id = rackdata_doc["rack_id"]

        # print("changed dict:::::::::",rackdata_doc)


        # check if the document already exists in the Elasticsearch 
        if es.exists(index="ea-racks", id=rack_id):
            es.update(index="ea-racks", id=rack_id, body={"doc":rackdata_doc})
            print(f"Updated the data for rack_id: {rack_id}")
        else:
            es.index(index="ea-racks", id=rack_id, document=rackdata_doc)
            print(f"Created new document for rack_id: {rack_id}")

        # es.index(
        #     index="ea-racks",
        #     document=rackdata_doc
        # )

        Rack_data.append(rackdata_doc)


        #Cleanup: Remove any racks in Elasticsearch that are no longer in the API
        # es_id = set() #created set
        # result = es.search(index="ea-racks", body={"query":{"match_all":{}}}, size=200) #searched for every doc inside ea-racks index and stored in result
        # for hit in result["hits"]["hits"] : #got ["hits"]["hits"] logic from index/_search ----query
        #     es_id.add(hit["_id"]) #appended every unique _id in es_id set

        # ids_to_delete = es_id - set(rack["rack_id"] for rack in Rack_data) #got extra racks inside elastic

        # for delete_id in ids_to_delete:
        #     es.delete(index="ea-racks", id=delete_id) #deleted extra racks
        #     print(f"deleted id: {delete_id}")

        # print('data fetched and stored in ElasticSearch')

fetch()


# ------------------------------------------------
# SCHEDULER
# ------------------------------------------------

schedule.every(5).minutes.do(fetch)

print("Scheduler Started. Data will be fetched every 5 minutes")

while True:
    schedule.run_pending()
    time.sleep(1)






   
