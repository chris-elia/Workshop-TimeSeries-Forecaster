import pandas as pd
import requests
import streamlit as st

def get_open_data_elia_df(dataset, start_date, end_date):
    """Gets and returns the selected dataset from the Elia Open Data Platform within a given time range

    Parameters
    ----------
    dataset: str
        the selected dataset identifier from the Elia Open Data Platform
    start_date: str
        The start date of the selected dataset, Format: "YYYY-MM-DD"
    end_date: str
        The end date of the selected dataset, Format: "YYYY-MM-DD"    
    

    Returns
    -------
    pd.Dataframe
        a dataframe containing the selected data
    
    """

    url = f"https://opendata.elia.be/api/v2/catalog/datasets/{dataset}/exports/"
    json_string = f"json?where=datetime in [date'{start_date}' .. date'{end_date}']"
    
    response = requests.get(url = url + json_string)

    # calling the Elia Open Data API
    df = pd.DataFrame(response.json())
    
    df.sort_values(by = "datetime", inplace = True)
    df.reset_index(inplace = True, drop =  True)    
    df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)

    return df

# get weather forecast from Rebase
def get_weather_forecast(start_date, end_date, latitude, longitude):

    """Gets and returns the weather forecast from rebase within a given time range

    Parameters
    ----------
    start_date: str
        The start date of the selected dataset, Format: "YYYY-MM-DD"
    end_date: str
        The end date of the selected dataset, Format: "YYYY-MM-DD"
    latitude: str
        The latitude value (Geo location) of the city for the weather forecast
    longitude: str
        The longitude value (Geo location) of the city for the weather forecast

    Returns
    -------
    pd.Dataframe
        a dataframe containing the selected data
    
    """

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Authentication
    url = "https://api.rebase.energy/weather/v2/query"
    headers = {"Authorization": st.secrets["REBASE_KEY"]}
    params = {
        'model': 'DWD_ICON-EU',
        'start-date': start_date,
        'end-date': end_date,
        'reference-time-freq': '24H',
        'forecast-horizon': 'latest',
        'latitude': latitude,
        'longitude': longitude,
        'variables': 'Temperature, WindSpeed, CloudCover'
    }
    response = requests.get(url, headers=headers, params=params)
    
    # Clean data
    df = pd.DataFrame(response.json())
    print(df)
    df = df.drop('ref_datetime', axis=1)
    df["valid_datetime"] = pd.to_datetime(df["valid_datetime"]).dt.tz_localize(None)

    df = df.rename(columns={'valid_datetime': 'datetime'})
    df = df.drop_duplicates(keep='last')
    df = df.fillna(0)

    return df
  

  