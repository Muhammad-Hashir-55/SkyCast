import tkinter as tk
from tkinter import messagebox
import requests
import json
import matplotlib.pyplot as plt
import geocoder  # For getting user location
import os
from datetime import datetime, timedelta
from tkinter import simpledialog
import webbrowser

API_KEY = 'e3fc52da351179b5d206febb3ffa9387'

class WeatherApp:
    def __init__(self, master):

        self.title_label = tk.Label(master, text="SkyCast", font=("Helvetica", 24, "bold"), bg="black", fg="#FFFFFF")
        self.title_label.pack(pady=10)

        self.master = master
        master.title("SkyCast")

        # Enhanced UI: Window dimensions and background color
        master.geometry("500x600")
        master.config(bg="#87CEEB")  # Sky blue background

        # Enhanced label for "Enter City"
        self.label = tk.Label(master, 
                      text="Enter City:", 
                      font=("Helvetica", 16, "bold"),  # Beautiful font style
                      fg="#3b5998",  # A nice blue color for the text
                      bg="#f0f0f0",  # Light background for contrast
                      padx=10, pady=10,  # Add padding for space around the text
                      relief="groove",  # Add a border around the label
                      bd=2)  # Border width
        self.label.pack(pady=10)  # Adding vertical padding around the label

        self.city_entry = tk.Entry(master)
        self.city_entry.pack()

        # Radio buttons for unit selection
        self.unit_var = tk.StringVar(value='metric')  # Default unit
        self.metric_radio = tk.Radiobutton(master, text="Celsius", variable=self.unit_var, value='metric')
        self.metric_radio.pack()
        self.imperial_radio = tk.Radiobutton(master, text="Fahrenheit", variable=self.unit_var, value='imperial')
        self.imperial_radio.pack()

        self.get_weather_button = tk.Button(master, text="Get Weather", command=self.get_weather)
        self.get_weather_button.pack()

        self.get_location_button = tk.Button(master, text="Get My Location Weather", command=self.get_location_weather)
        self.get_location_button.pack()

        self.favorite_button = tk.Button(master, text="Save to Favorites", command=self.save_favorite)
        self.favorite_button.pack()

        self.remove_favorite_button = tk.Button(master, text="Remove from Favorites", command=self.remove_favorite)
        self.remove_favorite_button.pack()

        self.favorite_label = tk.Label(master, text="Favorites:")
        self.favorite_label.pack()

        self.favorites_list = tk.Listbox(master)
        self.favorites_list.pack()

        self.plot_button = tk.Button(master, text="Plot Temperature", command=self.plot_temperature)
        self.plot_button.pack()

        # Create a frame for the new feature buttons
        feature_frame = tk.Frame(master, bg="#87CEEB")
        feature_frame.pack(pady=20)

        # New feature: User Feedback
        self.feedback_button = tk.Button(feature_frame, text="Give Feedback", command=self.get_user_feedback, font=("Helvetica", 12), bg="#4682B4", fg="white", bd=2, relief="raised")
        self.feedback_button.grid(row=0, column=0, padx=5)

    

        # New feature: Get weather alerts/notifications
        self.alerts_button = tk.Button(feature_frame, text="Check Weather Alerts", command=self.check_alerts, font=("Helvetica", 12), bg="#4682B4", fg="white", bd=2, relief="raised")
        self.alerts_button.grid(row=1, column=0, padx=5)

        # New feature: Historical weather data
        self.historical_button = tk.Button(feature_frame, text="View Historical Weather", command=self.view_historical_weather, font=("Helvetica", 12, "bold"), bg="#4682B4", fg="white", bd=2, relief="raised")
        self.historical_button.grid(row=1, column=1, padx=5)

        # Share on Social Media button
        self.share_button = tk.Button(text="Share on Social Media", command=self.share_on_social_media)
        self.share_button.pack()  # Adjust packing method as needed

        self.load_favorites()


    def load_favorites(self):
        if os.path.exists("favorites.txt"):
            with open("favorites.txt", "r") as f:
                for city in f:
                    self.favorites_list.insert(tk.END, city.strip())

    def get_weather(self):
        city = self.city_entry.get()
        if not city:
            messagebox.showerror("Error", "Please enter a city name.")
            return

        unit = self.unit_var.get()
        api_key = 'e3fc52da351179b5d206febb3ffa9387'
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={unit}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('cod') == 200:
                self.display_weather(data)
            else:
                messagebox.showerror("Error", f"API error: {data.get('message', 'Unknown error')}")
        except requests.exceptions.HTTPError as http_err:
            messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Network problem. Please check your connection.")
        except requests.exceptions.Timeout:
            messagebox.showerror("Timeout Error", "Request timed out. Try again later.")
        except Exception as err:
            messagebox.showerror("Error", f"An error occurred: {err}")

    def get_location_weather(self):
        g = geocoder.ip('me')
        lat, lng = g.latlng
        if lat and lng:
            unit = self.unit_var.get()
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={API_KEY}&units={unit}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                self.display_weather(data)
            else:
                messagebox.showerror("Error", "Unable to get weather data for your location.")
        else:
            messagebox.showerror("Error", "Unable to determine your location.")

    def display_sun_times(self, data):
        sunrise_timestamp = data['sys']['sunrise']
        sunset_timestamp = data['sys']['sunset']
    
        sunrise_time = datetime.fromtimestamp(sunrise_timestamp).strftime('%H:%M:%S')
        sunset_time = datetime.fromtimestamp(sunset_timestamp).strftime('%H:%M:%S')
    
        messagebox.showinfo("Sunrise and Sunset", f"Sunrise: {sunrise_time}\nSunset: {sunset_time}")


    def display_weather(self, data):
        main = data['main']
        wind = data['wind']
        weather = data['weather'][0]

        temperature = main['temp']
        humidity = main['humidity']
        wind_speed = wind['speed']
        weather_desc = weather['description']

        messagebox.showinfo("Weather Info",
                            f"Temperature: {temperature}°\n"
                            f"Humidity: {humidity}%\n"
                            f"Condition: {weather_desc}\n"
                            f"Wind Speed: {wind_speed} m/s")

        self.fetch_forecast(data['name'])

        self.display_sun_times(data)


    def fetch_forecast(self, city):
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={self.unit_var.get()}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            forecast = data['list'][:5]

            dates = [entry['dt_txt'] for entry in forecast]
            temperatures = [entry['main']['temp'] for entry in forecast]

            plt.plot(dates, temperatures, marker='o')
            plt.xlabel('Date and Time')
            plt.ylabel('Temperature (°)')
            plt.title(f'5-Day Temperature Forecast for {city}')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        else:
            messagebox.showerror("Error", "Forecast data not available.")


    def save_favorite(self):
        city = self.city_entry.get()
        if city and city not in self.favorites_list.get(0, tk.END):
            self.favorites_list.insert(tk.END, city)
            with open("favorites.txt", "a") as f:
                f.write(city + "\n")
        else:
            messagebox.showerror("Error", "City already in favorites or invalid.")

    def plot_temperature(self):
        favorites = self.favorites_list.get(0, tk.END)
        temperatures = []
        cities = []

        for city in favorites:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={self.unit_var.get()}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                temperature = data['main']['temp']
                temperatures.append(temperature)
                cities.append(city)

        if temperatures:
            plt.bar(cities, temperatures)
            plt.xlabel('Cities')
            plt.ylabel('Temperature (°)')
            plt.title('Current Temperature in Favorite Cities')
            plt.show()
        else:
            messagebox.showerror("Error", "No favorite cities to plot.")

    # Feature 1: Check weather alerts
    def check_alerts(self):
        city = self.city_entry.get()
        if not city:
            messagebox.showerror("Error", "Please enter a city name.")
            return

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            alerts = data.get('alerts', [])
            if alerts:
                alert_messages = "\n".join([f"{alert['event']}: {alert['description']}" for alert in alerts])
                messagebox.showinfo("Weather Alerts", alert_messages)
            else:
                messagebox.showinfo("No Alerts", "There are no weather alerts for this city.")
        else:
            messagebox.showerror("Error", "Unable to get weather alerts.")


    def get_user_feedback(self):
        feedback = tk.simpledialog.askstring("Feedback", "Please provide your feedback:")
        if feedback:
            with open("feedback.txt", "a") as f:
                f.write(feedback + "\n")
            messagebox.showinfo("Thank You!", "Your feedback has been recorded.")


    def share_on_social_media(self):
        # Define the weather info to share
        weather_info = "Check out the latest weather updates!"  # Modify this to include actual weather info
    
        platforms = {
            "Facebook": f"https://www.facebook.com/sharer/sharer.php?u=https://your-weather-app-url.com&quote={weather_info}",
            "Twitter": f"https://twitter.com/intent/tweet?text={weather_info}&url=https://your-weather-app-url.com",
            "Instagram": "https://www.instagram.com/"  # Instagram doesn't support direct sharing via URL, so we provide a link to the site
        }

        platform = simpledialog.askstring("Share", "Select a platform: (Facebook,X, Instagram)")

        if platform in platforms:
            webbrowser.open(platforms[platform])
        else:
            messagebox.showwarning("Warning", "Please select a valid platform.")






    def view_historical_weather(self):
        API_KEY = '6283fcfaaf2f4fa68d9145815241310'
        city = self.city_entry.get()
        if not city:
            messagebox.showerror("Error", "Please enter a city name.")
            return

        # Retrieve historical weather data for the last 5 days using WeatherAPI
        historical_temperatures = []
        days = []

        for i in range(5):
            # Calculate the date for each of the past 5 days
            date = (datetime.now() - timedelta(days=i+1)).strftime('%Y-%m-%d')

            # Make the API call to WeatherAPI for historical weather data
            historical_url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city}&dt={date}"
            response = requests.get(historical_url)

            if response.status_code == 200:
                historical_data = response.json()
                temp = historical_data['forecast']['forecastday'][0]['day']['avgtemp_c']
                historical_temperatures.append(temp)
                days.append(date)
            else:
                error_msg = response.json().get('error', {}).get('message', 'Failed to retrieve historical data.')
                messagebox.showerror("API Error", f"Error retrieving data: {error_msg}")
                return

        # Plot the historical data
        plt.plot(days, historical_temperatures, marker='o')
        plt.xlabel("Date")
        plt.ylabel("Temperature (°C)")
        plt.title(f"Historical Weather for {city}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def remove_favorite(self):
        selected_city_index = self.favorites_list.curselection()  # Get the selected city index
        if not selected_city_index:
            messagebox.showerror("Error", "Please select a city to remove.")
            return

        city = self.favorites_list.get(selected_city_index)  # Get the selected city name
        self.favorites_list.delete(selected_city_index)  # Remove the city from the listbox

        # Remove the city from the favorites.txt file
        with open("favorites.txt", "r") as f:
            favorites = f.readlines()
        with open("favorites.txt", "w") as f:
            for favorite in favorites:
                if favorite.strip() != city:
                    f.write(favorite)  # Write back all favorites except the removed one

        messagebox.showinfo("Success", f"{city} has been removed from favorites.")


if __name__ == "__main__":
    
    window = tk.Tk()
    


    weather_app = WeatherApp(window)
    window.config(bg="#ADD8E6")

    window.mainloop()
