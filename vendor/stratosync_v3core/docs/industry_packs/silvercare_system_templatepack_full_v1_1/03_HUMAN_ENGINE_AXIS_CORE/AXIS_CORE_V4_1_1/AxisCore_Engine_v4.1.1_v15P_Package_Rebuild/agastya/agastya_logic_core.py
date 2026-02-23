"""
Agastya Logic Core v1.0 Beta
Supports: Lite / Standard / Premium Plan Processing
"""

import json
from pathlib import Path
from vedanta_module import analyze_vedanta_patterns

# Load chapter data
def load_chapter_data(folder_path):
    data = []
    json_files = sorted(Path(folder_path).glob("*.json"))
    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data.extend(json.load(f))
    return data

# Load dictionary
def load_dictionary(dictionary_path):
    with open(dictionary_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Lite Plan: 50 Chapters Basic Structure
def run_lite_mode():
    chapters = load_chapter_data("agastya_100_filed")[:50]
    dictionary = load_dictionary("agastya_leaf_dictionary_v1.json")
    return {
        "plan": "lite",
        "chapters": chapters,
        "dictionary_used": dictionary
    }

# Standard Plan: 100 Chapters with Karma and Year Map
def run_standard_mode():
    chapters = load_chapter_data("agastya_100_filed")
    dictionary = load_dictionary("agastya_leaf_dictionary_v1.json")
    return {
        "plan": "standard",
        "chapters": chapters,
        "dictionary_used": dictionary,
        "year_map_included": True
    }

# Premium Plan: Includes Vedanta Logic
def run_premium_mode():
    chapters = load_chapter_data("agastya_100_filed")
    base_dict = load_dictionary("agastya_leaf_dictionary_v1.json")
    advanced_dict_path = Path("agastya_leaf_advanced_dictionaries")
    advanced_dicts = {}
    for file in advanced_dict_path.glob("*.json"):
        with open(file, 'r', encoding='utf-8') as f:
            advanced_dicts[file.name] = json.load(f)

    vedanta_results = analyze_vedanta_patterns(chapters)

    return {
        "plan": "premium",
        "chapters": chapters,
        "dictionary_used": base_dict,
        "advanced_dicts_used": advanced_dicts,
        "vedanta_analysis": vedanta_results
    }

# Main dispatcher
def run_agastya_analysis(plan_type):
    if plan_type == "lite":
        return run_lite_mode()
    elif plan_type == "standard":
        return run_standard_mode()
    elif plan_type == "premium":
        return run_premium_mode()
    else:
        raise ValueError("Unsupported plan type. Choose from: lite, standard, premium.")
