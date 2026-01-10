"""
ABAC service for attribute-based access control.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ABACService:
    """Service for ABAC evaluation."""
    
    def __init__(self):
        """Initialize ABAC service."""
        pass
    
    def evaluate_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Evaluate ABAC conditions against context.
        
        Args:
            conditions: Policy conditions
            context: Request context attributes
            
        Returns:
            Tuple of (matches, reason_codes)
        """
        if not conditions:
            return True, []
        
        reason_codes = []
        
        for key, expected_value in conditions.items():
            actual_value = context.get(key)
            
            # Special handling for different condition types
            if isinstance(expected_value, dict):
                # Complex condition evaluation
                if not self._evaluate_complex_condition(key, expected_value, actual_value):
                    return False, [f"ABAC_CONDITION_FAILED_{key.upper()}"]
                reason_codes.append(f"ABAC_CONDITION_PASSED_{key.upper()}")
            else:
                # Simple equality check
                if actual_value != expected_value:
                    return False, [f"ABAC_CONDITION_FAILED_{key.upper()}"]
                reason_codes.append(f"ABAC_CONDITION_PASSED_{key.upper()}")
        
        return True, reason_codes or ["ABAC_MATCH"]
    
    def _evaluate_complex_condition(self, key: str, condition: Dict[str, Any], value: Any) -> bool:
        """Evaluate complex condition with operators.
        
        Args:
            key: Condition key
            condition: Condition specification with operators
            value: Actual value to evaluate
            
        Returns:
            True if condition matches, False otherwise
        """
        # Support operators: eq, ne, gt, gte, lt, lte, in, not_in, contains
        operator = condition.get("operator", "eq")
        expected = condition.get("value")
        
        if value is None:
            return operator == "null" or (operator == "eq" and expected is None)
        
        try:
            if operator == "eq":
                return value == expected
            elif operator == "ne":
                return value != expected
            elif operator == "gt":
                return value > expected
            elif operator == "gte":
                return value >= expected
            elif operator == "lt":
                return value < expected
            elif operator == "lte":
                return value <= expected
            elif operator == "in":
                return value in expected if isinstance(expected, (list, set)) else False
            elif operator == "not_in":
                return value not in expected if isinstance(expected, (list, set)) else True
            elif operator == "contains":
                return expected in value if isinstance(value, (str, list, set)) else False
            elif operator == "regex":
                import re
                return bool(re.match(expected, str(value)))
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
        except Exception as e:
            logger.error(f"Error evaluating complex condition: {e}")
            return False


# Global service instance
_service: Optional[ABACService] = None


def get_abac_service() -> ABACService:
    """Get global ABAC service instance."""
    global _service
    if _service is None:
        _service = ABACService()
    return _service
