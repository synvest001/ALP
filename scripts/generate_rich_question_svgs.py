import os
import glob
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_SVG_DIR = BASE_DIR / "frontend" / "public" / "assets" / "svg"
DIST_SVG_DIR = BASE_DIR / "frontend" / "dist" / "assets" / "svg"
DATA_DIR = BASE_DIR / "frontend" / "public" / "data" / "question_bank"

PUBLIC_SVG_DIR.mkdir(parents=True, exist_ok=True)
DIST_SVG_DIR.mkdir(parents=True, exist_ok=True)

print("Compiling full high-fidelity SVG illustration library...")

LIBRARY = {}

# ==========================================
# 1. EVS (SCIENCE & NATURE) - PREMIUM ASSETS
# ==========================================

LIBRARY["plant_growth"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#bae6fd"/>
      <stop offset="60%" stop-color="#e0f2fe"/>
      <stop offset="100%" stop-color="#f0fdf4"/>
    </linearGradient>
    <linearGradient id="leafGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#4ade80"/>
      <stop offset="100%" stop-color="#15803d"/>
    </linearGradient>
    <linearGradient id="soilGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#854d0e"/>
      <stop offset="100%" stop-color="#582f0e"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="url(#skyGrad)"/>
  <g transform="translate(240, 45)">
    <circle cx="0" cy="0" r="28" fill="#facc15" stroke="#f59e0b" stroke-width="3"/>
    <g stroke="#f59e0b" stroke-width="3" stroke-linecap="round">
      <line x1="0" y1="-38" x2="0" y2="-45"/><line x1="27" y1="-27" x2="33" y2="-33"/>
      <line x1="38" y1="0" x2="45" y2="0"/><line x1="27" y1="27" x2="33" y2="33"/>
      <line x1="-27" y1="-27" x2="-33" y2="-33"/><line x1="-38" y1="0" x2="-45" y2="0"/>
    </g>
    <circle cx="-8" cy="-3" r="3" fill="#854d0e"/><circle cx="8" cy="-3" r="3" fill="#854d0e"/>
    <path d="M -8,8 Q 0,16 8,8" fill="none" stroke="#854d0e" stroke-width="2.5" stroke-linecap="round"/>
  </g>
  <path d="M 20,40 Q 30,25 45,30 Q 60,20 75,32 Q 90,28 95,45 Q 85,55 20,55 Z" fill="#ffffff" opacity="0.9"/>
  <g fill="#0284c7" opacity="0.85">
    <path d="M 80,75 C 80,75 75,85 75,90 A 5,5 0 0,0 85,90 C 85,85 80,75 80,75 Z"/>
    <path d="M 105,65 C 105,65 100,75 100,80 A 5,5 0 0,0 110,80 C 110,75 105,65 105,65 Z"/>
    <path d="M 95,95 C 95,95 90,105 90,110 A 5,5 0 0,0 100,110 C 100,105 95,95 95,95 Z"/>
  </g>
  <rect x="0" y="150" width="300" height="50" fill="url(#soilGrad)"/>
  <ellipse cx="150" cy="152" rx="140" ry="10" fill="#713f12"/>
  <g transform="translate(150, 150)">
    <path d="M 0,0 Q -2,-45 0,-85" fill="none" stroke="#16a34a" stroke-width="8" stroke-linecap="round"/>
    <path d="M 0,-45 C -40,-45 -55,-70 -35,-85 C -20,-75 -5,-55 0,-45 Z" fill="url(#leafGrad)" stroke="#15803d" stroke-width="2"/>
    <path d="M 0,-45 Q -20,-62 -35,-85" fill="none" stroke="#86efac" stroke-width="2"/>
    <path d="M 0,-65 C 40,-65 55,-90 35,-105 C 20,-95 5,-75 0,-65 Z" fill="url(#leafGrad)" stroke="#15803d" stroke-width="2"/>
    <path d="M 0,-65 Q 20,-82 35,-105" fill="none" stroke="#86efac" stroke-width="2"/>
    <circle cx="0" cy="-88" r="8" fill="#facc15" stroke="#eab308" stroke-width="2"/>
    <path d="M 0,-96 C -10,-108 0,-118 0,-118 C 0,-118 10,-108 0,-96 Z" fill="#22c55e"/>
  </g>
</svg>"""

LIBRARY["plant_roots"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="rootSoil" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#78350f"/><stop offset="100%" stop-color="#3c1d07"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#fefce8"/>
  <rect x="0" y="0" width="300" height="60" fill="#dcfce7"/>
  <path d="M 150,60 L 150,20" stroke="#16a34a" stroke-width="8" stroke-linecap="round"/>
  <path d="M 150,35 C 120,25 110,5 130,-5 C 145,15 150,25 150,35 Z" fill="#22c55e" stroke="#15803d" stroke-width="2"/>
  <path d="M 150,25 C 180,15 190,-5 170,-15 C 155,5 150,15 150,25 Z" fill="#22c55e" stroke="#15803d" stroke-width="2"/>
  <rect x="0" y="60" width="300" height="140" fill="url(#rootSoil)"/>
  <path d="M 0,60 Q 75,55 150,60 T 300,60" fill="none" stroke="#15803d" stroke-width="5"/>
  <g stroke="#fde047" stroke-linecap="round" fill="none">
    <path d="M 150,60 Q 155,100 148,140 T 152,185" stroke-width="7"/>
    <path d="M 150,85 Q 120,95 90,115 T 50,135" stroke-width="4.5"/>
    <path d="M 110,102 Q 95,120 70,130" stroke-width="3"/>
    <path d="M 148,115 Q 125,130 100,155 T 75,175" stroke-width="4"/>
    <path d="M 120,138 Q 110,160 95,170" stroke-width="2.5"/>
    <path d="M 152,90 Q 185,100 215,120 T 255,140" stroke-width="4.5"/>
    <path d="M 190,105 Q 210,125 230,135" stroke-width="3"/>
    <path d="M 150,125 Q 175,140 205,165 T 235,180" stroke-width="4"/>
    <path d="M 180,145 Q 195,165 210,175" stroke-width="2.5"/>
  </g>
  <g fill="#38bdf8" opacity="0.9">
    <circle cx="80" cy="110" r="4.5"/><circle cx="60" cy="140" r="4.5"/>
    <circle cx="115" cy="165" r="4.5"/><circle cx="195" cy="120" r="4.5"/>
    <circle cx="230" cy="150" r="4.5"/><circle cx="170" cy="175" r="4.5"/>
  </g>
</svg>"""

LIBRARY["leaves_sunlight"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="sunbeam" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#fef08a" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#fef08a" stop-opacity="0.05"/>
    </linearGradient>
    <linearGradient id="bigLeaf" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#4ade80"/>
      <stop offset="100%" stop-color="#166534"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#f0fdf4"/>
  <polygon points="20,0 120,0 200,160 60,160" fill="url(#sunbeam)"/>
  <polygon points="140,0 240,0 280,180 170,180" fill="url(#sunbeam)"/>
  <circle cx="60" cy="20" r="35" fill="#facc15" stroke="#f59e0b" stroke-width="4"/>
  <g transform="translate(150, 115) rotate(-15)">
    <path d="M -90,0 C -60,-70 50,-70 90,0 C 50,70 -60,70 -90,0 Z" fill="url(#bigLeaf)" stroke="#14532d" stroke-width="3"/>
    <line x1="-85" y1="0" x2="85" y2="0" stroke="#bbf7d0" stroke-width="4" stroke-linecap="round"/>
    <g stroke="#bbf7d0" stroke-width="2.5" stroke-linecap="round">
      <line x1="-50" y1="0" x2="-30" y2="-35"/><line x1="-50" y1="0" x2="-30" y2="35"/>
      <line x1="-15" y1="0" x2="10" y2="-42"/><line x1="-15" y1="0" x2="10" y2="42"/>
      <line x1="20" y1="0" x2="48" y2="-36"/><line x1="20" y1="0" x2="48" y2="36"/>
      <line x1="55" y1="0" x2="72" y2="-20"/><line x1="55" y1="0" x2="72" y2="20"/>
    </g>
    <ellipse cx="20" cy="-22" rx="9" ry="6" fill="#38bdf8" opacity="0.85" stroke="#ffffff" stroke-width="1.5"/>
    <circle cx="17" cy="-24" r="2" fill="#ffffff"/>
  </g>
</svg>"""

LIBRARY["sprouting_seed"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="seedSoil" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#713f12"/><stop offset="100%" stop-color="#451a03"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#fefce8"/>
  <rect x="0" y="90" width="300" height="110" fill="url(#seedSoil)"/>
  <path d="M 0,90 Q 75,85 150,90 T 300,90" stroke="#15803d" stroke-width="4" fill="none"/>
  <ellipse cx="60" cy="120" rx="6" ry="4" fill="#582f0e"/><ellipse cx="240" cy="140" rx="8" ry="5" fill="#582f0e"/>
  <g transform="translate(150, 115)">
    <path d="M 5,10 Q 15,35 8,60 T 12,75" fill="none" stroke="#fef08a" stroke-width="4.5" stroke-linecap="round"/>
    <path d="M 10,35 Q 25,48 30,55" fill="none" stroke="#fef08a" stroke-width="2.5" stroke-linecap="round"/>
    <path d="M -15,5 C -25,-10 -5,-25 15,-15 C 25,-5 20,15 5,20 C -10,25 -20,15 -15,5 Z" fill="#92400e" stroke="#713f12" stroke-width="2.5"/>
    <path d="M -5,12 C 5,8 10,-2 8,-12" fill="none" stroke="#fde047" stroke-width="3"/>
    <path d="M 0,-10 Q -5,-35 0,-65" fill="none" stroke="#22c55e" stroke-width="6" stroke-linecap="round"/>
    <path d="M 0,-65 C -25,-65 -35,-85 -20,-92 C -10,-85 0,-75 0,-65 Z" fill="#4ade80" stroke="#16a34a" stroke-width="2"/>
    <path d="M 0,-65 C 25,-65 35,-85 20,-92 C 10,-85 0,-75 0,-65 Z" fill="#4ade80" stroke="#16a34a" stroke-width="2"/>
  </g>
  <circle cx="150" cy="20" r="18" fill="#facc15" opacity="0.6"/>
</svg>"""

LIBRARY["polar_ice"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="aurora" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.4"/>
      <stop offset="50%" stop-color="#a855f7" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#22c55e" stop-opacity="0.4"/>
    </linearGradient>
    <linearGradient id="iceGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff"/><stop offset="40%" stop-color="#e0f2fe"/><stop offset="100%" stop-color="#7dd3fc"/>
    </linearGradient>
    <linearGradient id="seaGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0284c7"/><stop offset="100%" stop-color="#082f49"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#0f172a"/>
  <path d="M 0,30 Q 80,60 150,25 T 300,45 L 300,80 Q 220,50 150,75 T 0,60 Z" fill="url(#aurora)"/>
  <polygon points="20,120 70,70 120,120" fill="#334155"/>
  <polygon points="55,85 70,70 85,85 70,95" fill="#f8fafc"/>
  <polygon points="180,120 235,65 290,120" fill="#334155"/>
  <polygon points="220,80 235,65 250,80 235,90" fill="#f8fafc"/>
  <rect x="0" y="120" width="300" height="80" fill="url(#seaGrad)"/>
  <polygon points="30,140 70,110 180,110 215,140 170,165 60,165" fill="url(#iceGrad)" stroke="#38bdf8" stroke-width="2"/>
  <g transform="translate(125, 110)">
    <ellipse cx="0" cy="-18" rx="28" ry="20" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
    <ellipse cx="-24" cy="-28" rx="14" ry="12" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
    <ellipse cx="-34" cy="-27" rx="6" ry="5" fill="#f1f5f9"/>
    <ellipse cx="-37" cy="-28" rx="2.5" ry="2" fill="#0f172a"/>
    <circle cx="-25" cy="-32" r="2" fill="#0f172a"/>
    <circle cx="-16" cy="-37" r="4.5" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/>
    <rect x="-22" y="-6" width="10" height="15" rx="5" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
    <rect x="8" y="-6" width="10" height="15" rx="5" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
    <circle cx="28" cy="-22" r="4" fill="#ffffff"/>
  </g>
  <g transform="translate(180, 118)">
    <ellipse cx="0" cy="-12" rx="7" ry="12" fill="#0f172a"/>
    <ellipse cx="0" cy="-10" rx="4.5" ry="9" fill="#ffffff"/>
    <polygon points="-7,-12 -3,-14 -3,-8" fill="#f97316"/>
    <circle cx="-1" cy="-18" r="1.5" fill="#ffffff"/>
  </g>
</svg>"""

LIBRARY["desert_camel"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="desertSky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fdba74"/><stop offset="60%" stop-color="#fed7aa"/><stop offset="100%" stop-color="#fef08a"/>
    </linearGradient>
    <linearGradient id="duneGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#fde047"/><stop offset="100%" stop-color="#d97706"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="url(#desertSky)"/>
  <circle cx="230" cy="45" r="30" fill="#f59e0b" opacity="0.9"/>
  <circle cx="230" cy="45" r="42" fill="#fbbf24" opacity="0.3"/>
  <path d="M 0,110 Q 70,80 160,115 T 300,95 L 300,200 L 0,200 Z" fill="url(#duneGrad)" opacity="0.8"/>
  <path d="M 0,140 Q 110,110 200,145 T 300,130 L 300,200 L 0,200 Z" fill="#b45309"/>
  <g transform="translate(45, 120)" fill="#15803d" stroke="#14532d" stroke-width="2">
    <rect x="-5" y="-45" width="10" height="50" rx="5"/>
    <path d="M -5,-25 H -18 V -40" fill="none" stroke-width="6" stroke-linecap="round"/>
    <path d="M 5,-15 H 18 V -30" fill="none" stroke-width="6" stroke-linecap="round"/>
  </g>
  <g transform="translate(155, 128)" stroke="#78350f" stroke-width="2" fill="#d97706">
    <line x1="-20" y1="10" x2="-22" y2="42" stroke="#b45309" stroke-width="5" stroke-linecap="round"/>
    <line x1="-8" y1="10" x2="-6" y2="42" stroke="#b45309" stroke-width="5" stroke-linecap="round"/>
    <line x1="12" y1="10" x2="10" y2="42" stroke="#b45309" stroke-width="5" stroke-linecap="round"/>
    <line x1="24" y1="10" x2="26" y2="42" stroke="#b45309" stroke-width="5" stroke-linecap="round"/>
    <ellipse cx="0" cy="0" rx="30" ry="18"/>
    <circle cx="-12" cy="-16" r="14"/><circle cx="12" cy="-16" r="13"/>
    <rect x="-8" y="-14" width="16" height="18" rx="3" fill="#ef4444" stroke="#b91c1c" stroke-width="1.5"/>
    <path d="M 22,5 C 32,-5 36,-25 42,-35 C 44,-38 52,-38 55,-32 C 58,-28 54,-20 45,-15 C 38,-10 32,5 25,12 Z" fill="#d97706"/>
    <circle cx="48" cy="-33" r="2.5" fill="#451a03"/>
    <polygon points="41,-38 44,-45 47,-38" fill="#b45309"/>
    <path d="M -30,0 Q -38,15 -35,25" fill="none" stroke="#b45309" stroke-width="3" stroke-linecap="round"/>
  </g>
</svg>"""

LIBRARY["ocean_dolphin"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="seaDeep" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#38bdf8"/><stop offset="50%" stop-color="#0284c7"/><stop offset="100%" stop-color="#0c4a6e"/>
    </linearGradient>
    <linearGradient id="dolphinGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#e0f2fe"/><stop offset="50%" stop-color="#38bdf8"/><stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="url(#seaDeep)"/>
  <polygon points="40,0 80,0 120,200 60,200" fill="#ffffff" opacity="0.12"/>
  <polygon points="140,0 180,0 220,200 160,200" fill="#ffffff" opacity="0.12"/>
  <g transform="translate(0, 160)">
    <path d="M 10,40 Q 25,5 40,40 Q 55,10 70,40 Z" fill="#f43f5e"/>
    <path d="M 60,40 Q 75,-5 90,40 Q 105,15 120,40 Z" fill="#ec4899"/>
    <path d="M 200,40 Q 220,0 240,40 Q 255,10 270,40 Z" fill="#10b981"/>
  </g>
  <g fill="#ffffff" opacity="0.6">
    <circle cx="80" cy="120" r="4"/><circle cx="95" cy="95" r="6"/>
  </g>
  <g transform="translate(150, 85) rotate(-15)">
    <path d="M -70,25 C -40,-25 30,-30 70,5 C 50,25 -20,35 -70,25 Z" fill="url(#dolphinGrad)" stroke="#0369a1" stroke-width="2"/>
    <path d="M -50,23 C -20,-5 25,-10 55,8 C 30,22 -15,28 -50,23 Z" fill="#f0f9ff" opacity="0.7"/>
    <path d="M 68,3 C 78,6 82,10 70,14 Z" fill="#38bdf8" stroke="#0369a1" stroke-width="1.5"/>
    <path d="M -5,-25 C 0,-45 15,-40 18,-26 Z" fill="#0284c7" stroke="#0369a1" stroke-width="1.5"/>
    <path d="M 10,15 C 20,35 10,40 0,25 Z" fill="#0284c7" stroke="#0369a1" stroke-width="1.5"/>
    <polygon points="-70,25 -88,10 -80,25 -92,38 -70,28" fill="#0284c7" stroke="#0369a1" stroke-width="1.5"/>
    <circle cx="50" cy="2" r="2.5" fill="#0f172a"/>
    <path d="M 54,8 Q 62,11 68,7" fill="none" stroke="#0369a1" stroke-width="1.5" stroke-linecap="round"/>
  </g>
</svg>"""

LIBRARY["bird_nest"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="skyNest" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#dbeafe"/><stop offset="100%" stop-color="#f0fdf4"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="url(#skyNest)"/>
  <g fill="#78350f" stroke="#451a03" stroke-width="3">
    <path d="M 0,20 Q 40,70 80,120 L 0,200 Z"/>
    <path d="M 50,105 Q 120,115 220,135 Q 260,140 300,130 L 300,165 Q 200,175 40,140 Z"/>
  </g>
  <g fill="#22c55e" stroke="#15803d" stroke-width="2">
    <path d="M 30,70 C 15,50 40,30 55,50 C 65,70 45,80 30,70 Z"/>
    <path d="M 230,110 C 220,85 250,75 260,95 C 270,115 245,125 230,110 Z"/>
  </g>
  <g transform="translate(150, 115)">
    <ellipse cx="0" cy="0" rx="48" ry="18" fill="#713f12" stroke="#451a03" stroke-width="2.5"/>
    <g fill="#7dd3fc" stroke="#0284c7" stroke-width="2">
      <ellipse cx="-18" cy="-5" rx="10" ry="14" transform="rotate(-15 -18 -5)"/>
      <ellipse cx="2" cy="-8" rx="10" ry="14"/>
      <ellipse cx="20" cy="-4" rx="10" ry="14" transform="rotate(15 20 -4)"/>
    </g>
    <circle cx="-16" cy="-6" r="1.5" fill="#0369a1"/><circle cx="4" cy="-10" r="1.5" fill="#0369a1"/><circle cx="22" cy="-4" r="1.5" fill="#0369a1"/>
    <path d="M -50,0 C -50,35 50,35 50,0 C 35,8 -35,8 -50,0 Z" fill="#92400e" stroke="#451a03" stroke-width="3"/>
    <g stroke="#b45309" stroke-width="2" stroke-linecap="round">
      <path d="M -45,5 Q 0,28 45,5"/><path d="M -40,14 Q 0,34 40,14"/>
    </g>
  </g>
  <g transform="translate(235, 105) scale(0.9)">
    <ellipse cx="0" cy="0" rx="16" ry="12" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2"/>
    <circle cx="-12" cy="-10" r="10" fill="#60a5fa" stroke="#1d4ed8" stroke-width="2"/>
    <polygon points="-22,-10 -30,-8 -22,-6" fill="#f59e0b"/><circle cx="-15" cy="-12" r="2" fill="#000"/>
  </g>
</svg>"""

LIBRARY["sense_ears"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="earBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#faf5ff"/><stop offset="100%" stop-color="#ede9fe"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="url(#earBg)"/>
  <g fill="#8b5cf6" opacity="0.85">
    <g transform="translate(50, 45)">
      <ellipse cx="0" cy="15" rx="6" ry="4.5" transform="rotate(-20 0 15)"/><rect x="4" y="-5" width="3" height="20"/>
      <path d="M 7,-5 C 15,-2 18,5 16,10" fill="none" stroke="#8b5cf6" stroke-width="3" stroke-linecap="round"/>
    </g>
  </g>
  <g transform="translate(135, 100)">
    <path d="M -15,-60 C 25,-65 45,-35 45,5 C 45,45 25,65 5,65 C -15,65 -25,45 -20,25 C -15,10 -15,-30 -15,-60 Z" fill="#fed7aa" stroke="#ea580c" stroke-width="4"/>
    <path d="M 0,-40 C 22,-38 28,-15 28,10 C 28,30 18,42 5,42" fill="none" stroke="#ea580c" stroke-width="3.5" stroke-linecap="round"/>
    <ellipse cx="-2" cy="10" rx="5" ry="7" fill="#c2410c"/>
  </g>
  <g stroke-linecap="round" fill="none">
    <path d="M 195,75 A 35,35 0 0,1 195,125" stroke="#3b82f6" stroke-width="4.5"/>
    <path d="M 215,60 A 55,55 0 0,1 215,140" stroke="#8b5cf6" stroke-width="4"/>
    <path d="M 235,45 A 75,75 0 0,1 235,155" stroke="#ec4899" stroke-width="3.5"/>
  </g>
</svg>"""

LIBRARY["sense_eyes"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="eyeBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f0f9ff"/><stop offset="100%" stop-color="#e0f2fe"/>
    </linearGradient>
    <radialGradient id="irisGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#60a5fa"/><stop offset="70%" stop-color="#2563eb"/><stop offset="100%" stop-color="#1e3a8a"/>
    </radialGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="url(#eyeBg)"/>
  <g fill="none" stroke-width="6" stroke-linecap="round">
    <path d="M 40,65 Q 150,0 260,65" stroke="#f43f5e"/><path d="M 48,72 Q 150,15 252,72" stroke="#f59e0b"/>
    <path d="M 56,79 Q 150,30 244,79" stroke="#10b981"/><path d="M 64,86 Q 150,45 236,86" stroke="#3b82f6"/>
  </g>
  <g transform="translate(150, 130)">
    <path d="M -80,0 C -45,-45 45,-45 80,0 C 45,45 -45,45 -80,0 Z" fill="#ffffff" stroke="#1e293b" stroke-width="4"/>
    <circle cx="0" cy="0" r="32" fill="url(#irisGrad)" stroke="#1d4ed8" stroke-width="2"/>
    <circle cx="0" cy="0" r="15" fill="#0f172a"/>
    <circle cx="-8" cy="-8" r="6" fill="#ffffff"/><circle cx="8" cy="8" r="3" fill="#ffffff"/>
  </g>
</svg>"""

LIBRARY["sense_smell"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="smellBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#fff1f2"/><stop offset="100%" stop-color="#ffe4e6"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="url(#smellBg)"/>
  <g transform="translate(70, 130)">
    <path d="M 0,40 Q -10,0 -20,-30" fill="none" stroke="#16a34a" stroke-width="5" stroke-linecap="round"/>
    <g transform="translate(-20, -30)">
      <circle cx="0" cy="-14" r="12" fill="#fb7185"/><circle cx="-14" cy="0" r="12" fill="#fb7185"/>
      <circle cx="14" cy="0" r="12" fill="#fb7185"/><circle cx="0" cy="14" r="12" fill="#fb7185"/>
      <circle cx="0" cy="0" r="10" fill="#facc15"/>
    </g>
  </g>
  <g stroke-linecap="round" fill="none">
    <path d="M 90,80 Q 130,40 170,70 T 215,95" stroke="#ec4899" stroke-width="3.5" stroke-dasharray="8,6"/>
    <circle cx="135" cy="55" r="3" fill="#f43f5e"/><circle cx="175" cy="45" r="2.5" fill="#eab308"/>
  </g>
  <g transform="translate(225, 90)" stroke="#ea580c" stroke-width="4" stroke-linecap="round" fill="none">
    <path d="M -15,-40 C -12,-20 -5,0 12,5 C 24,8 24,20 12,24 C 0,26 -15,18 -15,12"/>
    <ellipse cx="6" cy="18" rx="4" ry="2.5" fill="#c2410c" stroke="none"/>
  </g>
</svg>"""

LIBRARY["heart_blood"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <radialGradient id="heartGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#f43f5e"/><stop offset="100%" stop-color="#be123c"/>
    </radialGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#fff1f2"/>
  <path d="M 0,100 L 70,100 L 80,75 L 90,125 L 100,60 L 110,135 L 120,100 L 180,100 L 190,75 L 200,125 L 210,60 L 220,135 L 230,100 L 300,100" fill="none" stroke="#fecdd3" stroke-width="5" stroke-linecap="round"/>
  <g transform="translate(150, 95)">
    <path d="M -18,-35 C -18,-55 0,-55 0,-35" fill="none" stroke="#ef4444" stroke-width="12" stroke-linecap="round"/>
    <path d="M 12,-30 C 12,-50 26,-50 26,-30" fill="none" stroke="#0284c7" stroke-width="10" stroke-linecap="round"/>
    <path d="M 0,45 C -55,10 -55,-30 -25,-35 C -5,-38 0,-15 0,-15 C 0,-15 5,-38 25,-35 C 55,-30 55,10 0,45 Z" fill="url(#heartGlow)" stroke="#9f1239" stroke-width="3.5"/>
    <path d="M -5,-10 Q -20,5 -22,20" fill="none" stroke="#fecdd3" stroke-width="2.5" stroke-linecap="round"/>
    <path d="M 5,-10 Q 20,5 22,20" fill="none" stroke="#93c5fd" stroke-width="2.5" stroke-linecap="round"/>
    <circle cx="-12" cy="-18" r="4" fill="#ffffff" opacity="0.8"/>
  </g>
</svg>"""

LIBRARY["winter_snow"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="winterSky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="url(#winterSky)"/>
  <ellipse cx="150" cy="205" rx="160" ry="35" fill="#f1f5f9"/>
  <ellipse cx="150" cy="200" rx="150" ry="28" fill="#ffffff"/>
  <g transform="translate(150, 45)" fill="#e2e8f0">
    <ellipse cx="0" cy="0" rx="55" ry="24"/><circle cx="-35" cy="-8" r="22"/><circle cx="35" cy="-8" r="22"/><circle cx="0" cy="-18" r="26"/>
  </g>
  <g stroke="#ffffff" stroke-width="2.5" stroke-linecap="round">
    <g transform="translate(150, 115) scale(0.9)">
      <line x1="0" y1="-25" x2="0" y2="25"/><line x1="-22" y1="-12" x2="22" y2="12"/><line x1="-22" y1="12" x2="22" y2="-12"/>
      <circle cx="0" cy="0" r="3.5" fill="#38bdf8"/>
    </g>
    <g transform="translate(70, 125) scale(0.7)">
      <line x1="0" y1="-20" x2="0" y2="20"/><line x1="-18" y1="-10" x2="18" y2="10"/><line x1="-18" y1="10" x2="18" y2="-10"/>
      <circle cx="0" cy="0" r="3" fill="#38bdf8"/>
    </g>
    <g transform="translate(230, 110) scale(0.75)">
      <line x1="0" y1="-20" x2="0" y2="20"/><line x1="-18" y1="-10" x2="18" y2="10"/><line x1="-18" y1="10" x2="18" y2="-10"/>
      <circle cx="0" cy="0" r="3" fill="#38bdf8"/>
    </g>
  </g>
</svg>"""

LIBRARY["radiant_sun"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <linearGradient id="daySky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#38bdf8"/><stop offset="100%" stop-color="#bae6fd"/>
    </linearGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="url(#daySky)"/>
  <g fill="#ffffff" opacity="0.9">
    <path d="M 20,150 Q 40,120 70,135 Q 95,115 120,135 Q 140,125 150,150 Z"/>
    <path d="M 180,160 Q 200,135 225,145 Q 250,125 270,145 Q 290,135 300,160 Z"/>
  </g>
  <g transform="translate(150, 95)">
    <g stroke="#f59e0b" stroke-width="4.5" stroke-linecap="round">
      <line x1="0" y1="-65" x2="0" y2="-80"/><line x1="46" y1="-46" x2="56" y2="-56"/>
      <line x1="65" y1="0" x2="80" y2="0"/><line x1="46" y1="46" x2="56" y2="56"/>
      <line x1="0" y1="65" x2="0" y2="80"/><line x1="-46" y1="46" x2="-56" y2="56"/>
      <line x1="-65" y1="0" x2="-80" y2="0"/><line x1="-46" y1="-46" x2="-56" y2="-56"/>
    </g>
    <circle cx="0" cy="0" r="50" fill="#facc15" stroke="#f59e0b" stroke-width="4"/>
    <ellipse cx="-16" cy="-8" rx="5.5" ry="7" fill="#78350f"/><ellipse cx="16" cy="-8" rx="5.5" ry="7" fill="#78350f"/>
    <circle cx="-18" cy="-10" r="2" fill="#ffffff"/><circle cx="14" cy="-10" r="2" fill="#ffffff"/>
    <circle cx="-25" cy="8" r="7" fill="#fb7185" opacity="0.6"/><circle cx="25" cy="8" r="7" fill="#fb7185" opacity="0.6"/>
    <path d="M -16,12 Q 0,28 16,12" fill="none" stroke="#78350f" stroke-width="4" stroke-linecap="round"/>
  </g>
</svg>"""

LIBRARY["planet_earth"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <radialGradient id="earthGlow" cx="40%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#38bdf8"/><stop offset="60%" stop-color="#0284c7"/><stop offset="100%" stop-color="#082f49"/>
    </radialGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#090d16"/>
  <g fill="#ffffff">
    <circle cx="35" cy="30" r="1.5"/><circle cx="85" cy="50" r="2"/><circle cx="240" cy="35" r="1.5"/><circle cx="270" cy="80" r="2.5"/>
  </g>
  <circle cx="150" cy="100" r="76" fill="#38bdf8" opacity="0.2"/>
  <circle cx="150" cy="100" r="68" fill="url(#earthGlow)" stroke="#38bdf8" stroke-width="2"/>
  <g fill="#22c55e" stroke="#16a34a" stroke-width="1.5">
    <path d="M 115,65 Q 130,55 145,65 Q 135,80 125,95 Q 120,105 130,115 Q 115,100 110,80 Z"/>
    <path d="M 130,118 Q 145,125 140,145 Q 130,160 125,145 Q 120,130 130,118 Z"/>
    <path d="M 160,55 Q 185,50 180,75 Q 195,85 190,115 Q 170,135 160,110 Q 155,90 160,55 Z"/>
    <ellipse cx="150" cy="36" rx="28" ry="8" fill="#ffffff"/>
  </g>
  <path d="M 105,75 Q 130,70 160,85 Q 180,80 195,75" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity="0.6"/>
</svg>"""

# ==========================================
# 2. ANIMALS - VIBRANT & FRIENDLY
# ==========================================

LIBRARY["cat"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#fef3c7"/>
  <g transform="translate(150, 110)">
    <!-- Ears -->
    <polygon points="-40,-25 -60,-65 -20,-45" fill="#f97316" stroke="#c2410c" stroke-width="3"/>
    <polygon points="-38,-30 -52,-58 -24,-44" fill="#fed7aa"/>
    <polygon points="40,-25 60,-65 20,-45" fill="#f97316" stroke="#c2410c" stroke-width="3"/>
    <polygon points="38,-30 52,-58 24,-44" fill="#fed7aa"/>
    <!-- Head -->
    <ellipse cx="0" cy="-10" rx="55" ry="45" fill="#f97316" stroke="#c2410c" stroke-width="3"/>
    <!-- Cheeks & Snout -->
    <ellipse cx="0" cy="8" rx="28" ry="18" fill="#fff7ed"/>
    <!-- Nose & Mouth -->
    <polygon points="0,0 -8,-7 8,-7" fill="#f43f5e"/>
    <path d="M 0,0 L 0,8 Q -10,18 -18,10 M 0,8 Q 10,18 18,10" fill="none" stroke="#c2410c" stroke-width="3" stroke-linecap="round"/>
    <!-- Eyes -->
    <ellipse cx="-22" cy="-16" rx="9" ry="12" fill="#10b981"/>
    <ellipse cx="-22" cy="-16" rx="4" ry="10" fill="#0f172a"/><circle cx="-25" cy="-20" r="3" fill="#ffffff"/>
    <ellipse cx="22" cy="-16" rx="9" ry="12" fill="#10b981"/>
    <ellipse cx="22" cy="-16" rx="4" ry="10" fill="#0f172a"/><circle cx="19" cy="-20" r="3" fill="#ffffff"/>
    <!-- Whiskers -->
    <g stroke="#7c2d12" stroke-width="2.5" stroke-linecap="round">
      <line x1="-30" y1="5" x2="-65" y2="0"/><line x1="-30" y1="12" x2="-62" y2="16"/>
      <line x1="30" y1="5" x2="65" y2="0"/><line x1="30" y1="12" x2="62" y2="16"/>
    </g>
  </g>
</svg>"""

LIBRARY["dog"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#ecfdf5"/>
  <g transform="translate(150, 110)">
    <!-- Floppy Ears -->
    <path d="M -40,-35 C -75,-30 -80,20 -55,30 C -45,10 -35,-15 -40,-35 Z" fill="#78350f" stroke="#451a03" stroke-width="3"/>
    <path d="M 40,-35 C 75,-30 80,20 55,30 C 45,10 35,-15 40,-35 Z" fill="#78350f" stroke="#451a03" stroke-width="3"/>
    <!-- Head -->
    <ellipse cx="0" cy="-15" rx="52" ry="46" fill="#b45309" stroke="#78350f" stroke-width="3"/>
    <!-- Snout -->
    <ellipse cx="0" cy="6" rx="30" ry="22" fill="#fde68a"/>
    <ellipse cx="0" cy="-4" rx="12" ry="8" fill="#1e293b"/>
    <path d="M 0,4 L 0,16 Q -12,24 -20,16 M 0,16 Q 12,24 20,16" fill="none" stroke="#78350f" stroke-width="3.5" stroke-linecap="round"/>
    <!-- Friendly Tongue -->
    <path d="M -6,18 C -6,28 6,28 6,18 Z" fill="#f43f5e"/>
    <!-- Eyes -->
    <circle cx="-20" cy="-22" r="8" fill="#1e293b"/><circle cx="-22" cy="-24" r="3" fill="#ffffff"/>
    <circle cx="20" cy="-22" r="8" fill="#1e293b"/><circle cx="18" cy="-24" r="3" fill="#ffffff"/>
  </g>
</svg>"""

LIBRARY["duck"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#e0f2fe"/>
  <!-- Water ripples -->
  <ellipse cx="150" cy="155" rx="110" ry="18" fill="#0284c7" opacity="0.3"/>
  <path d="M 20,165 Q 85,155 150,165 T 280,165" stroke="#38bdf8" stroke-width="3" fill="none"/>
  <!-- Duck Body -->
  <g transform="translate(140, 125)">
    <ellipse cx="0" cy="0" rx="48" ry="32" fill="#facc15" stroke="#eab308" stroke-width="3"/>
    <!-- Wing -->
    <path d="M -20,-10 C 10,-20 30,-5 15,15 C -5,25 -25,10 -20,-10 Z" fill="#eab308" stroke="#ca8a04" stroke-width="2"/>
    <!-- Duck Head -->
    <circle cx="-35" cy="-35" r="26" fill="#facc15" stroke="#eab308" stroke-width="3"/>
    <!-- Orange Beak -->
    <polygon points="-58,-32 -82,-28 -58,-22" fill="#f97316" stroke="#c2410c" stroke-width="2"/>
    <!-- Eye -->
    <circle cx="-42" cy="-40" r="5" fill="#0f172a"/><circle cx="-44" cy="-42" r="1.8" fill="#ffffff"/>
    <!-- Tail Feathers -->
    <polygon points="45,-5 68,-22 55,10" fill="#facc15" stroke="#eab308" stroke-width="2.5"/>
  </g>
</svg>"""

LIBRARY["sheep"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#dcfce7"/>
  <!-- Little green meadow mound -->
  <ellipse cx="150" cy="180" rx="130" ry="20" fill="#22c55e"/>
  <g transform="translate(150, 105)">
    <!-- Black Legs -->
    <rect x="-35" y="25" width="10" height="35" rx="5" fill="#334155"/>
    <rect x="-15" y="25" width="10" height="35" rx="5" fill="#334155"/>
    <rect x="15" y="25" width="10" height="35" rx="5" fill="#334155"/>
    <rect x="35" y="25" width="10" height="35" rx="5" fill="#334155"/>
    <!-- Cloud-like Fluffy Wool Body (high contrast contours) -->
    <g fill="#ffffff" stroke="#94a3b8" stroke-width="3">
      <circle cx="-40" cy="0" r="26"/><circle cx="40" cy="0" r="26"/>
      <circle cx="-20" cy="-25" r="26"/><circle cx="20" cy="-25" r="26"/>
      <circle cx="-20" cy="20" r="24"/><circle cx="20" cy="20" r="24"/>
      <circle cx="0" cy="0" r="32" fill="#f8fafc"/>
    </g>
    <!-- Dark Sheep Face -->
    <g transform="translate(-48, -15)">
      <!-- Droopy ears -->
      <ellipse cx="-20" cy="-8" rx="12" ry="6" fill="#1e293b" transform="rotate(-20 -20 -8)"/>
      <ellipse cx="20" cy="-8" rx="12" ry="6" fill="#1e293b" transform="rotate(20 20 -8)"/>
      <!-- Face -->
      <ellipse cx="0" cy="0" rx="18" ry="22" fill="#1e293b"/>
      <!-- Wool on forehead -->
      <circle cx="0" cy="-20" r="9" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>
      <!-- Friendly Eyes -->
      <circle cx="-7" cy="-4" r="3" fill="#ffffff"/><circle cx="-7" cy="-4" r="1.5" fill="#000"/>
      <circle cx="7" cy="-4" r="3" fill="#ffffff"/><circle cx="7" cy="-4" r="1.5" fill="#000"/>
      <path d="M -5,12 Q 0,16 5,12" stroke="#f43f5e" stroke-width="2" fill="none"/>
    </g>
  </g>
</svg>"""

LIBRARY["cow"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#fef3c7"/>
  <g transform="translate(150, 110)">
    <!-- Horns -->
    <path d="M -30,-45 Q -40,-65 -55,-55" fill="none" stroke="#eab308" stroke-width="5" stroke-linecap="round"/>
    <path d="M 30,-45 Q 40,-65 55,-55" fill="none" stroke="#eab308" stroke-width="5" stroke-linecap="round"/>
    <!-- Ears -->
    <ellipse cx="-45" cy="-35" rx="16" ry="8" fill="#f8fafc" stroke="#334155" stroke-width="2.5" transform="rotate(-15 -45 -35)"/>
    <ellipse cx="45" cy="-35" rx="16" ry="8" fill="#f8fafc" stroke="#334155" stroke-width="2.5" transform="rotate(15 45 -35)"/>
    <!-- Head with Black Patches -->
    <ellipse cx="0" cy="-20" rx="46" ry="40" fill="#ffffff" stroke="#334155" stroke-width="3"/>
    <path d="M -44,-30 Q -10,-45 -5,-20 Q -15,5 -46,0 Z" fill="#1e293b"/>
    <!-- Big Pink Muzzle / Snout -->
    <ellipse cx="0" cy="12" rx="34" ry="22" fill="#fbcfe8" stroke="#f472b6" stroke-width="3"/>
    <ellipse cx="-12" cy="12" rx="5" ry="7" fill="#831843"/>
    <ellipse cx="12" cy="12" rx="5" ry="7" fill="#831843"/>
    <path d="M -12,24 Q 0,30 12,24" stroke="#831843" stroke-width="3" fill="none" stroke-linecap="round"/>
    <!-- Eyes -->
    <circle cx="-20" cy="-24" r="7" fill="#ffffff" stroke="#1e293b" stroke-width="2"/>
    <circle cx="-20" cy="-24" r="4" fill="#0f172a"/><circle cx="-22" cy="-26" r="1.5" fill="#ffffff"/>
    <circle cx="20" cy="-24" r="7" fill="#ffffff" stroke="#1e293b" stroke-width="2"/>
    <circle cx="20" cy="-24" r="4" fill="#0f172a"/><circle cx="18" cy="-26" r="1.5" fill="#ffffff"/>
  </g>
</svg>"""

LIBRARY["lion"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#fefce8"/>
  <g transform="translate(150, 105)">
    <!-- Fluffy Glorious Mane -->
    <g fill="#b45309" stroke="#78350f" stroke-width="3">
      <circle cx="0" cy="-60" r="25"/><circle cx="42" cy="-42" r="25"/><circle cx="60" cy="0" r="25"/>
      <circle cx="42" cy="42" r="25"/><circle cx="0" cy="60" r="25"/><circle cx="-42" cy="42" r="25"/>
      <circle cx="-60" cy="0" r="25"/><circle cx="-42" cy="-42" r="25"/>
    </g>
    <!-- Ears -->
    <circle cx="-35" cy="-35" r="14" fill="#f59e0b" stroke="#b45309" stroke-width="2.5"/>
    <circle cx="-35" cy="-35" r="8" fill="#fef3c7"/>
    <circle cx="35" cy="-35" r="14" fill="#f59e0b" stroke="#b45309" stroke-width="2.5"/>
    <circle cx="35" cy="-35" r="8" fill="#fef3c7"/>
    <!-- Head -->
    <circle cx="0" cy="0" r="45" fill="#f59e0b" stroke="#b45309" stroke-width="3"/>
    <!-- Muzzle -->
    <ellipse cx="0" cy="14" rx="22" ry="15" fill="#fef3c7"/>
    <polygon points="0,5 -9,0 9,0" fill="#78350f"/>
    <path d="M 0,5 L 0,16 Q -8,22 -14,16 M 0,16 Q 8,22 14,16" fill="none" stroke="#78350f" stroke-width="3" stroke-linecap="round"/>
    <!-- Eyes -->
    <ellipse cx="-16" cy="-10" rx="6" ry="8" fill="#78350f"/><circle cx="-18" cy="-12" r="2" fill="#ffffff"/>
    <ellipse cx="16" cy="-10" rx="6" ry="8" fill="#78350f"/><circle cx="14" cy="-12" r="2" fill="#ffffff"/>
  </g>
</svg>"""

LIBRARY["honeybee"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#fef9c3"/>
  <!-- Golden Honeycomb pattern in corner -->
  <polygon points="30,30 50,20 70,30 70,50 50,60 30,50" fill="#fde047" stroke="#ca8a04" stroke-width="2"/>
  <polygon points="70,30 90,20 110,30 110,50 90,60 70,50" fill="#fde047" stroke="#ca8a04" stroke-width="2"/>
  <polygon points="50,60 70,50 90,60 90,80 70,90 50,80" fill="#fde047" stroke="#ca8a04" stroke-width="2"/>
  <!-- Honey drip -->
  <path d="M 70,90 Q 75,115 70,120 A 5,5 0 0,1 60,115 Q 65,90 70,90 Z" fill="#eab308"/>
  <!-- Happy Flying Bee -->
  <g transform="translate(170, 110)">
    <!-- Wings (Translucent) -->
    <ellipse cx="-5" cy="-40" rx="16" ry="28" fill="#bae6fd" opacity="0.8" stroke="#0284c7" stroke-width="2" transform="rotate(-25 -5 -40)"/>
    <ellipse cx="20" cy="-42" rx="14" ry="25" fill="#bae6fd" opacity="0.8" stroke="#0284c7" stroke-width="2" transform="rotate(20 20 -42)"/>
    <!-- Stinger -->
    <polygon points="-48,0 -35,-6 -35,6" fill="#0f172a"/>
    <!-- Striped Bee Body -->
    <ellipse cx="0" cy="0" rx="38" ry="25" fill="#facc15" stroke="#0f172a" stroke-width="3"/>
    <!-- Black Stripes -->
    <path d="M -15,-23 Q -10,0 -15,23 L -5,24 Q 0,0 -5,-24 Z" fill="#0f172a"/>
    <path d="M 10,-24 Q 15,0 10,24 L 20,22 Q 25,0 20,-22 Z" fill="#0f172a"/>
    <!-- Head -->
    <circle cx="35" cy="0" r="18" fill="#0f172a"/>
    <circle cx="36" cy="-4" r="5" fill="#ffffff"/><circle cx="37" cy="-5" r="2.5" fill="#000"/>
    <!-- Antennae -->
    <path d="M 42,-14 Q 52,-30 45,-36" fill="none" stroke="#0f172a" stroke-width="3" stroke-linecap="round"/>
    <circle cx="45" cy="-36" r="3" fill="#f59e0b"/>
  </g>
</svg>"""

LIBRARY["elephant"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f1f5f9"/>
  <g transform="translate(140, 105)">
    <!-- Giant Ear -->
    <path d="M -10,-40 C -70,-45 -80,25 -20,35 Z" fill="#cbd5e1" stroke="#64748b" stroke-width="3"/>
    <!-- Body -->
    <ellipse cx="20" cy="5" rx="55" ry="42" fill="#94a3b8" stroke="#475569" stroke-width="3"/>
    <!-- Legs -->
    <rect x="-10" y="30" width="16" height="35" rx="6" fill="#94a3b8" stroke="#475569" stroke-width="2.5"/>
    <rect x="35" y="30" width="16" height="35" rx="6" fill="#94a3b8" stroke="#475569" stroke-width="2.5"/>
    <!-- Head -->
    <circle cx="-15" cy="-10" r="34" fill="#94a3b8" stroke="#475569" stroke-width="3"/>
    <!-- Trunk curling UP happily -->
    <path d="M -38,5 Q -65,15 -60,-15 Q -55,-40 -40,-35" fill="none" stroke="#94a3b8" stroke-width="12" stroke-linecap="round"/>
    <path d="M -38,5 Q -65,15 -60,-15 Q -55,-40 -40,-35" fill="none" stroke="#475569" stroke-width="3" stroke-linecap="round"/>
    <!-- Tusk -->
    <path d="M -35,5 Q -45,15 -52,5" fill="none" stroke="#ffffff" stroke-width="5" stroke-linecap="round"/>
    <!-- Eye with smile -->
    <circle cx="-18" cy="-18" r="4" fill="#0f172a"/><circle cx="-20" cy="-20" r="1.5" fill="#ffffff"/>
  </g>
</svg>"""

LIBRARY["bear"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#fefce8"/>
  <g transform="translate(150, 105)">
    <!-- Ears -->
    <circle cx="-38" cy="-42" r="16" fill="#78350f" stroke="#451a03" stroke-width="3"/>
    <circle cx="-38" cy="-42" r="9" fill="#d97706"/>
    <circle cx="38" cy="-42" r="16" fill="#78350f" stroke="#451a03" stroke-width="3"/>
    <circle cx="38" cy="-42" r="9" fill="#d97706"/>
    <!-- Head -->
    <ellipse cx="0" cy="-8" rx="52" ry="45" fill="#78350f" stroke="#451a03" stroke-width="3.5"/>
    <!-- Snout -->
    <ellipse cx="0" cy="10" rx="26" ry="18" fill="#fef3c7"/>
    <ellipse cx="0" cy="4" rx="11" ry="7" fill="#1e293b"/>
    <path d="M 0,11 L 0,18 Q -8,25 -14,18 M 0,18 Q 8,25 14,18" fill="none" stroke="#451a03" stroke-width="3" stroke-linecap="round"/>
    <!-- Eyes -->
    <circle cx="-22" cy="-15" r="6" fill="#0f172a"/><circle cx="-24" cy="-17" r="2" fill="#ffffff"/>
    <circle cx="22" cy="-15" r="6" fill="#0f172a"/><circle cx="20" cy="-17" r="2" fill="#ffffff"/>
  </g>
</svg>"""

LIBRARY["zebra"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f1f5f9"/>
  <g transform="translate(150, 105)">
    <!-- Mane with black stripes -->
    <path d="M -15,-55 Q 0,-65 15,-55 L 12,-20 L -12,-20 Z" fill="#1e293b"/>
    <!-- Ears -->
    <polygon points="-28,-40 -38,-70 -18,-50" fill="#ffffff" stroke="#1e293b" stroke-width="2.5"/>
    <polygon points="28,-40 38,-70 18,-50" fill="#ffffff" stroke="#1e293b" stroke-width="2.5"/>
    <!-- Head -->
    <ellipse cx="0" cy="-15" rx="42" ry="38" fill="#ffffff" stroke="#1e293b" stroke-width="3"/>
    <!-- Bold Zebra Stripes -->
    <g fill="#1e293b">
      <polygon points="-40,-15 -20,-10 -40,-5"/>
      <polygon points="40,-15 20,-10 40,-5"/>
      <polygon points="-38,-28 -18,-24 -36,-18"/>
      <polygon points="38,-28 18,-24 36,-18"/>
      <polygon points="-5,-45 0,-25 5,-45"/>
    </g>
    <!-- Dark Muzzle -->
    <ellipse cx="0" cy="15" rx="26" ry="18" fill="#334155"/>
    <ellipse cx="-8" cy="14" rx="4" ry="5" fill="#0f172a"/>
    <ellipse cx="8" cy="14" rx="4" ry="5" fill="#0f172a"/>
    <!-- Eyes -->
    <circle cx="-18" cy="-18" r="6" fill="#0f172a"/><circle cx="-20" cy="-20" r="2" fill="#ffffff"/>
    <circle cx="18" cy="-18" r="6" fill="#0f172a"/><circle cx="16" cy="-20" r="2" fill="#ffffff"/>
  </g>
</svg>"""

# ==========================================
# 3. OBJECTS, PHONICS & WORLD KNOWLEDGE
# ==========================================

LIBRARY["apple"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <radialGradient id="appleGlow" cx="40%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#f87171"/><stop offset="70%" stop-color="#dc2626"/><stop offset="100%" stop-color="#991b1b"/>
    </radialGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#fef2f2"/>
  <g transform="translate(150, 115)">
    <!-- Apple Body -->
    <path d="M 0,-40 C 35,-65 75,-40 75,10 C 75,55 35,75 0,65 C -35,75 -75,55 -75,10 C -75,-40 -35,-65 0,-40 Z" fill="url(#appleGlow)" stroke="#7f1d1d" stroke-width="3.5"/>
    <!-- Stem -->
    <path d="M 0,-40 Q 5,-70 20,-75" fill="none" stroke="#78350f" stroke-width="5" stroke-linecap="round"/>
    <!-- Green Leaf -->
    <path d="M 5,-50 C 25,-75 55,-65 50,-50 C 35,-40 20,-45 5,-50 Z" fill="#22c55e" stroke="#15803d" stroke-width="2"/>
    <!-- Glossy Highlight -->
    <ellipse cx="-35" cy="-15" rx="12" ry="24" fill="#ffffff" opacity="0.4" transform="rotate(-25 -35 -15)"/>
  </g>
</svg>"""

LIBRARY["moon"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <defs>
    <radialGradient id="moonGlow" cx="40%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#fef08a"/><stop offset="80%" stop-color="#facc15"/><stop offset="100%" stop-color="#eab308"/>
    </radialGradient>
  </defs>
  <rect width="300" height="200" rx="16" fill="#0f172a"/>
  <!-- Stars -->
  <g fill="#ffffff">
    <circle cx="45" cy="40" r="2"/><circle cx="95" cy="65" r="1.5"/><circle cx="235" cy="45" r="2.5"/><circle cx="260" cy="140" r="2"/><circle cx="65" cy="155" r="2.5"/>
  </g>
  <!-- Crescent Moon with Face -->
  <g transform="translate(150, 100)">
    <path d="M -30,-60 A 65,65 0 1,0 45,50 A 52,52 0 0,1 -30,-60 Z" fill="url(#moonGlow)" stroke="#ca8a04" stroke-width="3"/>
    <!-- Sleeping Face -->
    <path d="M -12,-5 Q -6,0 0,-4" fill="none" stroke="#854d0e" stroke-width="2.5" stroke-linecap="round"/>
    <path d="M -10,12 Q 2,20 12,10" fill="none" stroke="#854d0e" stroke-width="2.5" stroke-linecap="round"/>
    <!-- Sleep Zzz -->
    <text x="35" y="-30" fill="#fde047" font-size="22" font-family="sans-serif" font-weight="bold">Z</text>
    <text x="52" y="-45" fill="#fde047" font-size="16" font-family="sans-serif" font-weight="bold">z</text>
  </g>
</svg>"""

LIBRARY["rainbow"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#e0f2fe"/>
  <!-- Rainbow Arches -->
  <g fill="none" stroke-width="10" stroke-linecap="round">
    <path d="M 40,160 A 110,110 0 0,1 260,160" stroke="#ef4444"/>
    <path d="M 50,160 A 100,100 0 0,1 250,160" stroke="#f97316"/>
    <path d="M 60,160 A 90,90 0 0,1 240,160" stroke="#eab308"/>
    <path d="M 70,160 A 80,80 0 0,1 230,160" stroke="#22c55e"/>
    <path d="M 80,160 A 70,70 0 0,1 220,160" stroke="#3b82f6"/>
    <path d="M 90,160 A 60,60 0 0,1 210,160" stroke="#8b5cf6"/>
  </g>
  <!-- Cloud Bases -->
  <g fill="#ffffff" stroke="#cbd5e1" stroke-width="2">
    <ellipse cx="45" cy="160" rx="35" ry="20"/><circle cx="30" cy="150" r="18"/><circle cx="60" cy="150" r="18"/>
    <ellipse cx="255" cy="160" rx="35" ry="20"/><circle cx="240" cy="150" r="18"/><circle cx="270" cy="150" r="18"/>
  </g>
</svg>"""

LIBRARY["tree"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f0fdf4"/>
  <!-- Sturdy Trunk -->
  <path d="M 135,200 L 142,100 L 158,100 L 165,200 Z" fill="#78350f" stroke="#451a03" stroke-width="3"/>
  <!-- Canopy of lush green foliage circles -->
  <g fill="#22c55e" stroke="#15803d" stroke-width="3">
    <circle cx="150" cy="65" r="45"/>
    <circle cx="110" cy="85" r="35"/><circle cx="190" cy="85" r="35"/>
    <circle cx="120" cy="115" r="30"/><circle cx="180" cy="115" r="30"/>
    <circle cx="150" cy="95" r="40" fill="#4ade80"/>
  </g>
  <!-- Apples in tree -->
  <g fill="#ef4444">
    <circle cx="130" cy="75" r="7"/><circle cx="170" cy="70" r="7"/>
    <circle cx="150" cy="110" r="7"/><circle cx="185" cy="95" r="7"/>
  </g>
</svg>"""

LIBRARY["kite"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#e0f2fe"/>
  <!-- Fluffy Cloud -->
  <ellipse cx="60" cy="60" rx="40" ry="20" fill="#ffffff"/>
  <!-- Diamond Kite -->
  <g transform="translate(160, 80) rotate(15)">
    <polygon points="0,-60 45,0 0,60 -45,0" fill="#f43f5e" stroke="#be123c" stroke-width="3"/>
    <polygon points="0,-60 45,0 0,0" fill="#3b82f6"/>
    <polygon points="0,0 -45,0 0,-60" fill="#facc15"/>
    <polygon points="0,0 45,0 0,60" fill="#22c55e"/>
    <!-- Cross struts -->
    <line x1="0" y1="-60" x2="0" y2="60" stroke="#ffffff" stroke-width="2.5"/>
    <line x1="-45" y1="0" x2="45" y2="0" stroke="#ffffff" stroke-width="2.5"/>
    <!-- Wavy Tail with Ribbons -->
    <path d="M 0,60 Q 20,95 -10,120 T 15,150" fill="none" stroke="#64748b" stroke-width="2.5" stroke-linecap="round"/>
    <polygon points="12,85 24,80 16,92" fill="#ec4899"/>
    <polygon points="-8,110 4,115 -2,122" fill="#f59e0b"/>
    <polygon points="12,138 22,132 18,145" fill="#a855f7"/>
  </g>
</svg>"""

LIBRARY["house"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f0fdf4"/>
  <!-- Ground -->
  <rect x="0" y="160" width="300" height="40" fill="#86efac"/>
  <g transform="translate(150, 115)">
    <!-- Chimney & Smoke -->
    <rect x="35" y="-70" width="20" height="40" fill="#b91c1c" stroke="#7f1d1d" stroke-width="2"/>
    <circle cx="45" cy="-80" r="8" fill="#e2e8f0" opacity="0.8"/>
    <circle cx="55" cy="-95" r="12" fill="#e2e8f0" opacity="0.6"/>
    <!-- Main House Walls -->
    <rect x="-65" y="-20" width="130" height="75" fill="#fef08a" stroke="#ca8a04" stroke-width="3"/>
    <!-- Roof -->
    <polygon points="0,-75 80,-20 -80,-20" fill="#ef4444" stroke="#b91c1c" stroke-width="3.5"/>
    <!-- Door -->
    <rect x="-18" y="15" width="36" height="40" rx="3" fill="#78350f" stroke="#451a03" stroke-width="2"/>
    <circle cx="10" cy="35" r="3" fill="#facc15"/>
    <!-- Windows -->
    <rect x="-50" y="-5" width="24" height="24" fill="#38bdf8" stroke="#0284c7" stroke-width="2"/>
    <line x1="-38" y1="-5" x2="-38" y2="19" stroke="#ffffff" stroke-width="2"/><line x1="-50" y1="7" x2="-26" y2="7" stroke="#ffffff" stroke-width="2"/>
    <rect x="26" y="-5" width="24" height="24" fill="#38bdf8" stroke="#0284c7" stroke-width="2"/>
    <line x1="38" y1="-5" x2="38" y2="19" stroke="#ffffff" stroke-width="2"/><line x1="26" y1="7" x2="50" y2="7" stroke="#ffffff" stroke-width="2"/>
  </g>
</svg>"""

LIBRARY["umbrella"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#e0f2fe"/>
  <!-- Raindrops -->
  <g fill="#0284c7" opacity="0.75">
    <path d="M 40,40 C 40,40 35,50 35,55 A 5,5 0 0,0 45,55 C 45,50 40,40 40,40 Z"/>
    <path d="M 90,60 C 90,60 85,70 85,75 A 5,5 0 0,0 95,75 C 95,70 90,60 90,60 Z"/>
    <path d="M 230,50 C 230,50 225,60 225,65 A 5,5 0 0,0 235,65 C 235,60 230,50 230,50 Z"/>
    <path d="M 260,80 C 260,80 255,90 255,95 A 5,5 0 0,0 265,95 C 265,90 260,80 260,80 Z"/>
  </g>
  <!-- Colorful Umbrella -->
  <g transform="translate(150, 110)">
    <!-- Shaft & Hook Handle -->
    <line x1="0" y1="-55" x2="0" y2="50" stroke="#334155" stroke-width="5" stroke-linecap="round"/>
    <path d="M 0,50 C 0,65 -20,65 -20,50" fill="none" stroke="#334155" stroke-width="5" stroke-linecap="round"/>
    <!-- Canopy (Tri-color) -->
    <path d="M -75,-15 C -75,-65 75,-65 75,-15 Q 50,0 25,-15 Q 0,0 -25,-15 Q -50,0 -75,-15 Z" fill="#ec4899" stroke="#be185d" stroke-width="3"/>
    <path d="M -25,-15 C -25,-60 25,-60 25,-15 Q 0,0 -25,-15 Z" fill="#38bdf8" stroke="#0284c7" stroke-width="2"/>
    <circle cx="0" cy="-58" r="4" fill="#facc15"/>
  </g>
</svg>"""

LIBRARY["doctor"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#ecfeff"/>
  <g transform="translate(150, 100)">
    <!-- White Coat & Stethoscope -->
    <path d="M -60,60 L -40,0 L 40,0 L 60,60 Z" fill="#ffffff" stroke="#0891b2" stroke-width="3"/>
    <!-- Red Cross Badge -->
    <rect x="-8" y="20" width="16" height="16" rx="2" fill="#ef4444"/>
    <rect x="-6" y="26" width="12" height="4" fill="#ffffff"/>
    <rect x="-2" y="22" width="4" height="12" fill="#ffffff"/>
    <!-- Stethoscope -->
    <path d="M -25,0 C -25,35 25,35 25,0" fill="none" stroke="#334155" stroke-width="4" stroke-linecap="round"/>
    <circle cx="0" cy="35" r="9" fill="#0891b2" stroke="#ffffff" stroke-width="2"/>
    <!-- Friendly Face -->
    <circle cx="0" cy="-35" r="28" fill="#fed7aa" stroke="#ea580c" stroke-width="2.5"/>
    <!-- Doctor Mirror / Headband -->
    <ellipse cx="0" cy="-60" rx="30" ry="6" fill="#0891b2"/>
    <circle cx="0" cy="-58" r="7" fill="#ffffff" stroke="#0891b2" stroke-width="2"/>
    <circle cx="-10" cy="-38" r="3" fill="#000"/><circle cx="10" cy="-38" r="3" fill="#000"/>
    <path d="M -10,-24 Q 0,-16 10,-24" fill="none" stroke="#c2410c" stroke-width="2.5" stroke-linecap="round"/>
  </g>
</svg>"""

LIBRARY["firefighter"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#fef2f2"/>
  <g transform="translate(150, 100)">
    <!-- Red Fire Engine / Truck -->
    <rect x="-80" y="-10" width="160" height="70" rx="10" fill="#ef4444" stroke="#b91c1c" stroke-width="3.5"/>
    <rect x="-65" y="5" width="40" height="30" rx="4" fill="#bae6fd" stroke="#0284c7" stroke-width="2"/>
    <!-- Yellow Siren Light on top -->
    <polygon points="-50,-24 -35,-24 -38,-10 -47,-10" fill="#facc15" stroke="#eab308" stroke-width="2"/>
    <!-- Wheels -->
    <circle cx="-45" cy="62" r="18" fill="#1e293b" stroke="#0f172a" stroke-width="3"/>
    <circle cx="-45" cy="62" r="7" fill="#94a3b8"/>
    <circle cx="45" cy="62" r="18" fill="#1e293b" stroke="#0f172a" stroke-width="3"/>
    <circle cx="45" cy="62" r="7" fill="#94a3b8"/>
    <!-- Ladder -->
    <rect x="-20" y="-22" width="95" height="12" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
    <line x1="0" y1="-22" x2="0" y2="-10" stroke="#64748b" stroke-width="2"/>
    <line x1="25" y1="-22" x2="25" y2="-10" stroke="#64748b" stroke-width="2"/>
    <line x1="50" y1="-22" x2="50" y2="-10" stroke="#64748b" stroke-width="2"/>
  </g>
</svg>"""

LIBRARY["baker"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#fffbeb"/>
  <g transform="translate(150, 100)">
    <!-- Chef / Baker Tall White Hat -->
    <path d="M -30,-30 C -50,-65 50,-65 30,-30 Z" fill="#ffffff" stroke="#d97706" stroke-width="3"/>
    <rect x="-25" y="-30" width="50" height="15" fill="#ffffff" stroke="#d97706" stroke-width="2.5"/>
    <!-- Fresh Golden Loaf of Bread -->
    <ellipse cx="0" cy="25" rx="55" ry="25" fill="#d97706" stroke="#92400e" stroke-width="3.5"/>
    <path d="M -30,20 Q -25,12 -20,22 M -5,18 Q 0,10 5,20 M 20,20 Q 25,12 30,22" stroke="#fef08a" stroke-width="3.5" fill="none" stroke-linecap="round"/>
    <!-- Steam Lines rising -->
    <path d="M -20,-5 Q -15,-15 -20,-20 M 0,-8 Q 5,-18 0,-24 M 20,-5 Q 25,-15 20,-20" stroke="#f59e0b" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  </g>
</svg>"""

LIBRARY["teacher"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f8fafc"/>
  <g transform="translate(150, 100)">
    <!-- Classroom Chalkboard -->
    <rect x="-100" y="-60" width="200" height="120" rx="8" fill="#065f46" stroke="#78350f" stroke-width="6"/>
    <!-- ABC 123 written on board -->
    <text x="-65" y="-15" fill="#ffffff" font-size="28" font-family="sans-serif" font-weight="bold">ABC</text>
    <text x="-65" y="25" fill="#fde047" font-size="28" font-family="sans-serif" font-weight="bold">123</text>
    <!-- Red Apple for Teacher -->
    <circle cx="55" cy="15" r="14" fill="#ef4444" stroke="#991b1b" stroke-width="1.5"/>
    <path d="M 55,2 Q 60,-5 62,-2" fill="none" stroke="#15803d" stroke-width="2.5"/>
  </g>
</svg>"""

LIBRARY["stars_count"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#1e1b4b"/>
  <!-- 5 Bright Golden Stars -->
  <g fill="#facc15" stroke="#eab308" stroke-width="2">
    <polygon transform="translate(50, 60) scale(1.1)" points="0,-20 6,-6 20,-6 9,3 13,16 0,8 -13,16 -9,3 -20,-6 -6,-6"/>
    <polygon transform="translate(110, 130) scale(1.2)" points="0,-20 6,-6 20,-6 9,3 13,16 0,8 -13,16 -9,3 -20,-6 -6,-6"/>
    <polygon transform="translate(150, 50) scale(1.3)" points="0,-20 6,-6 20,-6 9,3 13,16 0,8 -13,16 -9,3 -20,-6 -6,-6"/>
    <polygon transform="translate(200, 130) scale(1.1)" points="0,-20 6,-6 20,-6 9,3 13,16 0,8 -13,16 -9,3 -20,-6 -6,-6"/>
    <polygon transform="translate(250, 60) scale(1.2)" points="0,-20 6,-6 20,-6 9,3 13,16 0,8 -13,16 -9,3 -20,-6 -6,-6"/>
  </g>
</svg>"""

LIBRARY["apples_basket"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#fef2f2"/>
  <g transform="translate(150, 120)">
    <!-- Woven Basket -->
    <ellipse cx="0" cy="15" rx="80" ry="30" fill="#78350f" stroke="#451a03" stroke-width="3"/>
    <path d="M -80,15 Q -60,65 0,65 Q 60,65 80,15 Z" fill="#92400e" stroke="#451a03" stroke-width="3"/>
    <!-- Apples piled inside -->
    <g stroke="#991b1b" stroke-width="2" fill="#ef4444">
      <circle cx="-45" cy="0" r="22"/>
      <circle cx="-15" cy="-10" r="22"/>
      <circle cx="20" cy="-8" r="22"/>
      <circle cx="48" cy="2" r="22"/>
    </g>
    <!-- Little green leaves -->
    <path d="M -15,-32 C -5,-40 -5,-25 -15,-32 Z" fill="#22c55e"/>
    <path d="M 20,-30 C 30,-38 30,-23 20,-30 Z" fill="#22c55e"/>
  </g>
</svg>"""

LIBRARY["gems_comparison"] = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200" width="100%" height="100%">
  <rect width="300" height="200" rx="16" fill="#f8fafc"/>
  <!-- Left group (6 jewels) -->
  <g transform="translate(75, 100)">
    <rect x="-55" y="-60" width="110" height="120" rx="12" fill="#ecfeff" stroke="#06b6d4" stroke-width="3" stroke-dasharray="6,4"/>
    <g fill="#0284c7" stroke="#0369a1" stroke-width="2">
      <polygon transform="translate(-25, -35) scale(0.9)" points="0,-15 15,0 0,15 -15,0"/>
      <polygon transform="translate(25, -35) scale(0.9)" points="0,-15 15,0 0,15 -15,0"/>
      <polygon transform="translate(-25, 0) scale(0.9)" points="0,-15 15,0 0,15 -15,0"/>
      <polygon transform="translate(25, 0) scale(0.9)" points="0,-15 15,0 0,15 -15,0"/>
      <polygon transform="translate(-25, 35) scale(0.9)" points="0,-15 15,0 0,15 -15,0"/>
      <polygon transform="translate(25, 35) scale(0.9)" points="0,-15 15,0 0,15 -15,0"/>
    </g>
  </g>
  <!-- Right group (2 jewels) -->
  <g transform="translate(225, 100)">
    <rect x="-55" y="-60" width="110" height="120" rx="12" fill="#fff1f2" stroke="#f43f5e" stroke-width="3" stroke-dasharray="6,4"/>
    <g fill="#ec4899" stroke="#be185d" stroke-width="2">
      <polygon transform="translate(-20, 0) scale(1.2)" points="0,-15 15,0 0,15 -15,0"/>
      <polygon transform="translate(20, 0) scale(1.2)" points="0,-15 15,0 0,15 -15,0"/>
    </g>
  </g>
</svg>"""

# Match patterns
PROMPT_PATTERNS = [
  (r"plant need to grow", "plant_growth"),
  (r"drinks water from soil", "plant_roots"),
  (r"soaks up sunlight", "leaves_sunlight"),
  (r"grows into a new plant", "sprouting_seed"),
  (r"cold snowy ice", "polar_ice"),
  (r"hot desert", "desert_camel"),
  (r"under the ocean", "ocean_dolphin"),
  (r"birds build their homes", "bird_nest"),
  (r"sense uses your ears", "sense_ears"),
  (r"sense uses your eyes", "sense_eyes"),
  (r"smell flowers", "sense_smell"),
  (r"pumps blood", "heart_blood"),
  (r"falls from clouds in winter", "winter_snow"),
  (r"lights up the sky during day", "radiant_sun"),
  (r"home planet called", "planet_earth"),
  (r"cat", "cat"),
  (r"dog", "dog"),
  (r"duck|quack", "duck"),
  (r"sheep|baa", "sheep"),
  (r"cow|moo", "cow"),
  (r"lion|roar", "lion"),
  (r"bee|buzz", "honeybee"),
  (r"elephant", "elephant"),
  (r"bear", "bear"),
  (r"zebra", "zebra"),
  (r"apple", "apple"),
  (r"moon", "moon"),
  (r"rainbow", "rainbow"),
  (r"tree", "tree"),
  (r"kite", "kite"),
  (r"house", "house"),
  (r"umbrella", "umbrella"),
  (r"doctor|healthy", "doctor"),
  (r"fire truck|firefighter", "firefighter"),
  (r"baker|bread", "baker"),
  (r"teacher|school", "teacher"),
  (r"duckling|duck", "duck"),
  (r"strawberry|strawberries", "apple"),
  (r"honeybee|bees", "honeybee"),
  (r"acorn|squirrel", "tree"),
  (r"balloon|balloons", "rainbow"),
  (r"starfish", "stars_count"),
  (r"butterfly|butterflies", "honeybee"),
  (r"cookie|cookies|baker", "baker"),
  (r"diamond|diamonds|jewel|gem", "gems_comparison"),
  (r"mushroom|mushrooms", "plant_growth"),
  (r"bird|birds|nest", "bird_nest"),
  (r"seashell|ocean|dolphin", "ocean_dolphin"),
  (r"triangle|square|circle|rectangle|hexagon|shape", "pattern_circle_square"),
  (r"oval|sphere|cube|solid", "pattern_circle_square"),
  (r"giraffe|tallest", "zebra"),
  (r"elephant|heaviest", "elephant"),
  (r"train|vehicle|car|cars", "firefighter"),
  (r"feather|lightest", "bird_nest"),
  (r"bathtub|water", "ocean_dolphin"),
  (r"cheetah|fastest", "lion"),
  (r"flower|blossom|garden", "plant_growth"),
  (r"pattern|sequence", "pattern_circle_square"),
  (r"half|quarter|fraction|equal", "apple"),
  (r"frog|frogs|lily pad", "plant_growth"),
  (r"clock|chime|time", "radiant_sun"),
  (r"rabbit|hop", "plant_growth"),
  (r"puppy|dog", "dog"),
  (r"key|keys|castle", "house"),
  (r"how many stars", "stars_count"),
  (r"apples in the basket", "apples_basket"),
  (r"gems has more jewels", "gems_comparison"),
  (r"sun", "radiant_sun"),
  (r"snow|winter", "winter_snow"),
]

# Update SVGs for all files in question_bank and data directory
domain_files = glob.glob(str(DATA_DIR / "items_*.json"))
print(f"Scanning {len(domain_files)} domain bundles...")

total_updated = 0
for d_file in domain_files:
    with open(d_file, "r", encoding="utf-8") as f:
        items = json.load(f)
    
    for item in items:
        prompt = item.get("prompt_structure", {}).get("display_text", "").lower()
        matched = None
        for pat, key in PROMPT_PATTERNS:
            if re.search(pat, prompt):
                matched = key
                break
        
        # Fallback based on domain
        if not matched:
            dom = item.get("domain_id", "")
            if dom == "SCIENCE_EVS":
                matched = "plant_growth"
            elif dom == "WORLD_KNOWLEDGE":
                matched = "radiant_sun"
            elif dom == "ENGLISH_LANGUAGE":
                matched = "apple"
            elif dom == "MATHEMATICS":
                matched = "stars_count"
            else:
                matched = "radiant_sun"

        markup = LIBRARY.get(matched, LIBRARY["radiant_sun"])
        vas = item.get("prompt_structure", {}).get("visual_assets", [])
        if vas and vas[0].get("uri"):
            rel_name = vas[0]["uri"].replace("assets/svg/", "")
            for folder in [PUBLIC_SVG_DIR, DIST_SVG_DIR]:
                out_path = folder / rel_name
                with open(out_path, "w", encoding="utf-8") as out_fp:
                    out_fp.write(markup)
            total_updated += 1

print(f"Successfully generated and updated {total_updated} SVGs across all question items!")
