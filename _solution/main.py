from doctest import DocFileCase
from lib2to3.pgen2.pgen import DFAState
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


from modules.download_button import download_button
from modules.fetch_data import get_open_data_elia_df
from modules.forecast_univariate import run_forecast_univariate
from modules.forecast_multivariate import prepare_data_for_mv_fc, run_forecast_multivariate
from modules.helper import check_regressors



st.image("data/TimeSeriesForecaster.png")
"""
### Introduction
With this app you can forecast the Total Load, the PV production as well as the Wind production of the Belgium Electricity Grid. The live data is fetched from the
[Elia Open Data Platform](https://www.elia.be/en/grid-data/open-data). 

Please select the forecasting method and choose the data point to forecast from the drop-down menu. Next, choose the historical data to be used for training the model as well as the forecast horizon to predict. 
After the calculation, the results are displayed below with the option to export as .csv files.
"""

"""
### Forecasting Method
You can choose between univariate and multivariate forecasting: 

**Univariate** forecasting only takes historical data and tries to find patterns based on seasonality to predict the forecast. It is good and quick solution if the data includes periodicity and is not heavily dependent on other features. 

**Multivariate** forecasting adds additional features e.g. wind speed, solar radiation or temperature to the historical data to improve the forecast. If the rght additional features are selected, it will offer a better forecast but requires more time to calculate.

**Example:** If you have a PV system on-site, experiment with adding solar radiation as a feature. It could improve the forecast, as you will consume less energy from the grid when the sun is shining. This correlation can be represented by the additional sun radiation feature.  
"""


forecast_model = st.radio(
     "Select your forecasting method:",
     ('Univariate', 'Multivariate'))

st.markdown(
    """ ### Data Selection 
    Select the data from the Elia grid to forecast."""
    )

options = ["Total Load","PV production","Wind production" ]
option = st.selectbox(
        'Select the data',
            (options)
            )


"""
### Training Data and Forecast Horizon
Select the number of days (**Historical data in days**) that will be used for the model training. Next, choose the **Forecast Horizon in days**, the number of days you like to predict.
It is recommended to use a timeframe that includes reoccuring patterns for the model to detect. 

**Example:** If you have a weekly production site schedule, choose at least two weeks or more of data to train the model.
The more data and the longer forecast horizon are selected, the longer it will take to do the prediction.
"""
# Layout two columns
col1, col2 = st.columns(2) 

# Two sliders to select historical data and forecast horizon
no_days = col1.slider("Historical data in days.", min_value=1, max_value=14 )
button_periods_to_predict = col2.slider("Forecast Horizon in days", min_value = 1, max_value = 7 )
no_of_hours_to_predict = button_periods_to_predict *24

# Initiliazing empty variables
forecast = None
fig_forecast = None
fig_comp = None
reg_coef = None
forecast_ready= False
reg_coef = None
df = pd.DataFrame()

# specifying date
end_date_hist = datetime.now()
start_date_hist = end_date_hist - timedelta(days = no_days)

# datasets to catch external data from rebase
dataset_solar = "ods032"
dataset_load = "ods003"
dataset_wind =  "ods031"

# Additonal pop-up section if multivariate forecast is selected, 
# to choose additonal regressors 

if forecast_model == "Multivariate":
    
    """
    ### Choose Additional Regressors
    
    """
    add_regressors = st.multiselect(
        "Select the additional parameters for the forecast. At least, one has to be selected.",
        options = ["Sun Radiation", "Wind Speed", "Temperature"])

    if  not add_regressors:
        st.markdown("**Please select at least one additional parameter.**")

calc_start = st.button("Start Calculation")


# Univariate calculation

if forecast_model == "Univariate" and calc_start:

    # get and prepare data for total Load (univariate)
    if option == "Total Load": 
        # Catching and Formatting data for Total Load     
        df = get_open_data_elia_df(dataset_load, start_date_hist, end_date_hist)
        df = df.loc[:,["datetime", "eliagridload"]]
            
    #  get and prepare data for wind or PV production (univariate)
    if (option == "Wind production") or option == "PV production":

        # selecting the correct dataset
        if option == "Wind production":
            dataset = dataset_wind
        else:
            dataset = dataset_solar
        # Catching and Formatting data for Wind Production    
        df = get_open_data_elia_df(dataset, start_date_hist, end_date_hist) # 14 different departments
        
        df = df.groupby("datetime").sum()
        df.reset_index(inplace = True)
        df = df.loc[:,["datetime", "mostrecentforecast"]]
        df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize(None)

 
    # Calculation of Univariate Forecast
    forecast, fig_forecast, fig_comp= run_forecast_univariate(df, no_of_hours_to_predict)
    forecast_ready = True

# Multivariate calculation

if (forecast_model == "Multivariate") and calc_start:
    
    if add_regressors:
        solar, wind, temp = check_regressors(add_regressors) 
        lat = "50.85045"
        long= "4.34878"

        with st.spinner("The forecast is now being calculated."):

            if option == "PV production": 
                df_merged = prepare_data_for_mv_fc(dataset_solar, start_date_hist, end_date_hist, solar, wind, temp, lat,long)
               
            if option == "Wind production":           
                df_merged = prepare_data_for_mv_fc(dataset_wind, start_date_hist, end_date_hist, solar, wind, temp, lat,long)
        
            if option == "Total Load": 
                df_merged = prepare_data_for_mv_fc(dataset_load, start_date_hist, end_date_hist, solar, wind, temp, lat,long)
            
            # Start of the calculation
            forecast, fig_forecast, fig_comp, reg_coef = run_forecast_multivariate(df_merged, lat, long, no_of_hours_to_predict)
            df = df_merged.loc[:,["ds","y"]].rename(columns= {"ds":"datetime"})
            forecast_ready = True   

    else:
        st.write("Please select at least one regressor.")

if not df.empty and option is not None:

    """
    ### Historical Data
    The following section displays the selected historical data.
    """
    # Display the data from the API
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime")
    
    df = df.loc[start_date_hist:end_date_hist,:]
    st.line_chart(df)
    #st.write(df)
    df.reset_index(inplace = True)

if forecast_ready:
    
    """
    ### Forecast Results
    The following section displays the forecast results. It is divided into the forecast and a component plot.
    """
    """
    #### Forecast Plot
    """

    st.write(fig_forecast)
    forecast.rename(columns={"ds":"datetime"}, inplace = True)

    # selection of the most important columns of forecast dataframe to display
    st.write(forecast.loc[:,["datetime","yhat","yhat_lower","yhat_upper"]])
    st.markdown("#### Components Plot")
    st.write(fig_comp)

    if reg_coef is not None:

        """
        ### Additional Regressors
        
        """
        st.write(reg_coef)
        
    """
    ### Download Section
    You can download the **Input Data** and the **Forecast Results** as a .csv file. 
    The Input Data is fetched from the Elia Open Data Platform. 
    The Forecast Results include in-sample prediction (historical) and the out-of-sample prediction.
    """
    # get current data
    now = datetime.now()

    # function to convert dataframe to csv
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    col1, col2 = st.columns(2)
    col1.markdown(
            download_button(
                convert_df(df), 
                f'input_data_{now.strftime("%d/%m/%Y_%H:%M:%S")}.csv', 
                "Download Input Data Source"),
                unsafe_allow_html=True
            )

    col2.markdown(
            download_button(
                convert_df(forecast),
                f'forecast_data_{now.strftime("%d/%m/%Y_%H:%M:%S")}.csv',
                "Download Forecast Results"),
                unsafe_allow_html=True
            )
        

