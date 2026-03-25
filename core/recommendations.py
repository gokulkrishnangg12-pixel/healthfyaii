import requests

def get_healthier_alternatives(bad_ingredients):
    """
    Simulates calling OpenFoodFacts or a similar API to find healthier 
    alternatives based on avoiding bad ingredients.
    """
    # Real implementation would call something like:
    # url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1"
    # res = requests.get(url)

    # For demo purposes, we provide static realistic suggestions:
    suggestions = []
    
    warnings_lower = [w.lower() for w in bad_ingredients]
    
    if any("sugar" in w for w in warnings_lower):
        suggestions.append({
            "suggestion_name": "Zero-Sugar Substitute Option",
            "reason": "Contains no added sugars, sweetened with Stevia.",
            "image_url": ""
        })
        
    if any("salt" in w or "sodium" in w for w in warnings_lower):
        suggestions.append({
            "suggestion_name": "Low-Sodium Alternative",
            "reason": "Contains 50% less sodium compared to the scanned product.",
            "image_url": ""
        })
        
    if not suggestions:
        suggestions.append({
            "suggestion_name": "Organic Whole Food Variant",
            "reason": "Made from whole ingredients with no artificial additives.",
            "image_url": ""
        })
        
    return suggestions
