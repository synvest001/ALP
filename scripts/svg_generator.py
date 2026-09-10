import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_SVG_DIR = BASE_DIR / "frontend" / "public" / "assets" / "svg"
DIST_SVG_DIR = BASE_DIR / "frontend" / "dist" / "assets" / "svg"

PUBLIC_SVG_DIR.mkdir(parents=True, exist_ok=True)
DIST_SVG_DIR.mkdir(parents=True, exist_ok=True)

def save_svg(filename: str, content: str):
    for target_dir in [PUBLIC_SVG_DIR, DIST_SVG_DIR]:
        target_path = target_dir / filename
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
    print(f"Generated SVG: {filename}")

def car_svg(x: int, y: int, color="#e74c3c", scale=1.0):
    return f'''
    <g transform="translate({x},{y}) scale({scale})">
      <rect x="5" y="15" width="40" height="18" rx="5" fill="{color}" />
      <polygon points="12,15 18,5 32,5 38,15" fill="{color}" />
      <polygon points="15,13 19,7 24,7 24,13" fill="#ecf0f1" />
      <polygon points="26,13 26,7 31,7 35,13" fill="#ecf0f1" />
      <circle cx="14" cy="33" r="6" fill="#2c3e50" />
      <circle cx="14" cy="33" r="2.5" fill="#bdc3c7" />
      <circle cx="36" cy="33" r="6" fill="#2c3e50" />
      <circle cx="36" cy="33" r="2.5" fill="#bdc3c7" />
    </g>
    '''

