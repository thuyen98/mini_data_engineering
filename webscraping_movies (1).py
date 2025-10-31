

# Modify the code to extract Film, Year, and Rotten Tomatoes' Top 100 headers.

# Restrict the results to only the top 25 entries.

# Filter the output to print only the films released in the 2000s (year 2000 included).


import requests
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup

# ---------------------------------------------------------
# Step 1: Define constants
# ---------------------------------------------------------
url = 'https://web.archive.org/web/20230902185655/https://en.everybodywiki.com/100_Most_Highly-Ranked_Films'
db_name = 'Movies.db'
table_name = 'Top_25'
csv_path = '/home/project/top_25_films.csv'

# Create empty DataFrame with new column names
df = pd.DataFrame(columns=["Film", "Year", "Rotten Tomatoes' Top 100"])

# ---------------------------------------------------------
# Step 2: Scrape HTML data
# ---------------------------------------------------------
html_page = requests.get(url).text
soup = BeautifulSoup(html_page, 'html.parser')

# The first <tbody> contains the table we want
table_body = soup.find_all('tbody')[0]
rows = table_body.find_all('tr')

# ---------------------------------------------------------
# Step 3: Extract top 25 rows only
# ---------------------------------------------------------
for i, row in enumerate(rows):
    if i < 25:  # limit to top 25
        cols = row.find_all('td')
        if len(cols) >= 3:
            data_dict = {
                "Rotten Tomatoes' Top 100": cols[0].text.strip(),
                "Film": cols[1].text.strip(),
                "Year": cols[2].text.strip()
            }
            df = pd.concat([df, pd.DataFrame([data_dict])], ignore_index=True)
    else:
        break

# ---------------------------------------------------------
# Step 4: Filter films released in the 2000s (2000–2009)
# ---------------------------------------------------------
# Convert the 'Year' column to numeric (ignore errors)
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

# Keep only rows where Year is between 2000 and 2009
df_2000s = df[(df["Year"] >= 2000) & (df["Year"] <= 2009)]

# ---------------------------------------------------------
# Step 5: Print the filtered result
# ---------------------------------------------------------
print("🎬 Top Films from the 2000s (2000–2009):")
print(df_2000s)

# ---------------------------------------------------------
# Step 6: Save to CSV and SQLite database
# ---------------------------------------------------------
df_2000s.to_csv(csv_path, index=False)

conn = sqlite3.connect(db_name)
df_2000s.to_sql(table_name, conn, if_exists='replace', index=False)
conn.close()
