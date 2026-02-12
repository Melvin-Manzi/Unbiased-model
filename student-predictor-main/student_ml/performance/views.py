from django.shortcuts import render

# Create your views here.
from django.conf import settings
from pathlib import Path
import joblib
import numpy as np
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PredictionRecord

_model = None


def _get_model_path() -> Path:
    return Path(settings.BASE_DIR) / 'performance' / 'model.pkl'


def _get_model():
    global _model
    if _model is None:
        _model = joblib.load(_get_model_path())
    return _model


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        raise ValueError('extracurricular is required')
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {'true', '1', 'yes', 'y'}:
            return True
        if v in {'false', '0', 'no', 'n'}:
            return False
    raise ValueError('extracurricular must be a boolean (true/false)')


def _validate_inputs(hours_studied, previous_scores, extracurricular, sleep_hours, sample_papers):
    errors = {}

    if hours_studied < 0:
        errors['hours_studied'] = 'Must be 0 or more.'
    elif hours_studied > 18:
        errors['hours_studied'] = 'Unrealistic. Please enter 0–18 hours.'

    if previous_scores < 0 or previous_scores > 100:
        errors['previous_scores'] = 'Must be between 0 and 100.'

    if sleep_hours < 0:
        errors['sleep_hours'] = 'Must be 0 or more.'
    elif sleep_hours > 16:
        errors['sleep_hours'] = 'Unrealistic. Please enter 0–16 hours.'

    if sample_papers < 0:
        errors['sample_papers'] = 'Must be 0 or more.'
    elif sample_papers > 50:
        errors['sample_papers'] = 'Unrealistic. Please enter 0–50.'

    if not isinstance(extracurricular, bool):
        errors['extracurricular'] = 'Must be true/false.'

    return errors


def _make_advice(hours_studied, previous_scores, extracurricular, sleep_hours, sample_papers):
    advice = []

    if sleep_hours < 6:
        advice.append('Your sleep looks low. Try to aim for 7–9 hours for better learning and focus.')
    elif sleep_hours > 10:
        advice.append('Your sleep looks very high. If this is frequent, consider balancing sleep with daytime activity and study.')

    if hours_studied == 0:
        advice.append('You entered 0 study hours. Even small daily study sessions can improve performance over time.')
    elif hours_studied > 10:
        advice.append('You study a lot. Make sure to take breaks and avoid burnout (short breaks improve retention).')

    if previous_scores < 40:
        advice.append('Previous scores are low. Consider reviewing fundamentals and practicing with past questions regularly.')
    elif previous_scores > 85:
        advice.append('Great previous scores. Keep consistency and focus on weaker topics to maintain results.')

    if sample_papers == 0:
        advice.append('Try practicing sample/past papers—this helps with exam technique and time management.')

    if extracurricular:
        advice.append('Extracurricular activities can be healthy—just keep a good balance with study and rest.')

    return advice


def _make_warnings(hours_studied, previous_scores, extracurricular, sleep_hours, sample_papers):
    warnings = []

    if sleep_hours < 5:
        warnings.append('Very low sleep (<5h) can seriously reduce focus and memory. Consider prioritizing rest before increasing study load.')
    if hours_studied > 12:
        warnings.append('Very high study hours (>12h) may lead to burnout. Consider shorter focused sessions with breaks.')
    if hours_studied > 10 and sleep_hours < 6:
        warnings.append('High study + low sleep is an unhealthy combination. Try balancing study and sleep for sustainable performance.')
    if previous_scores > 90 and hours_studied == 0:
        warnings.append('High previous scores with 0 study hours is unusual. Double-check inputs if this is not accurate.')
    if sample_papers > 30:
        warnings.append('Very high number of sample papers. Ensure you also review mistakes and concepts, not only repetition.')
    if not extracurricular and hours_studied > 10:
        warnings.append('No extracurricular + very high study load. Consider adding some physical activity or breaks for overall wellbeing.')

    return warnings


def _field_constraints():
    return {
        'hours_studied': {
            'min': 0,
            'max': 18,
            'guide': 'Hours studied per day (0–18).',
        },
        'previous_scores': {
            'min': 0,
            'max': 100,
            'guide': 'Previous score percentage (0–100).',
        },
        'extracurricular': {
            'type': 'boolean',
            'guide': 'Extracurricular participation (true/false).',
        },
        'sleep_hours': {
            'min': 0,
            'max': 16,
            'guide': 'Sleep hours per day (0–16).',
        },
        'sample_papers': {
            'min': 0,
            'max': 50,
            'guide': 'Number of sample papers practiced (0–50).',
        },
    }


