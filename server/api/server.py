"""
Main module of the server file
"""

import connexion

from flask import redirect
from flask import render_template
from flask_cors import CORS



# create the application instance
app = connexion.App(__name__, specification_dir="./")

# Cead the swagger.yml file to configure the endpoints
app.add_api("swagger.yml")

CORS(app.app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Create a URL route in our application for "/"
@app.route("/")
def home():
    """
    This function just responds to the browser URL
    localhost:5000/

    :return:        the rendered templates "home.html"
    """
    return redirect("/api/ui", code=302)



if __name__ == "__main__":
    try:
        app.run(debug=True, threaded=False)
    except KeyboardInterrupt:
        pass