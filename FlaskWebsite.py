from flask import Flask, render_template_string, request, jsonify
import geocoder
import re
import csv

app = Flask(__name__)

CSV_FILENAME = "locations.csv"

def read_locations_from_csv():
    locations = []
    try:
        with open(CSV_FILENAME, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                locations.append({'lat': float(row['lat']), 'lng': float(row['lng'])})
    except FileNotFoundError:
        pass
    return locations

def location_exists_in_csv(lat, lng, address):
    """Check if the given location and address exist in the CSV file."""
    with open(CSV_FILENAME, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if float(row['lat']) == lat and float(row['lng']) == lng and row['address'] == address:
                return True
    return False


def append_location_to_csv(lat, lng, address):
    """Append the given location and address to the CSV file if they don't exist already."""
    with open(CSV_FILENAME, 'a+', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['lat', 'lng', 'address'])
        if file.tell() == 0:  # File is empty or new, write the header
            writer.writeheader()
        if not location_exists_in_csv(lat, lng, address):
            writer.writerow({'lat': lat, 'lng': lng, 'address': address})


@app.route('/', methods=['GET', 'POST'])
def index():
    previous_locations = read_locations_from_csv()
    error_message = ""
    latitude = None
    longitude = None

    if request.method == 'POST':
        input_data = request.form.get('inputBox')
        
        # Check if input is a valid coordinate string
        coord_pattern = re.compile(r"^[-+]?[0-9]{1,3}(?:\.\d+)?,\s*[-+]?[0-9]{1,2}(?:\.\d+)?$")
        if coord_pattern.match(input_data):
            # Handle successful coordinate input
            latitude, longitude = map(float, input_data.split(','))

        else:
            # Check if input is a valid address using Google Maps API
            g = geocoder.google(input_data, key='API-key-her')
            if g.ok:
                # Handle successful address input
                latitude, longitude = g.latlng
            else:
                error_message = "Coordinates or address invalid!"
                
        if latitude and longitude:
            append_location_to_csv(latitude, longitude, input_data)
            previous_locations.append({'lat': latitude, 'lng': longitude, 'address': input_data})

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Coordinate Input</title>
            <script src="https://maps.googleapis.com/maps/api/js?key=API-key-her"></script>
            <style>
                html, body {
                    height: 100%;
                    margin: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }
                #map {
                    height: 800px;
                    width: 1200px;
                    margin-top: 15px;
                }
                #inputBox {
                    width: 300px;
                    padding: 10px;
                    font-size: 16px;
                }
                .error {
                    color: red;
                    margin-top: 10px;
                }
            </style>
        </head>
        <body>
            <form method="post">
                <input id="inputBox" name="inputBox" type="text" placeholder="Enter coordinates or address">
                <input type="submit" value="Submit">
                {% if error_message %}
                    <div class="error">{{ error_message }}</div>
                {% endif %}
            </form>

            <div id="map"></div>

            <script>
                {% if latitude and longitude %}
                    function initMap() {
                        var location = {lat: {{ latitude }}, lng: {{ longitude }}};
                        var map = new google.maps.Map(document.getElementById('map'), {
                            zoom: 14,
                            center: location
                        });
                        var marker = new google.maps.Marker({
                            position: location,
                            map: map
                        });
                    }
                    initMap();
                {% endif %}
            </script>
        </body>
        </html>
    ''', error_message=error_message, latitude=latitude, longitude=longitude)

if __name__ == '__main__':
    app.run(debug=True)
