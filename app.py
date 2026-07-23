# ============================================================
# CAPSTONE MAIN APPLICATION
# Intelligent Healthcare Diagnostic Assistant
# Introduction to AI — 13-Week Capstone
# ============================================================

import warnings
from modules.knowledge_base import MedicalKnowledgeBase
from modules.bayesian_net import SimpleBayesianDiagnostics
from modules.ml_classifier import MLDiagnosticClassifier
from modules.neural_network import NeuralDiagnosticModel
from modules.agent import HealthcareDiagnosticAgent

warnings.filterwarnings('ignore')

# ── ANSI Colors ────────────────────────────────────────────


class C:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def banner():
    print(f"""
{C.BOLD}{C.BLUE}
╔══════════════════════════════════════════════════════════╗
║        🏥 INTELLIGENT HEALTHCARE DIAGNOSTIC AI           ║
║         Introduction to AI — Capstone Project            ║
║  Modules: Agents | Logic | Bayes | ML | DNN | Fuzzy      ║
╚══════════════════════════════════════════════════════════╝
{C.END}""")


def section(title: str):
    print(f"\n{C.BOLD}{C.YELLOW}{'═' * 60}{C.END}")
    print(f"{C.BOLD}{C.YELLOW}  {title}{C.END}")
    print(f"{C.BOLD}{C.YELLOW}{'═' * 60}{C.END}")


def build_system() -> HealthcareDiagnosticAgent:
    """Instantiate and wire all AI modules"""
    section("🔧 Building AI System — Registering Modules")

    agent = HealthcareDiagnosticAgent()

    print("\n  Initializing modules...")
    agent.register_module('KnowledgeBase', MedicalKnowledgeBase())
    agent.register_module('BayesianNet', SimpleBayesianDiagnostics())
    agent.register_module('MLClassifier', MLDiagnosticClassifier())
    agent.register_module('NeuralNetwork', NeuralDiagnosticModel())

    return agent