@api_view(['POST'])
def predict_performance(request):
    model_path = _get_model_path()
    if not model_path.exists():
        return Response(
            {
                'error': 'Model file not found',
                'expected_path': str(model_path),
            },
            status=500,
        )

    data = request.data or {}
    required_fields = [
        'hours_studied',
        'previous_scores',
        'extracurricular',
        'sleep_hours',
        'sample_papers',
    ]
    missing = [k for k in required_fields if k not in data]
    if missing:
        return Response(
            {
                'error': 'Missing required fields',
                'missing_fields': missing,
                'constraints': _field_constraints(),
                'expected_json_example': {
                    'hours_studied': 6,
                    'previous_scores': 70,
                    'extracurricular': True,
                    'sleep_hours': 7,
                    'sample_papers': 4,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        hours_studied = int(data.get('hours_studied'))
        previous_scores = int(data.get('previous_scores'))
        extracurricular = _parse_bool(data.get('extracurricular'))
        sleep_hours = int(data.get('sleep_hours'))
        sample_papers = int(data.get('sample_papers'))
    except Exception as e:
        return Response(
            {
                'error': 'Invalid input types',
                'details': str(e),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    errors = _validate_inputs(hours_studied, previous_scores, extracurricular, sleep_hours, sample_papers)
    if errors:
        return Response(
            {
                'error': 'Invalid input values',
                'field_errors': errors,
                'constraints': _field_constraints(),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    features = np.array([[
        hours_studied,
        previous_scores,
        1 if extracurricular else 0,
        sleep_hours,
        sample_papers,
    ]])
    prediction = _get_model().predict(features)[0]
    advice = _make_advice(hours_studied, previous_scores, extracurricular, sleep_hours, sample_papers)
    warnings = _make_warnings(hours_studied, previous_scores, extracurricular, sleep_hours, sample_papers)

    predicted = round(float(prediction), 2)

    PredictionRecord.objects.create(
        hours_studied=hours_studied,
        previous_scores=previous_scores,
        extracurricular=extracurricular,
        sleep_hours=sleep_hours,
        sample_papers=sample_papers,
        predicted_performance_index=predicted,
        advice=advice,
        warnings=warnings,
    )

    return Response({
        'predicted_performance_index': predicted,
        'advice': advice,
        'warnings': warnings,
    })


@api_view(['GET'])
def prediction_history(request):
    records = PredictionRecord.objects.order_by('-created_at')[:10]
    data = []
    for r in records:
        data.append(
            {
                'id': r.id,
                'created_at': r.created_at.isoformat(),
                'hours_studied': r.hours_studied,
                'previous_scores': r.previous_scores,
                'extracurricular': r.extracurricular,
                'sleep_hours': r.sleep_hours,
                'sample_papers': r.sample_papers,
                'predicted_performance_index': r.predicted_performance_index,
                'advice': r.advice,
                'warnings': r.warnings,
            }
        )

    return Response({'results': data})


def predict_ui(request):
    context = {
        'form': {},
        'predicted_performance_index': None,
        'error': None,
    }

    if request.method == 'POST':
        form = {
            'hours_studied': request.POST.get('hours_studied', ''),
            'previous_scores': request.POST.get('previous_scores', ''),
            'extracurricular': request.POST.get('extracurricular', 'false'),
            'sleep_hours': request.POST.get('sleep_hours', ''),
            'sample_papers': request.POST.get('sample_papers', ''),
        }
        context['form'] = form

        model_path = _get_model_path()
        if not model_path.exists():
            context['error'] = f"Model file not found at: {model_path}"
            return render(request, 'performance/predict_ui.html', context)

        try:
            features = np.array([[
                int(form['hours_studied']),
                int(form['previous_scores']),
                1 if form['extracurricular'] == 'true' else 0,
                int(form['sleep_hours']),
                int(form['sample_papers']),
            ]])
            prediction = _get_model().predict(features)[0]
            context['predicted_performance_index'] = round(float(prediction), 2)
        except Exception as e:
            context['error'] = str(e)

    return render(request, 'performance/predict_ui.html', context)