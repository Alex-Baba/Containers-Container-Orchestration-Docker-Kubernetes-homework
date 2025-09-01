from flask import Flask
import os
import time
import threading

# Create the Flask application
app = Flask(__name__)

# Define a route for the homepage
@app.route("/")
def hello_world():
    message = os.getenv("APP_MESSAGE", "Hello, World!")
    secret = os.getenv("APP_SECRET", "No secret set")
    return f"{message} | Secret: {secret}"

@app.route("/health")
def health():
    return "OK", 200

# Example: Write a counter every X minutes
def write_counter():
    counter = 0
    g="I am Groot"
    while True:
        with open("/data/counter.txt", "a") as f:
            f.write(str(g) + " counter: " + str(counter) + "\n")
            counter += 1
        time.sleep(10)  # every 10 seconds

threading.Thread(target=write_counter, daemon=True).start()

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)