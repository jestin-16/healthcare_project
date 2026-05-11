import os
import re

template_dir = r"f:\awt\appointments\templates\appointments"

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # If fade-in is present
    if 'fade-in' in content:
        # Pattern 1: class="something fade-in something_else" -> class="something something_else" data-aos="fade-up"
        # Since it could be at the end, middle, or start of the class string.
        # Actually, simpler approach:
        # Replace ' fade-in' with ''
        # Replace 'fade-in ' with ''
        # Replace 'fade-in' with ''
        # And add data-aos="fade-up" to the tag.
        
        # We can use regex to find class="..." containing fade-in
        def replace_class(match):
            class_str = match.group(1)
            # Remove fade-in from class
            new_class_str = re.sub(r'\bfade-in\b', '', class_str).strip()
            # Clean up extra spaces
            new_class_str = re.sub(r'\s+', ' ', new_class_str)
            
            if new_class_str:
                return f'class="{new_class_str}" data-aos="fade-up"'
            else:
                return f'data-aos="fade-up"'
                
        new_content = re.sub(r'class="([^"]*fade-in[^"]*)"', replace_class, content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filepath}")

for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            replace_in_file(os.path.join(root, file))
