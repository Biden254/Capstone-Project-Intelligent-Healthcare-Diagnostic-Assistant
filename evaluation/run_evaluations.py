# ============================================================
# EVALUATION MODULE — run_evaluation.py
# Run this from the project root:  python evaluation/run_evaluation.py
#
# Builds the AI system, generates a labeled synthetic test set,
# scores every module (+ the combined agent) against ground truth,
# prints a summary table, and saves confusion matrices + a module
# comparison bar chart to evaluation/output/.
# ============================================================

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Make sure ai_engine/ (a sibling of evaluation/) is importable
# regardless of where this script is invoked from.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ai_engine.modules.agent import HealthcareDiagnosticAgent
from ai_engine.modules.knowledge_base import MedicalKnowledgeBase
from ai_engine.modules.bayesian_net import SimpleBayesianDiagnostics
from ai_engine.modules.ml_classifier import MLDiagnosticClassifier
from ai_engine.modules.fuzzy_controller import FuzzySeverityAssessor
from ai_engine.modules.planner import TreatmentPlanner

try:
    from ai_engine.modules.neural_network import NeuralDiagnosticModel
    NN_AVAILABLE = True
except ImportError as e:
    NeuralDiagnosticModel = None
    NN_AVAILABLE = False
    print(f"NOTE: skipping NeuralNetwork evaluation — TensorFlow not installed ({e})")

from evaluation.metrics import generate_labeled_patients, evaluate_module, evaluate_agent
from evaluation.visualizations import (
    plot_confusion_matrix, plot_module_comparison, print_summary_table
)


def build_system():
    agent = HealthcareDiagnosticAgent()
    modules = {
        'KnowledgeBase': MedicalKnowledgeBase(),
        'BayesianNet': SimpleBayesianDiagnostics(),
        'MLClassifier': MLDiagnosticClassifier(),
    }
    if NN_AVAILABLE:
        modules['NeuralNetwork'] = NeuralDiagnosticModel()

    for name, module in modules.items():
        agent.register_module(name, module)
    # Fuzzy is diagnostic-irrelevant for accuracy scoring (it outputs
    # severity, not a disease label) — still register it so the agent's
    # combined report matches production behavior.
    agent.register_module('Fuzzy', FuzzySeverityAssessor())

    ml = agent._modules['MLClassifier']
    ml.train(verbose=False)

    if NN_AVAILABLE:
        nn = agent._modules['NeuralNetwork']
        nn.train(epochs=30, verbose=0)

    return agent, modules


def main():
    print("=" * 60)
    print("  AI System Evaluation")
    print("=" * 60)

    print("\nBuilding + training system...")
    agent, modules = build_system()

    print("Generating labeled synthetic test set...")
    test_set = generate_labeled_patients(n_per_class=15)
    print(f"  {len(test_set)} labeled patients across {len(set(l for _, l in test_set))} diseases")

    results_by_module = {}

    print("\nEvaluating individual modules...")
    for name, module in modules.items():
        if not hasattr(module, 'analyze'):
            continue
        print(f"  Scoring {name}...")
        result = evaluate_module(module, test_set)
        results_by_module[name] = result
        plot_confusion_matrix(name, result)

    print("  Scoring Agent (combined)...")
    agent_result = evaluate_agent(agent, test_set)
    results_by_module['Agent (combined)'] = agent_result
    plot_confusion_matrix('Agent (combined)', agent_result)

    print_summary_table(results_by_module)

    print("\nGenerating module comparison chart...")
    plot_module_comparison(results_by_module)

    print("\n" + "=" * 60)
    print("  Evaluation complete. See evaluation/output/ for plots.")
    print("=" * 60)

    return results_by_module


if __name__ == "__main__":
    main()
