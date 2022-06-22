from prophet import Prophet

def run_forecast_univariate(df, periods):

    """
    returns the univariate prophet forecast + two graphic objects (forecast & components)

    Parameters
    ----------
    df: DataFrame
        a dataframe that includes the historical data
    periods: int
        the time steps to forecast

    Returns
    -------
    forecast
        a dataframe containing the foecast data
    fig_forecast
        a figure forecast to plot
    fig_components
        a figure components to plot
    
    """

    #renaming columns for prophet convention
    df = df.rename(columns = {df.columns[0]: "ds", df.columns[1]:"y"})

    # creating a Prophet object 
    ## optional parameters can be set here like:
    ## seasonality, changepoints, uncertainty intervals etc. see help(Prophet)
    m = Prophet() 

    # fit() methods expects a dataframe with the column heads ds and y
    # fits the prophet model to the data
    m.fit(df)

    # Definition of forecast range
     ## periods: Int number of periods to forecast forward. 
     ## req: Any valid frequency for pd.date_range, such as 'D' or 'M'.
    future = m.make_future_dataframe(periods=periods, freq = "H")
    
    # Prediction
     ## expects a dataframe with dates for predictions 
     ## (created above with make_future_dataframe)
    forecast = m.predict(future)
    
    # plotting
    fig_forecast = m.plot(forecast)
    fig_comp = m.plot_components(forecast)
    
    return forecast, fig_forecast, fig_comp


