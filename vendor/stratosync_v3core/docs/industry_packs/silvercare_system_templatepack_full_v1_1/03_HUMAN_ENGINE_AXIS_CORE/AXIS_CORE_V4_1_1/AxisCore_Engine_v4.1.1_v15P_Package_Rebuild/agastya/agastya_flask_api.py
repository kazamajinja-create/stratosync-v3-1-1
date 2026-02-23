
# agastya_flask_api.py

from flask import Flask, request, jsonify, send_file
import os
from pdf_generator import generate_pdf_from_json
from line_json_generator import generate_line_json

app = Flask(__name__)

@app.route("/generate_pdf", methods=["POST"])
def pdf():
    content = request.get_json()
    with open("temp_data.json", "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False)
    generate_pdf_from_json("temp_data.json", "output.pdf")
    return send_file("output.pdf", as_attachment=True)

@app.route("/generate_line_json", methods=["POST"])
def line_json():
    content = request.get_json()
    with open("temp_data.json", "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False)
    generate_line_json("temp_data.json", "output_line.json")
    return send_file("output_line.json", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
