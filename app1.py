import streamlit as st
import pandas as pd
from datetime import datetime
import joblib  # assuming you have a saved model using joblib
import math
from streamlit_login_auth_ui.widgets import __login__
import warnings
warnings.filterwarnings("ignore")

def calculate_absolute_humidity(temperature, dew_point):
    # constants
    a = 17.27
    b = 237.7
    
    # check for dew point equal to or higher than temperature
    if dew_point >= temperature:
        # set absolute humidity to zero to prevent division by zero
        return 0.0
    else:
        # calculate saturation vapor pressure
        svp = (a * dew_point) / (b + dew_point)
        
        # check for temperature equal to zero
        if temperature == 0:
            # set absolute humidity to zero to prevent division by zero
            return 0.0
        else:
            # calculate absolute humidity
            ah = 6.112 * svp * math.exp((a * temperature) / (b + temperature)) / temperature
            return ah

# Load your pre-trained model (make sure to save your model as 'model.joblib')
model = joblib.load('model.joblib')
encoder = joblib.load('encoder.joblib')

def predict_bike_demand(input_df):
    prediction = model.predict(input_df)
    return prediction

def main():
    st.title("Sharing Demand Prediction for MotorCycle using Machine Learning")

    # User inputs
    date_input = st.date_input("Date (yyyy-mm-dd)")
    hour = st.number_input("Hour", min_value=0, max_value=23, step=1, format="%d")
    temperature = st.number_input("Temperature (°C)", format="%.2f")
    humidity = st.number_input("Humidity (%)", min_value=0, max_value=100, step=1, format="%d")
    wind_speed = st.number_input("Wind Speed (m/s)", format="%.2f")
    visibility = st.number_input("Visibility (10m)", format="%.2f")
    dew_point_temperature = st.number_input("Dew Point Temperature (°C)", format="%.2f")
    solar_radiation = st.number_input("Solar Radiation (MJ/m2)", format="%.2f")
    rainfall = st.number_input("Rainfall (mm)", format="%.2f")
    snowfall = st.number_input("Snowfall (cm)", format="%.2f")
    seasons = st.selectbox("select season", ['Winter','Spring','Summer','Autumn'], index=0)
    holiday = st.selectbox("select holiday", ['No Holiday','Holiday'], index=0)
    functioning_day = st.selectbox("select functioning day", ['Yes','No'], index=0)
    
    
    if st.button("Predict"):
        absolute_humidity = calculate_absolute_humidity(temperature, dew_point_temperature)
        date_time_obj = datetime.combine(date_input, datetime.min.time())
        date_year = date_time_obj.year
        date_month = date_time_obj.month
        date_day = date_time_obj.day
        date_hour = date_time_obj.hour
        date_minute = date_time_obj.minute
        date_second = date_time_obj.second

        encoder_data = {
            'Seasons':[seasons], 
            'Holiday':[holiday], 
            'Functioning_Day':[functioning_day]
        }
        encoder_data = pd.DataFrame(encoder_data)
        encoded_data = encoder.transform(encoder_data)
        encoded_df = pd.DataFrame(encoded_data, columns=encoder.get_feature_names_out(['Seasons', 'Holiday', 'Functioning_Day']))
        
        # Create DataFrame
        input_data = {
            'Hour': [hour],
            'Temperature': [temperature],
            'Humidity': [humidity],
            'Wind_speed': [wind_speed],
            'Visibility': [visibility],
            'Solar_Radiation': [solar_radiation],
            'Rainfall': [rainfall],
            'Snowfall': [snowfall],
            'Absolute_Humidity': [absolute_humidity],
            'Date_year': [date_year],
            'Date_month': [date_month],
            'Date_day': [date_day],
            'Date_hour': [date_hour],
            'Date_minute': [date_minute],
            'Date_second': [date_second]
        }

        input_df = pd.DataFrame(input_data)
        
        input_df = pd.concat([input_df.reset_index(drop=True),encoded_df.reset_index(drop=True)],axis=1)
        print(input_df.columns)
        # Predict
        prediction = predict_bike_demand(input_df)
        st.write(f"Predicted Bike Demand: {int(prediction[0])}")
        st.write(f"Available Bike Count : 50")

if __name__ == "__main__":
    __login__obj = __login__(auth_token = "dk_prod_XHG9DC6V4EMCB2J8X6GJA01AFJMS", 
                    company_name = "Shims",
                    width = 200, height = 250, 
                    logout_button_name = 'Logout', hide_menu_bool = False, 
                    hide_footer_bool = False, 
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

    LOGGED_IN = __login__obj.build_login_ui()

    if LOGGED_IN == True:
        main()
