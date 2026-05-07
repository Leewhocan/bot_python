def calculate_animal(answers_weights: list[dict]) -> str:
    totals = {}
    for weight_dict in answers_weights:
        for animal, points in weight_dict.items():
            totals[animal] = totals.get(animal, 0) + points
    max_score = max(totals.values())
    top_animals = [a for a, s in totals.items() if s == max_score]
    return top_animals[0]