def generate_see_saw(filename: str, left_count: int, right_known: int, right_missing: int):
    cars_left = "".join(car_svg(20 + (i % 4) * 45, 100 - (i // 4) * 35, color="#3498db", scale=0.85) for i in range(left_count))
    cars_right = "".join(car_svg(360 + i * 45, 100, color="#2ecc71", scale=0.85) for i in range(right_known))
    
    missing_box = f'''
    <g transform="translate({360 + right_known * 45}, 90)">
      <rect width="65" height="42" rx="8" fill="#f39c12" stroke="#d35400" stroke-width="3" stroke-dasharray="6,4"/>
      <text x="32" y="27" font-family="'Comic Sans MS', sans-serif" font-size="24" font-weight="bold" fill="#fff" text-anchor="middle" dominant-baseline="middle">?</text>
    </g>
    '''
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 240" width="100%" height="100%">
  <defs>
    <linearGradient id="beamGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#f1c40f"/>
      <stop offset="100%" stop-color="#e67e22"/>
    </linearGradient>
    <linearGradient id="baseGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#7f8c8d"/>
      <stop offset="100%" stop-color="#34495e"/>
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="4" flood-opacity="0.2"/>
    </filter>
  </defs>
  
  <rect width="600" height="240" rx="16" fill="#f8fafc" stroke="#e2e8f0" stroke-width="2"/>
  
  <!-- Fulcrum Base -->
  <polygon points="300,140 270,210 330,210" fill="url(#baseGrad)" filter="url(#shadow)"/>
  <circle cx="300" cy="140" r="10" fill="#e74c3c"/>
  <circle cx="300" cy="140" r="4" fill="#fff"/>
  
  <!-- Main Balanced Plank -->
  <rect x="40" y="132" width="520" height="16" rx="8" fill="url(#beamGrad)" filter="url(#shadow)"/>
  
  <!-- Left Pan Basket -->
  <rect x="50" y="125" width="200" height="8" rx="4" fill="#d35400"/>
  <!-- Right Pan Basket -->
  <rect x="350" y="125" width="200" height="8" rx="4" fill="#d35400"/>
  
  <!-- Left Side Cars -->
  {cars_left}
  
  <!-- Right Side Cars & Mystery Box -->
  {cars_right}
  {missing_box}
  
  <text x="300" y="30" font-family="'Comic Sans MS', sans-serif" font-size="18" font-weight="bold" fill="#334155" text-anchor="middle">
    Balanced Scale: {left_count} on Left = {right_known} + [ ? ] on Right
  </text>
</svg>'''
    save_svg(filename, svg)

def generate_car_set(filename: str, count: int, color="#3498db"):
    cars = "".join(car_svg(15 + i * 50, 10, color=color, scale=1.0) for i in range(count))
    width = max(100, 30 + count * 50)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 60" width="100%" height="100%">
  {cars}
</svg>'''
    save_svg(filename, svg)

def generate_dots(filename: str, count: int, color="#e74c3c"):
    dots_positions = {
        4: [(30, 30), (70, 30), (30, 70), (70, 70)],
        6: [(30, 25), (70, 25), (30, 50), (70, 50), (30, 75), (70, 75)],
        10: [(20, 30), (40, 30), (60, 30), (80, 30), (100, 30), (20, 70), (40, 70), (60, 70), (80, 70), (100, 70)]
    }
    coords = dots_positions.get(count, [(50, 50)])
    width = 120 if count == 10 else 100
    dots_svg = "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="{color}"/>' for x, y in coords)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 100" width="100%" height="100%">
  <rect width="{width}" height="100" rx="16" fill="#fff" stroke="#cbd5e1" stroke-width="3"/>
  {dots_svg}
</svg>'''
    save_svg(filename, svg)

def generate_ten_frame(filename: str, filled: int, total: int = 10):
    boxes = ""
    for i in range(total):
        row = i // 5
        col = i % 5
        x = 20 + col * 60
        y = 20 + row * 60
        is_filled = i < filled
        dot = f'<circle cx="{x + 25}" cy="{y + 25}" r="18" fill="#e74c3c" filter="url(#shadow)"/>' if is_filled else ''
        boxes += f'''
        <rect x="{x}" y="{y}" width="50" height="50" rx="6" fill="#f8fafc" stroke="#334155" stroke-width="3"/>
        {dot}
        '''
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 160" width="100%" height="100%">
  <defs>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="340" height="160" rx="16" fill="#fff" stroke="#94a3b8" stroke-width="3"/>
  {boxes}
</svg>'''
    save_svg(filename, svg)

def generate_monkeys_branch(filename: str):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 200" width="100%" height="100%">
  <rect width="500" height="200" rx="16" fill="#f0fdf4" stroke="#86efac" stroke-width="2"/>
  <path d="M 30,120 Q 250,90 470,120" stroke="#854d0e" stroke-width="16" fill="none" stroke-linecap="round"/>
  <!-- 5 monkeys on left -->
  <g fill="#a16207">
    <circle cx="80" cy="90" r="18"/>
    <circle cx="130" cy="85" r="18"/>
    <circle cx="180" cy="82" r="18"/>
    <circle cx="230" cy="80" r="18"/>
    <circle cx="280" cy="82" r="18"/>
  </g>
  <text x="180" y="50" font-family="'Comic Sans MS', sans-serif" font-size="18" font-weight="bold" fill="#15803d" text-anchor="middle">5 Monkeys on Left</text>
  <!-- 2 monkeys on right + box -->
  <g fill="#ea580c">
    <circle cx="360" cy="95" r="18"/>
    <circle cx="410" cy="100" r="18"/>
  </g>
  <rect x="440" y="80" width="40" height="40" rx="8" fill="#fef08a" stroke="#ca8a04" stroke-width="2" stroke-dasharray="4,2"/>
  <text x="460" y="105" font-family="'Comic Sans MS', sans-serif" font-size="20" font-weight="bold" fill="#854d0e" text-anchor="middle">?</text>
  <text x="410" y="50" font-family="'Comic Sans MS', sans-serif" font-size="18" font-weight="bold" fill="#15803d" text-anchor="middle">2 + [ ? ] on Right</text>
</svg>'''
    save_svg(filename, svg)

def generate_monkeys_option(filename: str, count: int):
    monkeys = "".join(f'<circle cx="{25 + i * 35}" cy="30" r="15" fill="#a16207"/><circle cx="{25 + i * 35}" cy="27" r="10" fill="#fde047"/>' for i in range(count))
    width = max(80, 20 + count * 35)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 60" width="100%" height="100%">
  {monkeys}
</svg>'''
    save_svg(filename, svg)

def generate_number_bond(filename: str, whole=9, part1=4):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 220" width="100%" height="100%">
  <rect width="300" height="220" rx="16" fill="#fdf4ff" stroke="#f0abfc" stroke-width="2"/>
  <line x1="150" y1="60" x2="90" y2="150" stroke="#c084fc" stroke-width="6"/>
  <line x1="150" y1="60" x2="210" y2="150" stroke="#c084fc" stroke-width="6"/>
  <circle cx="150" cy="60" r="35" fill="#9333ea"/>
  <text x="150" y="68" font-family="'Comic Sans MS', sans-serif" font-size="26" font-weight="bold" fill="#fff" text-anchor="middle">{whole}</text>
  <circle cx="90" cy="150" r="30" fill="#3b82f6"/>
  <text x="90" y="158" font-family="'Comic Sans MS', sans-serif" font-size="22" font-weight="bold" fill="#fff" text-anchor="middle">{part1}</text>
  <circle cx="210" cy="150" r="30" fill="#f59e0b" stroke="#d97706" stroke-width="3" stroke-dasharray="6,3"/>
  <text x="210" y="158" font-family="'Comic Sans MS', sans-serif" font-size="24" font-weight="bold" fill="#fff" text-anchor="middle">?</text>
</svg>'''
    save_svg(filename, svg)

def generate_number_line(filename: str):
    ticks = "".join(f'''
      <line x1="{40 + (i-4)*45}" y1="85" x2="{40 + (i-4)*45}" y2="115" stroke="#334155" stroke-width="3"/>
      <text x="{40 + (i-4)*45}" y="140" font-family="sans-serif" font-size="16" font-weight="bold" fill="#334155" text-anchor="middle">{i}</text>
    ''' for i in range(4, 11))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 350 180" width="100%" height="100%">
  <rect width="350" height="180" rx="16" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <line x1="20" y1="100" x2="330" y2="100" stroke="#334155" stroke-width="4"/>
  <polygon points="330,95 340,100 330,105" fill="#334155"/>
  {ticks}
  <!-- Hop arc from 4 to 10 -->
  <path d="M 40,85 Q 175,10 310,85" fill="none" stroke="#e11d48" stroke-width="4" stroke-dasharray="6,4"/>
  <text x="175" y="35" font-family="'Comic Sans MS', sans-serif" font-size="20" font-weight="bold" fill="#e11d48" text-anchor="middle">+ 6 hops</text>
</svg>'''
    save_svg(filename, svg)

def generate_bar_model(filename: str, whole=8, known=5):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 180" width="100%" height="100%">
  <rect width="360" height="180" rx="16" fill="#fff" stroke="#e2e8f0" stroke-width="2"/>
  <rect x="40" y="40" width="280" height="40" rx="6" fill="#3b82f6"/>
  <text x="180" y="66" font-family="sans-serif" font-size="20" font-weight="bold" fill="#fff" text-anchor="middle">Total = {whole}</text>
  <rect x="40" y="95" width="175" height="40" rx="6" fill="#10b981"/>
  <text x="127" y="121" font-family="sans-serif" font-size="18" font-weight="bold" fill="#fff" text-anchor="middle">{known}</text>
  <rect x="225" y="95" width="95" height="40" rx="6" fill="#f59e0b" stroke="#d97706" stroke-width="2" stroke-dasharray="4,2"/>
  <text x="272" y="121" font-family="sans-serif" font-size="22" font-weight="bold" fill="#fff" text-anchor="middle">?</text>
</svg>'''
    save_svg(filename, svg)

def generate_rod(filename: str, length: int, color="#3b82f6"):
    width = length * 35
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width + 20} 50" width="100%" height="100%">
  <rect x="10" y="10" width="{width}" height="30" rx="6" fill="{color}" stroke="#1e293b" stroke-width="2"/>
  <text x="{10 + width/2}" y="31" font-family="sans-serif" font-size="18" font-weight="bold" fill="#fff" text-anchor="middle">{length}</text>
</svg>'''
    save_svg(filename, svg)

def generate_equation_scale(filename: str, text: str):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 140" width="100%" height="100%">
  <rect width="400" height="140" rx="16" fill="#f8fafc" stroke="#3b82f6" stroke-width="3"/>
  <text x="200" y="75" font-family="'Courier New', monospace" font-size="30" font-weight="bold" fill="#1e293b" text-anchor="middle">{text}</text>
</svg>'''
    save_svg(filename, svg)

def generate_balance_pan(filename: str, title: str):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200" width="100%" height="100%">
  <rect width="400" height="200" rx="16" fill="#fefce8" stroke="#facc15" stroke-width="3"/>
  <polygon points="200,120 175,180 225,180" fill="#71717a"/>
  <circle cx="200" cy="120" r="8" fill="#e11d48"/>
  <rect x="60" y="115" width="280" height="10" rx="5" fill="#f59e0b"/>
  <rect x="70" y="105" width="80" height="10" rx="4" fill="#d97706"/>
  <rect x="250" y="105" width="80" height="10" rx="4" fill="#d97706"/>
  <text x="200" y="50" font-family="'Comic Sans MS', sans-serif" font-size="20" font-weight="bold" fill="#854d0e" text-anchor="middle">{title}</text>
</svg>'''
    save_svg(filename, svg)

def generate_mystery_bag_balance(filename: str):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200" width="100%" height="100%">
  <rect width="400" height="200" rx="16" fill="#fefce8" stroke="#facc15" stroke-width="3"/>
  <polygon points="200,130 175,190 225,190" fill="#71717a"/>
  <circle cx="200" cy="130" r="8" fill="#e11d48"/>
  <rect x="60" y="125" width="280" height="10" rx="5" fill="#f59e0b"/>
  
  <!-- Left Side: 5 and 3 blocks -->
  <rect x="80" y="95" width="50" height="30" rx="4" fill="#3b82f6"/>
  <text x="105" y="116" font-family="'Comic Sans MS', sans-serif" font-size="18" font-weight="bold" fill="#fff" text-anchor="middle">5</text>
  <rect x="135" y="95" width="40" height="30" rx="4" fill="#10b981"/>
  <text x="155" y="116" font-family="'Comic Sans MS', sans-serif" font-size="18" font-weight="bold" fill="#fff" text-anchor="middle">3</text>
  
  <!-- Right Side: Mystery Bag -->
  <path d="M 260,80 Q 250,100 250,125 L 330,125 Q 330,100 320,80 Z" fill="#8b5cf6"/>
  <path d="M 265,80 Q 290,90 315,80" stroke="#4c1d95" stroke-width="4" fill="none"/>
  <text x="290" y="115" font-family="'Comic Sans MS', sans-serif" font-size="28" font-weight="bold" fill="#fff" text-anchor="middle">?</text>

  <text x="200" y="45" font-family="'Comic Sans MS', sans-serif" font-size="22" font-weight="bold" fill="#854d0e" text-anchor="middle">Mystery Bag Balance</text>
</svg>'''
    save_svg(filename, svg)


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


def run():

    print("Generating all referenced math & scale SVGs...")
    generate_see_saw("toy_cars_3_4.svg", 7, 3, 4)
    generate_car_set("cars_3.svg", 3, "#3498db")
    generate_car_set("cars_4.svg", 4, "#2ecc71")
    generate_car_set("cars_7.svg", 7, "#e74c3c")
    
    generate_dots("dots_4.svg", 4)
    generate_dots("dots_6.svg", 6)
    generate_dots("dots_10.svg", 10)
    
    generate_ten_frame("ten_frame_6_4.svg", 6, 10)
    generate_ten_frame("ten_frame_counters_6_4.svg", 6, 10)
    
    generate_monkeys_branch("monkeys_branch_5_2.svg")
    generate_monkeys_option("monkeys_2.svg", 2)
    generate_monkeys_option("monkeys_3.svg", 3)
    generate_monkeys_option("monkeys_5.svg", 5)
    
    generate_number_bond("number_bond_9_4.svg", 9, 4)
    generate_number_line("number_line_4_to_10.svg")
    generate_bar_model("bar_model_8_5.svg", 8, 5)
    
    generate_rod("rod_3.svg", 3, "#3b82f6")
    generate_rod("rod_5.svg", 5, "#10b981")
    generate_rod("rod_8.svg", 8, "#8b5cf6")
    
    generate_equation_scale("eq_10_minus_box_eq_4_plus_2.svg", "10 - [ ? ] = 4 + 2")
    generate_equation_scale("eq_3_plus_5_eq_2_plus_box.svg", "3 + 5 = 2 + [ ? ]")
    generate_equation_scale("eq_4_plus_2_eq_6_plus_box.svg", "4 + 2 = 6 + [ ? ]")
    generate_equation_scale("eq_5_plus_box_8.svg", "5 + [ ? ] = 8")
    generate_equation_scale("eq_6_plus_4_eq_box_plus_3.svg", "6 + 4 = [ ? ] + 3")
    generate_equation_scale("eq_box_plus_4_9.svg", "[ ? ] + 4 = 9")
    generate_equation_scale("relational_rule_4_3_7.svg", "4 + 3 = 7")
    generate_equation_scale("structural_law_a_b_c.svg", "A + B = C")
    
    generate_balance_pan("multi_pan_scale_invariant.svg", "Balanced Multi-Pan Scale")
    generate_balance_pan("mystery_box_3_7.svg", "3 + [ ? ] = 7 Scale")
    generate_balance_pan("shape_symbol_square_3_7.svg", "Shape Symbols: ■ + 3 = 7")
    generate_mystery_bag_balance("split_bag_balance_8.svg")
    generate_balance_pan("three_addend_balance_2_3.svg", "2 + 3 + [ ? ] = 10")
    
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

    print("All SVGs successfully created!")

if __name__ == "__main__":
    run()
