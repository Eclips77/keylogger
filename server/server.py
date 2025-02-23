from flask import Flask, request, jsonify

app = Flask(__name__)

# Endpoint לקבלת הלוגים
@app.route('/logs', methods=['POST'])
def receive_logs():
    data = request.data  # הנתונים המוצפנים שמגיעים מהקליגר
    # כאן תוכל לבצע פענוח, שמירה או עיבוד אחר של הנתונים
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
