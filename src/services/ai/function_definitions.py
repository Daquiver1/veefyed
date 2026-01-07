"""AI Function Definitions for QuiverFood Agent - Decorator-Based Approach"""

import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, get_type_hints

from src.decorators.ai import AIFunctionRegistry
from src.models.conversation import FunctionDefinition, create_function_definition
from src.models.intent_classification import IntentType

app_logger = logging.getLogger("app")


class AIFunctionDefinitions:
    """Centralized function definitions for AI services - Auto-generated from decorators"""

    def __init__(self):
        """Initialize function definitions from registry"""
        self.definitions = self._build_definitions_from_registry()

    def _build_definitions_from_registry(self) -> Dict[str, FunctionDefinition]:
        """Build all function definitions from the decorator registry"""
        definitions = {}

        for function_name, func_info in AIFunctionRegistry._functions.items():
            definition = self._create_definition_from_func_info(
                function_name, func_info
            )
            definitions[function_name] = definition

        return definitions

    def _create_definition_from_func_info(
        self, function_name: str, func_info: Dict[str, Any]
    ) -> FunctionDefinition:
        """Create a FunctionDefinition from registry function info"""
        func = func_info["func"]
        signature = func_info["signature"]
        description = func_info["description"] or self._generate_description_from_name(
            function_name
        )

        # Extract parameters from function signature
        parameters = {}
        required = []

        for param_name, param in signature.parameters.items():
            # Skip 'self' parameter for bound methods
            if param_name == "self":
                continue

            param_info = self._extract_parameter_info(param_name, param, func)
            parameters[param_name] = param_info

            # Add to required if no default value
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        # Add validation constraints from docstring if present
        enhanced_description = self._enhance_description_with_constraints(
            func, description
        )

        return create_function_definition(
            name=function_name,
            description=enhanced_description,
            parameters=parameters,
            required=required,
        )

    def _extract_parameter_info(
        self, param_name: str, param: inspect.Parameter, func: Callable
    ) -> Dict[str, Any]:
        """Extract parameter information from function signature"""
        param_info = {"description": f"Parameter for {param_name}"}

        # Get type hints
        try:
            type_hints = get_type_hints(func)
            param_type = type_hints.get(param_name)

            if param_type:
                param_info.update(self._convert_type_to_schema(param_type, param_name))
        except Exception as e:
            # Fallback to string type if type hints fail
            app_logger.warning(f"Type hint extraction failed for {func.__name__}.{param_name}: {e}")
            param_info["type"] = "string"

        # Add default value if present
        if param.default != inspect.Parameter.empty:
            param_info["default"] = param.default

        return param_info

    def _convert_type_to_schema(
        self, python_type: type, param_name: str
    ) -> Dict[str, Any]:
        """Convert Python type hints to OpenAI function schema types"""
        type_mapping = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            list: {"type": "array", "items": {"type": "string"}},  # Default array of strings
            dict: {"type": "object"},
        }

        # Handle UUID specifically
        if hasattr(python_type, "__name__") and python_type.__name__ == "UUID":
            return {
                "type": "string",
                "description": f"UUID for {param_name.replace('_', ' ')}",
            }

        # Handle Optional types
        if hasattr(python_type, "__origin__") and python_type.__origin__ is type(None):
            # This is Optional[T] which is Union[T, None]
            args = getattr(python_type, "__args__", ())
            if args:
                return self._convert_type_to_schema(args[0], param_name)

        # Handle List[T] types
        if hasattr(python_type, "__origin__") and python_type.__origin__ is list:
            args = getattr(python_type, "__args__", ())
            if args:
                # Get the inner type for list items
                inner_type = args[0]
                inner_schema = self._convert_type_to_schema(inner_type, param_name)
                return {"type": "array", "items": inner_schema}
            else:
                return {"type": "array", "items": {"type": "string"}}

        base_type = getattr(python_type, "__origin__", python_type)
        return type_mapping.get(base_type, {"type": "string"})

    def _generate_description_from_name(self, function_name: str) -> str:
        """Generate a description from function name if none provided"""
        words = function_name.replace("_", " ").split()

        if words[0] in ["get", "fetch", "retrieve"]:
            return f"Retrieve {' '.join(words[1:])}"
        elif words[0] == "search":
            return f"Search for {' '.join(words[1:])}"
        elif words[0] == "create":
            return f"Create new {' '.join(words[1:])}"
        elif words[0] == "update":
            return f"Update existing {' '.join(words[1:])}"
        elif words[0] == "delete":
            return f"Delete {' '.join(words[1:])}"
        else:
            return f"Perform {function_name.replace('_', ' ')} operation"

    def get_functions_for_intent(self, intent: IntentType) -> List[str]:
        """Get relevant function names for a specific intent from registry"""
        intent_key = intent.value if hasattr(intent, "value") else str(intent)
        return AIFunctionRegistry._intent_map.get(intent_key, [])

    def get_all_function_names(self) -> List[str]:
        """Get list of all available function names from registry"""
        return list(AIFunctionRegistry._functions.keys())

    def get_function_definition(
        self, function_name: str
    ) -> Optional[FunctionDefinition]:
        """Get definition for a specific function"""
        return self.definitions.get(function_name)

    def refresh_definitions(self) -> None:
        """Refresh definitions from registry (useful for dynamic updates)"""
        self.definitions = self._build_definitions_from_registry()

    def _enhance_description_with_constraints(
        self, func: Callable, base_description: str
    ) -> str:
        """Enhance description with parameter constraints from function logic"""
        docstring = inspect.getdoc(func)

        # Add constraint information to description
        enhanced = base_description

        # Check if function has validation logic by examining the source
        try:
            source = inspect.getsource(func)
            if "Either" in source and "must be provided" in source:
                enhanced += " Note: Either category_id alone, or restaurant_id + name together must be provided."
        except Exception:
            app_logger.warning("Could not inspect function source for constraints")
            pass

        if docstring:
            enhanced += f" {docstring}"

        return enhanced

    def get_functions_by_priority(
        self, intent: IntentType, limit: Optional[int] = None
    ) -> List[str]:
        """Get functions for intent ordered by priority"""
        functions = self.get_functions_for_intent(intent)

        # Sort by priority (lower number = higher priority)
        sorted_functions = sorted(
            functions,
            key=lambda f: AIFunctionRegistry._functions.get(f, {}).get("priority", 999),
        )

        return sorted_functions[:limit] if limit else sorted_functions

    def get_function_metadata(self, function_name: str) -> Optional[Dict[str, Any]]:
        """Get complete metadata for a function including priority, intent, etc."""
        return AIFunctionRegistry._functions.get(function_name)


# Global instance for easy access
AI_FUNCTION_REGISTRY = AIFunctionDefinitions()


def get_ai_functions() -> AIFunctionDefinitions:
    """Get the global AI function registry"""
    return AI_FUNCTION_REGISTRY


def get_functions_for_intent(intent: IntentType) -> List[str]:
    """Convenience function to get functions for intent"""
    return AI_FUNCTION_REGISTRY.get_functions_for_intent(intent)


def get_function_definition(function_name: str) -> Optional[FunctionDefinition]:
    """Convenience function to get function definition"""
    return AI_FUNCTION_REGISTRY.get_function_definition(function_name)


def refresh_ai_functions() -> None:
    """Refresh the global AI function registry"""
    AI_FUNCTION_REGISTRY.refresh_definitions()
