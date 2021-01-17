# Import Dependencies
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import holidays
import warnings

warnings.filterwarnings('ignore')

loaded = False
crime_data_csv = "../data/crime/2012_2016_CrimeRate.csv"
homeless_data_csv = "../data/crime/2007-2016-Homelessness-USA.csv"
raw_crime_data_df = pd.DataFrame()
raw_homeless_data_df = pd.DataFrame()
clean_crime_data_df = pd.DataFrame()
time_blocks = []

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

# Reloads and cleans the data files if data changes
def reload_data():
    global loaded
    loaded = False
    clean_data()

# Cleans the data. Renames to columns to be better understood, replaces main
# crimes with more reader friendly desciptions. Also adds the Time block the 
# crimes were reported.
def clean_data(latlng_decimal=4):
    global clean_crime_data_df
    global nan_dropped_crime_df
    global time_blocks
    load_data_files()
    
    # Remove the nan values from the data (Nan values in Crime desc, Lat and Lng)
    nan_dropped_crime_df = raw_crime_data_df.dropna()
    # Convert the longitude and latitude to numeric
    nan_dropped_crime_df[["Longitude", "Latitude"]] = nan_dropped_crime_df[["Longitude", "Latitude"]].apply(pd.to_numeric)
    # Round to nearest two decimals for the lat and lng 
    nan_dropped_crime_df = nan_dropped_crime_df.round({"Latitude": latlng_decimal, "Longitude": latlng_decimal})
    
    # Renaming most columns so they are better understood.
    renamed_crime_df = nan_dropped_crime_df.rename(columns={"Date.Rptd":"Date Reported",
                                                 "DR.NO":"Case Number",
                                                 "DATE.OCC":"Date Occurred",
                                                 "TIME.OCC":"Time Occurred",
                                                 "AREA": "Area",
                                                 "AREA.NAME":"Area Name",
                                                 "Crm.Cd":"Crime Code",
                                                 "CrmCd.Desc":"Crime Description",
                                                 "Status.Desc":"Status Description"})
    # Change the date values to datetime object
    renamed_crime_df[["Date Reported", "Date Occurred"]] = renamed_crime_df[["Date Reported", "Date Occurred"]].apply(pd.to_datetime)
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
    month_occurred = []
    day_occurred = []
    dayofweek_occured = []
    
    holiday_bool = []
    ca_holidays = holidays.US(state="CA")    # CA holidays
    for crime in clean_crime_data_df['Date Occurred']:
        year = crime.year
        month = crime.month
        day = crime.day
        dayname = crime
        dayofweek = crime.weekday()
        
        # Check for holiday
        isholiday = crime in ca_holidays or \
                    crime.day_name() == "Sunday" or \
                    crime.day_name() == "Saturday"
        
        year_occurred.append(year)
        month_occurred.append(month)
        day_occurred.append(day)
        dayofweek_occured.append(dayofweek)
        holiday_bool.append(isholiday)
        
    clean_crime_data_df['Year of Crime'] = year_occurred
    clean_crime_data_df['Month of Year'] = month_occurred
    clean_crime_data_df['Day of Month'] = day_occurred
    clean_crime_data_df['Day of Week'] = dayofweek_occured
    
    clean_crime_data_df["Holiday"] = holiday_bool

    # Create 1 hour time blocks column. Times are rounded down to the nearest hour
    clean_crime_data_df["Time Block Occurred"] = (clean_crime_data_df["Time Occurred"] / 100).astype(int) *100

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


def collect_lat_lng_dist(crime_desc):
    # Closeby lat and lng
    if crime_desc == "All":
        df = clean_crime_data_df
    else:
        df = clean_crime_data_df[clean_crime_data_df["Crime Description"] == crime_desc]
        
    lat_lng_df = df[["Latitude", "Longitude"]].drop_duplicates()

    weights = []
    counter = 0   # for printing
    for lat_lng in lat_lng_df.iterrows():
        if counter%100 == 0:
            print("%d/%d" % (counter, len(lat_lng_df)), end='    \r', flush=True)
        weight = np.bitwise_and(np.isclose(df["Latitude"], lat_lng[1]["Latitude"]),
                   np.isclose(df["Longitude"], lat_lng[1]["Longitude"])).sum()
        weights.append(weight)
        counter = counter+1
    
    lat_lng_df["Weights"] = weights/np.array(weights).max()
    return lat_lng_df
