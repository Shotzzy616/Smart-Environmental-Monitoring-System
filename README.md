```markdown
# Smart Environmental Monitoring System

This project is a Smart Environmental Monitoring System that uses various sensors to collect environmental data and employs machine learning models for anomaly detection. The data is visualized in real-time through a web interface, providing users with insights into environmental conditions.

## Features

- **Real-Time Data Collection:** Uses ESP32S3 to gather temperature, humidity, and air quality data (LPG, CO, smoke).
- **Machine Learning Models:** Implements multiple anomaly detection models, including:
  - One-Class SVM
  - Local Outlier Factor
  - Isolation Forest
  - Elliptic Envelope
- **Web Interface:** A responsive website displays real-time data and predictions, allowing users to interact with the models and visualize data trends.
- **Model Parameters Adjustment:** Users can modify model parameters and see updated predictions in real-time.
- **Graphical Data Visualization:** Displays graphs for temperature, humidity, and gas readings, allowing for better data analysis.

## Technologies Used

- **Hardware:**
  - ESP32S3
  - DHT11 Temperature and Humidity Sensor
  - MQ-2 Gas Sensor (for LPG, CO, smoke detection)
  - Raspberry Pi

- **Software:**
  - Flask (Python) for the backend server
  - JavaScript, HTML, CSS for the frontend
  - Machine Learning Libraries: Scikit-learn for model implementations
  - Chart.js for graphing library

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- Scikit-learn
- Required libraries for the ESP32S3 (e.g., Arduino IDE)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Shotzzy616/smart-environmental-monitoring-system.git
   cd smart-environmental-monitoring-system
   ```

2. Install required Python packages:
   ```bash
   pip install Flask scikit-learn
   ```

3. Set up your ESP32S3 with the DHT11 and MQ-2 sensors, ensuring proper wiring and connections.

4. Run the Flask server:
   ```bash
   python app.py
   ```

5. Open your web browser and navigate to `http://localhost:5000` to view the web interface.

## Usage

- On the home page, view real-time temperature, humidity, and gas readings.
- Click the "Edit Model Parameters" button to adjust model parameters and see real-time predictions.
- Graphs will display trends in temperature, humidity, and gas data.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
