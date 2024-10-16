from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'supersecretkey'

API_KEY = 'e3fc52da351179b5d206febb3ffa9387'

# Load favorite cities from file
def load_favorites():
    if os.path.exists("favorites.txt"):
        with open("favorites.txt", "r") as f:
            return [city.strip() for city in f.readlines()]
    return []

# Save new favorite city to file
def save_favorite(city):
    if city not in load_favorites():
        with open("favorites.txt", "a") as f:
            f.write(city + "\n")

# Fetch current weather data for a city
def get_weather_data(city, unit='metric'):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Fetch 5-day forecast data for a city
def get_forecast_data(city, unit='metric'):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['list'][:5]
    else:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        city = request.form['city']
        unit = request.form['unit']
        weather_data = get_weather_data(city, unit)

        if weather_data:
            return render_template('index.html', weather=weather_data, unit=unit, favorites=load_favorites())
        else:
            flash("Error retrieving weather data. Please try again.")
            return redirect(url_for('index'))

    return render_template('index.html', weather=None, favorites=load_favorites())

@app.route("/forecast/<city>")
def forecast(city):
    forecast_data = get_forecast_data(city)
    if forecast_data:
        return render_template('forecast.html', forecast=forecast_data, city=city)
    else:
        flash("Error retrieving forecast data.")
        return redirect(url_for('index'))

@app.route("/add_favorite/<city>")
def add_favorite(city):
    save_favorite(city)
    flash(f"{city} has been added to favorites!")
    return redirect(url_for('index'))

@app.route("/plot")
def plot_temperature():
    cities = load_favorites()
    temperatures = []
    unit = 'metric'

    for city in cities:
        weather_data = get_weather_data(city, unit)
        if weather_data:
            temperatures.append(weather_data['main']['temp'])

    if temperatures:
        plt.figure(figsize=(10, 5))
        plt.bar(cities, temperatures, color='blue')
        plt.xlabel('Cities')
        plt.ylabel('Temperature (°C)')
        plt.title('Current Temperature in Favorite Cities')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()

        return render_template('plot.html', image=image_base64)
    else:
        flash("No favorite cities to plot.")
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
