# ---------------------------- IMPORT STATEMENTS ------------------------------- #
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import requests
from datetime import datetime
from requests.exceptions import HTTPError, RequestException
# ---------------------------- START FLASK FRAMEWORK ------------------------------- #
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfxfdd'
Bootstrap(app)


# ---------------------------- CREATE FORMS ------------------------------- #
def iss_overhead(user_latitude, user_longitude):
    # Use user-provided latitude and longitude in the API request
    response = requests.get(f"http://api.open-notify.org/iss-now.json?lat={user_latitude}&lon={user_longitude}")
    response.raise_for_status()
    data = response.json()
    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])
    # Check if the ISS is overhead based on user's location
    return user_latitude - 5 <= iss_latitude <= user_latitude + 5 and user_longitude - 5 <= iss_longitude <= user_longitude + 5


def is_dark(user_latitude, user_longitude):
    parameters = {
        "lat": user_latitude,
        "lng": user_longitude,
        "formatted": 0,
    }

    try:
        response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
        response.raise_for_status()
        data = response.json()
        sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
        sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])
        time_now = datetime.now()
        current_time = time_now.hour

        return current_time <= sunrise or current_time >= sunset
    except (HTTPError, RequestException, KeyError, ValueError) as e:
        # Handle any exceptions (HTTP errors, missing data, etc.)
        print(f"An error occurred: {str(e)}")
        return False


@app.route('/', methods=['GET', 'POST'])
def home():
    iss_is_overhead_result = None
    is_dark_now_result = None

    if request.method == 'POST':
        user_latitude = float(request.form['latitude'])
        user_longitude = float(request.form['longitude'])

        # Call functions with user-provided latitude and longitude
        iss_is_overhead_result = iss_overhead(user_latitude, user_longitude)
        is_dark_now_result = is_dark(user_latitude, user_longitude)
        return render_template('index.html', iss_is_overhead_result=iss_is_overhead_result,
                               is_dark_now_result=is_dark_now_result)
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
