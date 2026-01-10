from flask import Flask, send_file, jsonify
import subprocess
import os

app = Flask(__name__)

IMAGE_PATH = "/data/data/com.termux/files/home/latest.jpg"

@app.route('/snap')
def snap():
    try:
        # Delete previous image to ensure we don't send an old one if the camera fails
        if os.path.exists(IMAGE_PATH):
            os.remove(IMAGE_PATH)

        # Take photo using subprocess (safer than os.system)
        # capture_output=True allows us to see error messages from Termux if needed
        result = subprocess.run(
            ["termux-camera-photo", "-c", "0", IMAGE_PATH],
            capture_output=True,
            text=True
        )

        # Check if the command was successful
        if result.returncode != 0:
            return jsonify({"error": "Camera command failed", "details": result.stderr}), 500

        # Check if file was actually created
        if not os.path.exists(IMAGE_PATH):
            return jsonify({"error": "File was not created"}), 500

        # Return the file
        return send_file(IMAGE_PATH, mimetype='image/jpeg')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)