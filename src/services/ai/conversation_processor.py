"""Conversation Processing Service using Gemini SDK"""

from datetime import datetime
from typing import Any, Dict, List

from google import genai
from google.genai import types

from src.core.config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE
from src.models.conversation import (
    AIFunctionCallBase,
    ConversationProcessingRequest,
    ConversationProcessingResponse,
)
from src.models.core import GeminiResponse
from src.models.intent_classification import AIServiceType, IntentType
from src.services.ai.function_definitions import get_function_definition
from src.services.ai.prompts import AIPrompts


class ConversationProcessorService:
    """Clean conversation processing"""

    def __init__(self):
        """Initialize the conversation processor service"""
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    async def process_conversation(
        self, request: ConversationProcessingRequest
    ) -> ConversationProcessingResponse:
        """Process complex conversation request"""
        start_time = datetime.now()

        try:
            system_instruction = self._build_system_instruction(
                request.intent, request.conversation_context
            )

            messages = self._build_messages(request, system_instruction)

            if request.available_functions:
                response = await self._generate_with_functions(
                    messages, request.available_functions
                )
            else:
                response = await self._generate_text_only(messages)

            end_time = datetime.now()
            processing_time = int((end_time - start_time).total_seconds() * 1000)

            return ConversationProcessingResponse(
                text=response.text,
                function_calls=response.function_calls,
                success=True,
                processing_time_ms=processing_time,
                service_used=AIServiceType.GEMINI,
                tokens_used=response.tokens_used,
                model_used=GEMINI_MODEL,
                fallback_used=False,
                confidence=0.85,
            )

        except Exception as e:
            print(f"Conversation processing error: {str(e)}")
            raise

    async def process_function_results(
        self,
        original_request: ConversationProcessingRequest,
        function_results: List[Dict[str, Any]],
        original_response: ConversationProcessingResponse,
    ) -> ConversationProcessingResponse:
        """Send function results back to Gemini for proper formatting with conversation continuity"""
        try:
            system_instruction = (
                self._build_system_instruction(
                    original_request.intent, original_request.conversation_context
                )
                + "\n\nIMPORTANT: You just executed functions and got results. Now format and present the function results to the customer in a natural, user-friendly way.\n\nCRITICAL FORMATTING RULES:\n- ONLY present data that was actually returned by the functions - NEVER add anything extra\n- If function returned empty list [], clearly state the item was not found\n- NEVER show raw data objects, UUIDs, created_at, updated_at, or technical information\n- Present menu items as a nice list with names and prices ONLY if they exist in results\n- Present categories as a simple list ONLY if they exist in results\n- Use proper Ghana cedis formatting (GH₵X.XX) for prices from database\n- Be conversational but NEVER invent information\n- If search returned no results, say 'Sorry, we don't have that item' and suggest alternatives\n\nREVIEW FORMATTING RULES:\n- For reviews: Display each review with star rating (★★★★★) based on rating number\n- Show customer name and review text in a nice format\n- If no reviews found, say 'No reviews available for this restaurant yet'\n- For review creation: Classify review text sentiment on 1-5 scale (1=very negative, 5=very positive)\n- Convert rating numbers to star display: 1=★, 2=★★, 3=★★★, 4=★★★★, 5=★★★★★"
            )

            messages = [{"role": "system", "content": system_instruction}]

            for msg in original_request.conversation_history[-6:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

            messages.append({"role": "user", "content": original_request.message})

            if original_response.text:
                messages.append({"role": "model", "content": original_response.text})

            results_content = "Function results received:\n"
            for result in function_results:
                if result["success"]:
                    results_content += (
                        f"\n✅ {result['function']} executed successfully\n"
                    )
                    results_content += f"Data: {result['data']}\n"

                    if result["data"] == [] or result["data"] is None:
                        results_content += "IMPORTANT: No results found - item does not exist in menu\n"
                else:
                    results_content += f"\n❌ {result['function']} failed\n"

            messages.append(
                {
                    "role": "user",
                    "content": f"Here are the function results. Please present this information to me in a natural, formatted way:\n\n{results_content}",
                }
            )

            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    {"role": msg["role"], "parts": [{"text": msg["content"]}]}
                    for msg in messages
                    if msg["role"] != "system"
                ],
                config=types.GenerateContentConfig(
                    system_instruction={"parts": [{"text": messages[0]["content"]}]},
                    temperature=0.0,
                    max_output_tokens=500,
                    top_p=0.1,
                    top_k=10,
                ),
            )

            return ConversationProcessingResponse(
                text=response.text
                or "Currently experiencing technical difficulties. Please try again later.",
                function_calls=[],
                success=True,
                processing_time_ms=0,
                service_used=AIServiceType.GEMINI,
                tokens_used=response.usage_metadata.total_token_count or 0,
                model_used=GEMINI_MODEL,
                fallback_used=False,
                confidence=0.85,
            )

        except Exception as e:
            print(f"Function results processing error: {str(e)}")
            return None

    def _build_system_instruction(
        self, intent: IntentType, context: Dict[str, Any]
    ) -> str:
        """Build context-aware system instruction using prompts module."""
        base_instruction = AIPrompts.get_base_instruction(context)
        intent_instruction = AIPrompts.get_intent_instruction(intent)

        return f"{base_instruction}\n\n{intent_instruction}"

    def _build_messages(
        self, request: ConversationProcessingRequest, system_instruction: str
    ) -> List[Dict[str, str]]:
        """Build conversation messages for Gemini"""
        messages = [{"role": "system", "content": system_instruction}]

        # Add conversation history (last 6 messages for context)
        for msg in request.conversation_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": request.message})

        return messages

    async def _generate_text_only(
        self, messages: List[Dict[str, str]]
    ) -> GeminiResponse:
        """Generate text-only response"""
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    {"role": msg["role"], "parts": [{"text": msg["content"]}]}
                    for msg in messages
                    if msg["role"] != "system"
                ],
                config=types.GenerateContentConfig(
                    system_instruction={"parts": [{"text": messages[0]["content"]}]},
                    temperature=GEMINI_TEMPERATURE,
                    max_output_tokens=350,
                ),
            )

            return GeminiResponse(
                text=response.text or "I'm having trouble processing that request.",
                function_calls=[],
                tokens_used=response.usage_metadata.total_token_count or 0,
            )

        except Exception as e:
            print(f"Gemini text generation error: {str(e)}")
            raise

    async def _generate_with_functions(
        self, messages: List[Dict[str, str]], available_functions: List[str]
    ) -> GeminiResponse:
        """Generate response with function calling"""
        try:
            tools = []
            function_declarations = []

            for func_name in available_functions:
                func_def = get_function_definition(func_name)

                if func_def:
                    declaration = types.FunctionDeclaration(
                        name=func_def.name,
                        description=func_def.description,
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                param_name: self._build_gemini_schema(param_schema)
                                for param_name, param_schema in func_def.parameters.items()
                            },
                            required=func_def.required_parameters,
                        ),
                    )
                    function_declarations.append(declaration)

            if function_declarations:
                tools = [types.Tool(function_declarations=function_declarations)]

            print("These are the tools", tools)

            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    {"role": msg["role"], "parts": [{"text": msg["content"]}]}
                    for msg in messages
                    if msg["role"] != "system"
                ],
                config=types.GenerateContentConfig(
                    system_instruction={"parts": [{"text": messages[0]["content"]}]},
                    temperature=0.0,  # so it calls the function and not generating responses.
                    max_output_tokens=500,
                    tools=tools,
                    top_p=0.1,
                    top_k=10,
                ),
            )

            text_parts = []
            function_calls = []

            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.text:
                            text_parts.append(part.text)
                        elif part.function_call:
                            func_call = part.function_call
                            function_calls.append(
                                AIFunctionCallBase(
                                    name=func_call.name,
                                    args=dict(func_call.args) if func_call.args else {},
                                )
                            )

            return GeminiResponse(
                text=(
                    " ".join(text_parts)
                    if text_parts
                    else "I'm having trouble processing that request."
                ),
                function_calls=function_calls,
                tokens_used=response.usage_metadata.total_token_count or 0,
            )
        except Exception as e:
            print(f"Gemini function calling error: {str(e)}")
            raise

    def _build_gemini_schema(self, param_schema: Dict[str, Any]) -> types.Schema:
        """Build Gemini schema from our function parameter schema - simplified to avoid recursion"""
        try:
            if isinstance(param_schema, dict):
                schema_type = param_schema.get("type", "string").lower()
                description = param_schema.get("description", "Parameter")

                type_map = {
                    "string": types.Type.STRING,
                    "integer": types.Type.INTEGER,
                    "number": types.Type.NUMBER,
                    "boolean": types.Type.BOOLEAN,
                    "array": types.Type.ARRAY,
                    "object": types.Type.OBJECT,
                }

                gemini_type = type_map.get(schema_type, types.Type.STRING)

                schema_dict = {
                    "type": gemini_type,
                    "description": description,
                }

                if schema_type == "array":
                    schema_dict["items"] = types.Schema(
                        type=types.Type.OBJECT, description="Array item"
                    )

                return types.Schema(**schema_dict)

            else:
                return types.Schema(type=types.Type.STRING, description="Parameter")
        except Exception as e:
            print(f"Schema building error for {param_schema}: {e}")
            return types.Schema(type=types.Type.STRING, description="Parameter")
