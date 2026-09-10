#!/usr/bin/env python3
"""
scripts/visual_asset_builder.py

Generates clear, accurate, high-quality SVGs matching specific question items
(e.g., counting items in a chest, geometric shapes, clocks, scientific tools, animals).
"""

import math

def build_chest_counting_svg(item_type: str, count: int) -> str:
    """Draws an open treasure chest with exactly `count` items arranged to be easily counted."""
    item_type_lower = item_type.lower()
    
    # 2 rows of items max (up to 10 per row)
    rows = 1 if count <= 7 else 2
    per_row = math.ceil(count / rows)
    item_spacing = 22
    
    items_markup = []
    for i in range(count):
        row = i // per_row
        col = i % per_row
        items_in_this_row = min(per_row, count - row * per_row)
        start_x = -((items_in_this_row - 1) * item_spacing) / 2
        x = start_x + col * item_spacing
        y = -18 + row * 24
        
        if "acorn" in item_type_lower:
            items_markup.append(f"""
        <g transform="translate({x}, {y})">
          <ellipse cx="0" cy="5" rx="7" ry="9" fill="#a16207" stroke="#451a03" stroke-width="1.5"/>
          <path d="M -7,0 Q 0,-6 7,0" fill="#451a03" stroke="#292524" stroke-width="1.5"/>
          <rect x="-1" y="-8" width="2" height="4" fill="#292524"/>
        </g>""")
        elif "coin" in item_type_lower:
            items_markup.append(f"""
        <g transform="translate({x}, {y})">
          <circle cx="0" cy="0" r="8.5" fill="#facc15" stroke="#a16207" stroke-width="1.5"/>
          <text x="0" y="3" font-size="9" font-weight="bold" fill="#713f12" text-anchor="middle">★</text>
        </g>""")
        elif "pearl" in item_type_lower:
            items_markup.append(f"""
        <g transform="translate({x}, {y})">
          <circle cx="0" cy="0" r="8" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
          <circle cx="-2" cy="-2" r="3" fill="#ffffff"/>
        </g>""")
        else: # crystals / gems
            items_markup.append(f"""
        <g transform="translate({x}, {y})">
          <polygon points="0,-9 7,0 0,9 -7,0" fill="#38bdf8" stroke="#0284c7" stroke-width="1.5"/>
          <polygon points="0,-6 4,0 0,6 -4,0" fill="#bae6fd" opacity="0.6"/>
        </g>""")

    items_str = "".join(items_markup)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="chestWood" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#854d0e"/><stop offset="100%" stop-color="#451a03"/>
    </linearGradient>
    <linearGradient id="goldTrim" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#fde047"/><stop offset="100%" stop-color="#ca8a04"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#1e1b4b"/>
  <!-- Sparkles in background -->
  <g fill="#fde047" opacity="0.6">
    <circle cx="35" cy="40" r="2"/><circle cx="265" cy="50" r="2.5"/><circle cx="50" cy="160" r="1.5"/><circle cx="250" cy="150" r="2"/>
  </g>
  <!-- Open Chest Base -->
  <g transform="translate(150, 150)">
    <rect x="-95" y="-30" width="190" height="65" rx="10" fill="url(#chestWood)" stroke="#ca8a04" stroke-width="3.5"/>
    <rect x="-90" y="-26" width="180" height="10" fill="#713f12"/>
    <circle cx="0" cy="6" r="8" fill="url(#goldTrim)" stroke="#78350f" stroke-width="1.5"/>
    <rect x="-3" y="6" width="6" height="12" fill="#1e1b4b"/>
  </g>
  <!-- Open Lid Tilted Back -->
  <g transform="translate(150, 115)">
    <path d="M -95,0 Q 0,-38 95,0 L 85,-26 Q 0,-62 -85,-26 Z" fill="url(#chestWood)" stroke="#ca8a04" stroke-width="3"/>
  </g>
  <!-- Glowing Items Inside Chest -->
  <g transform="translate(150, 112)">
{items_str}
  </g>
