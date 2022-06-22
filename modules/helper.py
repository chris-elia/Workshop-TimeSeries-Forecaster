def check_regressors(add_regressors): 

    if "Sun Radiation" in add_regressors:
        solar = True
    else:
        solar = False
    if "Wind Speed" in add_regressors:
        wind = True
    else:
        wind = False
    if "Temperature" in add_regressors:
        temp = True
    else:
        temp = False
    print("solar, wind, temp "+ str(solar) + str(wind) + str(temp))
    return solar, wind, temp


  