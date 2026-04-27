from typing import Dict, List

from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes  # noqa: F401

from shared_functions import *

food_items: list = []

my_credentials = {"url": "https://us-south.ml.cloud.ibm.com"}
model_id = "ibm/granite-3-3-8b-instruct"
gen_parms = {"max_new_tokens": 400}
project_id = "skills-network"

model = ModelInference(
    model_id=model_id,
    credentials=my_credentials,
    params=gen_parms,
    project_id=project_id,
    space_id=None,
    verify=False,
)


def main():
    """Main entry point for the enhanced RAG chatbot."""
    try:
        print("🤖 Enhanced RAG-Powered Food Recommendation Chatbot")
        print("   Powered by IBM Granite & ChromaDB")
        print("=" * 55)

        global food_items
        food_items = load_food_data('./FoodDataSet.json')
        print(f"✅ Loaded {len(food_items)} food items")

        collection = create_similarity_search_collection(
            "enhanced_rag_food_chatbot",
            {'description': 'Enhanced RAG chatbot with IBM watsonx.ai integration'},
        )
        populate_similarity_collection(collection, food_items)
        print("✅ Vector database ready")

        print("🔗 Testing LLM connection...")
        test_response = model.generate(prompt="Hello", params=None)
        if test_response and "results" in test_response:
            print("✅ LLM connection established")
        else:
            print("❌ LLM connection failed")
            return

        enhanced_rag_food_chatbot(collection)

    except Exception as error:
        print(f"❌ Error: {error}")


def prepare_context_for_llm(query: str, search_results: List[Dict]) -> str:
    """Build a structured context string from search results for the LLM prompt."""
    if not search_results:
        return "No relevant food items found in the database."

    parts = [
        "Based on your query, here are the most relevant food options from our database:",
        "",
    ]
    for i, result in enumerate(search_results[:3], 1):
        parts.append(f"Option {i}: {result['food_name']}")
        parts.append(f"  - Description: {result['food_description']}")
        parts.append(f"  - Cuisine: {result['cuisine_type']}")
        parts.append(f"  - Calories: {result['food_calories_per_serving']} per serving")

        ingredients = result.get('food_ingredients')
        if ingredients:
            ing_str = ', '.join(ingredients[:5]) if isinstance(ingredients, list) else ingredients
            parts.append(f"  - Key ingredients: {ing_str}")

        if result.get('food_health_benefits'):
            parts.append(f"  - Health benefits: {result['food_health_benefits']}")
        if result.get('cooking_method'):
            parts.append(f"  - Cooking method: {result['cooking_method']}")
        if result.get('taste_profile'):
            parts.append(f"  - Taste profile: {result['taste_profile']}")

        parts.append(f"  - Similarity score: {result['similarity_score'] * 100:.1f}%")
        parts.append("")

    return "\n".join(parts)


def generate_llm_rag_response(query: str, search_results: List[Dict]) -> str:
    """Generate a response using IBM Granite with retrieved context."""
    try:
        context = prepare_context_for_llm(query, search_results)
        prompt = f"""You are a helpful food recommendation assistant.

User Query: "{query}"

Retrieved Food Information:
{context}

Provide a helpful, concise response that:
1. Acknowledges the user's request
2. Recommends 2-3 specific food items from the retrieved options
3. Explains why they match the request
4. Includes relevant details (cuisine, calories, health benefits)
5. Uses a friendly, conversational tone

Response:"""

        generated = model.generate(prompt=prompt, params=None)
        if generated and "results" in generated:
            text = generated["results"][0]["generated_text"].strip()
            if len(text) >= 50:
                return text

    except Exception as e:
        print(f"❌ LLM Error: {e}")

    return generate_fallback_response(query, search_results)


def generate_fallback_response(query: str, search_results: List[Dict]) -> str:
    """Simple fallback response when the LLM is unavailable."""
    if not search_results:
        return "I couldn't find any food items matching your request. Try describing what you're in the mood for with different words!"

    top = search_results[0]
    parts = [
        f"Based on your request for '{query}', I'd recommend {top['food_name']}.",
        f"It's a {top['cuisine_type']} dish with {top['food_calories_per_serving']} calories per serving.",
    ]
    if len(search_results) > 1:
        parts.append(f"Another great option would be {search_results[1]['food_name']}.")
    return " ".join(parts)


def enhanced_rag_food_chatbot(collection):
    """Enhanced RAG-powered conversational food chatbot."""
    print("\n" + "=" * 70)
    print("🤖 ENHANCED RAG FOOD RECOMMENDATION CHATBOT")
    print("   Powered by IBM's Granite Model")
    print("=" * 70)
    print("Ask me about food recommendations using natural language!")
    print("\nExample queries:")
    print("  • 'I want something spicy and healthy for dinner'")
    print("  • 'What Italian dishes do you recommend under 400 calories?'")
    print("  • 'Suggest some protein-rich breakfast options'")
    print("\nCommands: 'help', 'compare', 'quit'")
    print("-" * 70)

    conversation_history: List[str] = []

    while True:
        try:
            user_input = input("\n👤 You: ").strip()

            if not user_input:
                print("🤖 Bot: Please tell me what kind of food you're looking for!")
                continue

            if user_input.lower() in {'quit', 'exit', 'q'}:
                print("\n🤖 Bot: Thank you for using the Enhanced RAG Food Chatbot! 🍽️")
                break
            elif user_input.lower() in {'help', 'h'}:
                show_enhanced_rag_help()
            elif user_input.lower() == 'compare':
                handle_enhanced_comparison_mode(collection)
            else:
                handle_enhanced_rag_query(collection, user_input, conversation_history)
                conversation_history.append(user_input)
                if len(conversation_history) > 5:
                    conversation_history = conversation_history[-3:]

        except KeyboardInterrupt:
            print("\n\n🤖 Bot: Goodbye! Hope you find something delicious! 🍴")
            break
        except Exception as e:
            print(f"❌ Bot: Sorry, I encountered an error: {e}")


