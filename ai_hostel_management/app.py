import os

from app import create_app

# This file used to contain legacy raw‑SQL routes and a separate MySQL connection.
# The project now uses the flask application factory (`run.py`) and blueprints.
# Running this script directly used to cause errors such as "Unknown column 'password'"
# because the **users** table no longer has a plain `password` field.
#
# To start the application use:
#
#     python run.py
#
# or
#     flask --app run.py run
#
# The code below simply delegates to the factory for backwards compatibility.

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(debug=True)

