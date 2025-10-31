import glob
import pandas as pd
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# ---------------------------------------------------------
# Global variables
# ---------------------------------------------------------
log_file = "log_file.txt"
target_file = "transformed_data.csv"

# ---------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------
def extract_from_csv(file_to_process):
    dataframe = pd.read_csv(file_to_process)
    return dataframe

def extract_from_json(file_to_process):
    dataframe = pd.read_json(file_to_process, lines=True)
    return dataframe

def extract_from_xml(file_to_process):
    dataframe = pd.DataFrame(columns=["car_model", "year_of_manufacture", "price", "fuel"])
    tree = ET.parse(file_to_process)
    root = tree.getroot()

    for car in root:
        car_model = car.find("car_model").text
        year_of_manufacture = car.find("year_of_manufacture").text
        price = float(car.find("price").text)
        fuel = car.find("fuel").text

        row = {
            "car_model": car_model,
            "year_of_manufacture": year_of_manufacture,
            "price": price,
            "fuel": fuel
        }
        dataframe = pd.concat([dataframe, pd.DataFrame([row])], ignore_index=True)

    return dataframe

# ---------------------------------------------------------
# Combined extract function
# ---------------------------------------------------------
def extract():
    extracted_data = pd.DataFrame(columns=["car_model", "year_of_manufacture", "price", "fuel"])

    # Process all CSV files
    for csvfile in glob.glob("*.csv"):
        if csvfile != target_file:
            extracted_data = pd.concat([extracted_data, extract_from_csv(csvfile)], ignore_index=True)

    # Process all JSON files
    for jsonfile in glob.glob("*.json"):
        extracted_data = pd.concat([extracted_data, extract_from_json(jsonfile)], ignore_index=True)

    # Process all XML files
    for xmlfile in glob.glob("*.xml"):
        extracted_data = pd.concat([extracted_data, extract_from_xml(xmlfile)], ignore_index=True)

    return extracted_data

# ---------------------------------------------------------
# Transform function
# ---------------------------------------------------------
def transform(data):
    '''Round prices to two decimal places'''
    data["price"] = pd.to_numeric(data["price"], errors="coerce").round(2)
    return data

# ---------------------------------------------------------
# Load function
# ---------------------------------------------------------
def load_data(target_file, transformed_data):
    transformed_data.to_csv(target_file, index=False)

# ---------------------------------------------------------
# Logging function
# ---------------------------------------------------------
def log_progress(message):
    timestamp_format = '%Y-%m-%d %H:%M:%S'  # corrected format
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(log_file, "a") as f:
        f.write(f"{timestamp}, {message}\n")

# ---------------------------------------------------------
# ETL process
# ---------------------------------------------------------
log_progress("ETL Job Started")

# Extraction
log_progress("Extract phase Started")
extracted_data = extract()
log_progress("Extract phase Ended")

# Transformation
log_progress("Transform phase Started")
transformed_data = transform(extracted_data)
print("Transformed Data:")
print(transformed_data)
log_progress("Transform phase Ended")

# Loading
log_progress("Load phase Started")
load_data(target_file, transformed_data)
log_progress("Load phase Ended")

# Completion
log_progress("ETL Job Ended")
