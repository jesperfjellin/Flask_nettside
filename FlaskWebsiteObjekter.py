from flask import Flask, render_template_string, request
import csv
import os

app = Flask(__name__)

@app.after_request
def add_no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response

CSV_FILENAME = "objekter.csv"

def append_to_csv(lat, lng, obj):
    mode = 'a+' if os.path.exists(CSV_FILENAME) else 'w'
    with open(CSV_FILENAME, mode, newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['lat', 'lng', 'object'])
        if file.tell() == 0:  # File is empty, write the header
            writer.writeheader()
        writer.writerow({'lat': lat, 'lng': lng, 'object': obj})

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    object_name = request.form.get('object_name')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    location_response = request.form.get('location_response')

    if request.method == 'POST':
        if object_name:
            if location_response == "yes":
                if latitude and longitude:
                    append_to_csv(latitude, longitude, object_name)
                    message = "Objekt registrert!"
                    object_name = None  # Reset to show the initial form again
                else:
                    message = "Vennligst tillat lokalisering."
            elif location_response == "no":
                # Handle the 'no' response here. What do you want to happen?
                # For now, I'll just set a message.
                message = "Location not provided."
            else:
                message = "Current location?"
        else:
            message = "Vennligst fyll inn objektnavn."


    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Objekt Registrering</title>
            <script>
                function getLocation() {
                    if (navigator.geolocation) {
                            navigator.geolocation.getCurrentPosition(function(position) {
                                document.getElementById("latitude").value = position.coords.latitude;
                                document.getElementById("longitude").value = position.coords.longitude;
                                document.getElementById("locationForm").submit();
                                }, function(error) {
                                    alert("Error occurred. Error code: " + error.code);
                                    // error.code can be:
                                        // 0: unknown error
                                        // 1: permission denied
                                        // 2: position unavailable (error response from location provider)
                                        // 3: timed out
                                });
                            } else {
                                alert("Geolocation is not supported by this browser.");
                            }
                        

    window.onload = function() {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                alert("Latitude: " + position.coords.latitude + ", Longitude: " + position.coords.longitude);
            },
            function(error) {
                alert("Error occurred. Error code: " + error.code);
            }
        );
    }
</script>


        </head>
        <body>
            <form method="post" id="locationForm">
                {% if not object_name %}
                    <input name="object_name" type="text" placeholder="Hvilket objekt ønsker du å registrere?">
                    <input type="submit" value="Submit">
                {% elif not latitude and not longitude %}
                    <input type="hidden" name="object_name" value="{{ object_name }}">
                    <p>Current location?</p>
                    <button type="button" onclick="getLocation()">Yes</button>
                    <input type="hidden" name="latitude" id="latitude">
                    <input type="hidden" name="longitude" id="longitude">
                    <button type="submit" name="location_response" value="no">No</button>
                {% endif %}
            </form>
            
            {% if message %}
                <div>{{ message }}</div>
            {% endif %}
        </body>
        </html>
    ''', message=message, object_name=object_name)


if __name__ == '__main__':
    app.run(debug=True)
