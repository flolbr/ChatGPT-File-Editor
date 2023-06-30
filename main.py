import os
import sys

import quart
import quart_cors

from routes import projects_routes, api_routes, dashboard_routes

os.system('')  # Needed to enable VT100 support
sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=32, cols=999))

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# set env to development
app.config["ENV"] = "development"

# Register routes
app.register_blueprint(projects_routes)
app.register_blueprint(api_routes)
app.register_blueprint(dashboard_routes)


def main():
    """
    Main function to start the application.
    The application will be run in debug mode and will listen on all interfaces at port 5003.
    """
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()
