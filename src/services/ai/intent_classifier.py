"""Intent Classification Service using Groq"""

from datetime import datetime

from groq import AsyncGroq

from src.core.config import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE
from src.models.intent_classification import (
    AIServiceType,
    IntentClassificationRequest,
    IntentClassificationResponse,
    IntentType,
)
from src.services.ai.prompts import AIPrompts


class IntentClassifierService:
    """Decide what the customer wants (routing)"""

    def __init__(self):
        """Initialize the intent classifier service"""
        self.client = AsyncGroq(api_key=GROQ_API_KEY)

        self.intent_descriptions = {
            IntentType.GREETING: "Keywords: hello, hi, hey, good morning, greetings, start conversation",
            IntentType.BROWSE_MENU_CATEGORIES: "Keywords: menu, categories, what do you have, show food, browse, options, dishes available",
            IntentType.SEARCH_ITEM: "Keywords: do you have [food], find [item], specific food name, check availability, search dish",
            IntentType.ORDER_PLACEMENT: "Keywords: I want, order, buy, get, place order, add to cart, purchase [food]",
            IntentType.RESTAURANT_REVIEWS: "Keywords: reviews, ratings, feedback, testimonials, what do people say, comments",
            IntentType.RESTAURANT_ANALYTICS: "Keywords: analytics, statistics, reports, metrics, data, performance",
            IntentType.CUSTOMER_BASE_QUERY: "Keywords: customers, user search, customer info, database, customer analytics",
            IntentType.BULK_MESSAGING: "Restaurant owner wants to send bulk messages to customers",
            IntentType.RESTAURANT_INFO: "Keywords: location, address, hours, where, when open, contact, directions, phone",
            IntentType.GENERAL_HELP: "Keywords: help, assistance, questions, FAQ, how to, can you help, support",
            IntentType.BULK_MESSAGING: "Keywords: broadcast, mass message, send to all, marketing message, bulk SMS ",
            IntentType.UNKNOWN: "Any intent that does not match the above categories",
        }

    async def classify_intent(
        self,
        request: IntentClassificationRequest,
        conversation_history: list[dict[str, str]],
    ) -> IntentClassificationResponse:
        """Classify customer intent."""
        start_time = datetime.now()

        try:
            system_prompt = self._build_system_prompt(request)
            messages = self._build_messages(
                request, system_prompt, conversation_history
            )
            chat_completion = await self.client.chat.completions.create(
                messages=messages,
                model=GROQ_MODEL,
                max_tokens=20,
                temperature=GROQ_TEMPERATURE,
                top_p=0.1,
            )
            intent_str = chat_completion.choices[0].message.content.strip().lower()
            print(f"Intent classified as: {intent_str}")
            try:
                intent = IntentType(intent_str)
                confidence = 0.85
                fallback_used = False
            except ValueError:
                print(f"Unknown intent returned: {intent_str}")
                raise

            end_time = datetime.now()
            processing_time = int((end_time - start_time).total_seconds() * 1000)

            return IntentClassificationResponse(
                intent=intent,
                confidence=confidence,
                processing_time_ms=processing_time,
                service_used=AIServiceType.GROQ,
                fallback_used=fallback_used,
            )

        except Exception as e:
            print(f"Intent classification error: {str(e)}")
            return IntentClassificationResponse(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                processing_time_ms=0,
                service_used=AIServiceType.GROQ,
                fallback_used=True,
            )

    def _build_system_prompt(self, request: IntentClassificationRequest) -> str:
        """Build context-aware system prompt for classification using prompts module."""
        return AIPrompts.get_intent_classification_prompt(
            context=request.conversation_context,
            intent_descriptions=self.intent_descriptions,
        )

    def _build_messages(
        self,
        request: IntentClassificationRequest,
        system_prompt: str,
        conversation_history: list[dict[str, str]],
    ) -> list:
        """Build messages including conversation history for better classification"""
        messages = [{"role": "system", "content": system_prompt}]

        # Limit conversation history to last 4 messages to prevent confusion
        recent_history = (
            conversation_history[-4:]
            if len(conversation_history) > 4
            else conversation_history
        )

        for msg in recent_history:
            role = msg["role"]
            # groq uses model and not assistant like gemini
            if role == "model":
                role = "assistant"
            messages.append({"role": role, "content": msg["content"]})

        messages.append({"role": "user", "content": request.message})

        return messages
