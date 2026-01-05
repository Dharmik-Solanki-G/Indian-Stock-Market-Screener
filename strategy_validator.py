"""
Strategy Validator Module
Validates and sanitizes AI-generated strategy JSON to ensure compatibility with the stock screener.
"""

from typing import Dict, List, Tuple, Optional, Any
import json


# Valid indicator definitions
VALID_INDICATORS = {
    # Price/Volume (no period required)
    "close": {"requires_period": False},
    "open": {"requires_period": False},
    "high": {"requires_period": False},
    "low": {"requires_period": False},
    "volume": {"requires_period": False},
    "volume_turnover": {"requires_period": False},
    
    # Moving Averages (period required)
    "sma": {"requires_period": True, "default_period": 20},
    "ema": {"requires_period": True, "default_period": 20},
    "wma": {"requires_period": True, "default_period": 20},
    "hma": {"requires_period": True, "default_period": 20},
    "vwma": {"requires_period": True, "default_period": 20},
    
    # Momentum (period required)
    "rsi": {"requires_period": True, "default_period": 14},
    "macd": {"requires_period": True, "default_period": 12},
    "macd_signal": {"requires_period": True, "default_period": 9},
    "adx": {"requires_period": True, "default_period": 14},
    
    # Volatility (period required)
    "atr": {"requires_period": True, "default_period": 14},
    "atr_ratio": {"requires_period": True, "default_period": 14},
    "bb_high": {"requires_period": True, "default_period": 20},
    "bb_mid": {"requires_period": True, "default_period": 20},
    "bb_low": {"requires_period": True, "default_period": 20},
    
    # Volume indicators
    "volume_sma": {"requires_period": True, "default_period": 20},
}

VALID_OPERATORS = [">", "<", ">=", "<=", "==", "≈ (approx)"]
VALID_TIMEFRAMES = ["daily", "weekly", "monthly"]


