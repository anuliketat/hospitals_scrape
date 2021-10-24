import os
import pandas as pd
import numpy as np

from subprocess import call

DATA_PATH = os.path.join(os.getcwd(), 'RAW_DATA', 'FINAL_DATA_SCRAPE.csv')

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
    # clean beds/amb
    data = pd.read_csv(DATA_PATH).drop(['Unnamed: 0'], axis=1)
    print(data.columns)
    data['Beds'] = data['beds/amb'].apply(lambda x: split_list(x))\
                .apply(lambda x: np.NaN if type(x)==str else x)
    data['Ambulance'] = data['beds/amb'].apply(lambda x: split_list(x, 'Ambulances'))\
                        .apply(lambda x: np.NaN if type(x)==str else x)
    data = data.drop(['beds/amb'], axis=1)
    # clean fac/specs
    fac_spec_data = data['fac/specs'].apply(pd.Series)[['facilities', 'specialties']]
    data = pd.concat([data, fac_spec_data], axis=1)
    data = data.drop(['fac/specs'], axis=1)

    # save clean data
    OUTPUT_PATH = os.path.join(os.getcwd(), 'FINAL_DATA', 'FINAL_DATA_CLEAN.csv')
    if os.path.exists(OUTPUT_PATH):
        print('File exists in directory.')
    else:
        data.to_csv(OUTPUT_PATH, index=False)



