import pandas as pd
import requests
# import json
# import numpy as np
import os

BASEROW_ACCESS_TOKEN = os.environ.get("BASEROW_ACCESS_TOKEN")


def get_arr_vals(arr):
    return ", ".join([x["value"] for x in arr])


def process_dataset_row(d):
    return {
        "dataset": d["Name"],
        "notes": d["Notes"],
        "dataset_id": d["id"],
        "url": d["URL"],
        "websites": get_arr_vals(d["Websites"]),
        "organization": get_arr_vals(d["Organization"]),
        "agency": get_arr_vals(d["Agency"]),
        "last_modified": d["Last modified"],
        "last_modified_by": d["Last modified by"]["name"]
    }


def process_backup_row(d):
    if d["Metadata Available"]:
        metadata_avl = d["Metadata Available"]["value"]
    else:
        metadata_avl = ""
    return {
        "dataset": d["Dataset"][0]["value"],
        "dataset_id": d["Dataset"][0]["id"],
        "status": d["Status"]["value"],
        "url": d["Dataset URL"][0]["value"],
        "source_website": d["Website"][0]["value"],
        "organization": d["Organization"][0]["value"],
        "agency": d["Agency"][0]["value"],
        "download_date": d["Backup date"],
        "size": d["Backup size"],
        "maintainer": get_arr_vals(d["Maintainer"]),
        "download_location": d["Backup location"],
        "file_type": get_arr_vals(d["File type"]),
        "notes": d["Notes"],
        "metadata_available": metadata_avl,
        "metadata_url": d["Metadata URL"]
    }


backups_table = requests.get(
    (
        "https://baserow.datarescueproject.org/api/database/rows/table/640/"
        "?user_field_names=true"
    ),
    headers={
        "Authorization": f"Token {BASEROW_ACCESS_TOKEN}"
    }
)

rows = []
for row in backups_table.json()['results']:
    rows.append(process_backup_row(row))

backups = pd.DataFrame(rows)

dataset_table = requests.get(
    (
        "https://baserow.datarescueproject.org/api/database/rows/table/639/"
        "?user_field_names=true"
    ),
    headers={
        "Authorization": f"Token {BASEROW_ACCESS_TOKEN}"
    }
)

rows = []
for row in dataset_table.json()['results']:
    rows.append(process_dataset_row(row))

datasets = pd.DataFrame(rows)

datasets.to_csv("baserow_exports/datarescue_datasets.csv", index=False)
backups.to_csv("baserow_exports/datarescue_backups.csv", index=False)
