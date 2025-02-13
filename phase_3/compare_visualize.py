def compare_phonemes(actual, expected):
    """
    Compares actual and expected phonemes word by word, calculating phoneme match percentage.

    Parameters:
        actual (dict): A dictionary with words as keys and their actual phonemes as values.
        expected (dict): A dictionary with words as keys and their expected phonemes as values.

    Returns:
        list: A list of dictionaries containing word-level comparison results.
    """
    comparison_results = []
#commet
    for word, actual_phoneme in actual.items():
        expected_phoneme = expected.get(word, "")
        
        # Convert phonemes into character lists for letter-based comparison
        actual_list = list(actual_phoneme.replace(" ", ""))
        expected_list = list(expected_phoneme.replace(" ", ""))
        
        # Calculate matches
        matching_letters = sum(1 for a, e in zip(actual_list, expected_list) if a == e)
        total_letters = max(len(actual_list), len(expected_list))

        # Percentage match
        percentage_match = (matching_letters / total_letters) * 100 if total_letters > 0 else 0

        # Determine rating
        if percentage_match > 60:
            rating = "Excellent"
        elif percentage_match > 30:
            rating = "Good"
        else:
            rating = "Needs Improvement"

        comparison_results.append({
            "word": word,
            "actual": actual_phoneme,
            "expected": expected_phoneme,
            "percentage_match": percentage_match,
            "rating": rating
        })

    return comparison_results


def visualize_phoneme_comparison(comparison_results):
    """
    Displays a detailed summary of the phoneme comparison results.

    Parameters:
        comparison_results (list): A list of dictionaries containing word-level comparison results.
    """
    print("\n📊 Phoneme Comparison Summary:\n")
    for result in comparison_results:
        word = result['word']
        actual = result['actual']
        expected = result['expected']
        percentage = result['percentage_match']
        rating = result['rating']

        print(f"Word: {word}")
        print(f"  🎙️ Actual Phonemes  : {actual}")
        print(f"  📖 Expected Phonemes: {expected}")
        print(f"  ✅ Match Percentage : {percentage:.2f}%")
        print(f"  🌟 Rating           : {rating}")
        print("-" * 40)