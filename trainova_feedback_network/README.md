# Trainova Feedback Network

## Overview
The Trainova Feedback Network is a machine learning project designed to predict weight lifting performance based on previous workout data. It utilizes feedback mechanisms to improve prediction accuracy over time. The project is structured into several modules, each responsible for specific functionalities, making it modular and maintainable.

## Project Structure
```
trainova_feedback_network
├── src
│   ├── __init__.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── feedback_prediction_model.py
│   │   ├── lstm_model.py
│   │   └── base_model.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── weight_calculation.py
│   │   ├── rep_utils.py
│   │   └── feedback_utils.py
│   ├── features
│   │   ├── __init__.py
│   │   ├── feature_engineering.py
│   │   └── trend_analysis.py
│   └── prediction
│       ├── __init__.py
│       ├── predictor.py
│       └── feedback_processor.py
├── tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_prediction.py
├── README.md
├── setup.py
└── requirements.txt
```

## Installation
To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd trainova_feedback_network
pip install -r requirements.txt
```

## Docker Deployment
The project can be easily deployed using Docker:

```bash
docker-compose up -d
```

This will start the API service on port 5009. You can access the API at http://localhost:5009 or http://<server-ip>:5009 if deployed on a remote server.

## Usage
The main functionalities of the project include:

- **Weight Prediction**: Utilize the `Predictor` class to make predictions based on previous workouts.
- **Feedback Processing**: Use the `FeedbackProcessor` class to provide feedback on predictions and adjust weights accordingly.
- **Feature Engineering**: Enhance model performance by creating new features from existing data using the functions in `feature_engineering.py`.

## API Endpoints
The following endpoints are available when running the API server:

- `GET /`: Welcome message and API information
- `GET /health`: Health check endpoint
- `POST /predict`: Get weight prediction based on workout history
- `POST /feedback`: Provide feedback on a prediction

## Testing
Unit tests are provided to ensure the functionality of the models and utilities. To run the tests, use:

```bash
pytest tests/
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.