from datetime import datetime
from elasticsearch import Elasticsearch
import requests
import pytz
import schedule
import time
import pandas as pd
from django.http import HttpResponse

#Elastic configuration

es = Elasticsearch([{'host': 'localhost', 'port':9200, 'scheme':'http'}]) #update host and port as needed

# es = Elasticsearch(
#     "https://localhost:9200",
#     basic_auth=("elastic", "kRDBQ_TVoMYM9cvpULtg"),
#     verify_certs=False
# )

#Timestamp
def get_timestamp():

    timezone_current = pytz.timezone("Asia/Kolkata")
    return datetime.now(timezone_current).strftime("%Y-%m-%d %H:%M:%S")

#Function to clean numbers and handle invalid data
# def clean_number(value):
#     if value in (None,"-", ""):
#         return 0
#     try:
#         return int(value)
#     except (ValueError,TypeError): # "42.6"
#          return 0

# function to fetch and store data for DCIM racks 
#VVIMP 
def fetch():
    #API URL
    API_URL = "http://192.168.1.31:5000/api/asset-data"
    print(API_URL)

    #Fetch data from APIs
    response = requests.get(API_URL, verify= False) # verify=False tells Python not to verify the SSL/TLS certificate
    raw_data = response.json()
    results = raw_data["results"]

    #Dictionary creation
    Asset_data = []
    timestamp = get_timestamp()

    for data in results:
            assetdata_doc = {
              "Application Name": data.get("Application Name"),
              "Application Rating": data.get("Application Rating"),
              "Asset Category": data.get("Asset Category"),
              "Asset Mount": data.get("Asset Mount"),
              "Asset Name": data.get("Asset Name"),
              "Asset Tag MAC": data.get("Asset Tag MAC"),
              "Created By": data.get("Created By"),
              "Defined U Pos.": data.get("Defined U Pos."),
              "Detected Rack": data.get("Detected Rack"),
              "Defined U Pos.": data.get("Defined U Pos."),
              "Enclosure Name": data.get("Enclosure Name"),
              "Host Name": data.get("Host Name"),
              "Installation Date": data.get("Installation Date"),
              "Location": data.get("Location"),
              "Location Code": data.get("Location Code"),
              "Manufacturer": data.get("Manufacturer"),
              "Model Number": data.get("Model Number"),
              "Notes": data.get("Notes"),
              "Owner Name": data.get("Owner Name"),
              "PDU Socket Number": data.get("PDU Socket Number"),
              "Power Source": data.get("Power Source"),
              "Rack": data.get("Rack"),
              "Rated Power": data.get("Rated Power"),
              "SR No.": data.get("SR No."),
              "Second Owner Name": data.get("Second Owner Name"),
              "Serial Number": data.get("Serial Number"),
              "Status": data.get("Status"),
              "Type": data.get("Type"),
              "U Size": data.get("U Size"),
              "Zone": data.get("Zone"),
              "asset_id": data.get("id"),
              "timestamp": timestamp
            }

            asset_id = assetdata_doc["asset_id"]

            #Check if the document already exists in the Elasticsearch
            if es.exists(index="ea_assets", id=asset_id):
                 es.update(index="ea_assets", id= asset_id, body={"doc": assetdata_doc})
                 print(f"Updated the data for Asset id : {asset_id}")
            else:
                 es.index(index="ea_assets", id=asset_id, document=assetdata_doc)
                 print(f"Created new document for Asset id: {asset_id}")

            Asset_data.append(assetdata_doc)


            #Remove Assets in Elasticsearch that are no longer in the API
            es_id = set() #set Created
            results = es.search(index="ea_assets", body={"query":{"match_all":{}}}, size=500)
            for hit in results["hits"]["hits"]:
                 es_id.add(hit["_id"]) 

            ids_to_delete = es_id - set(asset["asset_id"] for asset in Asset_data)

            for delete_id in ids_to_delete:
                 es.delete(index="ea_assets", id=delete_id)
                 print(f"Deleted id: {delete_id}")

            print("data fetched and stored in Elasticsearch")

fetch()


# ------------------------------------------------
# SCHEDULER
# ------------------------------------------------

schedule.every(5).minutes.do(fetch)

print("Scheduler Started. Data will be fetched every 5 minutes")

while True:
    schedule.run_pending()
    time.sleep(1)

    