</svg>"""


def build_polygon_svg(shape_name: str, sides: int) -> str:
    """Draws a crisp geometric polygon with clear vertices."""
    name_clean = shape_name.strip().lower()
    
    if "triangle" in name_clean:
        points = "150,35 70,165 230,165"
        label = "Triangle (3 sides)"
    elif "rectangle" in name_clean:
        points = "60,60 240,60 240,140 60,140"
        label = "Rectangle (4 sides)"
    elif "square" in name_clean:
        points = "80,40 220,40 220,160 80,160"
        label = "Square (4 sides)"
    elif "pentagon" in name_clean:
        points = "150,35 235,95 200,165 100,165 65,95"
        label = "Pentagon (5 sides)"
    elif "hexagon" in name_clean:
        points = "150,35 225,75 225,145 150,185 75,145 75,75"
        label = "Hexagon (6 sides)"
    elif "octagon" in name_clean:
        points = "115,35 185,35 235,85 235,155 185,185 115,185 65,155 65,85"
        label = "Octagon (8 sides)"
    else: # Circle
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f8fafc"/>
  <circle cx="150" cy="100" r="65" fill="#60a5fa" stroke="#2563eb" stroke-width="4"/>
  <text x="150" y="185" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Circle (Curved boundary)</text>
</svg>"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="polyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/><stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#f8fafc"/>
  <polygon points="{points}" fill="url(#polyGrad)" stroke="#0369a1" stroke-width="4"/>
  <text x="150" y="190" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">{label}</text>
</svg>"""


def build_3d_shape_svg(shape_3d: str) -> str:
    """Draws 3D shapes: Sphere, Cube, Cylinder, Cone."""
    s_clean = shape_3d.strip().lower()
    
    if "sphere" in s_clean:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <radialGradient id="sphereGrad" cx="35%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#93c5fd"/><stop offset="60%" stop-color="#2563eb"/><stop offset="100%" stop-color="#1e3a8a"/>
    </radialGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#f1f5f9"/>
  <ellipse cx="150" cy="165" rx="60" ry="12" fill="#cbd5e1"/>
  <circle cx="150" cy="100" r="55" fill="url(#sphereGrad)"/>
  <text x="150" y="185" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Sphere (3D Ball)</text>
</svg>"""
    elif "cube" in s_clean:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f1f5f9"/>
  <ellipse cx="150" cy="165" rx="65" ry="14" fill="#cbd5e1"/>
  <!-- Top Face -->
  <polygon points="150,45 205,75 150,105 95,75" fill="#93c5fd" stroke="#1d4ed8" stroke-width="2.5"/>
  <!-- Left Face -->
  <polygon points="95,75 150,105 150,165 95,135" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2.5"/>
  <!-- Right Face -->
  <polygon points="150,105 205,75 205,135 150,165" fill="#1d4ed8" stroke="#1d4ed8" stroke-width="2.5"/>
  <text x="150" y="188" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Cube (3D Box)</text>
</svg>"""
    elif "cylinder" in s_clean:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f1f5f9"/>
  <ellipse cx="150" cy="165" rx="50" ry="12" fill="#cbd5e1"/>
  <!-- Cylinder Body -->
  <path d="M 105,75 L 105,150 A 45,14 0 0,0 195,150 L 195,75 Z" fill="#60a5fa" stroke="#1d4ed8" stroke-width="2.5"/>
  <!-- Bottom Rim -->
  <ellipse cx="150" cy="150" rx="45" ry="14" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2"/>
  <!-- Top Rim -->
  <ellipse cx="150" cy="75" rx="45" ry="14" fill="#93c5fd" stroke="#1d4ed8" stroke-width="2.5"/>
  <text x="150" y="188" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Cylinder (3D Column)</text>
