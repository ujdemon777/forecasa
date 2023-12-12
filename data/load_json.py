import json
import os

cur_dir = os.getcwd()
company_file_path = os.path.join(cur_dir , "data/leads.json")
txn_file_path = os.path.join(cur_dir , "data/txn.json")
lead_file_path = os.path.join(cur_dir,"data/lead.json")


def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


company_data = load_data_from_json(company_file_path)
txn_data = load_data_from_json(txn_file_path)
lead_data = load_data_from_json(lead_file_path)