import pandas as pd
import json
import xml.etree.ElementTree as ET
import logging
from datetime import datetime
import os

# ---------------------------------------------------------
# Setup logging
# ---------------------------------------------------------
logging.basicConfig(
    filename="log_file.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------
def extract_from_csv(file_path):
    try:
        logging.info(f"Extracting data from CSV file: {file_path}")
        return pd.read_csv(file_path)
    except Exception as e:
        logging.error(f"Error extracting from CSV: {e}")
        return pd.DataFrame()

def extract_from_json(file_path):
    try:
        logging.info(f"Extracting data from JSON file: {file_path}")
        with open(file_path, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except Exception as e:
        logging.error(f"Error extracting from JSON: {e}")
        return pd.DataFrame()

def extract_from_xml(file_path):
    try:
        logging.info(f"Extracting data from XML file: {file_path}")
        tree = ET.parse(file_path)
        root = tree.getroot()
        all_data = []

        for record in root.findall("record"):
            data_dict = {
                "car_model": record.find("car_model").text,
                "year_of_manufacture": record.find("year_of_manufacture").text,
                "price": record.find("price").text,
                "fuel": record.find("fuel").text
            }
            all_data.append(data_dict)

        return pd.DataFrame(all_data)
    except Exception as e:
        logging.error(f"Error extracting from XML: {e}")
        return pd.DataFrame()

# ---------------------------------------------------------
# Transformation function
# ---------------------------------------------------------
def transform_data(df):
    logging.info("Transforming data (rounding 'price' to 2 decimal places)")
    try:
        df["price"] = pd.to_numeric(df["price"], errors="coerce").round(2)
        return df
    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        return df

# ---------------------------------------------------------
# Loading function
# ---------------------------------------------------------
def load_data(df, target_file):
    logging.info(f"Loading transformed data into: {target_file}")
    try:
        df.to_csv(target_file, index=False)
        logging.info("Data successfully loaded.")
    except Exception as e:
        logging.error(f"Error loading data: {e}")

# ---------------------------------------------------------
# ETL process
# ---------------------------------------------------------
def run_etl():
    logging.info("ETL process started")

    # File paths (you can change if needed)
    csv_file = "data.csv"
    json_file = "data.json"
    xml_file = "data.xml"

    # Extract
    df_csv = extract_from_csv(csv_file)
    df_json = extract_from_json(json_file)
    df_xml = extract_from_xml(xml_file)

    # Combine all extracted data
    combined_data = pd.concat([df_csv, df_json, df_xml], ignore_index=True)

    # Transform
    transformed_data = transform_data(combined_data)

    # Load
    load_data(transformed_data, "transformed_data.csv")

    logging.info("ETL process completed successfully")

# ---------------------------------------------------------
# Run ETL and test
# ---------------------------------------------------------
if __name__ == "__main__":
    run_etl()
    print("ETL process finished. Check 'transformed_data.csv' and 'log_file.txt'.")
