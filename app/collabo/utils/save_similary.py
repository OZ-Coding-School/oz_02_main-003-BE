from recipes.models import Recipe, Recipe_ingredient
from collabo.models import RecipeSimilarity

def calculate_all_recipe_similarities():
    all_recipes = Recipe.objects.all()
    all_recipe_ingredients = {}
    
    for recipe in all_recipes:
        ingredients = Recipe_ingredient.objects.filter(recipe=recipe)
        ingredient_names = [ingredient.ingredient.name for ingredient in ingredients]
        all_recipe_ingredients[recipe.id] = set(ingredient_names)

    def jaccard_similarity(set1, set2):
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        similarity = round(intersection / union, 4) if union != 0 else 0.0000
        return similarity

    recipe_similarities = {}
    for recipe1 in all_recipes:
        for recipe2 in all_recipes:
            similarity = jaccard_similarity(all_recipe_ingredients[recipe1.id], all_recipe_ingredients[recipe2.id])
            recipe_similarities[(recipe1.id, recipe2.id)] = similarity

    return recipe_similarities

def save_all_recipe_similarities():
    recipe_similarities = calculate_all_recipe_similarities()
    for (recipe1_id, recipe2_id), similarity in recipe_similarities.items():
        # recipe1_id와 recipe2_id가 같은 경우 건너뛰기
        if recipe1_id == recipe2_id:
            continue

        recipe1 = Recipe.objects.get(id=recipe1_id)
        recipe2 = Recipe.objects.get(id=recipe2_id)
        RecipeSimilarity.objects.create(
            recipe=recipe1,
            similar_recipe=recipe2,
            similarity_score=similarity
        )