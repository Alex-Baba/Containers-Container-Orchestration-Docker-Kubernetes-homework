from flask import Flask

# Create the Flask application
app = Flask(__name__)

# Define a route for the homepage
@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/health")
def health():
    return "OK", 200

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)