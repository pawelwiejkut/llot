#!/usr/bin/env python3

import re

def fix_language_dropdowns():
    """Fix hardcoded languages in index-modern.html template"""
    
    template_file = "app/templates/index-modern.html"
    
    # Read the template
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern for hardcoded language options (excluding auto)
    hardcoded_pattern = r'<option value="([a-z]{2})"[^>]*>([^<]+)</option>'
    
    # Find all instances of hardcoded languages in select elements
    select_blocks = []
    
    # Pattern to match entire select blocks with hardcoded options
    select_pattern = r'(<select[^>]*>\s*)((?:<option[^>]*>[^<]*</option>\s*)+)(</select>)'
    
    def replace_select_options(match):
        select_start = match.group(1)
        options_block = match.group(2)
        select_end = match.group(3)
        
        # Check if this has hardcoded language options
        if 'value="en"' in options_block and 'value="de"' in options_block:
            # Check if it includes auto (source language) or not (target language)
            if 'value="auto"' in options_block:
                # Source language dropdown
                new_options = """{% for code, name in languages %}
                  <option value="{{ code }}" {% if code=='auto' %}selected{% endif %}>{{ name }}</option>
                {% endfor %}"""
            else:
                # Target language dropdown - exclude auto
                new_options = """{% for code, name in languages %}
                  {% if code != 'auto' %}
                    <option value="{{ code }}" {% if code=='de' %}selected{% endif %}>{{ name }}</option>
                  {% endif %}
                {% endfor %}"""
            
            return select_start + new_options + '\n              ' + select_end
        
        return match.group(0)  # Return unchanged if not a language dropdown
    
    # Replace all select blocks
    content = re.sub(select_pattern, replace_select_options, content, flags=re.MULTILINE | re.DOTALL)
    
    # Write back the fixed content
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed language dropdowns in index-modern.html")
    print("✅ All hardcoded languages replaced with template variables")

if __name__ == "__main__":
    fix_language_dropdowns()