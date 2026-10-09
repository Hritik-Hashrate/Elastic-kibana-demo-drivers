from datetime import datetime
from elasticsearch import Elasticsearch
import requests
import pytz


# =========================================================
# ELASTICSEARCH CONNECTION
# =========================================================

es = Elasticsearch([
    {
        "host": "localhost",
        "port": 9200,
        "scheme": "http"
    }
])


# =========================================================
# FUNCTION TO GET CURRENT TIMESTAMP
# =========================================================

def get_timestamp():

    timezone_current = pytz.timezone("Asia/Kolkata")

    return datetime.now(timezone_current).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# =========================================================
# FUNCTION TO FETCH AND STORE DATA
# =========================================================

def fetch():

    # -----------------------------------------------------
    # API URL
    # -----------------------------------------------------

    API_URL = "http://192.168.1.31:5000/api/rack-data"

    print("API URL:", API_URL)


    # -----------------------------------------------------
    # FETCH DATA FROM API
    # -----------------------------------------------------

    response = requests.get(
        API_URL,
        verify=False
    )

    # Check whether API request was successful
    response.raise_for_status()


    # -----------------------------------------------------
    # CONVERT API RESPONSE TO PYTHON OBJECT
    # -----------------------------------------------------

    raw_data = response.json()

    print("TYPE:", type(raw_data))


    # -----------------------------------------------------
    # GET RESULTS LIST
    # -----------------------------------------------------

    results = raw_data["results"]

    print("NUMBER OF RACKS:", len(results))


    # -----------------------------------------------------
    # PRINT DATA
    # -----------------------------------------------------

    print("DATA:", results)


    # -----------------------------------------------------
    # LIST TO STORE RACK DATA
    # -----------------------------------------------------

    Rack_data = []


    # -----------------------------------------------------
    # GET CURRENT TIMESTAMP
    # -----------------------------------------------------

    timestamp = get_timestamp()


    # =====================================================
    # LOOP THROUGH EACH RACK
    # =====================================================

    for data in results:

        # -------------------------------------------------
        # CREATE RACK DOCUMENT
        # -------------------------------------------------

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

            "id": data.get("id"),

            "timestamp": timestamp
        }


        # -------------------------------------------------
        # GET RACK ID
        # -------------------------------------------------

        rack_id = rackdata_doc["id"]


        # =================================================
        # CHECK WHETHER RACK ALREADY EXISTS
        # =================================================

        if es.exists(
            index="ea-racks",
            id=rack_id
        ):

            # -------------------------------------------------
            # UPDATE EXISTING DOCUMENT
            # -------------------------------------------------

            es.update(
                index="ea-racks",
                id=rack_id,
                doc=rackdata_doc
            )

            print(
                f"Updated the data for rack_id: {rack_id}"
            )


        else:

            # -------------------------------------------------
            # CREATE NEW DOCUMENT
            # -------------------------------------------------

            es.index(
                index="ea-racks",
                id=rack_id,
                document=rackdata_doc
            )

            print(
                f"Created new document for rack_id: {rack_id}"
            )


        # -------------------------------------------------
        # ADD DATA TO LIST
        # -------------------------------------------------

        Rack_data.append(rackdata_doc)


    # =====================================================
    # RETURN DATA
    # =====================================================

    return Rack_data


# =========================================================
# RUN FUNCTION
# =========================================================

fettch = fetch()

print("TOTAL DATA STORED:", len(fettch))