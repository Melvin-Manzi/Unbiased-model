# Student's Performance_Prediction_Unbiased Model__ML-predictor-

A Django + Django REST Framework student performance predictor.

## Features
- `/ui/` HTML form to enter student inputs and get a predicted performance index.
- `/api/predict/` JSON API endpoint (POST).
- Input validation (reasonable ranges) + human-friendly advice.

## Run locally (Windows)

### 1) Create & activate venv

```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install "django<5" djangorestframework joblib numpy pandas scikit-learn
```

### 3) Run migrations

```powershell
python .\student_ml\manage.py migrate
```

### 4) Train model (creates `student_ml/performance/model.pkl`)

Place `Student_Performance.csv` in the project root, then:

```powershell
python .\student_ml\performance\train_model.py
```

### 5) Start server

```powershell
python .\student_ml\manage.py runserver
```

Open:
- UI: http://127.0.0.1:8000/ui/
- API: http://127.0.0.1:8000/api/predict/

## API Example

`POST /api/predict/`

```json
{
  "hours_studied": 8,
  "previous_scores": 90,
  "extracurricular": true,
  "sleep_hours": 8,
  "sample_papers": 6
}
```
