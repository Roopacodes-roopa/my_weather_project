from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

KEY = "7519790416284d977db8eb6ae06f363c"

#  Season logic
def get_season(month):
    if month in [12, 1, 2]:
        return "Winter "
    elif month in [3, 4, 5]:
        return "Summer "
    elif month in [6, 7, 8]:
        return "Monsoon "
    else:
        return "Autumn "

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    error = None

    if request.method == 'POST':
        city_input = request.form.get('city')

        if not city_input:
            error = "Please enter at least one city"
            return render_template('index.html', data=results, error=error)

        cities = [c.strip() for c in city_input.split(',') if c.strip()]

        now = datetime.now()
        hour = now.hour
        month = now.month

        #  Time advice
        if hour < 12:
            time_advice = "Good Morning  - Fresh air walk"
        elif hour < 18:
            time_advice = "Good Afternoon - Stay hydrated"
        else:
            time_advice = "Good Evening  - Relax"

        season = get_season(month)

        for city in cities:
            try:
                #  Weather API
                weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={KEY}&units=metric"
                res = requests.get(weather_url)
                data = res.json()

                if data.get('cod') != 200:
                    continue

                temp = data['main']['temp']
                humidity = data['main']['humidity']
                desc = data['weather'][0]['description']
                wind = data['wind']['speed']

                lat = data['coord']['lat']
                lon = data['coord']['lon']

                #  AQI API
                aqi_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={KEY}"
                aqi_res = requests.get(aqi_url)
                aqi_json = aqi_res.json()

                aqi_value = aqi_json.get('list', [{}])[0].get('main', {}).get('aqi')

                #  AQI advice
                aqi_map = {
                    1: ("Good ", "Safe to go outside"),
                    2: ("Fair ", "Sensitive people take care"),
                    3: ("Moderate ", "Limit outdoor activity"),
                    4: ("Poor ", "Wear mask"),
                    5: ("Very Poor ", "Stay indoors")
                }

                status, health = aqi_map.get(aqi_value, ("N/A", "No data"))

                #  Outfit suggestion
                if temp < 15:
                    outfit = "Warm clothes "
                elif temp < 25:
                    outfit = "Light jacket "
                else:
                    outfit = "Light clothes & water "

                #  Travel suggestion
                if aqi_value and aqi_value <= 2 and temp < 30:
                    travel = "Good for travel "
                else:
                    travel = "Avoid travel "

                #  UV logic
                uv = "High UV " if temp > 30 else "Normal UV "

                results.append({
                    "city": city,
                    "temp": temp,
                    "humidity": humidity,
                    "desc": desc,
                    "wind": wind,
                    "aqi": aqi_value,
                    "status": status,
                    "health": health,
                    "outfit": outfit,
                    "time": time_advice,
                    "travel": travel,
                    "season": season,
                    "uv": uv
                })

            except Exception as e:
                print("Error:", e)
                error = "Network error!"

        if not results and not error:
            error = "City not found!"

    return render_template('index.html', data=results, error=error)


if __name__ == '__main__':
    app.run(debug=True)