</svg>"""
    else: # Cone
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f1f5f9"/>
  <ellipse cx="150" cy="165" rx="55" ry="12" fill="#cbd5e1"/>
  <!-- Cone Body -->
  <path d="M 150,45 L 95,150 A 55,15 0 0,0 205,150 Z" fill="#60a5fa" stroke="#1d4ed8" stroke-width="2.5"/>
  <!-- Cone Base -->
  <ellipse cx="150" cy="150" rx="55" ry="15" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2"/>
  <text x="150" y="188" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Cone (3D Hat)</text>
</svg>"""


def build_analog_clock_svg(hour: int) -> str:
    """Draws an analog clock with minute hand on 12 and hour hand on `hour`."""
    angle_deg = (hour % 12) * 30
    angle_rad = math.radians(angle_deg - 90)
    hx = 150 + 32 * math.cos(angle_rad)
    hy = 100 + 32 * math.sin(angle_rad)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f8fafc"/>
  <!-- Clock Outer Rim -->
  <circle cx="150" cy="100" r="70" fill="#ffffff" stroke="#0284c7" stroke-width="6"/>
  <!-- Clock Numbers -->
  <text x="150" y="48" font-size="13" font-weight="bold" fill="#1e293b" text-anchor="middle">12</text>
  <text x="204" y="104" font-size="13" font-weight="bold" fill="#1e293b" text-anchor="middle">3</text>
  <text x="150" y="160" font-size="13" font-weight="bold" fill="#1e293b" text-anchor="middle">6</text>
  <text x="96" y="104" font-size="13" font-weight="bold" fill="#1e293b" text-anchor="middle">9</text>
  <!-- Minute Hand (points straight up to 12) -->
  <line x1="150" y1="100" x2="150" y2="52" stroke="#0f172a" stroke-width="3" stroke-linecap="round"/>
  <!-- Hour Hand (points to {hour}) -->
  <line x1="150" y1="100" x2="{hx:.1f}" y2="{hy:.1f}" stroke="#dc2626" stroke-width="4.5" stroke-linecap="round"/>
  <!-- Center Pin -->
  <circle cx="150" cy="100" r="4.5" fill="#dc2626"/>
</svg>"""


def build_tool_svg(tool_name: str) -> str:
    """Draws scientific measurement tools: Thermometer, Scale, Ruler, Microscope, Magnet."""
    t = tool_name.lower()
    if "thermometer" in t:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f8fafc"/>
  <!-- Thermometer Tube -->
  <rect x="142" y="35" width="16" height="110" rx="8" fill="#e2e8f0" stroke="#94a3b8" stroke-width="2"/>
  <rect x="146" y="70" width="8" height="75" rx="4" fill="#ef4444"/>
  <circle cx="150" cy="150" r="18" fill="#ef4444" stroke="#b91c1c" stroke-width="2"/>
  <!-- Degree tick marks -->
  <line x1="162" y1="50" x2="170" y2="50" stroke="#64748b" stroke-width="2"/>
  <line x1="162" y1="70" x2="170" y2="70" stroke="#64748b" stroke-width="2"/>
  <line x1="162" y1="90" x2="170" y2="90" stroke="#64748b" stroke-width="2"/>
  <line x1="162" y1="110" x2="170" y2="110" stroke="#64748b" stroke-width="2"/>
  <text x="150" y="190" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Thermometer (Measures Temperature)</text>
</svg>"""
    elif "scale" in t:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f8fafc"/>
  <!-- Balance Scale Base & Post -->
  <polygon points="120,165 180,165 155,100 145,100" fill="#475569"/>
  <rect x="147" y="55" width="6" height="95" fill="#334155"/>
  <line x1="75" y1="65" x2="225" y2="65" stroke="#0f172a" stroke-width="4"/>
  <!-- Left Pan -->
  <line x1="75" y1="65" x2="55" y2="115" stroke="#64748b" stroke-width="1.5"/>
  <line x1="75" y1="65" x2="95" y2="115" stroke="#64748b" stroke-width="1.5"/>
  <path d="M 45,115 Q 75,135 105,115 Z" fill="#94a3b8" stroke="#475569" stroke-width="2"/>
  <!-- Right Pan -->
  <line x1="225" y1="65" x2="205" y2="115" stroke="#64748b" stroke-width="1.5"/>
  <line x1="225" y1="65" x2="245" y2="115" stroke="#64748b" stroke-width="1.5"/>
  <path d="M 195,115 Q 225,135 255,115 Z" fill="#94a3b8" stroke="#475569" stroke-width="2"/>
  <text x="150" y="188" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Balance Scale (Measures Mass)</text>
