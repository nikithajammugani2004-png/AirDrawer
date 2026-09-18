import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
@app.route('/ping')
def health():
    return jsonify({"status": "ok", "service": "AirDrawer"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5500))
    app.run(host="0.0.0.0", port=port, debug=False)