import os

def append_to_file(filepath, content):
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write("\n" + content)

def get_new_svg_functions():
    return """
def generate_apples(filename: str, count: int):
    # generate red circles with a green leaf
    apples = ""
    for i in range(count):
        x = 50 + (i % 5) * 60
        y = 50 + (i // 5) * 60
        apples += f'''<g transform="translate({x},{y})">
            <circle cx="0" cy="0" r="20" fill="#e74c3c" />
            <path d="M 0,-20 Q 10,-30 15,-20 Q 5,-10 0,-20 Z" fill="#2ecc71" />
        </g>'''
    
    width = 300
    height = 50 + ((count - 1) // 5 + 1) * 60
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <rect width="{width}" height="{height}" rx="16" fill="#fefce8" stroke="#facc15" stroke-width="3"/>
  {apples}
</svg>'''
    save_svg(filename, svg)

def generate_stars_v2(filename: str, count: int):
    stars = ""
    for i in range(count):
        x = 50 + (i % 5) * 60
        y = 50 + (i // 5) * 60
        stars += f'''<polygon transform="translate({x},{y}) scale(0.5)" points="0,-25 6,-8 24,-8 9,3 15,20 0,9 -15,20 -9,3 -24,-8 -6,-8" fill="#f1c40f" />'''
    
    width = 300
    height = 50 + ((count - 1) // 5 + 1) * 60
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <rect width="{width}" height="{height}" rx="16" fill="#1e293b" />
  {stars}
</svg>'''
    save_svg(filename, svg)

def generate_gems_comparison(filename: str, left_count: int, right_count: int):
    left_gems = ""
    right_gems = ""
    for i in range(left_count):
        x = 30 + (i % 3) * 40
        y = 30 + (i // 3) * 40
        left_gems += f'<polygon transform="translate({x},{y}) scale(0.6)" points="0,-15 15,0 0,15 -15,0" fill="#9b59b6" />'
    for i in range(right_count):
        x = 200 + (i % 3) * 40
        y = 30 + (i // 3) * 40
        right_gems += f'<polygon transform="translate({x},{y}) scale(0.6)" points="0,-15 15,0 0,15 -15,0" fill="#2ecc71" />'
        
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 350 150" width="100%" height="100%">
  <rect width="350" height="150" rx="16" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
  <rect x="20" y="20" width="130" height="110" rx="8" fill="#f1f5f9" />
  <rect x="190" y="20" width="130" height="110" rx="8" fill="#f1f5f9" />
  {left_gems}
  {right_gems}
</svg>'''
    save_svg(filename, svg)

def generate_simple_icon(filename: str, name: str):
    icons = {
        "sun": '<circle cx="100" cy="100" r="40" fill="#f1c40f" /><g stroke="#f39c12" stroke-width="6"><line x1="100" y1="30" x2="100" y2="10"/><line x1="100" y1="170" x2="100" y2="190"/><line x1="30" y1="100" x2="10" y2="100"/><line x1="170" y1="100" x2="190" y2="100"/><line x1="50" y1="50" x2="35" y2="35"/><line x1="150" y1="150" x2="165" y2="165"/><line x1="150" y1="50" x2="165" y2="35"/><line x1="50" y1="150" x2="35" y2="165"/></g>',
        "cat": '<circle cx="100" cy="110" r="50" fill="#e67e22" /><polygon points="60,70 50,20 90,65" fill="#e67e22" /><polygon points="140,70 150,20 110,65" fill="#e67e22" /><circle cx="80" cy="100" r="6" fill="#000" /><circle cx="120" cy="100" r="6" fill="#000" /><polygon points="95,120 105,120 100,125" fill="#e74c3c" />',
        "sheep": '<path d="M 50,100 Q 50,50 100,50 Q 150,50 150,100 Q 180,100 180,130 Q 180,160 150,160 Q 100,180 50,160 Q 20,160 20,130 Q 20,100 50,100 Z" fill="#fff" stroke="#bdc3c7" stroke-width="4"/><circle cx="70" cy="110" r="20" fill="#34495e" /><circle cx="65" cy="105" r="3" fill="#fff"/><circle cx="75" cy="105" r="3" fill="#fff"/>',
        "cloud_bird": '<path d="M 50,120 Q 50,80 90,80 Q 110,40 150,60 Q 180,50 190,80 Q 220,90 200,130 Q 210,160 170,160 Q 100,170 60,150 Q 30,140 50,120 Z" fill="#fff" /><path d="M 120,50 Q 130,40 140,50 Q 150,40 160,50 Q 150,45 140,50 Q 130,45 120,50 Z" stroke="#34495e" stroke-width="3" fill="none" transform="scale(2) translate(-30, 20)"/>',
        "spring_flower": '<path d="M 100,100 L 100,180" stroke="#2ecc71" stroke-width="6" /><circle cx="100" cy="90" r="20" fill="#f1c40f" /><circle cx="70" cy="90" r="15" fill="#e74c3c" /><circle cx="130" cy="90" r="15" fill="#e74c3c" /><circle cx="100" cy="60" r="15" fill="#e74c3c" /><circle cx="100" cy="120" r="15" fill="#e74c3c" />',
        "honeybee": '<ellipse cx="100" cy="100" rx="40" ry="25" fill="#f1c40f" /><line x1="80" y1="78" x2="80" y2="122" stroke="#000" stroke-width="6" /><line x1="100" y1="75" x2="100" y2="125" stroke="#000" stroke-width="6" /><line x1="120" y1="78" x2="120" y2="122" stroke="#000" stroke-width="6" /><path d="M 80,78 Q 90,40 110,60 Q 90,50 80,78 Z" fill="#bdc3c7" opacity="0.8" /><circle cx="135" cy="95" r="3" fill="#000" />',
        "pattern_circle_square": '<circle cx="50" cy="100" r="25" fill="#3498db" /><rect x="100" y="75" width="50" height="50" fill="#e74c3c" /><circle cx="200" cy="100" r="25" fill="#3498db" /><rect x="250" y="75" width="50" height="50" fill="#e74c3c" />'
    }
    content = icons.get(name, "")
    
    width = 300 if name == "pattern_circle_square" else 200
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 200" width="100%" height="100%">
  <rect width="{width}" height="200" rx="16" fill="#87CEEB" />
  {content}
</svg>'''
    save_svg(filename, svg)

"""