</svg>"""
    elif "ruler" in t:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f8fafc"/>
  <rect x="35" y="80" width="230" height="40" rx="4" fill="#fde047" stroke="#ca8a04" stroke-width="2.5"/>
  <!-- Tick Marks -->
  <g stroke="#854d0e" stroke-width="1.5">
    <line x1="50" y1="80" x2="50" y2="98"/><text x="50" y="112" font-size="10" font-weight="bold" fill="#713f12" text-anchor="middle">0</text>
    <line x1="85" y1="80" x2="85" y2="94"/>
    <line x1="120" y1="80" x2="120" y2="98"/><text x="120" y="112" font-size="10" font-weight="bold" fill="#713f12" text-anchor="middle">5</text>
    <line x1="155" y1="80" x2="155" y2="94"/>
    <line x1="190" y1="80" x2="190" y2="98"/><text x="190" y="112" font-size="10" font-weight="bold" fill="#713f12" text-anchor="middle">10</text>
    <line x1="225" y1="80" x2="225" y2="94"/>
    <line x1="250" y1="80" x2="250" y2="98"/><text x="250" y="112" font-size="10" font-weight="bold" fill="#713f12" text-anchor="middle">15</text>
  </g>
  <text x="150" y="160" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Ruler (Measures Length)</text>
</svg>"""
    elif "microscope" in t:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f8fafc"/>
  <!-- Microscope Base & Arm -->
  <path d="M 100,165 L 200,165 L 180,150 L 120,150 Z" fill="#334155"/>
  <path d="M 160,150 C 185,150 200,120 190,90 C 180,60 160,50 140,50" fill="none" stroke="#475569" stroke-width="12"/>
  <!-- Objective Lens & Tube -->
  <rect x="120" y="40" width="22" height="60" rx="3" fill="#64748b" stroke="#334155" stroke-width="2" transform="rotate(-15 130 70)"/>
  <!-- Stage -->
  <line x1="110" y1="125" x2="165" y2="125" stroke="#0f172a" stroke-width="5"/>
  <text x="150" y="188" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Microscope (Magnifies Specimens)</text>
</svg>"""
    else: # Magnet
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f8fafc"/>
  <!-- Horseshoe Magnet -->
  <path d="M 105,140 L 105,80 A 45,45 0 0,1 195,80 L 195,140" fill="none" stroke="#ef4444" stroke-width="28"/>
  <!-- Blue / Silver poles -->
  <rect x="91" y="125" width="28" height="20" fill="#3b82f6"/>
  <rect x="181" y="125" width="28" height="20" fill="#94a3b8"/>
  <text x="105" y="140" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">N</text>
  <text x="195" y="140" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">S</text>
  <text x="150" y="185" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Magnet (Attracts Iron)</text>
</svg>"""


