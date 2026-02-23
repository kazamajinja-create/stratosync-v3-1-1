
from variation_selector import select_style
from response_templates import templates

def generate_response(user_profile, style='random'):
    chosen_style = select_style(style)
    template = templates.get(chosen_style, templates['default'])
    return template.format(**user_profile)
