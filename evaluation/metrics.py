# ============================================================
# EVALUATION MODULE — metrics.py
# Generates a labeled synthetic test set and scores each AI
# module (and the combined agent) against ground truth:
# Accuracy, Precision, Recall, F1, Confusion Matrix.
# ============================================================

import random
from typing import Dict, List, Tuple

import numpy as np
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report,)

from ai_engine.modules.agent import PatientPercept

DISEASE_LABELS = [
    'flu', 'covid19', 'dengue', 'cardiac_event',
    'diabetes', 'common_cold', 'tuberculosis', 'meningitis',
]

# Symptom + vitals profile per disease, used to generate realistic
# synthetic ground-truth patients (same spirit as ml_classifier's
# synthetic data, but independent so evaluation/ has no hidden
# coupling to internals of any one module).
_PROFILES = {
    'flu': {
        'symptoms': {'fever': 0.90, 'cough': 0.85, 'fatigue': 0.88,
                      'headache': 0.70, 'body aches': 0.80},
        'temp': (37.8, 39.5), 'hr': (85, 105),
    },
    'covid19': {
        'symptoms': {'fever': 0.88, 'cough': 0.80, 'fatigue': 0.90,
                      'loss of smell': 0.85, 'headache': 0.65},
        'temp': (37.5, 39.2), 'hr': (85, 110),
    },
    'dengue': {
        'symptoms': {'fever': 0.98, 'rash': 0.75, 'joint pain': 0.85,
                      'headache': 0.90, 'fatigue': 0.80},
        'temp': (38.5, 40.0), 'hr': (90, 115),
    },
    'cardiac_event': {
        'symptoms': {'chest pain': 0.92, 'shortness of breath': 0.88,
                      'fatigue': 0.70, 'sweating': 0.75},
        'temp': (36.8, 37.5), 'hr': (105, 135),
    },
    'diabetes': {
        'symptoms': {'fatigue': 0.82, 'frequent urination': 0.95,
                      'excessive thirst': 0.92, 'blurred vision': 0.70},
        'temp': (36.5, 37.2), 'hr': (70, 95),
    },
    'common_cold': {
        'symptoms': {'cough': 0.90, 'fever': 0.50, 'headache': 0.60,
                      'fatigue': 0.55},
        'temp': (36.8, 38.0), 'hr': (70, 90),
    },
    'tuberculosis': {
        'symptoms': {'cough': 0.95, 'weight loss': 0.85,
                      'night sweats': 0.80, 'fatigue': 0.88, 'fever': 0.70},
        'temp': (37.2, 38.5), 'hr': (80, 100),
    },
    'meningitis': {
        'symptoms': {'headache': 0.95, 'stiff neck': 0.90, 'fever': 0.92,
                      'light sensitivity': 0.85, 'fatigue': 0.80},
        'temp': (38.8, 40.5), 'hr': (95, 125),
    },
}


def generate_labeled_patients(n_per_class: int = 15, seed: int = 123
                               ) -> List[Tuple[PatientPercept, str]]:
    """Generate a synthetic test set with known ground-truth diagnoses.

    Returns a list of (PatientPercept, true_label) tuples.
    """
    rng = random.Random(seed)
    cases = []

    for disease, profile in _PROFILES.items():
        for i in range(n_per_class):
            symptoms = [s for s, p in profile['symptoms'].items() if rng.random() < p]
            if not symptoms:
                symptoms = [rng.choice(list(profile['symptoms'].keys()))]

            temp = round(rng.uniform(*profile['temp']), 1)
            hr = rng.randint(*profile['hr'])
            age = rng.randint(18, 75)
            bp = f"{rng.randint(105, 150)}/{rng.randint(65, 95)}"

            percept = PatientPercept(
                patient_id=f"EVAL-{disease}-{i}",
                symptoms=symptoms,
                age=age,
                temperature=temp,
                heart_rate=hr,
                blood_pressure=bp,
            )
            cases.append((percept, disease))

    rng.shuffle(cases)
    return cases


def normalize_label(label: str) -> str:
    """Different modules emit diagnoses in different formats
    (e.g. 'covid19_suspected', 'myocardial_infarction'). Normalize
    to the canonical DISEASE_LABELS so accuracy can be computed fairly.
    """
    if not label:
        return 'unknown'
    normalized = label.lower().strip().replace(' ', '_')
    for suffix in ('_suspected', '_confirmed'):
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]
    alias_map = {'myocardial_infarction': 'cardiac_event'}
    normalized = alias_map.get(normalized, normalized)
    return normalized if normalized in DISEASE_LABELS else 'unknown'


def evaluate_module(module, test_set: List[Tuple[PatientPercept, str]]) -> Dict:
    """Run one module's .analyze() against the test set and score it."""
    y_true, y_pred = [], []

    for percept, true_label in test_set:
        result = module.analyze(percept)
        predicted = normalize_label(result.get('diagnosis', ''))
        y_true.append(true_label)
        y_pred.append(predicted)

    labels = DISEASE_LABELS + ['unknown']
    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=DISEASE_LABELS, average='macro', zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    report = classification_report(
        y_true, y_pred, labels=DISEASE_LABELS, zero_division=0
    )

    return {
        'accuracy': acc,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm,
        'labels': labels,
        'classification_report': report,
        'y_true': y_true,
        'y_pred': y_pred,
    }


def evaluate_agent(agent, test_set: List[Tuple[PatientPercept, str]]) -> Dict:
    """Evaluate the full agent's *combined* diagnosis (all modules
    aggregated together) against ground truth."""
    y_true, y_pred = [], []

    for percept, true_label in test_set:
        report = agent.run(percept)
        predicted = normalize_label(report.get('diagnosis', ''))
        y_true.append(true_label)
        y_pred.append(predicted)

    labels = DISEASE_LABELS + ['unknown']
    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=DISEASE_LABELS, average='macro', zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    return {
        'accuracy': acc,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm,
        'labels': labels,
        'y_true': y_true,
        'y_pred': y_pred,
    }