def build_creature_or_entity_svg(key: str) -> str:
    """Draws scientific specimens: Shark, Spider, Oak Tree, Camel, Dolphin, Heart, Sun, etc."""
    k = key.lower()
    if "shark" in k:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#e0f2fe"/>
  <!-- Shark Body -->
  <g transform="translate(150, 100)">
    <path d="M -80,10 Q 0,-35 85,-10 Q 95,0 80,10 Q 0,35 -80,10 Z" fill="#64748b" stroke="#334155" stroke-width="2"/>
    <!-- Dorsal Fin -->
    <polygon points="10,-22 25,-55 45,-20" fill="#64748b" stroke="#334155" stroke-width="2"/>
    <!-- Tail Fin -->
    <polygon points="-80,10 -115,-20 -95,10 -115,35" fill="#64748b" stroke="#334155" stroke-width="2"/>
    <!-- Pectoral Fin -->
    <polygon points="15,15 25,45 45,20" fill="#475569"/>
    <!-- Gills -->
    <line x1="30" y1="-8" x2="30" y2="8" stroke="#334155" stroke-width="2"/>
    <line x1="35" y1="-8" x2="35" y2="8" stroke="#334155" stroke-width="2"/>
    <line x1="40" y1="-8" x2="40" y2="8" stroke="#334155" stroke-width="2"/>
    <!-- Eye -->
    <circle cx="65" cy="-6" r="3" fill="#0f172a"/>
  </g>
  <text x="150" y="185" font-size="14" font-weight="bold" fill="#0369a1" text-anchor="middle">Shark (Breathes with Gills)</text>
</svg>"""
    elif "spider" in k:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f8fafc"/>
  <g transform="translate(150, 95)">
    <!-- 8 Legs -->
    <path d="M -20,-10 Q -55,-45 -70,-20 M -25,0 Q -65,-10 -75,15 M -25,10 Q -65,25 -65,55 M -20,18 Q -50,55 -40,75" fill="none" stroke="#1e293b" stroke-width="3.5" stroke-linecap="round"/>
    <path d="M 20,-10 Q 55,-45 70,-20 M 25,0 Q 65,-10 75,15 M 25,10 Q 65,25 65,55 M 20,18 Q 50,55 40,75" fill="none" stroke="#1e293b" stroke-width="3.5" stroke-linecap="round"/>
    <!-- Abdomen -->
    <ellipse cx="0" cy="18" rx="20" ry="26" fill="#0f172a"/>
    <!-- Cephalothorax -->
    <circle cx="0" cy="-12" r="14" fill="#1e293b"/>
    <!-- Eyes -->
    <circle cx="-4" cy="-16" r="2.5" fill="#f87171"/><circle cx="4" cy="-16" r="2.5" fill="#f87171"/>
  </g>
  <text x="150" y="188" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Spider (8 Jointed Legs)</text>
</svg>"""
    elif "camel" in k:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#fef3c7"/>
  <!-- Sand Dune -->
  <path d="M 0,160 Q 150,130 300,165 L 300,200 L 0,200 Z" fill="#fde68a"/>
  <!-- Camel Body with Hump -->
  <g transform="translate(150, 115)">
    <ellipse cx="0" cy="0" rx="42" ry="28" fill="#d97706"/>
    <!-- Hump -->
    <circle cx="5" cy="-22" r="20" fill="#d97706"/>
    <!-- Neck & Head -->
    <path d="M -30,-5 Q -55,-25 -45,-50 Q -35,-55 -30,-45" fill="none" stroke="#d97706" stroke-width="12" stroke-linecap="round"/>
    <!-- Legs -->
    <line x1="-25" y1="20" x2="-28" y2="55" stroke="#b45309" stroke-width="6"/>
    <line x1="-10" y1="20" x2="-10" y2="55" stroke="#d97706" stroke-width="6"/>
    <line x1="15" y1="20" x2="15" y2="55" stroke="#b45309" stroke-width="6"/>
    <line x1="30" y1="20" x2="32" y2="55" stroke="#d97706" stroke-width="6"/>
  </g>
  <text x="150" y="188" font-size="14" font-weight="bold" fill="#78350f" text-anchor="middle">Camel (Desert Adaptation)</text>
