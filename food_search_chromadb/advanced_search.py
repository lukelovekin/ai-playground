from shared_functions import *


def main():
    """Main entry point for the advanced search system."""
    try:
        print("🔎 Advanced Food Search System")
        print("=" * 50)
        print("Loading food database with advanced filtering capabilities...")

        food_items = load_food_data('./FoodDataSet.json')
        print(f"✅ Loaded {len(food_items)} food items successfully")

        collection = create_similarity_search_collection(
            "advanced_food_search",
            {'description': 'A collection for advanced search demos'},
        )
        populate_similarity_collection(collection, food_items)
        interactive_advanced_search(collection)

    except Exception as error:
        print(f"❌ Error initializing advanced search system: {error}")


def interactive_advanced_search(collection):
    """Interactive menu-driven advanced search."""
    print("\n" + "=" * 50)
    print("🔍 ADVANCED SEARCH WITH FILTERS")
    print("=" * 50)
    print("Search Options:")
    print("  1. Basic similarity search")
    print("  2. Cuisine-filtered search")
    print("  3. Calorie-filtered search")
    print("  4. Combined filters search")
    print("  5. Demonstration mode")
    print("  6. Help")
    print("  7. Exit")
    print("-" * 50)

    handlers = {
        '1': lambda: perform_basic_search(collection),
        '2': lambda: perform_cuisine_filtered_search(collection),
        '3': lambda: perform_calorie_filtered_search(collection),
        '4': lambda: perform_combined_filtered_search(collection),
        '5': lambda: run_search_demonstrations(collection),
        '6': show_advanced_help,
    }

    while True:
        try:
            choice = input("\n📌 Select option (1-7): ").strip()
            if choice == '7':
                print("👋 Exiting Advanced Search System. Goodbye!")
                break
            handler = handlers.get(choice)
            if handler:
                handler()
            else:
                print("⚠️ Invalid option. Please select 1-7.")
        except KeyboardInterrupt:
            print("\n\n⚡ System interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def perform_basic_search(collection):
    """Perform basic similarity search without filters."""
    print("\n🔍 BASIC SIMILARITY SEARCH")
    print("-" * 30)
    query = input("Enter search query: ").strip()
    if not query:
        print("⚠️ Please enter a search term")
        return
    print(f"\n⏳ Searching for '{query}'...")
    display_search_results(perform_similarity_search(collection, query, 5), "Basic Search Results")


def perform_cuisine_filtered_search(collection):
    """Perform cuisine-filtered similarity search."""
    print("\n🌍 CUISINE-FILTERED SEARCH")
    print("-" * 30)
    cuisines = ["Italian", "Thai", "Mexican", "Indian", "Japanese", "French",
                "Mediterranean", "American", "Health Food", "Dessert"]
    print("Available cuisines:")
    for i, cuisine in enumerate(cuisines, 1):
        print(f"  {i}. {cuisine}")

    query = input("\nEnter search query: ").strip()
    cuisine_choice = input("Enter cuisine number (or cuisine name): ").strip()

    if not query:
        print("⚠️ Please enter a search term")
        return

    if cuisine_choice.isdigit():
        idx = int(cuisine_choice) - 1
        cuisine_filter = cuisines[idx] if 0 <= idx < len(cuisines) else None
    else:
        cuisine_filter = cuisine_choice or None

    if not cuisine_filter:
        print("⚠️ Invalid cuisine selection")
        return

    print(f"\n⏳ Searching for '{query}' in {cuisine_filter} cuisine...")
    results = perform_filtered_similarity_search(
        collection, query, cuisine_filter=cuisine_filter, n_results=5
    )
    display_search_results(results, f"Cuisine-Filtered Results ({cuisine_filter})")


def perform_calorie_filtered_search(collection):
    """Perform calorie-filtered similarity search."""
    print("\n🔥 CALORIE-FILTERED SEARCH")
    print("-" * 30)
    query = input("Enter search query: ").strip()
    max_cal_input = input("Enter maximum calories (or press Enter for no limit): ").strip()

    if not query:
        print("⚠️ Please enter a search term")
        return

    max_calories = int(max_cal_input) if max_cal_input.isdigit() else None
    suffix = f" with max {max_calories} calories" if max_calories else ""
    print(f"\n⏳ Searching for '{query}'{suffix}...")

    results = perform_filtered_similarity_search(collection, query, max_calories=max_calories, n_results=5)
    label = f"under {max_calories} calories" if max_calories else "any calories"
    display_search_results(results, f"Calorie-Filtered Results ({label})")


def perform_combined_filtered_search(collection):
    """Perform search with multiple filters combined."""
    print("\n⚙️ COMBINED FILTERS SEARCH")
    print("-" * 30)
    query = input("Enter search query: ").strip()
    cuisine = input("Enter cuisine type (optional): ").strip()
    max_cal_input = input("Enter maximum calories (optional): ").strip()

    if not query:
        print("⚠️ Please enter a search term")
        return

    cuisine_filter = cuisine or None
    max_calories = int(max_cal_input) if max_cal_input.isdigit() else None

    filter_parts = []
    if cuisine_filter:
        filter_parts.append(f"cuisine: {cuisine_filter}")
    if max_calories:
        filter_parts.append(f"max calories: {max_calories}")
    filter_text = ", ".join(filter_parts) if filter_parts else "no filters"

    print(f"\n⏳ Searching for '{query}' with {filter_text}...")
    results = perform_filtered_similarity_search(
        collection, query,
        cuisine_filter=cuisine_filter,
        max_calories=max_calories,
        n_results=5,
    )
    display_search_results(results, f"Combined Filtered Results ({filter_text})")


def run_search_demonstrations(collection):
    """Run predefined demonstrations of different search types."""
    print("\n🎬 SEARCH DEMONSTRATIONS")
    print("=" * 40)

    demonstrations = [
        {"title": "Italian Cuisine Search", "query": "creamy pasta", "cuisine_filter": "Italian", "max_calories": None},
        {"title": "Low-Calorie Healthy Options", "query": "healthy meal", "cuisine_filter": None, "max_calories": 300},
        {"title": "Asian Light Dishes", "query": "light fresh meal", "cuisine_filter": "Japanese", "max_calories": 250},
    ]

    for i, demo in enumerate(demonstrations, 1):
        print(f"\n{i}. {demo['title']}")
        print(f"   Query: '{demo['query']}'")
        filters = []
        if demo['cuisine_filter']:
            filters.append(f"Cuisine: {demo['cuisine_filter']}")
        if demo['max_calories']:
            filters.append(f"Max Calories: {demo['max_calories']}")
        if filters:
            print(f"   Filters: {', '.join(filters)}")

        results = perform_filtered_similarity_search(
            collection,
            demo['query'],
            cuisine_filter=demo['cuisine_filter'],
            max_calories=demo['max_calories'],
            n_results=3,
        )
        display_search_results(results, demo['title'], show_details=False)
        input("\n▶️ Press Enter to continue...")


def display_search_results(results, title, show_details=True):
    """Display search results in a formatted layout."""
    print(f"\n📋 {title}")
    print("=" * 50)

    if not results:
        print("❌ No matching results found")
        print("   Try adjusting your search terms or filters")
        return

    for i, result in enumerate(results, 1):
        score = result['similarity_score'] * 100
        if show_details:
            print(f"\n{i}. 🍽️ {result['food_name']}")
            print(f"   Similarity Score: {score:.1f}%")
            print(f"   🌍 Cuisine:  {result['cuisine_type']}")
            print(f"   🔥 Calories: {result['food_calories_per_serving']}")
            print(f"   📝 {result['food_description']}")
        else:
            print(f"  {i}. {result['food_name']} ({score:.1f}% match)")

    print("=" * 50)


def show_advanced_help():
    """Display help for the advanced search system."""
    print("\n📖 ADVANCED SEARCH HELP")
    print("=" * 40)
    print("Search Types:")
    print("  1. Basic Search  - Standard similarity search")
    print("  2. Cuisine Filter - Search within specific cuisine types")
    print("  3. Calorie Filter - Search for foods under a calorie limit")
    print("  4. Combined Filters - Use multiple filters together")
    print("  5. Demonstrations   - See predefined search examples")
    print("\nTips:")
    print("  • Use descriptive terms: 'creamy', 'spicy', 'light'")
    print("  • Combine ingredients: 'chicken vegetables'")
    print("  • Filter by calories for dietary goals")


if __name__ == "__main__":
    main()
