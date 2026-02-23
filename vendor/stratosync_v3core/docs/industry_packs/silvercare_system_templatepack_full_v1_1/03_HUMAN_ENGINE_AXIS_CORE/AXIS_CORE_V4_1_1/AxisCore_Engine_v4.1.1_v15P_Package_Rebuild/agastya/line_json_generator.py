
# line_json_generator.py

import json

def generate_line_json(json_path, output_path="line_flex_messages.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    messages = []
    for chapter in data.get("chapters", []):
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": chapter.get("title", "No Title"), "weight": "bold", "size": "lg"},
                    {"type": "text", "text": chapter.get("content", "No Content"), "wrap": True}
                ]
            }
        }
        messages.append(bubble)

    flex_container = {"type": "carousel", "contents": messages}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(flex_container, f, ensure_ascii=False, indent=2)
