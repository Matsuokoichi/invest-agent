from .contract import RequiredContractEvaluator
from .decision import DecisionPolicyEvaluator
from .numeric import ReturnArithmeticEvaluator, ScenarioIntegrityEvaluator
from .schema import ReportSchemaEvaluator

EVALUATOR_REGISTRY = {
    "C001": ReportSchemaEvaluator,
    "C002": RequiredContractEvaluator,
    "N001": ReturnArithmeticEvaluator,
    "N003": ScenarioIntegrityEvaluator,
    "D001": DecisionPolicyEvaluator,
}

__all__ = ["EVALUATOR_REGISTRY"]
