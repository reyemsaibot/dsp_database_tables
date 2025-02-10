import argparse
import requests
import json
import pandas as pd
import utils


# Constants
excel_file = 'database_tables.xlsx'

def get_database_tables():
    header = utils.initializeGetOAuthSession(token_file, secrets_file)
    database_tables = []

    url = utils.get_url(dsp_host, 'list_of_spaces')
    response = requests.get(url,headers=header)
    space_list = response.json()

    for spaceID in space_list:
        url = utils.get_url(dsp_host, 'space_tables').format(**{"spaceID": spaceID})
        response = requests.get(url, headers=header)
        space_json = response.json()
        try:
            for table in space_json[spaceID]['tables']:
                tableName = table['tableName']
                usedDisk = round((table['usedDisk'] / 1000 / 1000),2) # MB
                usedMemory = round(table['usedMemory'] / 1000 / 1000,2)
                records = table['recordCount']
                database_tables.append((spaceID, tableName, usedDisk, usedMemory, records))
        except KeyError:
            continue



    df = pd.DataFrame(database_tables, columns=['Space', 'Table Name', 'Used Disk', 'Used Memory', 'Records'])
    df.to_excel(excel_file, sheet_name='Sheet1', index=False)

    # Format Excel
    utils.format_excel(excel_file)
    # Format the columns with the correct extensions
    utils.set_number_format(excel_file, "C", '#,##0.00 "MB"')
    utils.set_number_format(excel_file, "D", '#,##0.00 "MB"')
    utils.set_number_format(excel_file, "E", "#,##0")
    utils.sort_table(excel_file, "C")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get an overview of all tables over all spaces")
    parser.add_argument("-f", "--file", required=True, help="Path of parameter file")
    args = parser.parse_args()

    with open(args.file, 'r') as f:
        config = json.load(f)

    secrets_file = config["SETTINGS"]["secrets_file"]
    token_file = config["SETTINGS"]["token_file"]
    dsp_host = config["DATASPHERE"]["dsp_host"]

    # Now roll the dice and go to work
    print("Started...")
    get_database_tables()
    print("Ended")


