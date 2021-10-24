import pandas as pd
import os

from methods_scrape import *

cities = ['Hyderabad', 'Bangalore', 'Chennai', 'Mumbai', 'Delhi', 'Kolkata',
         'Ahmedabad', 'Pune', 'Nagpur', 'Indore', 'Visakhapatnam', 'Kanpur',
          'Jaipur', 'Lucknow']

URL = 'https://www.practo.com/search?results_type=hospital&q=%5B%7B%22word%22%3A%22hospital%22%2C%22autocompleted%22%3Atrue%2C%22category%22%3A%22type%22%7D%5D&city='

df_list = []
for CITY in cities:
    file = get_page_source(URL, CITY)
    hosp = scrape_list(file, CITY)
    data = scrape_info(hosp)
    final_data = scrape_services(data)
    print('\033[1m'+f'DONE {CITY}!'+'\033[0m')
    print(f'Total records for {CITY}:', final_data.shape[0])
    df_list.append(final_data)

FINAL_DATA = pd.concat(df_list, axis=0)
print(f'Total Records:{FINAL_DATA.shape[0]}, Total Attributes:{FINAL_DATA.shape[1]}')

# Save data as CSV
if not os.path.exists('RAW_DATA'):
    os.makedirs('RAW_DATA')
OUTPUT_PATH = os.path.join(os.getcwd(), 'RAW_DATA', 'FINAL_DATA_SCRAPE.csv')
if os.path.exists(OUTPUT_PATH):
    print('File exists in directory.')
else:
    FINAL_DATA.to_csv(OUTPUT_PATH, index=False)