class StrategyValidator:
    """Validates and sanitizes strategy JSON objects."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_strategy(self, strategy: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a complete strategy object.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Check required fields
        if not isinstance(strategy, dict):
            self.errors.append("Strategy must be a JSON object")
            return False, self.errors, self.warnings
        
        # Validate name
        if "name" not in strategy:
            self.errors.append("Missing required field: 'name'")
        elif not isinstance(strategy["name"], str) or not strategy["name"].strip():
            self.errors.append("'name' must be a non-empty string")
        
        # Validate description (optional but recommended)
        if "description" not in strategy:
            self.warnings.append("Missing 'description' field - recommended for clarity")
        
        # Validate conditions
        if "conditions" not in strategy:
            self.errors.append("Missing required field: 'conditions'")
        elif not isinstance(strategy["conditions"], list):
            self.errors.append("'conditions' must be an array")
        elif len(strategy["conditions"]) == 0:
            self.errors.append("'conditions' array cannot be empty")
        else:
            for i, condition in enumerate(strategy["conditions"]):
                cond_valid, cond_error = self.validate_condition(condition, i)
                if not cond_valid:
                    self.errors.append(f"Condition {i+1}: {cond_error}")
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def validate_condition(self, condition: Dict, index: int = 0) -> Tuple[bool, str]:
        """Validate a single condition object."""
        
        if not isinstance(condition, dict):
            return False, "Condition must be an object"
        
        # Check required fields
        if "lhs" not in condition:
            return False, "Missing 'lhs' (left-hand side)"
        if "operator" not in condition:
            return False, "Missing 'operator'"
        if "rhs" not in condition:
            return False, "Missing 'rhs' (right-hand side)"
        
        # Validate operator
        if condition["operator"] not in VALID_OPERATORS:
            return False, f"Invalid operator '{condition['operator']}'. Valid: {VALID_OPERATORS}"
        
        # Validate tolerance for approximate operator
        if condition["operator"] == "≈ (approx)":
            if "tolerance" not in condition:
                self.warnings.append(f"Condition {index+1}: '≈ (approx)' operator without 'tolerance' - defaulting to 1%")
        
        # Validate LHS (must be indicator)
        lhs_valid, lhs_error = self.validate_operand(condition["lhs"], "lhs")
        if not lhs_valid:
            return False, f"LHS error: {lhs_error}"
        
        # Validate RHS (can be indicator or value)
        rhs_valid, rhs_error = self.validate_operand(condition["rhs"], "rhs")
        if not rhs_valid:
            return False, f"RHS error: {rhs_error}"
        
        return True, ""
    
    def validate_operand(self, operand: Dict, side: str) -> Tuple[bool, str]:
        """Validate an operand (LHS or RHS)."""
        
        if not isinstance(operand, dict):
            return False, "Operand must be an object"
        
        if "type" not in operand:
            return False, "Missing 'type' field"
        
        op_type = operand["type"]
        
        if op_type == "value":
            if "value" not in operand:
                return False, "Value type missing 'value' field"
            if not isinstance(operand["value"], (int, float)):
                return False, "'value' must be a number"
            return True, ""
        
        elif op_type == "indicator":
            return self.validate_indicator(operand, side)
        
        else:
            return False, f"Invalid type '{op_type}'. Must be 'indicator' or 'value'"
    
    def validate_indicator(self, indicator: Dict, side: str) -> Tuple[bool, str]:
        """Validate an indicator operand."""
        
        # Check name
        if "name" not in indicator:
            return False, "Missing 'name' field"
        
        name = indicator["name"].lower()
        if name not in VALID_INDICATORS:
            return False, f"Unknown indicator '{name}'. Valid indicators: {list(VALID_INDICATORS.keys())}"
        
        # Check timeframe
        if "timeframe" not in indicator:
            self.warnings.append(f"'{name}' missing 'timeframe' - defaulting to 'daily'")
        elif indicator["timeframe"] not in VALID_TIMEFRAMES:
            return False, f"Invalid timeframe '{indicator['timeframe']}'. Valid: {VALID_TIMEFRAMES}"
        
        # Check offset
        if "offset" in indicator:
            if not isinstance(indicator["offset"], int) or indicator["offset"] < 0:
                return False, "'offset' must be a non-negative integer"
        
        # Check params/period for indicators that require it
        ind_config = VALID_INDICATORS[name]
        if ind_config["requires_period"]:
            params = indicator.get("params", {})
            if "period" not in params:
                self.warnings.append(f"'{name}' missing 'period' - defaulting to {ind_config['default_period']}")
            elif not isinstance(params["period"], int) or params["period"] < 1:
                return False, f"'{name}' period must be a positive integer"
        
        # RHS-only fields validation
        if side == "rhs":
            if "multiplier" in indicator:
                if not isinstance(indicator["multiplier"], (int, float)):
                    return False, "'multiplier' must be a number"
            if "add_offset" in indicator:
                if not isinstance(indicator["add_offset"], (int, float)):
                    return False, "'add_offset' must be a number"
        elif side == "lhs":
            if "multiplier" in indicator:
                self.warnings.append("'multiplier' on LHS will be ignored - only valid for RHS")
            if "add_offset" in indicator:
                self.warnings.append("'add_offset' on LHS will be ignored - only valid for RHS")
        
        return True, ""
    
    def sanitize_strategy(self, strategy: Dict) -> Dict:
        """
        Sanitize and fix common issues in a strategy.
        Returns a corrected copy of the strategy.
        """
        if not isinstance(strategy, dict):
            return {"name": "Invalid Strategy", "description": "", "conditions": []}
        
        sanitized = {
            "name": strategy.get("name", "Unnamed Strategy").strip(),
            "description": strategy.get("description", ""),
            "conditions": []
        }
        
        conditions = strategy.get("conditions", [])
        if not isinstance(conditions, list):
            conditions = []
        
        for condition in conditions:
            if not isinstance(condition, dict):
                continue
            
            sanitized_condition = self._sanitize_condition(condition)
            if sanitized_condition:
                sanitized["conditions"].append(sanitized_condition)
        
        return sanitized
    
    def _sanitize_condition(self, condition: Dict) -> Optional[Dict]:
        """Sanitize a single condition."""
        if "lhs" not in condition or "rhs" not in condition:
            return None
        
        sanitized = {
            "lhs": self._sanitize_operand(condition["lhs"], "lhs"),
            "operator": condition.get("operator", ">"),
            "rhs": self._sanitize_operand(condition["rhs"], "rhs")
        }
        
        if sanitized["lhs"] is None or sanitized["rhs"] is None:
            return None
        
        # Fix operator if invalid
        if sanitized["operator"] not in VALID_OPERATORS:
            sanitized["operator"] = ">"
        
        # Add tolerance for approx operator
        if sanitized["operator"] == "≈ (approx)":
            sanitized["tolerance"] = condition.get("tolerance", 1.0)
        
        return sanitized
    
    def _sanitize_operand(self, operand: Dict, side: str) -> Optional[Dict]:
        """Sanitize an operand."""
        if not isinstance(operand, dict):
            return None
        
        op_type = operand.get("type", "indicator")
        
        if op_type == "value":
            value = operand.get("value", 0)
            if not isinstance(value, (int, float)):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    value = 0
            return {"type": "value", "value": value}
        
        elif op_type == "indicator":
            name = str(operand.get("name", "close")).lower()
            if name not in VALID_INDICATORS:
                name = "close"
            
            sanitized = {
                "type": "indicator",
                "name": name,
                "timeframe": operand.get("timeframe", "daily"),
                "offset": max(0, int(operand.get("offset", 0)))
            }
            
            # Fix timeframe
            if sanitized["timeframe"] not in VALID_TIMEFRAMES:
                sanitized["timeframe"] = "daily"
            
            # Handle params
            ind_config = VALID_INDICATORS[name]
            if ind_config["requires_period"]:
                params = operand.get("params", {})
                period = params.get("period", ind_config["default_period"])
                if not isinstance(period, int) or period < 1:
                    period = ind_config["default_period"]
                sanitized["params"] = {"period": period}
            else:
                sanitized["params"] = {}
            
            # RHS-only fields
            if side == "rhs":
                if "multiplier" in operand:
                    sanitized["multiplier"] = float(operand.get("multiplier", 1.0))
                if "add_offset" in operand:
                    sanitized["add_offset"] = float(operand.get("add_offset", 0.0))
            
            return sanitized
        
        return None
    
    def suggest_fixes(self, errors: List[str]) -> List[str]:
        """Generate fix suggestions for common errors."""
        suggestions = []
        
        for error in errors:
            if "Missing required field: 'name'" in error:
                suggestions.append("Add a 'name' field with a descriptive strategy name")
            elif "Missing required field: 'conditions'" in error:
                suggestions.append("Add a 'conditions' array with at least one condition")
            elif "Unknown indicator" in error:
                suggestions.append(f"Valid indicators: {list(VALID_INDICATORS.keys())}")
            elif "Invalid operator" in error:
                suggestions.append(f"Valid operators: {VALID_OPERATORS}")
            elif "Invalid timeframe" in error:
                suggestions.append(f"Valid timeframes: {VALID_TIMEFRAMES}")
            elif "period must be" in error:
                suggestions.append("Period should be a positive integer like 14, 20, 50, etc.")
        
        return suggestions


def validate_json_string(json_str: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Parse and validate a JSON string as a strategy.
    
    Returns:
        Tuple of (is_valid, parsed_dict_or_none, error_message)
    """
    try:
        # Try to parse JSON
        strategy = json.loads(json_str)
        
        # Validate
        validator = StrategyValidator()
        is_valid, errors, warnings = validator.validate_strategy(strategy)
        
        if is_valid:
            # Sanitize for safety
            sanitized = validator.sanitize_strategy(strategy)
            return True, sanitized, ""
        else:
            error_msg = "; ".join(errors)
            return False, None, error_msg
            
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON: {str(e)}"
    except Exception as e:
        return False, None, f"Validation error: {str(e)}"


# For testing
if __name__ == "__main__":
    test_strategy = {
        "name": "Test Strategy",
        "description": "A test",
        "conditions": [
            {
                "lhs": {"type": "indicator", "name": "rsi", "params": {"period": 14}, "timeframe": "daily", "offset": 0},
                "operator": "<",
                "rhs": {"type": "value", "value": 30}
            }
        ]
    }
    
    validator = StrategyValidator()
    is_valid, errors, warnings = validator.validate_strategy(test_strategy)
    print(f"Valid: {is_valid}")
    print(f"Errors: {errors}")
    print(f"Warnings: {warnings}")
