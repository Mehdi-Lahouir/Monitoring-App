from datetime import datetime, timedelta
import pytz
import requests
from matplotlib import pyplot as plt
from io import BytesIO
import base64
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather_forecast(latitude, longitude):
    current_time = datetime.utcnow()
    start_time = current_time
    end_time = current_time + timedelta(hours=12)

    start_timestamp = start_time.replace(tzinfo=pytz.UTC).isoformat()
    end_timestamp = end_time.replace(tzinfo=pytz.UTC).isoformat()

    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current': 'temperature_2m,wind_speed_10m',
        'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m',
        'start': start_timestamp,
        'end': end_timestamp
    }

    response = requests.get(OPEN_METEO_API_URL, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return None
    

def plot_temperature(weather_data):
    hourly_data = weather_data.get('hourly', {}).get('temperature_2m', [])
    hourly_time = weather_data.get('hourly', {}).get('time', [])

    current_time = datetime.utcnow()
    end_time = current_time + timedelta(hours=12)

    timestamps = []
    temperatures = []

    for time, entry in zip(hourly_time, hourly_data):
        if isinstance(entry, (int, float)) and time and isinstance(time, str):
            timestamps.append(time)
            temperatures.append(entry)

    timestamps_dt = []
    timestamps_next = []
    current_date = current_time.date()

    for timestamp in timestamps:
        if timestamp:
            try:
                date_part, time_part = timestamp.split('T')

                timestamp_date = datetime.strptime(date_part, "%Y-%m-%d").date()
                if timestamp_date == current_date or timestamp_date == current_date + timedelta(days=1):
                    timestamp_with_date = f"{date_part} {time_part}"
                    timestamp_dt = datetime.strptime(timestamp_with_date, "%Y-%m-%d %H:%M")
                    timestamps_dt.append(timestamp_dt)
                else:
                    timestamp_with_date = f"{date_part} {time_part}"
                    timestamp_dt = datetime.strptime(timestamp_with_date, "%Y-%m-%d %H:%M")
                    timestamps_next.append(timestamp_dt)
            except ValueError:
                print(f"Skipping invalid timestamp: {timestamp}")

    next_12_hours_timestamps = []
    next_12_hours_temperatures = []

    for timestamp, temp, timestamp_dt in zip(timestamps, temperatures, timestamps_dt):
        if timestamp and current_time <= timestamp_dt <= end_time:
            next_12_hours_timestamps.append(timestamp_dt)
            next_12_hours_temperatures.append(temp)

    next_12_hours_timestamps_num = mdates.date2num(next_12_hours_timestamps)

    fig, ax = plt.subplots()

    ax.plot(next_12_hours_timestamps_num, next_12_hours_temperatures, label='Temperature (°C)')

    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

    ax.set_xlabel('Time (UTC)')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Hourly Temperature Forecast (Next 12 hours)')
    ax.legend()
    ax.grid(True)

    for timestamp, temp in zip(next_12_hours_timestamps_num, next_12_hours_temperatures):
        ax.text(timestamp, temp, f'{temp}°C', ha='center', va='bottom')

    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')
    plt.close()

    return image_base64

import matplotlib.dates as mdates
import pytz

def make_temperature_prediction(timestamps, temperatures):
    timestamps_np = np.array([np.datetime64(timestamp) for timestamp in timestamps])
    timestamps_np_numeric = timestamps_np.view('int64').reshape(-1, 1)

    temperatures_np = np.array(temperatures)

    model = LinearRegression().fit(timestamps_np_numeric, temperatures_np)

    timedelta_1day = np.timedelta64(1, 'D')  
    next_day_timestamps_np = timestamps_np + timedelta_1day
    next_day_timestamps_np_numeric = next_day_timestamps_np.view('int64').reshape(-1, 1)

    predictions = model.predict(next_day_timestamps_np_numeric)

    fig, ax = plt.subplots()
    ax.plot(next_day_timestamps_np, predictions, label='Temperature Prediction (Next Day)')
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature Prediction for Next Day(s)')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.grid(True)

    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

    return image_base64


def extract_hourly_data(weather_data):
    hourly_data = weather_data.get('hourly', {}).get('temperature_2m', [])
    hourly_time = weather_data.get('hourly', {}).get('time', [])

    current_time = datetime.utcnow()
    end_time = current_time + timedelta(hours=12)

    timestamps = []
    temperatures = []

    for time, entry in zip(hourly_time, hourly_data):
        if isinstance(entry, (int, float)) and time and isinstance(time, str):
            timestamps.append(time)
            temperatures.append(entry)

    timestamps_dt = []
    timestamps_next = []
    current_date = current_time.date()

    for timestamp in timestamps:
        if timestamp:
            try:
                date_part, time_part = timestamp.split('T')
                timestamp_date = datetime.strptime(date_part, "%Y-%m-%d").date()
                if timestamp_date == current_date or timestamp_date == current_date + timedelta(days=1):
                    timestamp_with_date = f"{date_part} {time_part}"
                    timestamp_dt = datetime.strptime(timestamp_with_date, "%Y-%m-%d %H:%M")
                    timestamps_dt.append(timestamp_dt)
                else:
                    timestamp_with_date = f"{date_part} {time_part}"
                    timestamp_dt = datetime.strptime(timestamp_with_date, "%Y-%m-%d %H:%M")
                    timestamps_next.append(timestamp_dt)
            except ValueError:
                print(f"Skipping invalid timestamp: {timestamp}")

    min_length = min(len(timestamps_next), len(temperatures))
    return timestamps_next[:min_length], temperatures[:min_length]