def handle_enhanced_rag_query(collection, query: str, conversation_history: List[str]):
    """Handle a user query with RAG + IBM Granite."""
    print(f"\n🔍 Searching vector database for: '{query}'...")
    search_results = perform_similarity_search(collection, query, 3)

    if not search_results:
        print("🤖 Bot: I couldn't find any food items matching your request.")
        print("   Try describing what you're in the mood for with different words!")
        return

    print(f"✅ Found {len(search_results)} relevant matches")
    print("⏳ Generating AI-powered response...")
    ai_response = generate_llm_rag_response(query, search_results)
    print(f"\n🤖 Bot: {ai_response}")

    print("\n📋 Search Results Details:")
    print("-" * 45)
    for i, result in enumerate(search_results[:3], 1):
        print(
            f"{i}. 🍽️ {result['food_name']} | "
            f"{result['cuisine_type']} | "
            f"{result['food_calories_per_serving']} cal | "
            f"{result['similarity_score'] * 100:.1f}% match"
        )


def handle_enhanced_comparison_mode(collection):
    """AI-powered comparison between two food queries."""
    print("\n⚖️ ENHANCED COMPARISON MODE")
    print("-" * 35)
    query1 = input("Enter first food query: ").strip()
    query2 = input("Enter second food query: ").strip()

    if not query1 or not query2:
        print("⚠️ Please enter both queries for comparison")
        return

    print(f"\n⏳ Analysing '{query1}' vs '{query2}' with AI...")
    results1 = perform_similarity_search(collection, query1, 3)
    results2 = perform_similarity_search(collection, query2, 3)

    comparison = generate_llm_comparison(query1, query2, results1, results2)
    print(f"\n🤖 AI Analysis: {comparison}")

    print("\n📊 DETAILED COMPARISON")
    print("=" * 60)
    q1_label = f"Query 1: {query1[:20]}..." if len(query1) > 20 else f"Query 1: {query1}"
    q2_label = f"Query 2: {query2[:20]}..." if len(query2) > 20 else f"Query 2: {query2}"
    print(f"{q1_label:<30} | {q2_label}")
    print("-" * 60)
    for i in range(min(max(len(results1), len(results2)), 3)):
        left = f"{results1[i]['food_name']} ({results1[i]['similarity_score']*100:.0f}%)" if i < len(results1) else "---"
        right = f"{results2[i]['food_name']} ({results2[i]['similarity_score']*100:.0f}%)" if i < len(results2) else "---"
        print(f"{left[:30]:<30} | {right[:30]}")


def generate_llm_comparison(
    query1: str, query2: str, results1: List[Dict], results2: List[Dict]
) -> str:
    """Generate an AI-powered comparison between two queries."""
    try:
        context1 = prepare_context_for_llm(query1, results1[:3])
        context2 = prepare_context_for_llm(query2, results2[:3])
        prompt = f"""Compare these two food preference queries:

Query 1: "{query1}"
Top Results:
{context1}

Query 2: "{query2}"
Top Results:
{context2}

Briefly compare: key differences, any similarities, and the best pick from each query.
Comparison:"""
        generated = model.generate(prompt=prompt, params=None)
        if generated and "results" in generated:
            return generated["results"][0]["generated_text"].strip()
    except Exception:
        pass
    return generate_simple_comparison(query1, query2, results1, results2)


def generate_simple_comparison(
    query1: str, query2: str, results1: List[Dict], results2: List[Dict]
) -> str:
    """Simple text comparison fallback."""
    if not results1 and not results2:
        return "No results found for either query."
    if not results1:
        return f"Found results for '{query2}' but none for '{query1}'."
    if not results2:
        return f"Found results for '{query1}' but none for '{query2}'."
    return (
        f"For '{query1}', I recommend {results1[0]['food_name']}. "
        f"For '{query2}', {results2[0]['food_name']} would be perfect."
    )


def show_enhanced_rag_help():
    """Display help for the enhanced RAG chatbot."""
    print("\n📖 ENHANCED RAG CHATBOT HELP")
    print("=" * 45)
    print("How to get the best recommendations:")
    print("  • Be specific: 'healthy Italian pasta under 350 calories'")
    print("  • Mention preferences: 'spicy comfort food for cold weather'")
    print("  • Include context: 'light breakfast for a busy morning'")
    print("\nSpecial features:")
    print("  • Vector similarity search finds relevant foods")
    print("  • AI analysis provides contextual explanations")
    print("  • Smart comparison between different preferences")
    print("\nCommands:")
    print("  • 'compare' - AI-powered comparison of two queries")
    print("  • 'help'    - Show this help menu")
    print("  • 'quit'    - Exit the chatbot")


if __name__ == "__main__":
    main()