if __name__ == "__main__":
    filepath = "c:/Users/Asus/ALP/scripts/svg_generator.py"
    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()
    
    # Check if we already appended
    if "generate_apples" not in original:
        # Insert before run()
        parts = original.split("def run():")
        new_content = parts[0] + get_new_svg_functions() + "\ndef run():\n" + parts[1]
        
        # Add new generations to run()
        run_block = """
    generate_apples("apples_4.svg", 4)
    generate_apples("apples_6.svg", 6)
    generate_apples("apples_8.svg", 8)
    
    generate_stars_v2("stars_3.svg", 3)
    generate_stars_v2("stars_5.svg", 5)
    generate_stars_v2("stars_7.svg", 7)
    
    generate_gems_comparison("gems_comparison_6_2.svg", 6, 2)
    
    generate_simple_icon("sun.svg", "sun")
    generate_simple_icon("cat.svg", "cat")
    generate_simple_icon("sheep.svg", "sheep")
    generate_simple_icon("cloud_bird.svg", "cloud_bird")
    generate_simple_icon("spring_flower.svg", "spring_flower")
    generate_simple_icon("honeybee.svg", "honeybee")
    generate_simple_icon("pattern_circle_square.svg", "pattern_circle_square")
"""
        new_content = new_content.replace('print("All SVGs successfully created!")', run_block + '\n    print("All SVGs successfully created!")')
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Updated svg_generator.py successfully.")
    else:
        print("svg_generator.py already updated.")
