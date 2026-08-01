# ============================================================
# Bridge between Django and the ai_engine package.
# Builds the agent + trains the learning modules once (lazily,
# on first use) and hands back the same instance every call.
# ============================================================

from ai_engine.modules.agent import HealthcareDiagnosticAgent
from ai_engine.modules.knowledge_base import MedicalKnowledgeBase
from ai_engine.modules.bayesian_net import SimpleBayesianDiagnostics
from ai_engine.modules.ml_classifier import MLDiagnosticClassifier
from ai_engine.modules.fuzzy_controller import FuzzySeverityAssessor
from ai_engine.modules.planner import TreatmentPlanner

try:
    from ai_engine.modules.neural_network import NeuralDiagnosticModel
    NN_AVAILABLE = True
    NN_IMPORT_ERROR = None
except ImportError as e:
    NeuralDiagnosticModel = None
    NN_AVAILABLE = False
    NN_IMPORT_ERROR = str(e)

_agent = None
_planner = None
_status = {"modules": [], "nn_available": NN_AVAILABLE, "nn_error": NN_IMPORT_ERROR}


def get_system():
    """Build + train the system on first call; reuse it after that."""
    global _agent, _planner

    if _agent is not None:
        return _agent, _planner

    agent = HealthcareDiagnosticAgent()
    modules = {
        'KnowledgeBase': MedicalKnowledgeBase(),
        'BayesianNet':   SimpleBayesianDiagnostics(),
        'MLClassifier':  MLDiagnosticClassifier(),
        'Fuzzy':         FuzzySeverityAssessor(),
    }
    if NN_AVAILABLE:
        modules['NeuralNetwork'] = NeuralDiagnosticModel()

    for name, module in modules.items():
        agent.register_module(name, module)

    ml = agent._modules.get('MLClassifier')
    if ml is not None:
        ml.train(verbose=False)

    nn = agent._modules.get('NeuralNetwork')
    if nn is not None:
        nn.train(epochs=30, verbose=0)

    _status["modules"] = list(modules.keys())
    _agent = agent
    _planner = TreatmentPlanner()
    return _agent, _planner


def get_status():
    return dict(_status, ready=_agent is not None)
