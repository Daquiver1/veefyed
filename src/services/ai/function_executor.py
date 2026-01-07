"""AI Function Executor Service"""

import inspect
from typing import Any, Dict, get_type_hints

from databases import Database

from src.db.repositories.customer import CustomerRepository
from src.db.repositories.menu_category import MenuCategoryRepository
from src.db.repositories.menu_item import MenuItemRepository
from src.db.repositories.order import OrderRepository
from src.db.repositories.order_item import OrderItemRepository
from src.db.repositories.restaurant import RestaurantRepository
from src.db.repositories.restaurant_faq import RestaurantFaqRepository
from db.repositories.image import ReviewRepository
from src.decorators.ai import AIFunctionRegistry
from src.models.conversation import AIFunctionCallBase


class FunctionExecutorService:
    """Executes AI function calls using your existing repositories"""

    def __init__(self, db: Database):
        """Initialize with database and repositories"""
        self.db = db
        self.repositories = {}
        self._initialize_repositories()

    def _initialize_repositories(self) -> None:
        """Auto-discover and initialize all AI-enabled repositories"""
        repository_classes = [
            CustomerRepository,
            MenuCategoryRepository,
            MenuItemRepository,
            RestaurantFaqRepository,
            RestaurantRepository,
            OrderRepository,
            OrderItemRepository,
            ReviewRepository,
        ]

        for repo_class in repository_classes:
            instance = repo_class(self.db)
            self.repositories[repo_class.__name__] = instance

        self._bind_repository_methods()

    def _bind_repository_methods(self) -> None:
        """Bind unbound methods to repository instances"""
        for function_name, func_info in AIFunctionRegistry._functions.items():
            func = func_info["func"]

            if hasattr(func, "__qualname__"):
                class_name = func.__qualname__.split(".")[0]

                if class_name in self.repositories:
                    repository_instance = self.repositories[class_name]
                    method_name = func.__name__
                    bound_method = getattr(repository_instance, method_name)

                    AIFunctionRegistry._functions[function_name]["func"] = bound_method

    async def execute_function(
        self,
        function_call: AIFunctionCallBase,
        session_id: str,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Execute any registered AI function dynamically"""
        function_name = function_call.name

        if function_name not in AIFunctionRegistry._functions:
            return {
                "success": False,
                "error": f"Unknown function: {function_name}",
                "data": None,
            }

        try:
            func_info = AIFunctionRegistry._functions[function_name]
            func = func_info["func"]
            signature = func_info["signature"]

            print(f"Signature params: {list(signature.parameters.keys())}")
            print(f"Context provided: {context}")
            print(f"Gemini function args: {function_call.args}")

            # Core contextual IDs that should never be overridden by Gemini
            core_context_keys = {
                "restaurant_id",
                "session_id",
                "phone_number",
                "restaurant_name",
                "current_state",
                "profile_id",
            }

            enhanced_args = {**context}

            # Add Gemini's extracted args, but preserve core context values
            for key, value in function_call.args.items():
                if key in core_context_keys and key in context:
                    print(
                        f"Preserving core context {key}: {context[key]} (ignoring Gemini's: {value})"
                    )
                    continue
                else:
                    # Use Gemini's extracted value for non-core keys (like category_id, item_id)
                    enhanced_args[key] = value
                    print(f"Using Gemini's extracted {key}: {value}")

            print(f"Enhanced args (hybrid approach): {enhanced_args}")

            function_args = self._get_function_args_only(enhanced_args, signature)
            converted_args = self._convert_args_to_types(function_args, signature)

            print(f"Final args being passed to {function_name}: {converted_args}")

            result = await func(**converted_args)

            return {"success": True, "data": result}

        except Exception as e:
            print(f"Function execution error: {str(e)}")
            import traceback

            traceback.print_exc()
            return {"success": False, "error": str(e), "data": None}

    def _convert_args_to_types(
        self, args: Dict[str, Any], signature: inspect.Signature
    ) -> Dict[str, Any]:
        """Convert string arguments to proper types based on function signature"""
        from uuid import UUID

        converted = {}
        type_hints = {}

        try:
            type_hints = get_type_hints(signature)
        except Exception:
            pass

        for param_name, _ in signature.parameters.items():
            if param_name == "self":
                continue

            if param_name in args:
                value = args[param_name]
                param_type = type_hints.get(param_name)

                if param_type == UUID and isinstance(value, str):
                    converted[param_name] = UUID(value)
                elif param_type == bool and isinstance(value, str):
                    converted[param_name] = value.lower() in ("true", "1", "yes", "on")
                elif param_type == int and isinstance(value, str):
                    converted[param_name] = int(value)
                elif param_type == float and isinstance(value, str):
                    converted[param_name] = float(value)
                else:
                    converted[param_name] = value

        return converted

    def _get_function_args_only(
        self, args: Dict[str, Any], signature: inspect.Signature
    ) -> Dict[str, Any]:
        """Extract only the arguments that the function expects"""
        function_params = {
            name for name in signature.parameters.keys() if name != "self"
        }
        return {k: v for k, v in args.items() if k in function_params}
