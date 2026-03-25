def classify_ingredients(ingredients_list):
    """
    Classifies ingredients into Safe / Harmful / Neutral based on rules.
    """
    harmful_keywords = ["sugar", "palm oil", "e621", "msg", "trans fat", "artificial"]
    neutral_keywords = ["salt", "wheat", "flour", "yeast"]
    
    results = []
    warnings = []
    health_score = 100
    
    for ing in ingredients_list:
        ing_lower = ing.lower().strip()
        if any(kw in ing_lower for kw in harmful_keywords):
            risk = "High"
            desc = f"Contains potentially harmful ingredient: {ing}"
            health_score -= 15
            warnings.append(ing)
        elif any(kw in ing_lower for kw in neutral_keywords):
            risk = "Medium"
            desc = "Moderate consumption recommended."
            health_score -= 5
        else:
            risk = "Low"
            desc = "Generally recognized as safe."
            
        results.append({
            "ingredient_name": ing,
            "risk_level": risk,
            "description": desc
        })
        
    # Threshold checks
    grade = "A"
    if health_score < 40:
        grade = "F"
    elif health_score < 60:
        grade = "D"
    elif health_score < 80:
        grade = "C"
    elif health_score < 90:
        grade = "B"
        
    return {
        "health_score": max(0, health_score),
        "grade": grade,
        "warnings": warnings,
        "ingredient_logs": results
    }

def apply_personalization(base_results, user_profile):
    """
    Adjusts health score and warnings based on user's health conditions.
    """
    if not user_profile:
        return base_results

    warnings = list(base_results.get('warnings', []))
    score = base_results.get('health_score', 100)
    
    # Check conditions
    if user_profile.diabetes and any("sugar" in w.lower() for w in warnings):
        warnings.append("CRITICAL: High sugar matches Diabetes condition.")
        score -= 20
        
    if user_profile.hypertension and any("salt" in w.lower() for w in warnings):
        warnings.append("CRITICAL: High sodium matches Hypertension condition.")
        score -= 15
        
    if user_profile.vegan and any("milk" in w.lower() or "egg" in w.lower() for w in warnings):
        warnings.append("WARNING: Non-vegan ingredients detected.")
        score -= 20
        
    # Re-calculate grade
    grade = "A"
    if score < 40: grade = "F"
    elif score < 60: grade = "D"
    elif score < 80: grade = "C"
    elif score < 90: grade = "B"
    
    base_results['health_score'] = max(0, score)
    base_results['grade'] = grade
    base_results['warnings'] = warnings
    
    return base_results

def analyze_levels(ingredients_list, nutrition_data):
    """
    Analyzes specific categories: preservatives, additives, sugar, fat, carbs, other injurious substances.
    """
    preservatives_kw = ["sodium benzoate", "potassium sorbate", "nitrate", "bha", "bht", "sulfite"]
    additives_kw = ["e621", "msg", "color", "flavor", "sweetener", "artificial"]
    injurious_kw = ["trans fat", "high fructose corn syrup", "hydrogenated", "palm oil"]
    
    found_preservatives = [i for i in ingredients_list if any(p in i.lower() for p in preservatives_kw)]
    found_additives = [i for i in ingredients_list if any(a in i.lower() for a in additives_kw)]
    found_injurious = [i for i in ingredients_list if any(inj in i.lower() for inj in injurious_kw)]
    
    sugar_g = nutrition_data.get('sugar_g', 0)
    fat_g = nutrition_data.get('fat_g', 0)
    carb_g = nutrition_data.get('carb_g', 0)
    
    sugar_lvl = "High" if sugar_g > 15 else ("Medium" if sugar_g > 5 else "Low")
    fat_lvl = "High" if fat_g > 20 else ("Medium" if fat_g > 10 else "Low")
    carb_lvl = "High" if carb_g > 50 else ("Medium" if carb_g > 20 else "Low")
    
    def get_count_level(count, high_thresh, med_thresh):
        if count >= high_thresh: return "High"
        if count >= med_thresh: return "Medium"
        return "Low"
        
    return {
        "preservatives": get_count_level(len(found_preservatives), 2, 1),
        "additives": get_count_level(len(found_additives), 3, 1),
        "sugar_level": f"{sugar_g}g ({sugar_lvl})",
        "fat_level": f"{fat_g}g ({fat_lvl})",
        "carb_level": f"{carb_g}g ({carb_lvl})",
        "other_injurious_substances": ", ".join(found_injurious) if found_injurious else "None Detected"
    }
