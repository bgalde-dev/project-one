# Import Dependencies
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings

warnings.filterwarnings('ignore')

loaded = False
crime_data_csv = "../data/crime/2012_2016_CrimeRate.csv"
homeless_data_csv = "../data/crime/2007-2016-Homelessness-USA.csv"
raw_crime_data_df = pd.DataFrame()
raw_homeless_data_df = pd.DataFrame()
clean_crime_data_df = pd.DataFrame()

# Loads the crime and homeless data files to raw dataframes
def load_data_files():
    global raw_crime_data_df
    global raw_homeless_data_df
    global loaded
    if not loaded:
        raw_crime_data_df = pd.read_csv(crime_data_csv)
        raw_homeless_data_df = pd.read_csv(homeless_data_csv)
        print(f'LOADING DATA FILES {crime_data_csv} and {homeless_data_csv}')
        loaded = True
    else:
        print(f'DATA FILES ALREADY LOADED ... To reload data use reload_data()')

# Reloads the data files if data changes
def reload_data():
    global loaded
    loaded = False
    load_data_files()

# Cleans the data. Renames to columns to be better understood, replaces main
# crimes with more reader friendly desciptions.
def clean_data():
    global clean_crime_data_df
    load_data_files()
    # Renaming most columns so they are better understood.
    renamed_crime_df = raw_crime_data_df.rename(columns={"Date.Rptd":"Date Reported",
                                                 "DR.NO":"Case Number",
                                                 "DATE.OCC":"Date Occurred",
                                                 "TIME.OCC":"Time Occurred",
                                                 "AREA": "Area",
                                                 "AREA.NAME":"Area Name",
                                                 "Crm.Cd":"Crime Code",
                                                 "CrmCd.Desc":"Crime Description",
                                                 "Status.Desc":"Status Description"})

    # Replacing the all capital crime description with less captials for the four crime types being investigated.
    data_replace = renamed_crime_df.replace({'ASSAULT WITH DEADLY WEAPON':'ADW',
                                         'BATTERY':'Battery',
                                         'THEFT':'Theft',
                                         'VANDALISM':'Vandalism'})

    # Grabbing only the data with the four crime types being investigated.
    clean_crime_data_df = data_replace.loc[((data_replace['Crime Description'] == 'ADW') |
                             (data_replace['Crime Description'] == 'Battery') |
                             (data_replace['Crime Description'] == 'Theft') |
                             (data_replace['Crime Description'] == 'Vandalism'))]

    # Looping through the Date Occurred splitting the date into its three components and grabbing the year to
    # put into a list to make a new column for grouping.
    year_occurred = []

    for crime in clean_crime_data_df['Date Occurred']:
        year = crime.split('/')
        year_occurred.append(year[2])
        
    clean_crime_data_df['Year of Crime'] = year_occurred

# Grabbing Total Homeless Count in LA County.  Removed commas from count data.
def homeless_counts():
    homeless_counts = raw_homeless_data_df.loc[((raw_homeless_data_df['Measures'] == "Total Homeless") &
                                        (raw_homeless_data_df['CoC Name'] == "Los Angeles City & County CoC") & 
                                        (raw_homeless_data_df['State'] == 'CA')) 
                                        & ((raw_homeless_data_df['Year'] == "1/1/2012") 
                                        | (raw_homeless_data_df['Year'] == "1/1/2013") 
                                        | (raw_homeless_data_df['Year'] == "1/1/2014") 
                                        | (raw_homeless_data_df['Year'] == "1/1/2015") 
                                        | (raw_homeless_data_df['Year'] == "1/1/2016"))]
    homeless_counts_fixed = homeless_counts.replace(',','',regex=True)
    return homeless_counts_fixed



