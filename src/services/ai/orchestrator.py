"""AI Orchestrator Service"""

from datetime import datetime
from typing import Dict, List, Union

from databases import Database

from src.db.repositories.conversation_message import \
    ConversationMessageRepository
from src.db.repositories.conversation_session import \
    ConversationSessionRepository
from src.enums.intent_type import get_simple_intents
from src.enums.message_role import MessageRole
from src.models.conversation import (ConversationProcessingRequest,
                                     ConversationProcessingResponse)
from src.models.conversation_message import ConversationMessageCreate
from src.models.conversation_session import (ConversationSessionInDb,
                                             ConversationSessionUpdate)
from src.models.core import AIResponse
from src.models.intent_classification import (IntentClassificationRequest,
                                              IntentClassificationResponse,
                                              IntentType)
from src.services.ai.conversation_processor import ConversationProcessorService
from src.services.ai.function_definitions import get_functions_for_intent
from src.services.ai.function_executor import FunctionExecutorService
from src.services.ai.intent_classifier import IntentClassifierService


class AIOrchestrator:
    """Main AI Orchestrator that coordinates all AI services"""

    def __init__(self, db: Database):
        """Initialize the AI orchestrator with all services"""
        self.db = db

        self.intent_classifier = IntentClassifierService()
        self.conversation_processor = ConversationProcessorService()
        self.function_executor = FunctionExecutorService(db)
        self.session_repo = ConversationSessionRepository(db)
        self.message_repo = ConversationMessageRepository(db)

        self.simple_intents = get_simple_intents()

    async def handle_message(
        self,
        *,
        phone_number: str,
        message: str,
        session_id: str,
    ) -> AIResponse:
        """Main entry point for processing customer messages"""
        try:
            session = await self._get_session(session_id)

            intent_response = await self._classify_intent(message, session)
            if intent_response.intent == IntentType.UNKNOWN:
                return AIResponse(
                    message="I'm not sure what you want. Can you please rephrase your request?",
                    type="unknown_intent",
                    error="Intent classification failed",
                    function_results=None,
                )
            if intent_response.intent in self.simple_intents:
                response = await self._handle_simple_intent(
                    intent_response.intent, session
                )
            else:
                response = await self._handle_complex_intent(
                    intent_response.intent, message, session
                )

            await self._update_session_after_response(
                session, intent_response.intent, response
            )

            await self._save_conversation_messages(
                session, message, response, intent_response
            )

            print(f"Response generated: {response}")

            response.metadata = {
                "session_id": session.id,
                "intent": intent_response.intent.value,
                "intent_confidence": intent_response.confidence,
                "processing_time_ms": intent_response.processing_time_ms,
                "fallback_used": intent_response.fallback_used,
                "timestamp": datetime.utcnow().isoformat(),
            }

            return response

        except Exception as e:
            print(f"AI Orchestrator error: {str(e)}")
            return await self._error_response(phone_number, str(e))

    async def _get_session(
        self,
        session_id: str,
    ) -> ConversationSessionInDb:
        """Get existing session or create new one"""
        session = await self.session_repo.get_session(session_id=session_id)
        if session is None:
            raise ValueError(
                f"Session {session_id} not found and cannot create session without required data"
            )
        return session

    async def _get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get formatted conversation history for AI processing"""
        try:
            return await self.message_repo.get_ai_conversation_history(
                session_id=session_id,
            )
        except Exception as e:
            print(f"Error getting conversation history: {str(e)}")
            return []

    async def _save_conversation_messages(
        self,
        session: ConversationSessionInDb,
        user_message: str,
        ai_response: AIResponse,
        intent_response: IntentClassificationResponse,
    ) -> None:
        """Save user message and AI response to conversation history"""
        try:
            user_msg = ConversationMessageCreate(
                conversation_session_id=session.id,
                role=MessageRole.USER,
                content=user_message,
                intent=intent_response.intent,
                intent_confidence=intent_response.confidence,
                processing_time_ms=intent_response.processing_time_ms,
                success=True,
            )
            await self.message_repo.create_conversation_message(user_msg)

            function_calls_count = (
                len(ai_response.function_results) if ai_response.function_results else 0
            )
            assistant_msg = ConversationMessageCreate(
                conversation_session_id=session.id,
                role=MessageRole.MODEL,
                content=ai_response.message,
                intent=intent_response.intent,
                intent_confidence=intent_response.confidence,
                processing_time_ms=intent_response.processing_time_ms,
                function_calls_count=function_calls_count,
                success=not ai_response.error,
            )
            await self.message_repo.create_conversation_message(assistant_msg)

        except Exception as e:
            print(f"Error saving conversation messages: {str(e)}")

    async def _classify_intent(
        self, message: str, session: ConversationSessionInDb
    ) -> IntentClassificationResponse:
        """Classify message intent using intent classifier"""
        context = session.context.copy()
        context.update(
            {
                "current_state": session.current_state.value,
                "restaurant_id": (
                    str(session.restaurant_id) if session.restaurant_id else None
                ),
                "restaurant_name": session.restaurant_name,
            }
        )

        request = IntentClassificationRequest(
            message=message, conversation_context=context
        )
        messages_history = await self._get_conversation_history(session.id)

        return await self.intent_classifier.classify_intent(request, messages_history)

    async def _handle_simple_intent(
        self, intent: IntentType, session: ConversationSessionInDb
    ) -> AIResponse:
        """Handle simple intents with predefined responses"""
        simple_responses = {
            IntentType.GREETING: {
                "message": f"Hello {session.context.get('user_name', '')}!\nWelcome to {session.restaurant_name} 🍽️\n\nI can help you with:\n\n🏪 View restaurant info\n🍽️ Show menu items\n🛒 Place an order\n⭐ Check customer reviews\n\nTap any of the buttons below or type out what you want to do!",
                "type": "greeting",
            },
            IntentType.GENERAL_HELP: {
                "message": "I can help you:\n\n🍽️ Browse restaurant menu\n\n💳 Place and pay for orders\n\nWhat would you like to do?",
                "type": "help_menu",
            },
        }

        response_data = simple_responses.get(
            intent,
            {
                "message": f"I'm here to help! What would you like to know about {session.restaurant_name}?",
                "type": "general_response",
            },
        )

        return AIResponse(
            message=response_data["message"],
            type=response_data["type"],
            error="",
            function_results=None,
        )

    async def _handle_complex_intent(
        self, intent: IntentType, message: str, session: ConversationSessionInDb
    ) -> AIResponse:
        """Handle complex intents using conversation processor and function execution"""
        try:
            if intent in [IntentType.CUSTOMER_BASE_QUERY, IntentType.BULK_MESSAGING]:
                user_role = session.user_role
                allowed_roles = {"restaurant_owner", "restaurant_manager", "admin", "restaurant_staff"}
                if user_role.value not in allowed_roles:
                    return AIResponse(
                        message="⚠️ Access denied. Customer base queries are only available to restaurant owners and managers.",
                        type="access_denied",
                        error="Insufficient permissions for customer base query",
                        function_results=None,
                    )
            context = session.context.copy()
            context.update(
                {
                    "current_state": session.current_state.value,
                    "restaurant_id": str(session.restaurant_id),
                    "restaurant_name": session.restaurant_name,
                    "session_id": str(session.id),
                    "profile_id": str(session.profile_id),
                    "phone_number": session.phone_number,
                }
            )

            available_functions = get_functions_for_intent(intent)

            conversation_history = await self._get_conversation_history(session.id)

            processing_request = ConversationProcessingRequest(
                message=message,
                intent=intent,
                conversation_context=context,
                available_functions=available_functions,
                conversation_history=conversation_history,
            )

            max_iterations = 3  # Prevent infinite loops
            all_function_results = []
            current_request = processing_request
            final_ai_response = None

            for iteration in range(max_iterations):
                print(f"=== Iteration {iteration + 1} ===")

                ai_response = await self.conversation_processor.process_conversation(
                    current_request
                )

                print(f"Gemini response iteration {iteration + 1}:", ai_response)
                final_ai_response = ai_response

                if not ai_response.function_calls:
                    print(
                        f"No function calls in iteration {iteration + 1}, ending loop"
                    )
                    break

                iteration_results = []
                for function_call in ai_response.function_calls:
                    print(f"Executing function: {function_call.name}")
                    result = await self.function_executor.execute_function(
                        function_call=function_call,
                        session_id=session.id,
                        context=context,
                    )

                    formatted_result = {
                        "function": function_call.name,
                        "success": result.get("success", False),
                        "data": result.get("data"),
                        "iteration": iteration + 1,
                    }

                    iteration_results.append(formatted_result)
                    all_function_results.append(formatted_result)
                    print(f"Function {function_call.name} result: {formatted_result}")

                if iteration < max_iterations - 1:  # Don't prepare for last iteration
                    current_request = self._prepare_next_iteration_request(
                        current_request, iteration_results, ai_response
                    )

            if all_function_results:
                formatted_response = (
                    await self.conversation_processor.process_function_results(
                        original_request=processing_request,
                        function_results=all_function_results,
                        original_response=final_ai_response,
                    )
                )

                final_message = (
                    formatted_response.text
                    if formatted_response
                    else final_ai_response.text
                )
                print("Final formatted message:", final_message)
            else:
                final_message = (
                    final_ai_response.text
                    if final_ai_response
                    else "I couldn't process your request."
                )
                print("No functions executed, using text response:", final_message)

            return AIResponse(
                message=final_message,
                type=self._get_response_type(intent, all_function_results),
                error="",
                function_results=all_function_results,
            )

        except Exception as e:
            print(f"Complex intent handling error: {str(e)}")
            return AIResponse(
                message="I'm having trouble processing that request right now. Could you please try again?",
                type="error",
                error=str(e),
            )

    def _prepare_next_iteration_request(
        self,
        original_request: ConversationProcessingRequest,
        iteration_results: List[Dict],
        ai_response: ConversationProcessingResponse,
    ) -> ConversationProcessingRequest:
        """Let Gemini analyze function results and extract what it needs for next iteration"""
        results_context = "Function execution results:\n"
        for result in iteration_results:
            if result["success"] and result["data"]:
                formatted_data = self._format_function_data_for_gemini(result["data"])
                results_context += f"""
