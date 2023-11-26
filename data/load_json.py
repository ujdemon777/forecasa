import json

# file_path = "/Users/shtlpmac042/Desktop/forecasa/data/loads.json"



def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

company_data = load_data_from_json("/Users/shtlpmac042/Desktop/forecasa/data/leads.json")
txn_data = load_data_from_json("/Users/shtlpmac042/Desktop/forecasa/data/txn.json")