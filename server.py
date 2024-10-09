from flask import Flask, request, jsonify, render_template, redirect, url_for
import joblib, os
import pandas as pd
import numpy as np

app = Flask(__name__)

scaler_path = "models/scaler.pkl"
svm = "models/svm.pkl"
lof = "models/lof.pkl"
isof = "models/isof.pkl"
eliptic = "models/elliptic.pkl"


if os.path.exists(svm) and os.path.exists(lof) and os.path.exists(isof) and os.path.exists(eliptic) and os.path.exists(scaler_path):
    svm_model = joblib.load(svm)
    lof_model = joblib.load(lof)
    isof_model = joblib.load(isof)
    elliptic_model = joblib.load(eliptic)
    scaler = joblib.load(scaler_path)
else:
    raise FileNotFoundError("Model or scaler file not found.")

csv_file = 'data/collected_data.csv'
csv_prediction = 'data/predicted_data.csv'
csv_train = 'data/train_data.csv'

if not os.path.exists(csv_file):
    with open(csv_file, 'w') as f:
        f.write('Timestamp,Temperature (°C),Humidity (%),lpg,co,smoke\n')
        
if not os.path.exists(csv_prediction):
    with open(csv_prediction, 'w') as f:
        f.write('Timestamp,Temperature (°C),Humidity (%),lpg,co,smoke,svm,lof,isof,elliptic\n')
        
        
        
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/parameters')
def get_parameters():
    return render_template('parameters.html')

@app.route('/set_params', methods=['POST'])
def set_params():
    model_name = request.json.get('model')
    parameters = request.json.get('parameters')
    
    train_data = pd.read_csv(csv_train)
    data = train_data[['Temperature (°C)', 'Humidity (%)']]

    test_data = pd.read_csv(csv_file)
    last_test_data = test_data.tail(1)
    last_data = last_test_data[['Temperature (°C)', 'Humidity (%)']]

    if model_name and parameters:
        if model_name == 'svm':
            # Set parameters for the One-Class SVM
            svm_model.set_params(**parameters)
            svm_model.fit(data)  # Retrain the SVM model with new data
            new_predictions = svm_model.predict(last_data)
        elif model_name == 'lof':
            # Set parameters for Local Outlier Factor
            lof_model.set_params(**parameters)
            lof_model.fit(data)
            new_predictions = lof_model.predict(last_data)
        elif model_name == 'isof':
            # Set parameters for Isolation Forest
            isof_model.set_params(**parameters)
            isof_model.fit(data)
            new_predictions = isof_model.predict(last_data)
        elif model_name == 'elliptic':
            # Set parameters for Elliptic Envelope
            elliptic_model.set_params(**parameters)
            elliptic_model.fit(data)
            new_predictions = elliptic_model.predict(last_data)
        
        # Send the new predictions back to the frontend
        return jsonify({
            "status": "Parameters updated and model retrained successfully",
            "predictions": new_predictions
        }), 200
    else:
        return jsonify({"error": "Invalid model or parameters"}), 400





@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        return redirect(url_for("user", usr=user))
    else:
        return render_template("index.html")
    
@app.route("/home")
def user(usr):
    return f"<h1>Welcome, {usr}!</h1>"


@app.route('/send_data', methods=['POST'])
def receive_data():
    global csv_file
    data = request.json
    
    # Extract temperature, humidity, and gas data (LPG, CO, Smoke)
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    lpg = data.get('lpg')          
    co = data.get('co')            
    smoke = data.get('smoke')      
    timestamp = data.get('timestamp')
    
    if temperature is not None and humidity is not None and lpg is not None and co is not None and smoke is not None:
        # DataFrame
        new_data = pd.DataFrame({
            'Timestamp': [timestamp],
            'Temperature (°C)': [temperature],
            'Humidity (%)': [humidity],
            'LPG': [lpg],        # Store LPG reading
            'CO': [co],          # Store CO reading
            'Smoke': [smoke]     # Store Smoke reading
        })
        test_data = new_data[['Temperature (°C)', 'Humidity (%)']]

        # Append new data to the CSV file
        new_data.to_csv(csv_file, mode='a', header=False, index=False)

        # Normalize new data and predict anomalies
        new_data_scaled = scaler.transform(test_data)
        svm_prediction = svm_model.predict(new_data_scaled)
        lof_prediction = lof_model.predict(new_data_scaled)
        isof_prediction = isof_model.predict(new_data_scaled)
        elliptic_prediction = elliptic_model.predict(new_data_scaled)

        # Return response
        response = {
            'timestamp': timestamp,
            'temperature': temperature,
            'humidity': humidity,
            'lpg': lpg,          
            'co': co,            
            'smoke': smoke,      
            'svm': int(svm_prediction[0]), 
            'lof': int(lof_prediction[0]),
            'isof': int(isof_prediction[0]),
            'elliptic': int(elliptic_prediction[0])  # 1 for normal, -1 for anomaly
        }
        
        # Log the prediction to a CSV file
        predict = pd.DataFrame({
            'Timestamp': [timestamp],
            'Temperature (°C)': [temperature],
            'Humidity (%)': [humidity],
            'LPG': [lpg],
            'CO': [co],
            'Smoke': [smoke],
            'svm': [int(svm_prediction[0])],
            'lof': [int(lof_prediction[0])],
            'isof': [int(isof_prediction[0])],
            'elliptic': [int(elliptic_prediction[0])]  # 1 for normal, -1 for anomaly
        })

        # Append new prediction data to the CSV file
        predict.to_csv(csv_prediction, mode='a', header=False, index=False)
        
        return jsonify(response), 200
    else:
        return jsonify({"error": "Invalid data received."}), 400


@app.route('/get_data', methods=['GET'])
def send_data():
    # Load historical data for the last n entries
    data_history = pd.read_csv(csv_prediction)
    return jsonify(data_history.tail(10).to_dict(orient='records')), 200

@app.route('/latest_data', methods=['GET'])
def latest_data():
    # Read the latest data from the CSV file
    if os.path.exists(csv_prediction):
        df = pd.read_csv(csv_prediction)
        # Get the latest entry
        latest_entry = df.tail(1).to_dict(orient='records')[0]
        return jsonify(latest_entry), 200
    else:
        return jsonify({"error": "No data available."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)