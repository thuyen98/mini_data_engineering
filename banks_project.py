# Code for ETL operations on Bank Market Cap data
# Importing the required libraries

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

# Known values
url = 'https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks'
table_attribs = ["Name", "MC_USD_Billion"]
exchange_rate_csv_path = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-PY0221EN-Coursera/labs/v2/exchange_rate.csv'
output_csv_path = './Largest_banks_data.csv'
db_name = 'Banks.db'
table_name = 'Largest_banks'

def log_progress(message):
    ''' This function logs the mentioned message of a given stage of the
    code execution to a log file. Function returns nothing'''

    timestamp_format = '%Y-%m-%d %H:%M:%S'  # Year-Month-Day Hour:Minute:Second
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)

    with open('code_log.txt', 'a') as f:
        f.write(timestamp + ' : ' + message + '\n')

# Make first log entry
log_progress('Preliminaries complete. Initiating ETL process')

def extract(url, table_attribs):
    ''' 
    This function extracts the required information from the Wikipedia page 
    and saves it to a dataframe. The function returns the dataframe.
    '''
    page = requests.get(url).text
    data = BeautifulSoup(page, 'html.parser')

    # Create empty dataframe
    df = pd.DataFrame(columns=table_attribs)

    # Find all tables on the page
    tables = data.find_all('tbody')

    # Select the correct table (By market capitalization)
    rows = tables[0].find_all('tr')

    # Loop through table rows
    for row in rows:
        cols = row.find_all('td')
        if len(cols) != 0:
            name = cols[1].text.strip()  # Bank Name
            mc_usd = cols[2].text.strip()  # Market Cap (US$ billion)
            
            # Clean and convert market cap value
            mc_usd = float(mc_usd.replace('\n', '').replace(',', ''))

            # Append to dataframe
            data_dict = {"Name": name, "MC_USD_Billion": mc_usd}
            df1 = pd.DataFrame(data_dict, index=[0])
            df = pd.concat([df, df1], ignore_index=True)

    return df

df = extract(url, table_attribs)
print(df)
log_progress('Data extraction complete. Initiating Transformation process')


def transform(df, csv_path):
    ''' 
    This function accesses the CSV file for exchange rate
    information, and adds three columns to the data frame,
    each containing the transformed version of Market Cap
    column to respective currencies
    '''
    # Read the exchange rate CSV file
    exchange_rate = pd.read_csv(csv_path)
    
    # Convert to dictionary {Currency: Rate}
    exchange_rate = exchange_rate.set_index('Currency').to_dict()['Rate']

    # Create new columns for GBP, EUR, INR
    df['MC_GBP_Billion'] = [np.round(x * exchange_rate['GBP'], 2) for x in df['MC_USD_Billion']]
    df['MC_EUR_Billion'] = [np.round(x * exchange_rate['EUR'], 2) for x in df['MC_USD_Billion']]
    df['MC_INR_Billion'] = [np.round(x * exchange_rate['INR'], 2) for x in df['MC_USD_Billion']]

    return df

# df = extract(url, table_attribs)
# print(df)

df = transform(df, exchange_rate_csv_path)
print(df)
log_progress('Data transformation complete. Initiating Loading process')

def load_to_csv(df, output_path):
    '''
    This function saves the final data frame as a CSV file in
    the provided path. Function returns nothing.
    '''
    df.to_csv(output_path, index=False)

load_to_csv(df, output_csv_path)
log_progress('Data saved to CSV file')

def load_to_db(df, sql_connection, table_name):
    '''
    This function saves the final data frame to a database
    table with the provided name. Function returns nothing.
    '''
    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)

# Initiate SQLite3 connection
sql_connection = sqlite3.connect('Banks.db')
log_progress('SQL Connection initiated')

load_to_db(df, sql_connection, table_name)
log_progress('Data loaded to Database as a table, Executing queries')


def run_query(query_statement, sql_connection):
    '''
    This function runs the query on the database table and
    prints the output on the terminal. Function returns nothing.
    '''
    print(f"\nExecuting query: {query_statement}")
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)
# Run Queries
run_query("SELECT * FROM Largest_banks", sql_connection)
run_query("SELECT AVG(MC_GBP_Billion) FROM Largest_banks", sql_connection)
run_query("SELECT Name FROM Largest_banks LIMIT 5", sql_connection)

log_progress('Process Complete')