✅ Function: {result['function']}
Data: {formatted_data}
Instructions: Analyze this data and extract any IDs, names, or values needed for subsequent function calls.
"""
            else:
                results_context += f"❌ Function: {result['function']} - Failed\n"

        enhanced_message = f"""
TASK: The customer originally requested: "{original_request.message}"

{results_context}

NEXT STEPS REQUIRED:
Based on the function results above, you MUST now call the next function to complete the customer's request.

SPECIFIC INSTRUCTIONS:
- Look at the customer's original request and identify what category they want
- Find that category in the function results data above
- Extract the 'id' value from the matching category (this is the category_id)  
- Call get_menu_items function with the extracted category_id
- Do NOT generate a response without calling the function first

MANDATORY: You MUST call get_menu_items function next. Do not provide any text response."""

        return ConversationProcessingRequest(
            message=enhanced_message,
            intent=original_request.intent,
            conversation_context=original_request.conversation_context,
            available_functions=original_request.available_functions,
            conversation_history=original_request.conversation_history,
        )

    def _format_function_data_for_gemini(
        self, data: Union[Dict, List, str, int, float, None]
    ) -> str:
        """Format function result data in a way Gemini can easily parse and extract values from"""
        if data is None:
            return "No data returned"

        try:
            if isinstance(data, list):
                if not data:
                    return "Empty list"

                formatted_items = []
                for item in data:
                    if hasattr(item, "dict"):
                        item_dict = item.dict()
                        formatted_items.append(item_dict)
                    elif isinstance(item, dict):
                        formatted_items.append(item)
                    else:
                        formatted_items.append(str(item))

                return str(formatted_items)

            elif hasattr(data, "dict"):
                return str(data.dict())

            elif isinstance(data, dict):
                return str(data)

            else:
                return str(data)

        except Exception as e:
            print(f"Error formatting data for Gemini: {e}")
            return f"Data formatting error: {str(data)[:200]}..."

    def _get_response_type(
        self, intent: IntentType, function_results: List[Dict]
    ) -> str:
        """Determine response type based on intent and function results"""
        if any(not result["success"] for result in function_results):
            return "error"

        type_map = {
            IntentType.BROWSE_MENU_CATEGORIES: "menu_display",
            IntentType.SEARCH_ITEM: "search_results",
        }

        return type_map.get(intent, "general_response")

    async def _update_session_after_response(
        self,
        session: ConversationSessionInDb,
        intent: IntentType,
        response: AIResponse,
    ) -> None:
        """Update session state after processing response"""
        context = session.context.copy()

        new_state = session.current_state

        if response.function_results:
            for result in response.function_results:
                context["last_function_call"] = result["function"]
                context["last_function_success"] = result["success"]

        session_update = ConversationSessionUpdate(
            current_state=new_state,
            context=context,
        )
        await self.session_repo.update_session(
            session_id=session.id, session_update=session_update
        )

    async def _error_response(self, phone_number: str, error: str) -> AIResponse:
        """Generate error response"""
        return AIResponse(
            message="I'm experiencing some technical difficulties right now. Please try again in a moment, or contact our support team if the problem persists.",
            type="system_error",
            error=error,
            metadata={"timestamp": datetime.utcnow().isoformat(), "error": True},
        )
