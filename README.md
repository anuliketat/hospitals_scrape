# Hospitals Data Scraping
Hospitals in India.

## Getting started
These instructions will get you a copy of the project up and running on your local machine.

### Folder Structure
```
├── FINAL_DATA                                      # Final cleaned data csv file
│   └── FINAL_DATA_CLEAN.csv                        
├── RAW_DATA                                        # sourced structured raw data
│   └── FINAL_DATA_SCRAPE.csv
│   └── hospital_database_2.xlsx
├── Report                                          # report
│   └── SWEETVIZ_REPORT.html                        
│── methods_scrape.py                               # functions & methods for scraping    
│── scraper.py                                      # script that runs the scrape    
│── clean_data.py                                   # script for cleaning and processing
│── requirements.txt                                # required packages
└── run.py                                          # Main script that runs everything sequentially to get final data
```


### Prerequisites
Requires `python 3.x.x`.

### Installation
First create a python virtual environment using [anaconda/miniconda](https://conda.io/docs/user-guide/tasks/manage-environments.html) or [virtualenv](https://virtualenv.pypa.io/en/latest/)
Install the required packages from `requirements.txt` by running `pip install -r requirements.txt`
Make sure the Chrome driver and Chrome browser are to the latest version. 

### Running
Clone the repository. Activate the virtual environment you created and then execute `python run.py`

## Acknowledgements
README inspired from https://gist.github.com/PurpleBooth/109311bb0361f32d87a2