</svg>"""
    elif "tree" in k:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f0fdf4"/>
  <ellipse cx="150" cy="170" rx="90" ry="12" fill="#dcfce7"/>
  <!-- Trunk -->
  <rect x="138" y="95" width="24" height="75" rx="4" fill="#78350f"/>
  <!-- Foliage Canopy -->
  <circle cx="150" cy="70" r="45" fill="#16a34a"/>
  <circle cx="115" cy="85" r="35" fill="#22c55e"/>
  <circle cx="185" cy="85" r="35" fill="#15803d"/>
  <text x="150" y="188" font-size="14" font-weight="bold" fill="#166534" text-anchor="middle">Oak Tree (Grows from Acorn)</text>
</svg>"""
    elif "heart" in k:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <radialGradient id="heartGlow" cx="40%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#f87171"/><stop offset="100%" stop-color="#b91c1c"/>
    </radialGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#fef2f2"/>
  <path d="M 150,65 C 150,35 110,35 110,65 C 110,95 150,135 150,145 C 150,135 190,95 190,65 C 190,35 150,35 150,65 Z" fill="url(#heartGlow)" stroke="#991b1b" stroke-width="3"/>
  <text x="150" y="185" font-size="14" font-weight="bold" fill="#991b1b" text-anchor="middle">The Heart (Pumps Blood)</text>
</svg>"""
    else: # Sun / Celestial
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fef08a"/><stop offset="70%" stop-color="#eab308"/><stop offset="100%" stop-color="#ca8a04"/>
    </radialGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#0f172a"/>
  <!-- Sun Rays -->
  <g stroke="#facc15" stroke-width="4" stroke-linecap="round">
    <line x1="150" y1="35" x2="150" y2="15"/>
    <line x1="150" y1="165" x2="150" y2="185"/>
    <line x1="85" y1="100" x2="65" y2="100"/>
    <line x1="215" y1="100" x2="235" y2="100"/>
    <line x1="105" y1="55" x2="90" y2="40"/>
    <line x1="195" y1="145" x2="210" y2="160"/>
    <line x1="105" y1="145" x2="90" y2="160"/>
    <line x1="195" y1="55" x2="210" y2="40"/>
  </g>
  <circle cx="150" cy="100" r="45" fill="url(#sunGlow)"/>
  <text x="150" y="188" font-size="14" font-weight="bold" fill="#fef08a" text-anchor="middle">The Sun (Our Closest Star)</text>
</svg>"""


def build_landmark_svg(landmark_name: str) -> str:
    """Draws famous world landmarks: Pyramids, Eiffel Tower."""
    l = landmark_name.lower()
    if "pyramid" in l:
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#e0f2fe"/>
  <path d="M 0,155 Q 150,135 300,160 L 300,200 L 0,200 Z" fill="#fde68a"/>
  <!-- Great Pyramid -->
  <polygon points="150,55 70,160 175,160" fill="#d97706" stroke="#b45309" stroke-width="2"/>
  <polygon points="150,55 175,160 215,155" fill="#b45309" stroke="#92400e" stroke-width="2"/>
  <!-- Small Pyramid -->
  <polygon points="215,95 170,160 250,160" fill="#f59e0b" stroke="#d97706" stroke-width="1.5"/>
  <text x="150" y="188" font-size="14" font-weight="bold" fill="#78350f" text-anchor="middle">Pyramids of Giza (Africa)</text>
</svg>"""
    else: # Eiffel Tower
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f1f5f9"/>
  <!-- Eiffel Tower -->
  <path d="M 147,25 L 153,25 L 155,75 L 165,125 L 185,165 L 165,165 L 158,135 Q 150,120 142,135 L 135,165 L 115,165 L 135,125 L 145,75 Z" fill="#475569" stroke="#1e293b" stroke-width="2"/>
  <line x1="140" y1="80" x2="160" y2="80" stroke="#1e293b" stroke-width="3"/>
  <line x1="132" y1="125" x2="168" y2="125" stroke="#1e293b" stroke-width="3"/>
  <text x="150" y="188" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Eiffel Tower (Europe)</text>
</svg>"""
