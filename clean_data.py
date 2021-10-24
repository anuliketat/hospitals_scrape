import os
import pandas as pd
import numpy as np

from subprocess import call

DATA_PATH = os.path.join(os.getcwd(), 'RAW_DATA', 'FINAL_DATA_SCRAPE.csv')
secondary_data = os.path.join(os.getcwd(), 'RAW_DATA', 'hospital_database_2.xlsx')

def split_list(x, _str='Beds'):
    if isinstance(x, str):
        lis = eval(x)
        for i in lis:
            split = i.split(' - ')
            if _str in split:
                x = int(split[-1])
            else:
                x = None
        return x
    return x

if not os.path.exists(DATA_PATH):
    print('File Not Found')
    user_input = str(input('Do you want to run the scraper.py:'+' (y/n): ')).lower().strip()
    call(["python", "scraper.py"]) if user_input=='y' else print('Cool!')
else:
    data = pd.read_csv(DATA_PATH).drop(['Unnamed: 0'], axis=1)
    # Get State from city
    conditions = [
                (data['city'] == 'Ahmedabad'),
                (data['city'] == 'Chennai'),
                (data['city'] == 'Delhi'),
                (data['city'] == 'Indore'),
                (data['city'] == 'Jaipur'),
                (data['city'] == 'Kanpur'),
                (data['city'] == 'Kolkata'),
                (data['city'] == 'Lucknow'),
                (data['city'] == 'Mumbai'),
                (data['city'] == 'Nagpur'),
                (data['city'] == 'Bangalore'),
                (data['city'] == 'Pune'),
                (data['city'] == 'Hyderabad'),]
    choices = ['Gujarat', 'Tamil Nadu', 'Delhi', 'Madhya Pradesh', 'Rajasthan', 'Uttar Pradesh',
                'West Bengal', 'Uttar Pradesh', 'Maharashtra', 'Maharashtra', 'Karnataka',
                'Maharashtra', 'Telangana']
    data['State'] = np.select(conditions, choices)

    # Get other attributes
    data["key"] = data["name"] + "-" + data["State"]
    df_2 = pd.read_excel(secondary_data).drop(['Sr_No'], axis=1)
    df_2["key2"] = df_2["Hospital_Name"] + "-" + df_2["State"]
    df_hosp_final = pd.merge(data, df_2, left_on='key', right_on = 'key2', how='left')
    df_hosp_final = df_hosp_final[['name', 'url', 'loc', 'city', 'State_x', 'Pincode', 'rating',
                                    'address', 'doctors','type', 'beds/amb', 'fac/specs',
                                    'services','Location_Coordinates','State_ID', 'District_ID']]

    df_hosp_final['Pincode'] = df_hosp_final['Pincode'].astype(str)
    df_hosp_final['Pincode'] = df_hosp_final['Pincode'].str.replace(r'ÿ', '')
    df_hosp_final['Location_Coordinates'] = df_hosp_final['Location_Coordinates'].astype(str)
    df_hosp_final[['Latitude', 'Longitude']] = df_hosp_final['Location_Coordinates'].str.split(',', expand=True)
    df_hosp_final['Latitude'] = df_hosp_final['Latitude'].str.replace(r'[', '')
    df_hosp_final['Longitude'] = df_hosp_final['Longitude'].str.replace(r']', '')

    # clean beds/amb
    df_hosp_final['Beds'] = df_hosp_final['beds/amb'].apply(lambda x: split_list(x))\
                .apply(lambda x: np.NaN if type(x)==str else x)
    df_hosp_final['Ambulance'] = df_hosp_final['beds/amb'].apply(lambda x: split_list(x, 'Ambulances'))\
                        .apply(lambda x: np.NaN if type(x)==str else x)
    df_hosp_final = df_hosp_final.drop(['beds/amb'], axis=1)
    # clean fac/specs
    df_hosp_final['fac/specs'] = df_hosp_final['fac/specs'].apply(lambda x: eval(x) if type(x)==str else x)
    fac_spec_data = df_hosp_final['fac/specs'].apply(pd.Series)[['facilities', 'specialties']]
    df_hosp_final = pd.concat([df_hosp_final, fac_spec_data], axis=1)
    df_hosp_final = df_hosp_final.drop(['fac/specs'], axis=1)

    # save clean data
    OUTPUT_PATH = os.path.join(os.getcwd(), 'FINAL_DATA', 'FINAL_DATA_CLEAN.csv')
    if os.path.exists(OUTPUT_PATH):
        print('File exists in directory.')
    else:
        df_hosp_final.to_csv(OUTPUT_PATH, index=False)
        print(f'File saved in {OUTPUT_PATH}')



