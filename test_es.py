from elasticsearch import Elasticsearch

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "kRDBQ_TVoMYM9cvpULtg"),
    verify_certs=False
)

print("Connected:", es.ping())

print(es.info())
