from flask import Flask, send_from_directory
from routes.api import api_blueprint
import os

app = Flask(__name__, static_folder='static/build')

app.register_blueprint(api_blueprint, url_prefix='/api')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)