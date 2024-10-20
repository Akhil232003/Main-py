import requests
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# API key and cities to monitor
api_key = '58652401ac8662fa24d14314a0483100'
cities = ['delhi', 'mumbai', 'chennai', 'bangalore', 'kolkata', 'hyderabad']
temp_threshold = 35  
consecutive_updates = 2 
# Function to get weather data from OpenWeatherMap API
def get_weather_data(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None
def kelvin_to_celsius(kelvin):
    return kelvin - 273.15
def extract_weather_info(weather_data):
    if weather_data:
        temp_k = weather_data['main']['temp']
        feels_like_k = weather_data['main']['feels_like']
        weather_main = weather_data['weather'][0]['main']
        timestamp = weather_data['dt']
        
        return {
            'temp_c': kelvin_to_celsius(temp_k),
            'feels_like_c': kelvin_to_celsius(feels_like_k),
            'weather': weather_main,
            'timestamp': timestamp
        }
    return None
def daily_weather_summary(weather_data_list):
    df = pd.DataFrame(weather_data_list)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    daily_summary = df.resample('D', on='timestamp').agg({
        'temp_c': ['mean', 'max', 'min'],
        'weather': lambda x: x.mode()[0]  
    })
    return daily_summary
def plot_daily_summary(daily_summary):
    daily_summary['temp_c']['mean'].plot(kind='line', title="Average Daily Temperature")
    plt.ylabel('Temperature (°C)')
    plt.xlabel('Date')
    plt.grid(True)
    plt.show() 
def check_alerts(weather_data_list):
    df = pd.DataFrame(weather_data_list)
    df['exceeds_threshold'] = df['temp_c'] > temp_threshold
    if df['exceeds_threshold'].tail(consecutive_updates).all():
        print(f"ALERT: Temperature exceeded {temp_threshold}°C for {consecutive_updates} consecutive updates.")
def run_weather_monitoring(interval=300):
    weather_data_list = []
    while True:
        for city in cities:
            weather_data = get_weather_data(city, api_key)
            weather_info = extract_weather_info(weather_data)
            if weather_info:
                print(f"Weather data for {city}: {weather_info}")
                weather_data_list.append(weather_info)
        
        check_alerts(weather_data_list)

        if len(weather_data_list) > 0 and datetime.now().hour == 23:
            daily_summary = daily_weather_summary(weather_data_list)
            plot_daily_summary(daily_summary)

        time.sleep(interval)
run_weather_monitoring()

