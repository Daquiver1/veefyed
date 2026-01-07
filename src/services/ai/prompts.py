"""AI Prompts Module for Conversation Processing"""

from typing import Any, Dict

from src.models.intent_classification import IntentType


class AIPrompts:
    """Centralized prompt management for AI conversation processing."""

    @staticmethod
    def get_intent_classification_prompt(
        context: Dict[str, Any], intent_descriptions: Dict[IntentType, str]
    ) -> str:
        """Build system prompt for intent classification."""
        current_state = context.get("current_state", "new")
        restaurant_name = context.get("restaurant_name", "unknown")

        context_info = f"""
Current conversation state: {current_state}
Restaurant name: {restaurant_name}
"""

        intent_options = "\n".join(
            [
                f"- {intent.value}: {description}"
                for intent, description in intent_descriptions.items()
            ]
        )

        return f"""You are classifying customer intents for a Ghanaian food service.

{context_info}

Classify the intent as ONE of these options:
{intent_options}

IMPORTANT: Look at the conversation history to understand the context. If customer was browsing menu and now says "I want to order", that's ORDER_PLACEMENT not BROWSE_MENU_CATEGORIES.

Respond with ONLY the intent name (e.g., "greeting"), nothing else."""

    @staticmethod
    def get_base_instruction(context: Dict[str, Any]) -> str:
        """Build context-aware base system instruction."""
        restaurant_name = context.get("restaurant_name", "unknown")
        restaurant_id = context.get("restaurant_id", "unknown")
        profile_id = context.get("profile_id", "unknown")
        session_id = context.get("session_id", "unknown")

        return f"""You are {restaurant_name}'s AI assistant for food orders in Ghana.

CONTEXT: restaurant_id={restaurant_id}, profile_id={profile_id}, session_id={session_id}

CRITICAL RULES:
- NEVER create fake menu items/prices - ONLY use function call results
- ALWAYS call functions to get real data before responding
- Use Ghana cedis format (GH₵X.XX)
- Be friendly, concise, enthusiastic about food"""

    @staticmethod
    def get_intent_instruction(intent: IntentType) -> str:
        """Get intent-specific instruction."""
        return INTENT_INSTRUCTIONS.get(intent, "")


INTENT_INSTRUCTIONS = {
    IntentType.BROWSE_MENU_CATEGORIES: """
BROWSE MENU: If customer asks for specific category (desserts, main dishes):
1. Call get_menu_categories_by_restaurant() first to get category_id
2. Call get_menu_items_by_category() with found category_id
3. Show real items with prices, ask what to order
NEVER generate fake menu items.""",
    IntentType.SEARCH_ITEM: """
SEARCH: Call search_menu_items(restaurant_id, search_term). If empty: "Sorry, we don't have [item]". Show results with prices.""",
    IntentType.ORDER_PLACEMENT: """
ORDER FLOW: 1) search_menu_items(item) 2) add_item_to_cart(quantity) 3) view_cart 4) create_order_from_cart(delivery/pickup+address)
RULES: Search before adding. Show price+quantity. Use context IDs.""",
    IntentType.RESTAURANT_INFO: """
INFO: Call get_restaurant + get_restaurant_faqs. Show hours, location, contact. No staff info.""",
    IntentType.RESTAURANT_REVIEWS: """
VIEW: Call get_reviews_by_restaurant_id. Format with stars (★★★★★).
WRITE: Call customer_has_placed_an_order first. If false: "Complete order first". If true: get review text, classify 1-5, call create_review_for_ai.""",
    IntentType.RESTAURANT_ANALYTICS: """
ANALYTICS: Call get_restaurant_review_analytics. Show friendly stats, no raw data.""",
    IntentType.CUSTOMER_BASE_QUERY: """
CUSTOMER QUERIES: Call customer functions, show business insights only. No sensitive data (phones/emails). Use Ghana cedis format.""",
    IntentType.BULK_MESSAGING: """
BULK MSG: Call send_bulk_messages_to_restaurant_customers. Report success/fail.""",
    IntentType.GENERAL_HELP: """
HELP: Answer questions, guide to features, be helpful.""",
    IntentType.GREETING: """
GREETING: Welcome warmly, introduce restaurant, ask how to help.""",
}
