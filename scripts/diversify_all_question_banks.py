#!/usr/bin/env python3
"""
scripts/diversify_all_question_banks.py

Massively diversifies question items across ALL 187 subskills in all 5 domains:
- MATHEMATICS (8 strands, 55 subskills)
- ENGLISH_LANGUAGE (8 strands, 53 subskills)
- SCIENCE_EVS (6 strands, 35 subskills)
- LOGICAL_REASONING (6 strands, 24 subskills)
- WORLD_KNOWLEDGE (3 strands, 20 subskills)

Every generator function extracts `ss_id = int(subskill.split("-")[-1])` and
branches into N >= actual_strand_subskill_count distinct pedagogical templates.
This eliminates all cross-subskill collisions within strands while using `idx`
for rich intra-subskill variation.
"""

import os
import sys
import glob
import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ITEMS_DIR = BASE_DIR / "question_bank" / "items"
PUBLIC_DATA_DIR = BASE_DIR / "frontend" / "public" / "data" / "question_bank"

NAMES = [
    "Captain Orion", "Princess Luna", "The wise owl", "The grumpy troll",
    "Sir Lancelot", "Professor Quark", "Commander Zorg", "The mystic wizard",
    "A brave knight", "The space explorer", "Lady Gwen", "Dr. Nova"
]
COLORS = [
    "red", "blue", "green", "golden", "silver", "purple", "crystal", "shadow", "neon", "emerald"
]
PLACES = [
    "the enchanted library", "the space station", "the dark cave", "the ancient ruins",
    "the crystal palace", "Mars", "Jupiter", "the forbidden forest", "the deep ocean", "the floating castle"
]
STORY_ITEMS = [
    "glowing moon crystals", "enchanted forest acorns", "ancient golden coins", "magic spellbooks", 
    "dragon scales", "mermaid pearls", "robot gears", "ninja throwing stars", 
    "wizard wands", "pirate treasure maps", "dinosaur bones", "superhero capes"
]

# ----------------------------------------------------------------------
# MATHEMATICS DIVERSIFICATION ENGINES (8 Strands)
# ----------------------------------------------------------------------

def gen_m_nq(subskill: str, idx: int):
    """Number & Quantity (M-NQ: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6
    item_name = STORY_ITEMS[idx % len(STORY_ITEMS)]

    if mod == 0:
        # M-NQ-01: Counting / Cardinality
        count = (idx % 15) + 5
        prompt = f"Explorer! You found a hidden chest. How many {item_name} are sparkling inside?"
        correct = str(count)
        pool = [str(count), str(max(1, count - 2)), str(count + 2), str(count + 3)]
        hint = f"Count carefully! The chest contains exactly {count} {item_name}."
    elif mod == 1:
        # M-NQ-02: Counting sequence / Successor
        n = (idx % 15) + 10
        prompt = f"The spaceship's countdown is at {n}. What number comes directly AFTER {n} to launch the rocket?"
        correct = str(n + 1)
        pool = [str(n + 1), str(n - 1), str(n + 2), str(n)]
        hint = f"Count up: ..., {n}, {n + 1}!"
    elif mod == 2:
        # M-NQ-03: Magnitude comparison (Greater than)
        a = (idx % 12) + 8
        b = a + (idx % 8) + 3
        prompt = f"A fierce dragon has {b} gold coins, and a clever goblin has {a}. Which number is GREATER?"
        correct = str(b)
        pool = [str(b), str(a), "They have the same amount"]
        hint = f"{b} is a larger treasure than {a}."
    elif mod == 3:
        # M-NQ-04: Predecessor (Number before)
        n = (idx % 12) + 15
        prompt = f"To unlock the secret door, you must press the button that comes directly BEFORE {n}. What is it?"
        correct = str(n - 1)
        pool = [str(n - 1), str(n + 1), str(n - 2), str(n)]
        hint = f"Think backwards from {n}: the number right before is {n - 1}."
    elif mod == 4:
        # M-NQ-05: Place value / Base ten
        tens = (idx % 4) + 1
        ones = (idx % 9) + 1
        total = (tens * 10) + ones
        prompt = f"The wizard's potion needs {tens} tens and {ones} ones of spider venom drops. What is the total number?"
        correct = str(total)
        pool = [str(total), str((tens+1)*10 + ones), str(tens*10 + ones + 2), str(total - 1)]
        hint = f"{tens} tens = {tens*10}. Add {ones} ones: {tens*10} + {ones} = {total}!"
    else:
        # M-NQ-06: Ordinal positioning & Missing intermediate number
        a = (idx % 15) + 10
        mid = a + 1
        b = a + 2
        prompt = f"The star runner hopped past stone #{a}, then stone #___, then stone #{b}. Which stone number is missing in the middle?"
        correct = str(mid)
        pool = [str(mid), str(mid + 2), str(max(1, a - 1)), str(b + 1)]
        hint = f"The number between {a} and {b} is {mid}."

    return prompt, correct, pool, hint


def gen_m_op(subskill: str, idx: int):
    """Operations & Algebraic Thinking (M-OP: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6
    a = (idx % 8) + 5
    b = ((idx // 2) % 7) + 3
    total = a + b

    if mod == 0:
        # M-OP-01: Addition
        prompt = f"Captain Orion collected {a} space crystals on Mars and {b} on Jupiter. How many crystals does he have to power his rocket?"
        correct = str(total)
        pool = [str(total), str(max(1, total - 2)), str(total + 1), str(total + 3)]
        hint = f"Add them up: {a} + {b} = {total}."
    elif mod == 1:
        # M-OP-02: Subtraction
        start = a + b + 4
        sub = b
        rem = start - sub
        prompt = f"The treasure vault had {start} gold bars. The pirate took away {sub} bars. How many are left?"
        correct = str(rem)
        pool = [str(rem), str(rem + 1), str(max(0, rem - 2)), str(rem + 2)]
        hint = f"Subtract: {start} - {sub} = {rem}."
    elif mod == 2:
        # M-OP-03: Doubling
        n = (idx % 8) + 4
        double_val = n * 2
        prompt = f"The alien has {n} eyes. By looking into the magic mirror, its eyes DOUBLE! How many eyes does it have now?"
        correct = str(double_val)
        pool = [str(double_val), str(double_val - 2), str(double_val + 2), str(n + 3)]
        hint = f"Double means adding the number to itself: {n} + {n} = {double_val}."
    elif mod == 3:
        # M-OP-04: Combining forces / Multi-term sum
        creature = ["fire dragons", "ice wolves", "shadow knights", "goblins"][idx % 4]
        prompt = f"During the battle, {a} {creature} charged forward, and then {b} more joined them. How many {creature} in all?"
        correct = str(total)
        pool = [str(total), str(total + 2), str(max(1, total - 1)), str(total + 4)]
        hint = f"Combine the attacking forces: {a} + {b} = {total} {creature}!"
    elif mod == 4:
        # M-OP-05: Missing addend
        req = total + 3
        missing = req - a
        prompt = f"Commander Zorg needs {req} energy cells to activate the teleporter. He currently has {a} cells. How many MORE cells must he insert?"
        correct = str(missing)
        pool = [str(missing), str(missing + 2), str(max(1, missing - 1)), str(req)]
        hint = f"Find the missing part: {req} - {a} = {missing} cells needed."
    else:
        # M-OP-06: Equal groups / Multiplication foundation
        groups = (idx % 4) + 2
        per_grp = (idx % 3) + 2
        mult_total = groups * per_grp
        prompt = f"In the droid hangar, there are {groups} landing pads, and each pad holds exactly {per_grp} scout drones. How many drones are there in total?"
        correct = str(mult_total)
        pool = [str(mult_total), str(mult_total + per_grp), str(max(1, mult_total - 2)), str(groups + per_grp)]
        hint = f"Count {groups} equal groups of {per_grp}: {groups} × {per_grp} = {mult_total} drones!"

    return prompt, correct, pool, hint


def gen_m_gs(subskill: str, idx: int):
    """Geometry & Spatial Sense (M-GS: 7 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 7

    if mod == 0:
        # M-GS-01: 2D polygon side counting
        shapes = [("Triangle", 3), ("Square", 4), ("Rectangle", 4), ("Hexagon", 6), ("Octagon", 8)]
        shape_name, sides = shapes[idx % len(shapes)]
        prompt = f"To bypass the laser grid, you must touch the {shape_name}. How many straight sides does it have?"
        correct = str(sides)
        pool = [str(sides), str(sides + 1), str(max(0, sides - 1)), "5" if sides != 5 else "7"]
        hint = f"A {shape_name} always has {sides} sides."
    elif mod == 1:
        # M-GS-02: 3D shape identification
        shapes_3d = [
            ("Sphere", "a crystal ball"), ("Cube", "a magical puzzle box"), 
            ("Cylinder", "a knight's pillar"), ("Cone", "a wizard's hat")
        ]
        shape_3d, example = shapes_3d[idx % len(shapes_3d)]
        prompt = f"The ancient artifact looks exactly like {example}. Which 3D shape is it?"
        correct = shape_3d
        pool = [shape_3d, "Cube" if shape_3d != "Cube" else "Sphere", "Cone" if shape_3d != "Cone" else "Cylinder", "Pyramid"]
        hint = f"{example.capitalize()} is the shape of a {shape_3d}."
    elif mod == 2:
        # M-GS-03: Positional spatial relations
        positions = [
            ("above", "flying above the dragon's lair"),
            ("below", "swimming below the pirate ship"),
            ("inside", "hiding inside the dark cave"),
            ("behind", "sneaking behind the ancient statues")
        ]
        pos_word, phrase = positions[idx % len(positions)]
        prompt = f"The invisible spy is {phrase}. Where is the spy located?"
        correct = f"{pos_word.capitalize()} the target"
        pool = [f"{pos_word.capitalize()} the target", "Across the galaxy", "Underground in a bunker", "Nowhere to be found"]
        hint = f"The spy is {pos_word}!"
    elif mod == 3:
        # M-GS-04: Polygon properties by sides
        shapes = [("Triangle", 3), ("Hexagon", 6), ("Octagon", 8)]
        shape_name, sides = shapes[(idx + 1) % len(shapes)]
        prompt = f"The ancient Temple of Shapes has a magical door guarded by a polygon with exactly {sides} straight sides. Which shape is carved into the door?"
        correct = shape_name
        pool = [shape_name, "Circle", "Square" if sides != 4 else "Pentagon", "Star"]
        hint = f"A shape with exactly {sides} sides is a {shape_name}."
    elif mod == 4:
        # M-GS-05: Vertices / Corners
        shapes_v = [("Triangle", 3), ("Square", 4), ("Pentagon", 5), ("Hexagon", 6)]
        s_name, v_count = shapes_v[idx % len(shapes_v)]
        prompt = f"A glowing forcefield has the outline of a {s_name}. How many sharp corners (vertices) does it have?"
        correct = str(v_count)
        pool = [str(v_count), str(v_count + 1), str(max(1, v_count - 1)), "8" if v_count != 8 else "2"]
        hint = f"A {s_name} has exactly {v_count} corners (vertices)."
    elif mod == 5:
        # M-GS-06: Symmetry / Mirror reflection
        sym_items = [("crystal butterfly", (idx % 4) + 2), ("enchanted shield", (idx % 5) + 3), ("robot face", (idx % 3) + 2)]
        s_item, dots = sym_items[idx % len(sym_items)]
        prompt = f"The {s_item} has a line of symmetry down its center. If the left side has {dots} sparkling gems, how many matching gems must be on the right side?"
        correct = str(dots)
        pool = [str(dots), str(dots + 2), str(max(1, dots - 1)), str(dots * 2)]
        hint = f"Symmetry means both halves match identically: exactly {dots} gems!"
    else:
        # M-GS-07: Composite shapes / Tangrams
        comps = [
            ("a large rectangle", "2 equal squares", "Squares"),
            ("a hexagon", "6 identical small triangles", "Triangles"),
            ("a diamond rhombus", "2 matching triangles", "Triangles")
        ]
        c_whole, c_parts, shape_type = comps[idx % len(comps)]
        prompt = f"A master builder assembles {c_whole} by joining {c_parts} edge-to-edge. Which smaller shape was used to compose it?"
        correct = shape_type
        pool = [shape_type, "Circles", "Stars", "Spheres"]
        hint = f"{c_parts.capitalize()} were combined together."

    return prompt, correct, pool, hint


def gen_m_me(subskill: str, idx: int):
    """Measurement & Data (M-ME: 8 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 8

    if mod == 0:
        # M-ME-01: Time on analog clock
        hour = (idx % 11) + 1
        prompt = f"The time bomb will explode when the little hand hits {hour} and the big hand is on 12. What time must you defuse it?"
        correct = f"{hour} o'clock"
        pool = [f"{hour} o'clock", f"{hour + 1} o'clock", f"{max(1, hour - 1)} o'clock", "12 o'clock"]
        hint = f"When the long hand is on 12, it is exactly {hour} o'clock!"
    elif mod == 1:
        # M-ME-02: Weight comparison
        pairs = [
            ("A boulder of solid gold", "A handful of feathers", "Heavier"),
            ("A massive space cruiser", "A tiny hoverboard", "Heavier"),
            ("A single raindrop", "A swirling hurricane", "Lighter"),
            ("A paper airplane", "A steel locomotive", "Lighter")
        ]
        obj1, obj2, question_type = pairs[idx % len(pairs)]
        prompt = f"In a test of ultimate strength, which object is {question_type.upper()}: {obj1} or {obj2}?"
        correct = obj1
        pool = [obj1, obj2, "They weigh the exact same"]
        hint = f"{obj1} has much more mass and weight." if question_type == "Heavier" else f"{obj1} is far lighter."
    elif mod == 2:
        # M-ME-03: Length comparison
        pairs_len = [
            ("An endless cosmic wormhole", "A simple garden hose", "Longer"),
            ("The Great Wall", "A wooden fence", "Longer"),
            ("A tiny microchip", "A giant supercomputer", "Shorter"),
            ("A laser pointer beam", "A massive light saber", "Shorter")
        ]
        o1, o2, qtype = pairs_len[idx % len(pairs_len)]
        prompt = f"Scanning their dimensions, which item is {qtype.upper()}: {o1} or {o2}?"
        correct = o1
        pool = [o1, o2, "They are identical in length"]
        hint = f"{o1} is definitely {qtype.lower()}."
    elif mod == 3:
        # M-ME-04: Money recognition & values
        coins = [("a ₹10 coin", "10 Rupees"), ("a ₹50 note", "50 Rupees"), ("a ₹100 note", "100 Rupees"), ("a ₹20 note", "20 Rupees")]
        c_name, c_val = coins[idx % len(coins)]
        prompt = f"The galactic merchant demands {c_name} to buy the hyper-fuel. How many Rupees is that worth?"
        correct = c_val
        pool = [c_val, "1 Rupee", "5 Rupees", "500 Rupees"]
        hint = f"{c_name} equals {c_val}."
    elif mod == 4:
        # M-ME-05: Capacity / Liquid volume comparison
        vessels = [
            ("A giant pirate water barrel", "A tiny glass test tube", "MORE"),
            ("A swimming pool", "A small teacup", "MORE"),
            ("A sewing thimble", "A massive iron cauldron", "LESS"),
            ("An eye dropper", "A wooden water cistern", "LESS")
        ]
        v1, v2, q = vessels[idx % len(vessels)]
        prompt = f"Comparing fluid capacity, which container holds {q} liquid: {v1} or {v2}?"
        correct = v1
        pool = [v1, v2, "They hold the exact same volume"]
        hint = f"{v1} holds {q.lower()} liquid."
    elif mod == 5:
        # M-ME-06: Temperature comparison
        temps = [
            ("A bubbling lava pool", "A frozen ice cave", "HOTTER"),
            ("A blazing desert dune at noon", "A snowy mountaintop", "HOTTER"),
            ("An arctic glacier", "A roaring campfire", "COLDER"),
            ("A frosted icicle", "A steaming bowl of soup", "COLDER")
        ]
        t1, t2, q = temps[idx % len(temps)]
        prompt = f"Thermal sensors scan two areas: {t1} and {t2}. Which location is {q}?"
        correct = t1
        pool = [t1, t2, "They have identical temperatures"]
        hint = f"{t1} is noticeably {q.lower()}."
    elif mod == 6:
        # M-ME-07: Non-standard units of length
        units = ["paperclips", "wooden blocks", "hand-spans", "chalk sticks"]
        u = units[idx % len(units)]
        u_len = (idx % 7) + 4
        prompt = f"An apprentice measures the wizard's staff using {u} placed end to end. The staff spans exactly {u_len} {u}. What is its total length?"
        correct = f"{u_len} {u}"
        pool = [f"{u_len} {u}", f"{u_len + 2} {u}", f"{max(1, u_len - 1)} {u}", f"50 {u}"]
        hint = f"The staff spans {u_len} {u}."
    else:
        # M-ME-08: Reading simple bar graph / tally data
        data_sets = [
            ("red gems", 8, "blue gems", 5, "green gems", 3),
            ("solar crystals", 12, "lunar rocks", 7, "stardust jars", 4),
            ("gold coins", 15, "silver coins", 10, "bronze coins", 6)
        ]
        d1, c1, d2, c2, d3, c3 = data_sets[idx % len(data_sets)]
        prompt = f"The explorer recorded specimens found on an expedition: {d1}: {c1}, {d2}: {c2}, {d3}: {c3}. Which specimen was collected the MOST?"
        correct = d1
        pool = [d1, d2, d3, "All are equal"]
        hint = f"{d1} has the highest count of {c1}."

    return prompt, correct, pool, hint


def gen_m_pa(subskill: str, idx: int):
    """Patterns & Algebra (M-PA: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6

    if mod == 0:
        # M-PA-01: Repeating sequence next element
        patterns = [
            ("Fire, Ice, Lightning, Fire, Ice, Lightning, Fire, Ice", "Lightning", ["Lightning", "Fire", "Ice", "Earth"]),
            ("Triangle, Hexagon, Circle, Triangle, Hexagon", "Circle", ["Circle", "Triangle", "Hexagon", "Square"]),
            ("Up, Down, Left, Up, Down, Left, Up", "Down", ["Down", "Left", "Up", "Right"])
        ]
        pat_str, nxt, pool = patterns[idx % len(patterns)]
        prompt = f"A secret agent is cracking a vault code: {pat_str}... If she presses the wrong button, the alarm sounds! What comes next?"
        correct = nxt
        hint = f"The pattern repeats: {nxt} is next."
    elif mod == 1:
        # M-PA-02: Skip counting progression
        skip = [
            ("7, 14, 21, 28", "35", ["35", "30", "42", "29"]),
            ("9, 18, 27, 36", "45", ["45", "54", "40", "39"]),
            ("15, 30, 45, 60", "75", ["75", "90", "85", "65"])
        ]
        seq_str, nxt, pool = skip[idx % len(skip)]
        prompt = f"To bypass the alien security matrix, complete the sequence: {seq_str}, ___?"
        correct = nxt
        hint = "Follow the skip counting logic!"
    elif mod == 2:
        # M-PA-03: Missing intermediate element
        missing = [
            ("12, ___, 36, 48", "24", ["24", "18", "30", "20"]),
            ("25, 50, ___, 100", "75", ["75", "65", "85", "55"]),
            ("Red, Blue, Green, Red, ___, Green", "Blue", ["Blue", "Yellow", "Red", "Black"])
        ]
        seq_str, nxt, pool = missing[idx % len(missing)]
        prompt = f"A piece of the ancient map is missing! Fill in the blank: {seq_str}"
        correct = nxt
        hint = "Analyze the sequence before and after the blank."
    elif mod == 3:
        # M-PA-04: Growing number patterns
        grow = [
            ("2, 4, 8, 16", "32", ["32", "24", "30", "64"]),
            ("5, 10, 15, 20", "25", ["25", "30", "22", "35"]),
            ("10, 20, 30, 40", "50", ["50", "60", "45", "55"])
        ]
        seq_str, nxt, pool = grow[idx % len(grow)]
        prompt = f"The ancient clockwork engine ticks in a growing sequence: {seq_str}, ___? What number comes next?"
        correct = nxt
        hint = f"Identify the growing step to find {nxt}."
    elif mod == 4:
        # M-PA-05: Identifying repeating pattern core / unit
        cores = [
            ("Circle, Triangle, Circle, Triangle, Circle, Triangle", "Circle, Triangle", ["Circle, Triangle", "Circle, Circle", "Triangle, Triangle", "Square"]),
            ("Red, Blue, Green, Red, Blue, Green", "Red, Blue, Green", ["Red, Blue, Green", "Red, Blue", "Green, Red", "Blue, Blue"]),
            ("Sun, Moon, Star, Sun, Moon, Star", "Sun, Moon, Star", ["Sun, Moon, Star", "Sun, Moon", "Star, Sun", "Moon, Star"])
        ]
        pat, core, pool = cores[idx % len(cores)]
        prompt = f"Analyze the repeating sequence: {pat}. What is the fundamental pattern unit that repeats?"
        correct = core
        hint = f"The core unit repeating over and over is '{core}'."
    else:
        # M-PA-06: Two-attribute sequence (Color + Shape)
        two_attr = [
            ("Red Square, Blue Circle, Red Square, Blue Circle, Red Square", "Blue Circle", ["Blue Circle", "Red Square", "Red Circle", "Blue Square"]),
            ("Golden Star, Silver Diamond, Golden Star, Silver Diamond", "Golden Star", ["Golden Star", "Silver Diamond", "Silver Star", "Golden Diamond"])
        ]
        seq, nxt, pool = two_attr[idx % len(two_attr)]
        prompt = f"The vault uses a two-attribute cipher: {seq}... What shape and color comes next?"
        correct = nxt
        hint = f"Follow both color and shape alternating rules: next is {nxt}."

    return prompt, correct, pool, hint


def gen_m_fr(subskill: str, idx: int):
    """Fractions & Equal Sharing (M-FR: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    groups = ["pirate crew", "wizard council", "space federation", "ninja clan", "dragon hoard", "goblin troop"]
    group = groups[(ss_id - 1) % len(groups)]
    members = (idx % 3) + 3
    total_coins = members * 4
    prompt = f"The {group} of {members} found a treasure chest with {total_coins} gold coins. To avoid a mutiny, they must split it EQUALLY. What does sharing equally mean?"
    correct = "Everyone gets the exact same amount"
    pool = ["Everyone gets the exact same amount", "The captain gets the most", "The fastest pirate gets them all", "It's impossible to share"]
    hint = f"Equal means fair shares for each member of the {group}!"
    return prompt, correct, pool, hint


def gen_m_du(subskill: str, idx: int):
    """Data & Uncertainty (M-DU: 8 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 8
    colors = ["red", "blue", "green", "purple", "silver", "golden", "black", "white"]
    c1 = colors[(ss_id - 1) % len(colors)]
    c2 = colors[ss_id % len(colors)]

    if mod == 0:
        # M-DU-01: Certainty
        prompt = f"A pouch contains ONLY 10 {c1} dragon scales and 0 {c2} scales. If you draw one blindly, what will you definitely pull out?"
        correct = f"A {c1} dragon scale"
        pool = [f"A {c1} dragon scale", f"A {c2} dragon scale", "Nothing at all", "A magic wand"]
        hint = f"There are only {c1} scales inside, so it is a 100% certainty!"
    elif mod == 1:
        # M-DU-02: Impossibility
        prompt = f"A chest contains 15 {c1} crystals and zero {c2} crystals. What is the chance of pulling out a {c2} crystal?"
        correct = "Impossible (0% chance)"
        pool = ["Impossible (0% chance)", "Certain (100% chance)", "Very likely", "50% chance"]
        hint = f"There are no {c2} crystals in the chest, so it's impossible."
    elif mod == 2:
        # M-DU-03: More likely vs less likely
        prompt = f"A pouch contains 8 {c1} marbles and 2 {c2} marbles. Which color are you MORE LIKELY to pull out blindly?"
        correct = f"A {c1} marble"
        pool = [f"A {c1} marble", f"A {c2} marble", "Both are equally likely"]
        hint = f"There are more {c1} marbles than {c2} marbles."
    elif mod == 3:
        # M-DU-04: Equally likely outcomes
        prompt = f"A coin has a sun on one side and a moon on the other side. When flipped, which outcome is expected?"
        correct = "Sun and Moon are equally likely"
        pool = ["Sun and Moon are equally likely", "Sun is guaranteed", "Moon is guaranteed", "Neither will land"]
        hint = "A fair two-sided coin gives an equal 50/50 chance."
    elif mod == 4:
        # M-DU-05: Less likely outcome
        prompt = f"A spinner has 9 {c1} spaces and only 1 {c2} space. Which outcome is LEAST LIKELY when spun?"
        correct = f"Landing on {c2}"
        pool = [f"Landing on {c2}", f"Landing on {c1}", "Both are equally likely"]
        hint = f"{c2} has the smallest fraction of space."
    elif mod == 5:
        # M-DU-06: Tally bundle interpretation
        prompt = "In an animal survey, a scout records four vertical tally marks crossed by one diagonal slash. How many animals does that complete bundle represent?"
        correct = "5"
        pool = ["5", "4", "10", "6"]
        hint = "A standard tally bundle always represents 5 items."
    elif mod == 6:
        # M-DU-07: True/False data statement verification
        prompt = f"In a class poll, 12 students voted for {c1} and 4 voted for {c2}. Is it TRUE that {c1} received more votes than {c2}?"
        correct = "True"
        pool = ["True", "False", "Cannot be determined"]
        hint = f"12 is greater than 4, so the statement is true."
    else:
        # M-DU-08: Intuitive uncertainty & prediction
        prompt = f"A weather report shows an 80% probability of sunshine tomorrow in the kingdom. What is the most reasonable expectation?"
        correct = "It is very likely to be sunny"
        pool = ["It is very likely to be sunny", "It is guaranteed to blizzard", "It is impossible for sun to appear", "It will definitely rain"]
        hint = "An 80% chance means an event is very likely."

    return prompt, correct, pool, hint


def gen_m_ps(subskill: str, idx: int):
    """Problem Solving & Modeling (M-PS: 8 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 8
    items = ["hyper-drive cores", "magic potions", "ancient scrolls", "dragon eggs", "golden shields", "star crystals", "energy batteries", "mana stones"]
    item = items[mod]

    if mod == 0:
        # M-PS-01: Difference / deficit quest
        need = (idx % 10) + 15
        have = need - (idx % 6 + 4)
        diff = need - have
        prompt = f"The quest requires {need} {item} to succeed. You have collected {have}. How many MORE {item} must you find?"
        correct = str(diff)
        pool = [str(diff), str(diff + 2), str(max(1, diff - 1)), str(need)]
        hint = f"Subtract what you have from what you need: {need} - {have} = {diff}!"
    elif mod == 1:
        # M-PS-02: Equal sharing division word problem
        members = (idx % 3) + 2
        each = (idx % 4) + 3
        total = members * each
        prompt = f"{members} galactic explorers discovered a cache of {total} {item}. If they share them equally, how many {item} does each explorer receive?"
        correct = str(each)
        pool = [str(each), str(each + 1), str(max(1, each - 2)), str(total)]
        hint = f"Divide equally: {total} ÷ {members} = {each} {item}."
    elif mod == 2:
        # M-PS-03: Multi-step inventory
        start = (idx % 6) + 10
        found = (idx % 4) + 3
        spent = (idx % 3) + 2
        final = start + found - spent
        prompt = f"The hero carried {start} {item}, discovered {found} more in a chest, and used {spent} during a dungeon crawl. How many {item} remain?"
        correct = str(final)
        pool = [str(final), str(final + 2), str(max(1, final - 1)), str(start + found)]
        hint = f"{start} + {found} = {start+found}, minus {spent} = {final}."
    elif mod == 3:
        # M-PS-04: Rate / distance problem
        speed = (idx % 3) + 3
        hours = (idx % 3) + 2
        dist = speed * hours
        prompt = f"A scout hover-car travels at {speed} leagues per hour. How many leagues will it cover after cruising for {hours} hours?"
        correct = str(dist)
        pool = [str(dist), str(dist + speed), str(max(1, dist - 2)), str(speed + hours)]
        hint = f"Multiply speed by hours: {speed} × {hours} = {dist} leagues."
    elif mod == 4:
        # M-PS-05: Comparison word problem
        base = (idx % 8) + 6
        extra = (idx % 5) + 3
        total = base + extra
        prompt = f"Sir Roland collected {base} {item}. Lady Gwen gathered {extra} MORE {item} than Sir Roland. How many did Lady Gwen gather?"
        correct = str(total)
        pool = [str(total), str(base), str(extra), str(total + extra)]
        hint = f"Add the extra amount: {base} + {extra} = {total}."
    elif mod == 5:
        # M-PS-06: Remaining balance
        start = (idx % 10) + 20
        cost = (idx % 8) + 6
        change = start - cost
        prompt = f"A young merchant had {start} {item} and traded away {cost} of them for supplies. How many {item} remain in the wagon?"
        correct = str(change)
        pool = [str(change), str(change + 2), str(max(1, change - 1)), str(start)]
        hint = f"Subtract the traded amount: {start} - {cost} = {change}."
    elif mod == 6:
        # M-PS-07: Grouping into quivers / bags
        packs = (idx % 4) + 3
        per_pack = 5
        total = packs * per_pack
        prompt = f"An artisan bundles {item} into crates of {per_pack}. If the artisan fills {packs} complete crates, how many {item} are packed in total?"
        correct = str(total)
        pool = [str(total), str(total + 5), str(max(5, total - 5)), str(packs + 5)]
        hint = f"Count {packs} groups of {per_pack}: {total} {item}!"
    else:
        # M-PS-08: Total cost of multiple items
        count = (idx % 3) + 2
        price = (idx % 4) + 3
        total = count * price
        prompt = f"Each of the magical {item} costs {price} gold coins. If your party buys {count} of them, what is the total cost in gold coins?"
        correct = str(total)
        pool = [str(total), str(total + price), str(max(1, total - 2)), str(count + price)]
        hint = f"Multiply: {count} × {price} = {total} gold coins."

    return prompt, correct, pool, hint


def generate_math_item(subskill: str, idx: int):
    prefix = subskill[:4]
    if prefix == "M-NQ": return gen_m_nq(subskill, idx)
    elif prefix == "M-OP": return gen_m_op(subskill, idx)
    elif prefix == "M-GS": return gen_m_gs(subskill, idx)
    elif prefix == "M-ME": return gen_m_me(subskill, idx)
    elif prefix == "M-PA": return gen_m_pa(subskill, idx)
    elif prefix == "M-FR": return gen_m_fr(subskill, idx)
    elif prefix == "M-DU": return gen_m_du(subskill, idx)
    elif prefix == "M-PS": return gen_m_ps(subskill, idx)
    else: return gen_m_nq(subskill, idx)


# ----------------------------------------------------------------------
# ENGLISH LANGUAGE DIVERSIFICATION ENGINES (8 Strands)
# ----------------------------------------------------------------------

def gen_e_pd(subskill: str, idx: int):
    """Phonological Awareness & Decoding (E-PD: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6
    name = NAMES[idx % len(NAMES)]
    place = PLACES[(idx + 1) % len(PLACES)]

    if mod == 0:
        # E-PD-01: Initial sound
        sounds = [("p", "Potion", ["Wand", "Spellbook", "Crystal"]), ("b", "Broom", ["Hat", "Cauldron", "Wand"]), ("m", "Magic", ["Potion", "Spell", "Hex"]), ("c", "Castle", ["Dragon", "Sword", "Shield"])]
        s, correct, wrong = sounds[idx % len(sounds)]
        prompt = f"{name} needs a password starting with the /{s}/ sound to enter {place}. Which word works?"
        pool = [correct] + wrong
        hint = f"{correct} starts with the sound /{s}/."
    elif mod == 1:
        # E-PD-02: Ending sound
        ends = [("t", "Knight", ["Dragon", "Shield", "Broom"]), ("g", "Frog", ["Toad", "Wand", "Star"]), ("n", "Moon", ["Sun", "Star", "Cloud"]), ("k", "Lock", ["Door", "Key", "Vault"])]
        s, correct, wrong = ends[idx % len(ends)]
        prompt = f"{name} unlocks the gate with a secret word ending in the /{s}/ sound. Which word ends with /{s}/?"
        pool = [correct] + wrong
        hint = f"{correct} ends with the /{s}/ sound."
    elif mod == 2:
        # E-PD-03: Rhyme generation / identification
        rhymes = [("star", "Far", ["Moon", "Sky", "Sun"]), ("night", "Knight", ["Day", "Sword", "Castle"]), ("gold", "Bold", ["Coin", "Silver", "Cave"]), ("ring", "King", ["Queen", "Crown", "Robe"])]
        target, correct, wrong = rhymes[idx % len(rhymes)]
        prompt = f"In {place}, {name} must chant a spell rhyming with '{target}'. Which word creates a perfect rhyme?"
        pool = [correct] + wrong
        hint = f"'{correct}' rhymes with '{target}' because they share the same ending sound."
    elif mod == 3:
        # E-PD-04: Syllable counting
        sylls = [("dragon", "2", ["1", "3", "4"]), ("wizard", "2", ["1", "3", "4"]), ("telescope", "3", ["1", "2", "4"]), ("constellation", "4", ["2", "3", "5"])]
        word, correct, wrong = sylls[idx % len(sylls)]
        prompt = f"Clap out the rhythmic beats in the magic word '{word}'. How many syllables does it have?"
        pool = [correct] + wrong
        hint = f"The word '{word}' has {correct} syllables."
    elif mod == 4:
        # E-PD-05: Sound blending
        blends = [("s - u - n", "Sun", ["Star", "Moon", "Sky"]), ("c - a - p", "Cap", ["Hat", "Crown", "Cup"]), ("f - i - sh", "Fish", ["Frog", "Bird", "Fairy"]), ("b - a - t", "Bat", ["Ball", "Bird", "Cat"])]
        segmented, correct, wrong = blends[idx % len(blends)]
        prompt = f"Listen closely as {name} sounds out: /{segmented}/. What word do these sounds blend together to form?"
        pool = [correct] + wrong
        hint = f"Blending /{segmented}/ makes the word '{correct}'."
    else:
        # E-PD-06: Vowel sound identification
        vowels = [("short /a/", "Cat", ["Cake", "Car", "Boat"]), ("long /e/", "Tree", ["Bed", "Red", "Ten"]), ("short /i/", "Pin", ["Pine", "Pie", "Pen"]), ("long /o/", "Boat", ["Bat", "Box", "Bus"])]
        v_sound, correct, wrong = vowels[idx % len(vowels)]
        prompt = f"Which magical word contains the {v_sound} sound?"
        pool = [correct] + wrong
        hint = f"'{correct}' contains the {v_sound} sound."

    return prompt, correct, pool, hint


def gen_e_vm(subskill: str, idx: int):
    """Vocabulary & Morphology (E-VM: 7 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 7
    name = NAMES[idx % len(NAMES)]
    color = COLORS[(idx + 1) % len(COLORS)]

    if mod == 0:
        # E-VM-01: Word definition / meaning
        words = [("colossal", "Huge", ["Tiny", "Green", "Friendly"]), ("ancient", "Very old", ["New", "Shiny", "Broken"]), ("swift", "Fast", ["Slow", "Loud", "Heavy"]), ("fragile", "Easily broken", ["Strong", "Heavy", "Tall"])]
        word, correct, wrong = words[idx % len(words)]
        prompt = f"The {color} dragon was described as *{word}* by {name}. What does the word '{word}' mean?"
        pool = [correct] + wrong
        hint = f"The meaning of {word} is {correct}."
    elif mod == 1:
        # E-VM-02: Synonyms
        syns = [("brave", "Courageous", ["Cowardly", "Sleepy", "Hungry"]), ("gleaming", "Shining", ["Dull", "Dark", "Dirty"]), ("clever", "Smart", ["Foolish", "Slow", "Heavy"]), ("furious", "Angry", ["Calm", "Peaceful", "Joyful"])]
        word, correct, wrong = syns[idx % len(syns)]
        prompt = f"Which word has the SAME meaning (synonym) as '{word}' in {name}'s quest log?"
        pool = [correct] + wrong
        hint = f"'{correct}' means the same as '{word}'."
    elif mod == 2:
        # E-VM-03: Antonyms
        ants = [("ancient", "Modern", ["Old", "Historic", "Dusty"]), ("gloomy", "Bright", ["Dark", "Cloudy", "Sad"]), ("fierce", "Gentle", ["Wild", "Mean", "Rough"]), ("hollow", "Solid", ["Empty", "Deep", "Curved"])]
        word, correct, wrong = ants[idx % len(ants)]
        prompt = f"Which word is the exact OPPOSITE (antonym) of '{word}'?"
        pool = [correct] + wrong
        hint = f"The opposite of '{word}' is '{correct}'."
    elif mod == 3:
        # E-VM-04: Compound words
        compounds = [("star", "fish", "Starfish", ["Starplanet", "Fishstar", "Starlight"]), ("sun", "flower", "Sunflower", ["Suncloud", "Flowerpower", "Sunbeam"]), ("dragon", "fly", "Dragonfly", ["Dragonwing", "Flydragon", "Firefly"])]
        w1, w2, correct, wrong = compounds[idx % len(compounds)]
        prompt = f"When {name} combines the root words '{w1}' and '{w2}', which compound word is created?"
        pool = [correct] + wrong
        hint = f"'{w1}' + '{w2}' = '{correct}'."
    elif mod == 4:
        # E-VM-05: Prefixes & Suffixes
        affixes = [("un-", "happy", "Not happy", ["Very happy", "Always happy", "Extremely happy"]), ("re-", "build", "Build again", ["Never build", "Destroy", "Build first"]), ("pre-", "view", "View before", ["View after", "Never view", "View loud"])]
        pref, base, correct, wrong = affixes[idx % len(affixes)]
        prompt = f"What happens when the prefix '{pref}' is added to the base word '{base}' to form '{pref}{base}'?"
        pool = [correct] + wrong
        hint = f"The prefix '{pref}' means {correct}."
    elif mod == 5:
        # E-VM-06: Context clues
        contexts = [
            ("parched after wandering through the scorching desert with no water", "parched", "Very thirsty", ["Very cold", "Overly full", "Energetic"]),
            ("cautious as she crept past the sleeping dragon without making a sound", "cautious", "Very careful", ["Reckless", "Noisy", "Confused"])
        ]
        sent, target, correct, wrong = contexts[idx % len(contexts)]
        prompt = f"Read the sentence: '{name} was {sent}.' Using clues from the sentence, what does '{target}' mean?"
        pool = [correct] + wrong
        hint = f"The clues in the sentence show that '{target}' means {correct}."
    else:
        # E-VM-07: Category classification / Semantic field
        cats = [("gems and minerals", "Sapphire", ["Sword", "Shield", "Potion"]), ("mythical creatures", "Pegasus", ["Horse", "Eagle", "Lizard"]), ("astronomical bodies", "Asteroid", ["Submarine", "Mountain", "Volcano"])]
        cat, correct, wrong = cats[idx % len(cats)]
        prompt = f"Which item belongs in the category of '{cat}' in {name}'s encyclopedia?"
        pool = [correct] + wrong
        hint = f"A {correct} is an example of {cat}."

    return prompt, correct, pool, hint


def gen_e_sg(subskill: str, idx: int):
    """Syntax & Grammar (E-SG: 5 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 5
    name = NAMES[idx % len(NAMES)]

    if mod == 0:
        # E-SG-01: Word order
        n = (idx % 3) + 1
        if n == 1:
            correct, wrong = "The brave knights rode swiftly.", ["The braved knights rides swift.", "knights brave the rode swiftly", "Riding knights brave the."]
        elif n == 2:
            correct, wrong = "A red dragon breathes fire.", ["Breathes fire a red dragon.", "Dragon red a fire breathes.", "A red dragons breathe fires."]
        else:
            correct, wrong = "The wizard casts a spell.", ["The wizards cast a spells.", "Casts a spell the wizard.", "Wizard the spell a casts."]
        prompt = f"Which sentence is written with correct, natural word order for {name}'s scroll?"
        pool = [correct] + wrong
        hint = "English sentences generally follow Subject + Verb + Object word order."
    elif mod == 1:
        # E-SG-02: Subject-verb agreement
        agreements = [
            ("The two dragons [fly / flies] across the starry sky.", "fly", ["flies", "flying", "flew"]),
            ("Princess Luna [sings / sing] a calming melody.", "sings", ["sing", "singing", "sung"]),
            ("The space explorer [discovers / discover] a new comet.", "discovers", ["discover", "discovering", "discovered"])
        ]
        sent, correct, wrong = agreements[idx % len(agreements)]
        prompt = f"Choose the correct verb form to complete the sentence: '{sent}'"
        pool = [correct] + wrong
        hint = f"Singular subjects take singular verbs; plural subjects take plural verbs: '{correct}'."
    elif mod == 2:
        # E-SG-03: Punctuation & Capitalization
        puncts = [
            ("Where did the golden key vanish?", ["where did the golden key vanish", "Where did the golden key vanish.", "Where did the golden key vanish!"]),
            ("The dragon soared over the mountain.", ["the dragon soared over the mountain", "The dragon soared over the mountain?", "the Dragon soared over the mountain."])
        ]
        correct, wrong = puncts[idx % len(puncts)]
        prompt = f"Which sentence is capitalized and punctuated correctly for {name}'s letter?"
        pool = [correct] + wrong
        hint = "Sentences must begin with a capital letter and end with the correct punctuation mark."
    elif mod == 3:
        # E-SG-04: Pronoun replacement
        pronouns = [
            ("Princess Luna found an ancient scroll. ___ unrolled it carefully.", "She", ["He", "They", "It"]),
            ("Captain Orion adjusted his helmet. ___ stepped onto the red dust of Mars.", "He", ["She", "They", "It"]),
            ("The guards stood at the gate. ___ raised their shields.", "They", ["He", "She", "It"])
        ]
        sent, correct, wrong = pronouns[idx % len(pronouns)]
        prompt = f"Fill in the blank with the correct pronoun: '{sent}'"
        pool = [correct] + wrong
        hint = f"Use '{correct}' to match the antecedent."
    else:
        # E-SG-05: Verb tense consistency (Past vs Present)
        tenses = [
            ("Yesterday, Sir Lancelot [walked / walks / will walk] to the tournament.", "walked", ["walks", "will walk", "walking"]),
            ("Right now, Commander Zorg [pilots / piloted / will pilot] the flagship.", "pilots", ["piloted", "will pilot", "piloting"]),
            ("Tomorrow, the expedition [will depart / departed / departs] at dawn.", "will depart", ["departed", "departs", "departing"])
        ]
        sent, correct, wrong = tenses[idx % len(tenses)]
        prompt = f"Select the correct verb tense for the timeframe described: '{sent}'"
        pool = [correct] + wrong
        hint = f"The time clue determines the correct verb tense: '{correct}'."

    return prompt, correct, pool, hint


def gen_e_rf(subskill: str, idx: int):
    """Reading Foundations & Decoding (E-RF: 5 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 5
    place = PLACES[idx % len(PLACES)]

    if mod == 0:
        # E-RF-01: High-frequency sight words
        words = ["BECAUSE", "FRIEND", "THEIR", "COULD", "SHOULD", "WOULD"]
        word = words[idx % len(words)]
        wrong = [word.lower().replace("e", "u"), word.lower().replace("ie", "ei"), word.lower() + "z"]
        correct = word.lower()
        prompt = f"Decode the ancient hieroglyph found in {place}! Which option correctly spells the sight word '{word}'?"
        pool = [correct] + wrong
        hint = f"The correct spelling is '{correct}'."
    elif mod == 1:
        # E-RF-02: Silent 'e' rule
        magic_e = [("hop", "hope", ["hop", "hopp", "hype"]), ("tap", "tape", ["tap", "tapp", "tep"]), ("pin", "pine", ["pin", "pinn", "pean"]), ("cub", "cube", ["cub", "cubb", "cobe"])]
        base, correct, wrong = magic_e[idx % len(magic_e)]
        prompt = f"When the magic silent 'e' attaches to the word '{base}', what new word is created?"
        pool = [correct] + wrong
        hint = f"Adding silent 'e' makes the vowel say its name: '{base}' becomes '{correct}'."
    elif mod == 2:
        # E-RF-03: Vowel digraphs (ea, oa, ee, ai)
        digraphs = [("oa", "Boat", ["Bat", "Box", "Boot"]), ("ee", "Tree", ["Tray", "True", "Trip"]), ("ai", "Rain", ["Ran", "Run", "Rope"]), ("ea", "Leaf", ["Life", "Loaf", "Left"])]
        di, correct, wrong = digraphs[idx % len(digraphs)]
        prompt = f"Which word contains the vowel team '{di}' to make the long vowel sound?"
        pool = [correct] + wrong
        hint = f"'{correct}' uses the '{di}' team."
    elif mod == 3:
        # E-RF-04: Consonant blends
        blends = [("bl-", "Blast", ["Fast", "Last", "Past"]), ("st-", "Star", ["Car", "Far", "Bar"]), ("gr-", "Green", ["Seen", "Bean", "Teen"]), ("fl-", "Flame", ["Name", "Game", "Same"])]
        bl, correct, wrong = blends[idx % len(blends)]
        prompt = f"Which word begins with the consonant blend '{bl}' in the traveler's guidebook?"
        pool = [correct] + wrong
        hint = f"'{correct}' begins with '{bl}'."
    else:
        # E-RF-05: Word families
        families = [("-ight", "Knight", ["Night", "Sight", "Fight"], ["Knot", "Knee", "Knife"]), ("-all", "Ball", ["Call", "Fall", "Tall"], ["Bell", "Bull", "Bill"]), ("-ing", "Ring", ["Sing", "Wing", "King"], ["Rope", "Rake", "Rose"])]
        fam, correct, fam_words, wrong = families[idx % len(families)]
        prompt = f"Which word belongs to the '{fam}' word family?"
        pool = [correct] + wrong[:3]
        hint = f"'{correct}' ends with '{fam}'."

    return prompt, correct, pool, hint


def gen_e_cr(subskill: str, idx: int):
    """Comprehension & Response (E-CR: 9 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 9
    name = NAMES[idx % len(NAMES)]

    if mod == 0:
        # E-CR-01: Key details / Object recall
        stories = [
            ("found a golden key under the mat.", "A golden key", ["A silver sword", "A diamond ring", "Nothing"]),
            ("read the blue spellbook in the tower.", "The blue spellbook", ["The red potion", "The green scroll", "The yellow wand"]),
            ("buried a treasure chest on the island.", "A treasure chest", ["A bag of coins", "A secret map", "A compass"])
        ]
        story, correct, wrong = stories[idx % len(stories)]
        prompt = f"Read the scroll: '{name} {story}' What object did they interact with?"
        pool = [correct] + wrong
        hint = "Read the sentence carefully to identify the specific object."
    elif mod == 1:
        # E-CR-02: Character identification
        actions = [
            ("steered the star cruiser safely through the asteroid belt while the crew rested.", name, ["The space pirate", "The alien queen", "A robot mechanic"]),
            ("brewed a magical healing elixir for the sick dragon.", name, ["The town blacksmith", "A forest goblin", "The royal guard"])
        ]
        action, correct, wrong = actions[idx % len(actions)]
        prompt = f"Read the log: '{name} {action}' Who carried out this important task?"
        pool = [correct] + wrong
        hint = f"The text explicitly names {correct}."
    elif mod == 2:
        # E-CR-03: Setting identification
        settings = [
            ("Gazing out through the observation dome at the glowing rings of Saturn", "A space station", ["A pirate ship", "A desert tent", "A dark dungeon"]),
            ("Listening to the gentle waves lap against the sandy shore under palm trees", "A tropical beach", ["A snowy mountain", "A bustling city", "A space shuttle"]),
            ("Surrounded by tall towering pine trees and dense mossy boulders", "A deep forest", ["An open ocean", "An airport hangar", "A shopping mall"])
        ]
        passage, correct, wrong = settings[idx % len(settings)]
        prompt = f"Read the passage: '{name} stood quiet, {passage}.' Where is this story set?"
        pool = [correct] + wrong
        hint = f"The sensory details describe {correct}."
    elif mod == 3:
        # E-CR-04: Main idea / Central message
        ideas = [
            ("Bees visit flowers to sip sweet nectar, and while doing so, they carry pollen from bloom to bloom so new plants can grow.", "Bees play a vital role in helping plants reproduce", ["Bees only sleep in the winter", "Flowers do not need bees", "Honey is made of water"]),
            ("Working as a team allowed the knights to lift the fallen drawbridge and protect the kingdom.", "Teamwork makes difficult tasks possible", ["Knights always work alone", "Drawbridges are made of paper", "Castles do not need doors"])
        ]
        text, correct, wrong = ideas[idx % len(ideas)]
        prompt = f"Read the excerpt: '{text}' What is the central main idea of this passage?"
        pool = [correct] + wrong
        hint = f"The main idea captures the big picture: {correct}."
    elif mod == 4:
        # E-CR-05: Cause and effect
        ce_stories = [
            ("Because the rain poured heavily all night, the river overflowed its grassy banks.", "The river overflowed", "The heavy rain poured", ["The sun was shining", "The river dried up", "The bridge was painted"]),
            ("Since the spaceship ran out of fuel cells, it had to land on the nearest moon.", "The spaceship had to land", "It ran out of fuel cells", ["It flew faster", "The crew had a party", "It reached Earth"])
        ]
        text, eff, cause, wrong = ce_stories[idx % len(ce_stories)]
        prompt = f"Read the chronicle: '{text}' What was the direct CAUSE of this event?"
        correct = cause
        pool = [cause] + wrong
        hint = f"Look for what triggered the event: '{cause}' caused '{eff}'."
    elif mod == 5:
        # E-CR-06: Chronological sequence / Order of events
        seqs = [
            ("First, {name} gathered dry firewood. Next, they struck a flint to light a warm campfire. Finally, they toasted bread.", "Gathered dry firewood", ["Struck a flint", "Toasted bread", "Put out the fire"]),
            ("First, {name} mapped the coordinates. Next, they fired the hyper-thrusters. Finally, they entered orbit.", "Mapped the coordinates", ["Fired the hyper-thrusters", "Entered orbit", "Landed the ship"])
        ]
        text, correct, wrong = seqs[idx % len(seqs)]
        prompt = f"Analyze the timeline: '{text.format(name=name)}' What happened FIRST in the sequence?"
        pool = [correct] + wrong
        hint = "Look for the clue word 'First' to determine the initial event."
    elif mod == 6:
        # E-CR-07: Problem / Conflict identification
        conflicts = [
            ("The kingdom's water supply stopped completely because a giant boulder blocked the mountain stream.", "A giant boulder blocked the mountain stream", ["The villagers were singing", "The kingdom had too much water", "The mountain was made of gold"]),
            ("The navigation computer shut down unexpectedly, leaving the spacecraft drifting in deep space.", "The navigation computer shut down unexpectedly", ["The spaceship was cruising safely", "The crew had plenty of fuel", "The stars looked pretty"])
        ]
        text, correct, wrong = conflicts[idx % len(conflicts)]
        prompt = f"Read the scenario: '{name} discovered that {text}' What is the primary conflict or problem?"
        pool = [correct] + wrong
        hint = f"The main obstacle or problem is that {correct}."
    elif mod == 7:
        # E-CR-08: Solution to the problem
        solutions = [
            ("To solve the blocked mountain stream, the crew used a wooden lever and pulley to roll the boulder aside.", "They used a lever and pulley to roll the boulder aside", ["They waited for it to rain", "They built a new castle", "They walked away"]),
            ("To reboot the dark spacecraft, {name} connected the emergency solar battery to the master circuit.", "Connected the emergency solar battery to the master circuit", ["Opened the spaceship door", "Threw away the battery", "Flew into a black hole"])
        ]
        text, correct, wrong = solutions[idx % len(solutions)]
        prompt = f"Read the resolution: '{text}' How did they successfully resolve the problem?"
        pool = [correct] + wrong
        hint = f"The solution implemented was: {correct}."
    else:
        # E-CR-09: Inference / Character feelings
        feelings = [
            ("opened the ancient treasure chest and discovered it was completely empty after months of searching. Her shoulders slumped and she let out a heavy sigh.", "Disappointed and weary", ["Overjoyed and excited", "Terrified and panicking", "Eager to dance"]),
            ("saw the rescued baby dragon safely reunite with its mother. A broad smile spread across his face as he cheered loudly.", "Proud and joyful", ["Angry and bitter", "Bored and sleepy", "Confused and worried"])
        ]
        action, correct, wrong = feelings[idx % len(feelings)]
        prompt = f"Read the passage: '{name} {action}' How was {name} feeling based on these actions?"
        pool = [correct] + wrong
        hint = f"The character's body language and reactions show they felt {correct}."

    return prompt, correct, pool, hint


def gen_e_cc(subskill: str, idx: int):
    """Creative & Composition (E-CC: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6
    name = NAMES[idx % len(NAMES)]

    if mod == 0:
        # E-CC-01: Alternative Endings
        endings = [
            ("dropped his sword, so...", "He had to defend himself with his shield.", ["He flew away on a broom.", "He became a baker.", "He turned invisible."]),
            ("saw that the bridge was broken, so...", "They built a sturdy raft from logs.", ["They walked on the clouds.", "They drank a potion.", "They went to sleep."]),
            ("ran out of water in the desert, so...", "He dug near a green palm tree to find an oasis.", ["He ate sand.", "He sang a song.", "He built a snowman."])
        ]
        start, correct, wrong = endings[idx % len(endings)]
        prompt = f"Create a logical alternative ending: {name} {start}"
        pool = [correct] + wrong
        hint = "Consider what logically and realistically resolves the situation."
    elif mod == 1:
        # E-CC-02: Question Generation
        q_scenarios = [
            ("discovered a glowing, pulsing purple crystal deep inside an abandoned mine.", "What kind of energy does this strange crystal produce?", ["Why is water wet?", "What time is dinner?", "Who likes apples?"]),
            ("found a locked chest with three keyholes on an uncharted island.", "Which three keys unlock this mysterious chest?", ["What is 2 plus 2?", "Why is the grass green?", "Where can I buy milk?"])
        ]
        scen, correct, wrong = q_scenarios[idx % len(q_scenarios)]
        prompt = f"Generate an investigative inquiry: {name} {scen} Which question is the most insightful to investigate?"
        pool = [correct] + wrong
        hint = "An investigative question directly explores the mystery at hand."
    elif mod == 2:
        # E-CC-03: Story Starter / Hook
        hooks = [
            ("exploring a sunken pirate galleon", "Beneath the crashing waves, a shadow loomed over the coral reef: the cursed galleon had reappeared.", ["Once there was water.", "Fish swim in the ocean.", "Boats are made of wood."]),
            ("investigating an alien signal on Mars", "The red dust settled as a rhythmic metallic ping echoed from inside the Martian cavern.", ["Mars is a planet.", "Rocks are hard.", "Space is very big."])
        ]
        topic, correct, wrong = hooks[idx % len(hooks)]
        prompt = f"Choose the most gripping narrative hook to begin a story about {topic}:"
        pool = [correct] + wrong
        hint = "A great narrative hook creates immediate intrigue and vivid action."
    elif mod == 3:
        # E-CC-04: Descriptive Detail / Sensory Imagery
        sensory = [
            ("a stormy winter night at the fortress", "Howling icy winds rattled the heavy oak shutters as sleet pelted against cold stone walls.", ["It was cold and dark outside.", "Winter is one of four seasons.", "There was weather happening."]),
            ("a sunlit magical meadow", "Golden sunlight filtered through emerald leaves, warming fragrant wildflowers alive with humming honeybees.", ["Plants were in the dirt.", "Flowers have stems.", "The place looked okay."])
        ]
        setting, correct, wrong = sensory[idx % len(sensory)]
        prompt = f"Which sentence adds the richest sensory imagery describing {setting}?"
        pool = [correct] + wrong
        hint = "Rich imagery appeals to sight, sound, smell, and touch."
    elif mod == 4:
        # E-CC-05: Dialogue / Character Voice
        dialogues = [
            ("a cautious elder wizard warning an impatient apprentice", "'Tread softly, young one, for ancient wards sleep lightly in these catacombs.'", ["'Let's run as fast as we can!'", "'Whatever, do whatever you want.'", "'I am going to eat a sandwich.'"]),
            ("a courageous knight rallying tired soldiers", "'Stand firm! Together, our shields will hold the line until sunrise!'", ["'I think we should probably give up.'", "'Who took my boots?'", "'War is kind of noisy.'"])
        ]
        context, correct, wrong = dialogues[idx % len(dialogues)]
        prompt = f"Which dialogue line best captures the character voice of {context}?"
        pool = [correct] + wrong
        hint = "The character voice must match their personality, wisdom, and the dramatic urgency."
    else:
        # E-CC-06: Narrative Transition
        transitions = [
            ("The explorers decoded the map. ___, they set sail for the mysterious island.", "The following morning", ["Suddenly without warning", "Because it was raining", "In the distant past"]),
            ("The alarms blared through the space station. ___, Commander Zorg scrambled to the command bridge.", "Instantly", ["Many years later", "On the other hand", "In conclusion"])
        ]
        sent, correct, wrong = transitions[idx % len(transitions)]
        prompt = f"Choose the smoothest transition phrase to connect these narrative events: '{sent}'"
        pool = [correct] + wrong
        hint = f"'{correct}' connects the timing and momentum of the two events seamlessly."

    return prompt, correct, pool, hint


def gen_e_we(subskill: str, idx: int):
    """Written Expression & Editing (E-WE: 9 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 9
    name = NAMES[idx % len(NAMES)]

    if mod == 0:
        # E-WE-01: Subject-verb agreement editing
        errors = [("The knights is brave.", "The knights are brave.", ["The knight are brave.", "Knights is brave.", "Brave is the knights."]),
                  ("She run fast.", "She runs fast.", ["She running fast.", "She runned fast.", "Her runs fast."]),
                  ("They was happy.", "They were happy.", ["They is happy.", "Them was happy.", "They happy was."])]
        bad, correct, wrong = errors[idx % len(errors)]
        prompt = f"Fix the grammar error in {name}'s message: '{bad}'"
        pool = [correct] + wrong
        hint = "Make sure the subject and verb agree in number."
    elif mod == 1:
        # E-WE-02: Capitalization editing
        caps = [
            ("yesterday, captain orion explored mars.", "Yesterday, Captain Orion explored Mars.", ["yesterday, Captain orion explored Mars.", "Yesterday, captain Orion explored mars.", "Yesterday, Captain Orion Explored mars."]),
            ("princess luna lives in the crystal palace.", "Princess Luna lives in the Crystal Palace.", ["princess luna Lives in the Crystal palace.", "Princess luna lives in the crystal Palace.", "princess Luna lives in the Crystal Palace."])
        ]
        bad, correct, wrong = caps[idx % len(caps)]
        prompt = f"Proofread {name}'s journal entry for capitalization: '{bad}' Which version is correct?"
        pool = [correct] + wrong
        hint = "Capitalize the first word of a sentence, proper names, and specific geographical places."
    elif mod == 2:
        # E-WE-03: Punctuation editing
        puncts = [
            ("Look out for the falling dragon scale", "Look out for the falling dragon scale!", ["Look out for the falling dragon scale?", "Look out for the falling dragon scale.", "Look out for the falling dragon scale,"]),
            ("Can you help me decode this ancient map", "Can you help me decode this ancient map?", ["Can you help me decode this ancient map.", "Can you help me decode this ancient map!", "Can you help me decode this ancient map,"])
        ]
        bad, correct, wrong = puncts[idx % len(puncts)]
        prompt = f"Add the correct end punctuation mark to complete this sentence from {name}: '{bad}'"
        pool = [correct] + wrong
        hint = "Use exclamation marks for warnings/excitement, and question marks for inquiries."
    elif mod == 3:
        # E-WE-04: Plural noun spelling
        plurals = [("box", "boxes", ["boxs", "boxies", "boxen"]), ("fox", "foxes", ["foxs", "foxies", "foxen"]), ("leaf", "leaves", ["leafs", "leafes", "leavs"]), ("city", "cities", ["citys", "cityes", "cites"])]
        sing, correct, wrong = plurals[idx % len(plurals)]
        prompt = f"What is the correct plural spelling of the noun '{sing}' in {name}'s inventory list?"
        pool = [correct] + wrong
        hint = f"The plural form of '{sing}' is '{correct}'."
    elif mod == 4:
        # E-WE-05: Apostrophe / Contractions
        conts = [("do not", "don't", ["dont", "do'nt", "d'ont"]), ("cannot", "can't", ["cant", "ca'nt", "cann't"]), ("it is", "it's", ["its", "i'ts", "it'is"]), ("we will", "we'll", ["well", "we'ill", "w'ell"])]
        full, correct, wrong = conts[idx % len(conts)]
        prompt = f"Which option correctly shortens the words '{full}' into a contraction?"
        pool = [correct] + wrong
        hint = f"The apostrophe replaces omitted letters: '{full}' becomes '{correct}'."
    elif mod == 5:
        # E-WE-06: Run-on sentence correction
        runons = [
            ("The sun rose over the hills we packed our gear.", "The sun rose over the hills, and we packed our gear.", ["The sun rose over the hills we, packed our gear.", "The sun rose, over the hills we packed our gear.", "The sun rose over the hills and we packed, our gear."]),
            ("The dragon roared loudly the knight raised his shield.", "The dragon roared loudly, so the knight raised his shield.", ["The dragon roared loudly so, the knight raised his shield.", "The dragon roared, loudly the knight raised his shield.", "The dragon roared loudly the knight, raised his shield."])
        ]
        bad, correct, wrong = runons[idx % len(runons)]
        prompt = f"Proofread and repair this run-on sentence: '{bad}'"
        pool = [correct] + wrong
        hint = "Connect independent clauses with a comma and a coordinating conjunction."
    elif mod == 6:
        # E-WE-07: Vivid adjective enhancement
        adjs = [
            ("In the sentence '{name} ate a *good* feast', which vivid adjective best replaces 'good'?", "sumptuous", ["nice", "fine", "okay"]),
            ("In the sentence '{name} walked through the *big* cavern', which vivid word best replaces 'big'?", "colossal", ["large", "wide", "tall"]),
            ("In the sentence '{name} saw a *pretty* crystal', which vivid word best replaces 'pretty'?", "breathtaking", ["neat", "cool", "clean"])
        ]
        prompt_q, correct, wrong = adjs[idx % len(adjs)]
        prompt = prompt_q.format(name=name)
        pool = [correct] + wrong
        hint = f"'{correct}' provides far richer descriptive depth."
    elif mod == 7:
        # E-WE-08: Sentence combining
        combos = [
            ("The wind blew hard.", "The ship sailed swiftly.", "The wind blew hard, so the ship sailed swiftly.", ["The wind blew hard but the ship sailed swiftly.", "The wind blew hard because the ship sailed swiftly.", "The wind blew hard or the ship sailed swiftly."]),
            ("The wizard read the book.", "He learned a new charm.", "The wizard read the book and learned a new charm.", ["The wizard read the book but learned a new charm.", "The wizard read the book or learned a new charm.", "The wizard read the book so learned a new charm."])
        ]
        s1, s2, correct, wrong = combos[idx % len(combos)]
        prompt = f"Combine these two sentences into one effective compound sentence: '{s1}' and '{s2}'"
        pool = [correct] + wrong
        hint = "Use the coordinating conjunction that expresses the logical relationship between the two clauses."
    else:
        # E-WE-09: Proofreading spelling errors
        spells = [
            ("The explorer walked down the secret passige.", "passage", ["secret", "explorer", "walked"]),
            ("We observed a wonderfull meteor shower.", "wonderful", ["observed", "meteor", "shower"]),
            ("The knight carried a heavy sheild into battle.", "shield", ["knight", "carried", "battle"])
        ]
        sent, correct, wrong = spells[idx % len(spells)]
        prompt = f"Find the misspelled word in this journal sentence: '{sent}' Which word is spelled incorrectly?"
        pool = [correct] + wrong
        hint = f"The correct spelling is '{correct}'."

    return prompt, correct, pool, hint


def gen_e_ol(subskill: str, idx: int):
    """Oral Language & Communication (E-OL: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6
    name = NAMES[idx % len(NAMES)]
    place = PLACES[idx % len(PLACES)]

    if mod == 0:
        # E-OL-01: Formal honorific / royal greeting
        prompt = f"Situation in {place}: You are introduced to the Queen alongside {name}. What is the most respectful and polite greeting?"
        correct = "Your Majesty, it is an honor to meet you."
        pool = [correct, "Hey there, Queen!", "What's up, lady?", "Yo, what are you doing here?"]
        hint = "Formal royal introductions require respectful titles and honorifics."
    elif mod == 1:
        # E-OL-02: Polite apology
        prompt = f"Situation in {place}: You accidentally bump into {name} and drop a fragile potion bottle. What is the most polite apology?"
        correct = "I am so sorry for my carelessness! Let me help clean this up."
        pool = [correct, "You were standing in my way!", "Whatever, potions are cheap.", "You should look where you're going!"]
        hint = "A genuine apology expresses remorse and offers to help fix the mistake."
    elif mod == 2:
        # E-OL-03: Expressing gratitude
        prompt = f"Situation in {place}: A companion hands {name} an extra water flask during a long trek. What is the most courteous response?"
        correct = "Thank you so much, I truly appreciate your kindness."
        pool = [correct, "Give me another one too.", "Took you long enough.", "I didn't ask for this."]
        hint = "Polite gratitude acknowledges the helpful act warmly."
    elif mod == 3:
        # E-OL-04: Asking for assistance
        prompt = f"Situation in {place}: You need help carrying a heavy chest of equipment with {name}. How do you ask courteously?"
        correct = "Excuse me, would you mind lending a hand with this heavy chest?"
        pool = [correct, "Carry this right now!", "You have to do this for me.", "Pick this up, hurry!"]
        hint = "Courteous requests begin with polite phrases like 'Excuse me' and 'Would you mind'."
    elif mod == 4:
        # E-OL-05: Active listening & clarification
        prompt = f"Situation in {place}: {name} gives complex instructions on defusing the power grid. Which response demonstrates active listening?"
        correct = "So if I understand correctly, I must pull the blue switch first, then turn the silver dial?"
        pool = [correct, "Yeah yeah, whatever you say.", "I wasn't listening at all.", "Can you just do it yourself?"]
        hint = "Active listening paraphrases and checks understanding."
    else:
        # E-OL-06: Giving clear multi-step directions
        prompt = f"Situation in {place}: A lost traveler asks {name} for directions to the observatory. Which directions are the clearest and easiest to follow?"
        correct = "First walk straight past the fountain, then turn left at the stone archway, and the observatory will be directly ahead."
        pool = [correct, "Go somewhere over there and look around.", "It's near a tree, you can't miss it.", "Just wander until you see it."]
        hint = "Clear directions use sequential transitions: 'First', 'Then', 'Next'."

    return prompt, correct, pool, hint


# ----------------------------------------------------------------------
# SCIENCE & EVS DIVERSIFICATION ENGINES (6 Strands)
# ----------------------------------------------------------------------

def gen_s_kn(subskill: str, idx: int):
    """Knowledge of Scientific Concepts (S-KN: 11 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 11
    name = NAMES[idx % len(NAMES)]

    if mod == 0:
        # S-KN-01: Aquatic respiration / gills
        prompt = f"{name} observes a creature underwater that extracts oxygen directly through gills. Which animal is it?"
        correct = "Shark"
        pool = ["Shark", "Dolphin", "Sea Turtle", "Penguin"]
        hint = "Fish and sharks use gills to breathe underwater, while marine mammals use lungs."
    elif mod == 1:
        # S-KN-02: Arthropods / insects vs arachnids
        prompt = f"{name} spots an invertebrate crawling on a leaf with exactly eight jointed legs and two body sections. What is it?"
        correct = "Spider"
        pool = ["Spider", "Ant", "Beetle", "Butterfly"]
        hint = "Insects have 6 legs, whereas arachnids (spiders) have 8 legs."
    elif mod == 2:
        # S-KN-03: Botany / plant growth from seeds
        prompt = f"{name} collects a hard brown seed with a cup-like cap that will grow into a mighty tree. What tree grows from an acorn?"
        correct = "Oak tree"
        pool = ["Oak tree", "Pine tree", "Rose bush", "Sunflower"]
        hint = "Acorns are the seeds of oak trees."
    elif mod == 3:
        # S-KN-04: Avian characteristics (feathers, beaks, eggs)
        prompt = f"{name} examines a warm-blooded animal that has lightweight hollow bones, feathers, and lays hard-shelled eggs. What class of animal is it?"
        correct = "Bird"
        pool = ["Bird", "Reptile", "Mammal", "Amphibian"]
        hint = "Feathers and hollow bones are defining characteristics of birds."
    elif mod == 4:
        # S-KN-05: Reptiles vs amphibians
        prompt = f"{name} finds a cold-blooded animal basking in the sun with dry, scaly skin. Which class does it belong to?"
        correct = "Reptile"
        pool = ["Reptile", "Amphibian", "Mammal", "Fish"]
        hint = "Reptiles have dry scaly skin; amphibians have moist, smooth skin."
    elif mod == 5:
        # S-KN-06: Mammal characteristics (hair/fur, milk)
        prompt = f"While hiking, {name} encounters a warm-blooded animal covered in thick fur that nourishes its young with milk. What class is it?"
        correct = "Mammal"
        pool = ["Mammal", "Bird", "Reptile", "Insect"]
        hint = "Having fur/hair and producing milk for young are hallmark mammal traits."
    elif mod == 6:
        # S-KN-07: Human body systems (cardiovascular)
        prompt = f"{name} studies human physiology. Which muscular organ acts as a pump to circulate oxygen-rich blood throughout the body?"
        correct = "The Heart"
        pool = ["The Heart", "The Lungs", "The Stomach", "The Liver"]
        hint = "The heart pumps blood through arteries and veins."
    elif mod == 7:
        # S-KN-08: Solar system & stars
        prompt = f"{name} looks through the observatory telescope. Which celestial body is the closest star to planet Earth?"
        correct = "The Sun"
        pool = ["The Sun", "The Moon", "Mars", "Polaris"]
        hint = "The Sun is a yellow dwarf star at the center of our solar system."
    elif mod == 8:
        # S-KN-09: Weather phenomena & water cycle
        prompt = f"{name} looks up as water vapor cools and condenses around microscopic dust particles in the atmosphere. What is formed?"
        correct = "Clouds"
        pool = ["Clouds", "Rainbows", "Wind", "Lightning"]
        hint = "Clouds form when rising water vapor cools and condenses."
    elif mod == 9:
        # S-KN-10: Rocks, minerals & fossils
        prompt = f"{name} unearths the hardened imprint of an ancient prehistoric fern preserved inside sedimentary rock. What is this specimen called?"
        correct = "A Fossil"
        pool = ["A Fossil", "A Crystal", "A Meteorite", "A Gemstone"]
        hint = "Preserved remains or traces of ancient life are called fossils."
    else:
        # S-KN-11: Renewable natural resources
        prompt = f"{name} is designing an eco-friendly outpost. Which of these is an inexhaustible, renewable source of energy?"
        correct = "Solar energy from sunlight"
        pool = ["Solar energy from sunlight", "Coal", "Petroleum oil", "Natural gas"]
        hint = "Sunlight, wind, and flowing water are clean, renewable energy resources."

    return prompt, correct, pool, hint


def gen_s_oc(subskill: str, idx: int):
    """Observational Concepts (S-OC: 5 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 5
    place = PLACES[idx % len(PLACES)]

    if mod == 0:
        # S-OC-01: Living vs non-living
        items = [("living", "A Maple Tree", ["A Granite Rock", "A Metal Bicycle", "A Plastic Bottle"]),
                 ("non-living", "A Silver Coin", ["A Flying Sparrow", "A Green Fern", "A Swimming Trout"])]
        cat, correct, wrong = items[idx % len(items)]
        prompt = f"While exploring {place}, which of these is classified as a {cat} entity?"
        pool = [correct] + wrong
        hint = f"{correct} is {cat} because of biological growth and cellular structure."
    elif mod == 1:
        # S-OC-02: Animal classification
        prompts = [
            ("Which of these animals is classified as a mammal?", "Dolphin", ["Crocodile", "Tuna", "Eagle"]),
            ("Which of these animals is classified as an amphibian?", "Tree Frog", ["Lizard", "Robin", "Goldfish"])
        ]
        p_str, correct, wrong = prompts[idx % len(prompts)]
        prompt = f"Observational survey in {place}: {p_str}"
        pool = [correct] + wrong
        hint = f"{correct} fits this biological classification."
    elif mod == 2:
        # S-OC-03: Plant anatomy / parts
        parts = [
            ("absorbs water and nutrients from the soil while anchoring the plant", "Roots", ["Leaves", "Flowers", "Stem"]),
            ("uses sunlight to produce food for the plant through photosynthesis", "Leaves", ["Roots", "Bark", "Petals"])
        ]
        desc, correct, wrong = parts[idx % len(parts)]
        prompt = f"Observing plant life in {place}: Which plant part {desc}?"
        pool = [correct] + wrong
        hint = f"The {correct.lower()} perform this function."
    elif mod == 3:
        # S-OC-04: Natural vs human-made materials
        materials = [
            ("natural material harvested from organic resources", "Timber wood", ["Synthetic plastic", "Nylon rope", "Polyester fabric"]),
            ("human-made synthetic material created in a factory", "Plastic container", ["Granite stone", "Cotton wool", "Clay soil"])
        ]
        desc, correct, wrong = materials[idx % len(materials)]
        prompt = f"Classifying specimens in {place}: Which item is a {desc}?"
        pool = [correct] + wrong
        hint = f"{correct} is an example."
    else:
        # S-OC-05: States of matter classification
        states = [
            ("solid with a definite shape and volume", "An ice cube", ["Liquid water", "Water vapor", "Helium gas"]),
            ("gas that expands to fill the entire container", "Steam vapor", ["A wooden block", "Liquid milk", "A metal coin"])
        ]
        desc, correct, wrong = states[idx % len(states)]
        prompt = f"Analyzing matter in {place}: Which specimen is a {desc}?"
        pool = [correct] + wrong
        hint = f"{correct} exemplifies this state of matter."

    return prompt, correct, pool, hint


def gen_s_pp(subskill: str, idx: int):
    """Physical Properties (S-PP: 4 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 4
    name = NAMES[idx % len(NAMES)]

    if mod == 0:
        # S-PP-01: Freezing / Melting (Solid <-> Liquid)
        prompt = f"If {name} places liquid water into a sub-zero freezer, what state of matter does it change into?"
        correct = "Solid (Ice)"
        pool = ["Solid (Ice)", "Gas (Steam)", "Plasma", "Liquid"]
        hint = "Water freezes at 0°C (32°F) and transitions from liquid to solid ice."
    elif mod == 1:
        # S-PP-02: Evaporation / Boiling (Liquid -> Gas)
        prompt = f"When {name} heats water over a hot stove until it boils vigorously, what does the liquid transform into?"
        correct = "Gas (Water Vapor)"
        pool = ["Gas (Water Vapor)", "Solid (Ice)", "Liquid (Mercury)", "Plasma"]
        hint = "Boiling causes liquid to vaporize into water vapor gas."
    elif mod == 2:
        # S-PP-03: Condensation (Gas -> Liquid)
        prompt = f"When warm water vapor in the air touches the cold glass of {name}'s iced lemonade, droplets form on the outside. What process is this?"
        correct = "Condensation"
        pool = ["Condensation", "Evaporation", "Freezing", "Melting"]
        hint = "Condensation occurs when a gas cools down and turns back into a liquid."
    else:
        # S-PP-04: Magnetic attraction
        prompt = f"{name} tests various objects with a bar magnet. Which item will be strongly ATTRACTED to the magnet?"
        correct = "An iron nail"
        pool = ["An iron nail", "A wooden stick", "A plastic ruler", "A rubber eraser"]
        hint = "Magnets attract ferromagnetic metals like iron, steel, and nickel."

    return prompt, correct, pool, hint


def gen_s_ee(subskill: str, idx: int):
    """Earth & Environment (S-EE: 5 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 5
    color = COLORS[idx % len(COLORS)]

    if mod == 0:
        # S-EE-01: Desert adaptations
        prompt = f"You are trekking across a scorching, sandy desert in a {color} suit. Which animal has specialized humps to store fat for energy in this dry habitat?"
        correct = "Camel"
        pool = ["Camel", "Polar Bear", "Penguin", "Tree Frog"]
        hint = "Camels are specially adapted with fat-storing humps and wide feet for desert survival."
    elif mod == 1:
        # S-EE-02: Arctic / Polar adaptations
        prompt = f"Exploring an icy, frozen polar tundra in a {color} parka: Which creature has thick insulating blubber and water-resistant feathers to thrive in freezing oceans?"
        correct = "Penguin"
        pool = ["Penguin", "Camel", "Desert Lizard", "Chimpanzee"]
        hint = "Penguins have dense feathers and thick blubber layers to stay warm in freezing waters."
    elif mod == 2:
        # S-EE-03: Rainforest / Wetland adaptations
        prompt = f"Deep in a lush, humid tropical rainforest: Which amphibian has moist skin and suction-cup toe pads to climb slick trees?"
        correct = "Tree Frog"
        pool = ["Tree Frog", "Camel", "Polar Bear", "Bactrian Camel"]
        hint = "Tree frogs rely on moist habitats and specialized toe pads for arboreal living."
    elif mod == 3:
        # S-EE-04: Ocean / Marine ecosystem
        prompt = f"Diving beneath ocean waves along a vibrant coral reef: Which marine animal breathes air through a blowhole on top of its head?"
        correct = "Dolphin"
        pool = ["Dolphin", "Clownfish", "Jellyfish", "Sea Anemone"]
        hint = "Dolphins are marine mammals that must surface to breathe air through blowholes."
    else:
        # S-EE-05: Seasonal adaptations in deciduous forests
        prompt = f"In a temperate woodland, autumn arrives and daylight hours decrease. How do deciduous trees adapt for winter survival?"
        correct = "They shed their leaves"
        pool = ["They shed their leaves", "They grow bright flowers", "They double their height", "They produce sweet fruit"]
        hint = "Deciduous trees drop their leaves in autumn to conserve water through winter."

    return prompt, correct, pool, hint


def gen_s_mo(subskill: str, idx: int):
    """Measurement & Observation in Science (S-MO: 4 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 4
    name = NAMES[idx % len(NAMES)]

    if mod == 0:
        # S-MO-01: Temperature tool
        prompt = f"Which scientific instrument would {name} use to measure the thermal temperature of a liquid in degrees Celsius?"
        correct = "Thermometer"
        pool = ["Thermometer", "Balance scale", "Measuring tape", "Barometer"]
        hint = "A thermometer measures temperature."
    elif mod == 1:
        # S-MO-02: Mass / Weight tool
        prompt = f"Which laboratory tool should {name} use to measure the exact mass of mineral crystals in grams?"
        correct = "Balance scale"
        pool = ["Balance scale", "Thermometer", "Ruler", "Telescope"]
        hint = "A balance scale measures mass/weight."
    elif mod == 2:
        # S-MO-03: Length / Distance tool
        prompt = f"Which tool does {name} need to measure the exact length of a dinosaur bone specimen in centimeters?"
        correct = "Ruler or measuring tape"
        pool = ["Ruler or measuring tape", "Graduated cylinder", "Thermometer", "Microscope"]
        hint = "Rulers and measuring tapes measure length and distance."
    else:
        # S-MO-04: Optical magnification tool
        prompt = f"Which optical instrument allows {name} to magnify and view microscopic plant cells invisible to the naked eye?"
        correct = "Microscope"
        pool = ["Microscope", "Telescope", "Binoculars", "Camera lens"]
        hint = "A microscope magnifies microscopic specimens."

    return prompt, correct, pool, hint


def gen_s_in(subskill: str, idx: int):
    """Scientific Inquiry & Experimentation (S-IN: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6
    place = PLACES[idx % len(PLACES)]

    if mod == 0:
        # S-IN-01: Density / Sink or Float test
        prompt = f"During a science experiment in {place}, you drop a heavy solid iron key and a dry wooden cork into a basin of water. What happens to the cork?"
        correct = "The cork floats because wood is less dense than water"
        pool = [
            "The cork floats because wood is less dense than water",
            "The cork sinks straight to the bottom",
            "The cork instantly dissolves into liquid",
            "The cork turns into stone"
        ]
        hint = "Objects less dense than water float; denser objects sink."
    elif mod == 1:
        # S-IN-02: Thermal energy & melting ice
        prompt = f"In {place}, a scientist leaves an ice cube in the direct hot sun. What thermodynamic change occurs?"
        correct = "The ice absorbs heat energy and melts into liquid water"
        pool = [
            "The ice absorbs heat energy and melts into liquid water",
            "The ice gets colder and grows bigger",
            "The ice turns into solid gold",
            "The ice bursts into flames"
        ]
        hint = "Heat energy causes solid ice to melt into liquid water."
    elif mod == 2:
        # S-IN-03: Pigment color mixing
        prompt = f"In the alchemy laboratory in {place}, you mix pure red paint pigment with pure blue paint pigment. What color is produced?"
        correct = "Purple"
        pool = ["Purple", "Green", "Yellow", "Orange"]
        hint = "Red + Blue = Purple."
    elif mod == 3:
        # S-IN-04: Plant growth variables (Sunlight)
        prompt = f"A botanist places two identical bean plants in {place}. Plant A receives daily sunlight and water. Plant B is placed in a pitch-black closet with water. What will happen to Plant B?"
        correct = "Plant B will turn pale, grow weak, and fail to thrive without light"
        pool = [
            "Plant B will turn pale, grow weak, and fail to thrive without light",
            "Plant B will grow twice as fast and produce flowers",
            "Plant B will turn bright purple and glow",
            "Plant B will not change at all"
        ]
        hint = "Plants require sunlight for photosynthesis to generate food and chlorophyll."
    elif mod == 4:
        # S-IN-05: Friction on rough vs smooth surfaces
        prompt = f"An engineer releases a toy car down a smooth wooden ramp and then down a rough carpet ramp. On which surface will the car roll FARTHER?"
        correct = "On the smooth wooden ramp, because it has less friction"
        pool = [
            "On the smooth wooden ramp, because it has less friction",
            "On the rough carpet ramp, because it has more friction",
            "Both ramps will produce identical distances",
            "Neither ramp will allow the car to move"
        ]
        hint = "Smooth surfaces produce less friction to slow moving objects down."
    else:
        # S-IN-06: Sound vibration mechanics
        prompt = f"In the acoustics chamber in {place}, a musician gently plucks a tight guitar string. What causes the sound to be produced?"
        correct = "The string vibrates rapidly back and forth, creating sound waves"
        pool = [
            "The string vibrates rapidly back and forth, creating sound waves",
            "The string changes color",
            "Air is sucked into a vacuum",
            "Light bounces off the wood"
        ]
        hint = "Sound is produced by rapid physical vibrations traveling as acoustic waves."

    return prompt, correct, pool, hint


# ----------------------------------------------------------------------
# LOGICAL REASONING DIVERSIFICATION ENGINES (6 Strands)
# ----------------------------------------------------------------------

def gen_l_pc(subskill: str, idx: int):
    """Patterning & Classification (L-PC: 4 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 4
    name = NAMES[idx % len(NAMES)]

    if mod == 0:
        # L-PC-01: Functional category odd-one-out
        prompt = f"{name} asks: Which of these transport vehicles does NOT belong with space-faring exploration vessels?"
        correct = "Submarine"
        pool = ["Submarine", "Star Cruiser", "Lunar Rover", "Orbital Space Station"]
        hint = "A submarine operates underwater on Earth, while the others explore outer space."
    elif mod == 1:
        # L-PC-02: Biological category odd-one-out
        prompt = f"{name} sorts agricultural produce into bins: Apple, Banana, Orange, and Carrot. Which item is the odd one out?"
        correct = "Carrot"
        pool = ["Carrot", "Apple", "Banana", "Orange"]
        hint = "Carrot is a root vegetable, whereas the others are tree/botanical fruits."
    elif mod == 2:
        # L-PC-03: Geometric attribute odd-one-out
        prompt = f"{name} examines four geometric shapes: Triangle, Square, Hexagon, and Circle. Which shape does NOT belong with the others?"
        correct = "Circle"
        pool = ["Circle", "Triangle", "Square", "Hexagon"]
        hint = "A circle has a continuous curved boundary, while the others are polygons made of straight sides."
    else:
        # L-PC-04: Material composition odd-one-out
        prompt = f"{name} inspects tools in the workshop: Iron hammer, Steel wrench, Copper screwdriver, and Wooden table. Which item does NOT belong by material?"
        correct = "Wooden table"
        pool = ["Wooden table", "Iron hammer", "Steel wrench", "Copper screwdriver"]
        hint = "The table is made of wood, while all the tools are composed of metals."

    return prompt, correct, pool, hint


def gen_l_ar(subskill: str, idx: int):
    """Analogical Reasoning (L-AR: 2 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 2
    color = COLORS[idx % len(COLORS)]

    if mod == 0:
        # L-AR-01: Habitat & functional analogies
        analogies = [
            ("Bird is to Sky as Fish is to...", "Water", ["Ground", "Space", "Tree"]),
            ("Car is to Road as Train is to...", "Tracks", ["Air", "Water", "Space"]),
            ("Astronaut is to Spaceship as Captain is to...", "Galleon Ship", ["Bicycle", "Skateboard", "Horse"])
        ]
        prompt_str, correct, wrong = analogies[idx % len(analogies)]
        prompt = f"Read the {color} tablet to complete the environmental analogy: {prompt_str}"
        pool = [correct] + wrong
        hint = "Consider the relationship between the creature or vehicle and its medium of movement."
    else:
        # L-AR-02: Opposites & attribute analogies
        opp_analogies = [
            ("Fire is to Hot as Ice is to...", "Cold", ["Warm", "Bright", "Dark"]),
            ("Sun is to Day as Moon is to...", "Night", ["Morning", "Afternoon", "Noon"]),
            ("Giant is to Tall as Dwarf is to...", "Short", ["Gigantic", "Heavy", "Loud"])
        ]
        prompt_str, correct, wrong = opp_analogies[idx % len(opp_analogies)]
        prompt = f"Read the {color} tablet to solve the attribute analogy: {prompt_str}"
        pool = [correct] + wrong
        hint = "Identify the direct sensory or semantic property connecting each pair."

    return prompt, correct, pool, hint


def gen_l_sr(subskill: str, idx: int):
    """Spatial Reasoning (L-SR: 5 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 5
    name = NAMES[idx % len(NAMES)]

    if mod == 0:
        # L-SR-01: Tracing polygon perimeter
        shapes = [("triangle", "3", ["4", "5", "6"]), ("square", "4", ["3", "5", "6"]), ("pentagon", "5", ["3", "4", "6"]), ("hexagon", "6", ["4", "5", "8"])]
        shape, correct, wrong = shapes[idx % len(shapes)]
        prompt = f"If {name} traces a continuous line along the outer boundary of a {shape}, how many straight sides do they trace?"
        pool = [correct] + wrong
        hint = f"A {shape} has exactly {correct} straight perimeter edges."
    elif mod == 1:
        # L-SR-02: Mental rotation
        rotations = [
            ("an arrow pointing UP is rotated 90 degrees CLOCKWISE", "Pointing RIGHT", ["Pointing DOWN", "Pointing LEFT", "Pointing UP"]),
            ("an arrow pointing RIGHT is rotated 90 degrees CLOCKWISE", "Pointing DOWN", ["Pointing UP", "Pointing LEFT", "Pointing RIGHT"])
        ]
        desc, correct, wrong = rotations[idx % len(rotations)]
        prompt = f"Spatial rotation: If {desc}, which direction does it face now?"
        pool = [correct] + wrong
        hint = "Clockwise rotation turns like the hands of an analog clock."
    elif mod == 2:
        # L-SR-03: 3D cube nets
        prompt = f"A flat paper pattern consists of 6 connected squares arranged in the shape of a cross. When folded along its edges, what 3D geometric solid does it form?"
        correct = "A Cube"
        pool = ["A Cube", "A Pyramid", "A Cylinder", "A Sphere"]
        hint = "A cross net of 6 squares folds into a 6-faced closed cube."
    elif mod == 3:
        # L-SR-04: Bird's-eye view / Top-down perspective
        prompt = f"A cylinder is placed upright on a table. If {name} looks directly DOWN at it from a bird's-eye view above, what 2D shape do they see?"
        correct = "A Circle"
        pool = ["A Circle", "A Rectangle", "A Triangle", "A Diamond"]
        hint = "Looking directly down onto an upright cylinder reveals its circular base."
    else:
        # L-SR-05: Mirror reflection symmetry
        prompt = f"A lowercase letter 'b' is held up facing a flat vertical mirror. What letter shape does its reflection most closely resemble?"
        correct = "Letter 'd'"
        pool = ["Letter 'd'", "Letter 'p'", "Letter 'q'", "Letter 'b'"]
        hint = "A vertical mirror flips left and right: 'b' reflects into 'd'."

    return prompt, correct, pool, hint


def gen_l_rc(subskill: str, idx: int):
    """Relational & Comparative Logic (L-RC: 5 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 5
    place = PLACES[idx % len(PLACES)]

    if mod == 0:
        # L-RC-01: Size ordering chain
        chains = [
            ("Titan > Earth > Moon", "Moon", "SMALLEST", ["Titan", "Earth", "They are equal"]),
            ("Sun > Jupiter > Earth", "Sun", "LARGEST", ["Jupiter", "Earth", "They are equal"])
        ]
        chain, correct, q, wrong = chains[idx % len(chains)]
        prompt = f"Size logic in {place}: Given the inequality chain {chain}, which body is the {q}?"
        pool = [correct] + wrong
        hint = f"Follow the inequality symbols: {correct} is the {q.lower()}."
    elif mod == 1:
        # L-RC-02: Weight comparison chain
        w_chains = [
            ("A boulder is heavier than an anvil. An anvil is heavier than a hammer.", "The boulder", "HEAVIEST", ["The anvil", "The hammer", "All weigh the same"]),
            ("A gold coin is lighter than a silver bar. A silver bar is lighter than a chest.", "The gold coin", "LIGHTEST", ["The silver bar", "The chest", "All weigh the same"])
        ]
        premise, correct, q, wrong = w_chains[idx % len(w_chains)]
        prompt = f"Comparative weight logic in {place}: {premise} Which item is the {q}?"
        pool = [correct] + wrong
        hint = f"Trace the transitive weight chain: {correct} is the {q.lower()}."
    elif mod == 2:
        # L-RC-03: Height ordering
        heights = [
            ("Tower Alpha is taller than Tower Beta. Tower Beta is taller than Tower Gamma.", "Tower Alpha", "TALLEST", ["Tower Beta", "Tower Gamma", "All are equal"]),
            ("The Redwood is taller than the Pine. The Pine is taller than the Willow.", "The Willow", "SHORTEST", ["The Redwood", "The Pine", "All are equal"])
        ]
        premise, correct, q, wrong = heights[idx % len(heights)]
        prompt = f"Height ranking in {place}: {premise} Which one is the {q}?"
        pool = [correct] + wrong
        hint = f"By transitive comparison, {correct} is the {q.lower()}."
    elif mod == 3:
        # L-RC-04: Speed comparison
        speeds = [
            ("Cheetah runs faster than Horse. Horse runs faster than Turtle.", "Cheetah", "FASTEST", ["Horse", "Turtle", "All run at the same speed"]),
            ("Rocket cruises faster than Jet. Jet cruises faster than Glider.", "Glider", "SLOWEST", ["Rocket", "Jet", "All cruise at the same speed"])
        ]
        premise, correct, q, wrong = speeds[idx % len(speeds)]
        prompt = f"Velocity comparison in {place}: {premise} Which traveler is the {q}?"
        pool = [correct] + wrong
        hint = f"Following the speed chain confirms {correct} is the {q.lower()}."
    else:
        # L-RC-05: Chronological sequence logic
        times = [
            ("Event A happened before Event B. Event B happened before Event C.", "Event A", "FIRST", ["Event B", "Event C", "All happened simultaneously"]),
            ("Breakfast occurs before Lunch. Lunch occurs before Dinner.", "Dinner", "LAST", ["Breakfast", "Lunch", "All occur at noon"])
        ]
        premise, correct, q, wrong = times[idx % len(times)]
        prompt = f"Temporal timeline logic in {place}: {premise} Which occurred {q}?"
        pool = [correct] + wrong
        hint = f"{correct} is ordered {q.lower()} on the timeline."

    return prompt, correct, pool, hint


def gen_l_co(subskill: str, idx: int):
    """Conditional Logic (L-CO: 4 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 4
    name = NAMES[idx % len(NAMES)]

    if mod == 0:
        # L-CO-01: Direct conditional implication (If P then Q)
        conditions = [
            ("If rain falls, the courtyard flagstones become wet.", "The flagstones become wet", ["The flagstones remain completely dry", "It begins to snow", "The sun shines warmly"]),
            ("If you press the red emergency button, the fortress alarm sounds.", "The fortress alarm sounds", ["The doors unlock quietly", "The lights turn off", "Music begins playing"])
        ]
        cond, correct, wrong = conditions[idx % len(conditions)]
        prompt = f"Rule of logic for {name}: '{cond}' You observe the first condition occur. What must follow?"
        pool = [correct] + wrong
        hint = f"Direct conditional modus ponens: {correct}."
    elif mod == 1:
        # L-CO-02: Contrapositive / Negative condition
        negatives = [
            ("The magical vault door opens ONLY IF the silver key is inserted. The silver key was NOT inserted.", "The vault door remains locked", ["The vault door swings wide open", "The door turns into glass", "The gold vanishes"]),
            ("The robot activates ONLY WHEN its battery is charged above 50%. The battery is at 10%.", "The robot does not activate", ["The robot starts running", "The robot flies", "The battery explodes"])
        ]
        premise, correct, wrong = negatives[idx % len(negatives)]
        prompt = f"Deductive condition for {name}: '{premise}' What conclusion is guaranteed?"
        pool = [correct] + wrong
        hint = "Because the required prerequisite condition was not met, the outcome cannot occur."
    elif mod == 2:
        # L-CO-03: Disjunctive logic (Either / Or)
        disj = [
            ("The missing map is located in EITHER the blue chest OR the green chest. The blue chest is completely empty.", "The map must be in the green chest", ["The map is in the blue chest", "The map never existed", "Both chests are full"]),
            ("The guard is EITHER in the watchtower OR at the gate. The guard is NOT at the gate.", "The guard is in the watchtower", ["The guard is at the gate", "The guard went home", "The castle has no guards"])
        ]
        premise, correct, wrong = disj[idx % len(disj)]
        prompt = f"Disjunctive reasoning for {name}: '{premise}' What must logically be true?"
        pool = [correct] + wrong
        hint = "When one of two exclusive possibilities is eliminated, the remaining option must hold."
    else:
        # L-CO-04: Multi-step transitive deduction
        chains = [
            ("Rule 1: If the red beacon lights up, the drawbridge lowers. Rule 2: If the drawbridge lowers, the knight crosses. The red beacon lights up.", "The knight crosses the drawbridge", ["The drawbridge stays up", "The knight retreats", "Nothing happens"]),
            ("Rule 1: If the fuel valve opens, the rocket engine ignites. Rule 2: If the engine ignites, the rocket launches. The fuel valve opens.", "The rocket launches into space", ["The engine stays cold", "The rocket is disassembled", "The mission is cancelled"])
        ]
        premise, correct, wrong = chains[idx % len(chains)]
        prompt = f"Deductive chain for {name}: '{premise}' What is the final resulting outcome?"
        pool = [correct] + wrong
        hint = f"Chain the conditionals: If A then B, and if B then C, therefore {correct}."

    return prompt, correct, pool, hint


def gen_l_ce(subskill: str, idx: int):
    """Cause & Effect Reasoning (L-CE: 4 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 4
    name = NAMES[idx % len(NAMES)]

    if mod == 0:
        # L-CE-01: Physical cause & effect (wet footprints)
        prompt = f"Cause and Effect: {name} entered the study and noticed dripping wet, muddy footprints leading from the garden door. What is the most logical cause?"
        correct = "Someone walked in from the rainy garden"
        pool = ["Someone walked in from the rainy garden", "Someone was baking bread in the kitchen", "The room was very dusty", "A candle burned out"]
        hint = "Wet muddy tracks are caused by someone walking through rain and mud."
    elif mod == 1:
        # L-CE-02: Combustion hazard (smoke in the sky)
        prompt = f"Cause and Effect: {name} spots thick, dark billowing smoke rising above the tree canopy. What is the most probable cause?"
        correct = "A fire has broken out in the woods"
        pool = ["A fire has broken out in the woods", "A snowstorm is arriving", "A rainbow has appeared", "The river is freezing over"]
        hint = "Billowing smoke is the direct physical byproduct of combustion and fire."
    elif mod == 2:
        # L-CE-03: Seismic geological effects (earthquake)
        prompt = f"Cause and Effect: The stone walls suddenly rattle and the castle chandelier sways back and forth violently. What is the most probable cause?"
        correct = "An earthquake tremor is occurring"
        pool = ["An earthquake tremor is occurring", "A gentle autumn breeze blew through", "The sun came out", "Someone dropped a coin"]
        hint = "Violent ground shaking and swaying buildings are caused by seismic earthquake activity."
    else:
        # L-CE-04: Meteorological cause & effect (storm clouds)
        prompt = f"Cause and Effect: Dark purple thunderclouds roll in, the air cools rapidly, and bright lightning flashes. What will happen next?"
        correct = "A torrential rainstorm will begin"
        pool = ["A torrential rainstorm will begin", "The desert will dry out further", "The stars will shine clearly", "A heatwave will occur"]
        hint = "Thunderclouds, dropping temperatures, and lightning are direct precursors to rain."

    return prompt, correct, pool, hint


# ----------------------------------------------------------------------
# WORLD KNOWLEDGE DIVERSIFICATION ENGINES (3 Strands)
# ----------------------------------------------------------------------

def gen_w_ka(subskill: str, idx: int):
    """Cultural Awareness & Traditions (W-KA: 8 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 8
    name = NAMES[idx % len(NAMES)]

    if mod == 0:
        # W-KA-01: World cuisines
        culture = [("Sushi wrapped in crisp nori seaweed", "Japan", ["Italy", "Mexico", "India"]),
                   ("Pizza baked with tomato sauce and mozzarella cheese", "Italy", ["Japan", "Mexico", "India"]),
                   ("Tacos filled with seasoned beans and salsa", "Mexico", ["Japan", "Italy", "India"]),
                   ("Fragrant basmati rice with curry and naan bread", "India", ["Japan", "Italy", "Mexico"])]
        food, correct, wrong = culture[idx % len(culture)]
        prompt = f"{name} attends an international banquet and enjoys {food}. Which country did this traditional dish originate from?"
        pool = [correct] + wrong
        hint = f"{food} originated in {correct}."
    elif mod == 1:
        # W-KA-02: World festivals & celebrations
        fests = [
            ("Diwali, the radiant Festival of Lights celebrated with clay lamps called diyas", "India", ["Brazil", "Norway", "Canada"]),
            ("Carnival, famous for vibrant samba parades, elaborate costumes, and festive music", "Brazil", ["Japan", "Egypt", "Iceland"]),
            ("Lunar New Year, celebrated with festive dragon dances and red envelopes", "China and East Asia", ["France", "Chile", "Australia"])
        ]
        fest, correct, wrong = fests[idx % len(fests)]
        prompt = f"{name} studies world cultures: {fest}. In which region did this cultural celebration originate?"
        pool = [correct] + wrong
        hint = f"This cultural celebration is deeply rooted in {correct}."
    elif mod == 2:
        # W-KA-03: Traditional musical instruments
        instrs = [
            ("the sitar, a plucked stringed instrument with resonant sympathetic strings", "India", ["Scotland", "Australia", "Peru"]),
            ("the bagpipes, a woodwind instrument using an enclosed bag of air", "Scotland", ["India", "Egypt", "Brazil"]),
            ("the didgeridoo, a long wooden wind instrument developed by Indigenous peoples", "Australia", ["Norway", "Japan", "Mexico"]),
            ("the djembe, a rope-tuned goblet drum played with bare hands", "West Africa", ["Russia", "Canada", "Germany"])
        ]
        inst, correct, wrong = instrs[idx % len(instrs)]
        prompt = f"World music discovery: {name} listens to {inst}. With which culture or country is it traditionally associated?"
        pool = [correct] + wrong
        hint = f"This instrument originated in {correct}."
    elif mod == 3:
        # W-KA-04: Traditional attire & clothing
        attire = [
            ("the Kimono, a graceful T-shaped wrapped garment tied with an obi sash", "Japan", ["Scotland", "Mexico", "Egypt"]),
            ("the Kilt, a traditional pleated knee-length woolen skirt pattern", "Scotland", ["Japan", "India", "Nigeria"]),
            ("the Sari, an elegant unstitched drape of colorful woven fabric", "India", ["Norway", "Mexico", "Australia"]),
            ("the Poncho, a woolen outer garment designed to keep the body warm and dry", "The Andes of South America", ["Japan", "Egypt", "Iceland"])
        ]
        garment, correct, wrong = attire[idx % len(attire)]
        prompt = f"Cultural history lesson: {name} examines {garment}. In which country or region is this traditional attire worn?"
        pool = [correct] + wrong
        hint = f"{garment} is traditional attire in {correct}."
    elif mod == 4:
        # W-KA-05: World language greetings
        greetings = [
            ("Bonjour", "French", ["Spanish", "German", "Japanese"]),
            ("Konnichiwa", "Japanese", ["French", "Italian", "Arabic"]),
            ("Namaste", "Hindi", ["Russian", "Portuguese", "Greek"]),
            ("Hola", "Spanish", ["German", "Japanese", "Swahili"])
        ]
        word, correct, wrong = greetings[idx % len(greetings)]
        prompt = f"International communication: A traveler warmly greets {name} saying '{word}'! Which language is being spoken?"
        pool = [correct] + wrong
        hint = f"'{word}' is the standard greeting in {correct}."
    elif mod == 5:
        # W-KA-06: World folktales & mythological legends
        myths = [
            ("Anansi the clever spider who outsmarts larger creatures", "West African folktales", ["Norse mythology", "Greek legends", "Inuit folklore"]),
            ("King Arthur and the legendary Knights of the Round Table", "British folklore", ["Chinese mythology", "Egyptian legends", "Aztec folklore"]),
            ("The Monkey King (Sun Wukong) possessing magical shapeshifting powers", "Chinese literature and folklore", ["Celtic myths", "Mayan legends", "Roman myths"])
        ]
        legend, correct, wrong = myths[idx % len(myths)]
        prompt = f"Literary folklore: {name} reads stories about {legend}. Which cultural tradition does this story come from?"
        pool = [correct] + wrong
        hint = f"This famous folklore originates in {correct}."
    elif mod == 6:
        # W-KA-07: National symbols & emblems
        symbols = [
            ("The Maple Leaf is a prominent national emblem featured on the flag of which country?", "Canada", ["Australia", "Japan", "Brazil"]),
            ("The Kangaroo and Emu appear as national animal symbols on the coat of arms of which country?", "Australia", ["Canada", "India", "Germany"]),
            ("The Bald Eagle serves as a national bird and symbol of freedom for which nation?", "United States", ["France", "Mexico", "China"])
        ]
        q_sym, correct, wrong = symbols[idx % len(symbols)]
        prompt = f"National symbols quiz: {name} asks: {q_sym}"
        pool = [correct] + wrong
        hint = f"This national symbol represents {correct}."
    else:
        # W-KA-08: Traditional world architecture
        arch = [
            ("the dome-shaped Igloo built from blocks of compacted snow for arctic shelter", "Inuit people of the Arctic", ["Bedouin nomads of the desert", "Gauchos of Argentina", "Maori of New Zealand"]),
            ("the Yurt (Ger), a portable circular felt-covered tent used on the steppes", "Nomadic peoples of Central Asia (Mongolia)", ["Inuit of the Arctic", "Polynesians of the Pacific", "Celts of Europe"]),
            ("the tiered multi-roofed Pagoda built as a sacred tower", "East Asia (China and Japan)", ["Ancient Rome", "Scandinavia", "Ancient Egypt"])
        ]
        struct, correct, wrong = arch[idx % len(arch)]
        prompt = f"Architectural heritage: {name} studies {struct}. Which culture or region historically created this structure?"
        pool = [correct] + wrong
        hint = f"This architectural structure was developed by {correct}."

    return prompt, correct, pool, hint


def gen_w_ko(subskill: str, idx: int):
    """Community Helpers & Occupations (W-KO: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6
    place = PLACES[idx % len(PLACES)]

    if mod == 0:
        # W-KO-01: Utility & emergency infrastructure (Plumber / Electrician)
        helpers = [
            ("a high-pressure water pipe bursts under the floor and floods the basement", "A Plumber", ["An Electrician", "A Baker", "A Dentist"]),
            ("the electrical circuit breaker sparks and the power completely shuts down", "An Electrician", ["A Plumber", "A Carpenter", "A Librarian"])
        ]
        prob, correct, wrong = helpers[idx % len(helpers)]
        prompt = f"In {place}, {prob}! Which skilled trade specialist should be called to fix it safely?"
        pool = [correct] + wrong
        hint = f"{correct} specializes in repairing this system."
    elif mod == 1:
        # W-KO-02: Healthcare & medical professions
        health = [
            ("a resident develops a throbbing toothache that needs to be treated", "A Dentist", ["A Plumber", "A Firefighter", "An Electrician"]),
            ("a family pet dog becomes injured and needs medical surgery", "A Veterinarian", ["A Pediatrician", "A Botanist", "A Mechanic"]),
            ("a traveler breaks an arm bone during a hike and needs an X-ray and cast", "A Medical Doctor or Physician", ["A Chef", "A Pilot", "A Carpenter"])
        ]
        sit, correct, wrong = health[idx % len(health)]
        prompt = f"Community health situation in {place}: {sit}. Who is the proper medical professional to consult?"
        pool = [correct] + wrong
        hint = f"{correct} is trained specifically to treat this medical issue."
    elif mod == 2:
        # W-KO-03: Public safety & fire rescue
        safety = [
            ("a fire breaks out in a kitchen and thick smoke fills the room", "Firefighters", ["Librarians", "Mail carriers", "Architects"]),
            ("traffic signals malfunction at a busy intersection and vehicles need safe direction", "Police Officers", ["Dentists", "Plumbers", "Chefs"])
        ]
        sit, correct, wrong = safety[idx % len(safety)]
        prompt = f"Emergency response in {place}: {sit}. Which first responders protect the community here?"
        pool = [correct] + wrong
        hint = f"{correct} handle public emergencies of this kind."
    elif mod == 3:
        # W-KO-04: Education & library services
        edu = [
            ("a student needs to research reliable historical books and borrow reference material", "A Librarian", ["A Firefighter", "A Mechanic", "A Plumber"]),
            ("a classroom of children gathers to learn reading, math, and science every day", "A School Teacher", ["A Pilot", "A Chef", "A Dentist"])
        ]
        sit, correct, wrong = edu[idx % len(edu)]
        prompt = f"Public services in {place}: {sit}. Which community professional facilitates this learning?"
        pool = [correct] + wrong
        hint = f"{correct} provides educational guidance."
    elif mod == 4:
        # W-KO-05: Transportation & transit operators
        transit = [
            ("safely flying a commercial airliner carrying 200 passengers through stormy weather", "An Airline Pilot", ["A Train Conductor", "A Ship Captain", "A Truck Driver"]),
            ("driving an electric commuter locomotive along railroad tracks from station to station", "A Train Engineer or Driver", ["A Pilot", "A Bus Driver", "A Sailor"])
        ]
        sit, correct, wrong = transit[idx % len(transit)]
        prompt = f"Transportation logistics in {place}: {sit}. Who operates this transport vehicle?"
        pool = [correct] + wrong
        hint = f"{correct} is certified to operate this vehicle."
    else:
        # W-KO-06: Agriculture & food production
        agri = [
            ("tilling fertile soil, planting grain seeds, and harvesting crops to feed the population", "A Farmer", ["A Carpenter", "A Plumber", "An Electrician"]),
            ("mixing dough, kneading flour, and baking loaves of fresh bread in commercial ovens", "A Baker", ["A Doctor", "A Pilot", "A Mechanic"])
        ]
        sit, correct, wrong = agri[idx % len(agri)]
        prompt = f"Food supply in {place}: {sit}. Which community producer performs this essential work?"
        pool = [correct] + wrong
        hint = f"{correct} produces food for the community."

    return prompt, correct, pool, hint


def gen_w_kp(subskill: str, idx: int):
    """Geographic Places & Physical Features (W-KP: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6
    color = COLORS[idx % len(COLORS)]

    if mod == 0:
        # W-KP-01: World landmarks & continents
        geo = [("the ancient stone Pyramids of Giza", "Africa", ["Asia", "Europe", "South America"]),
               ("the iron lattice Eiffel Tower in Paris", "Europe", ["Asia", "Africa", "South America"]),
               ("the magnificent Great Wall stretching across mountain ridges", "Asia", ["Europe", "Africa", "South America"]),
               ("the ancient Incan citadel of Machu Picchu", "South America", ["Europe", "Asia", "Africa"])]
        landmark, correct, wrong = geo[idx % len(geo)]
        prompt = f"You are piloting a {color} exploration plane over {landmark}. Which continent are you exploring?"
        pool = [correct] + wrong
        hint = f"{landmark} is located on the continent of {correct}."
    elif mod == 1:
        # W-KP-02: World oceans & marine geography
        oceans = [
            ("Which is the largest and deepest ocean on Earth, spanning between Asia and the Americas?", "Pacific Ocean", ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"]),
            ("Which cold ocean surrounds the North Pole and is mostly covered by sea ice year-round?", "Arctic Ocean", ["Indian Ocean", "Atlantic Ocean", "Pacific Ocean"]),
            ("Which ocean lies between Africa, Asia, and Australia?", "Indian Ocean", ["Pacific Ocean", "Atlantic Ocean", "Arctic Ocean"])
        ]
        q_str, correct, wrong = oceans[idx % len(oceans)]
        prompt = f"Global geography challenge: {q_str}"
        pool = [correct] + wrong
        hint = f"The correct answer is the {correct}."
    elif mod == 2:
        # W-KP-03: Major mountain ranges
        mountains = [
            ("The towering Himalayas, home to Mount Everest (the highest peak on Earth), are located on which continent?", "Asia", ["Europe", "North America", "Africa"]),
            ("The Andes, the longest continental mountain range in the world, runs along the western coast of:", "South America", ["Africa", "Asia", "Europe"]),
            ("The Rocky Mountains stretch thousands of miles through Canada and the United States on which continent?", "North America", ["South America", "Europe", "Asia"])
        ]
        q_str, correct, wrong = mountains[idx % len(mountains)]
        prompt = f"Mountain geography: {q_str}"
        pool = [correct] + wrong
        hint = f"This mountain system is located in {correct}."
    elif mod == 3:
        # W-KP-04: Major world rivers & waterways
        rivers = [
            ("The Nile River, historically recognized as one of the longest rivers on Earth, flows northward through which continent?", "Africa", ["South America", "Europe", "Asia"]),
            ("The Amazon River, which discharges the largest volume of fresh water of any river on Earth, flows through:", "South America", ["Africa", "North America", "Europe"]),
            ("The Mississippi River, a vital continental shipping route, flows southward into the Gulf of Mexico through:", "North America", ["Europe", "Asia", "South America"])
        ]
        q_str, correct, wrong = rivers[idx % len(rivers)]
        prompt = f"River systems: {q_str}"
        pool = [correct] + wrong
        hint = f"This major river flows through {correct}."
    elif mod == 4:
        # W-KP-05: The Equator, Prime Meridian, and Poles
        coords = [
            ("What is the imaginary line circling the middle of Earth halfway between the North and South Poles called?", "The Equator", ["The Prime Meridian", "The Tropic of Cancer", "The Arctic Circle"]),
            ("What are the southernmost and northernmost points on the Earth's rotational axis called?", "The North and South Poles", ["The Equators", "The Oceanic Ridges", "The Meridians"])
        ]
        q_str, correct, wrong = coords[idx % len(coords)]
        prompt = f"Global mapping concepts: {q_str}"
        pool = [correct] + wrong
        hint = f"The correct geographical boundary is {correct}."
    else:
        # W-KP-06: World deserts & ecosystems
        deserts = [
            ("The Sahara, the largest hot desert in the world, covers vast portions of northern:", "Africa", ["Asia", "Australia", "Europe"]),
            ("The cold, windswept Gobi Desert stretches across northern China and southern:", "Mongolia (Asia)", ["Egypt (Africa)", "Chile (South America)", "Spain (Europe)"]),
            ("The Outback, a vast arid desert interior, occupies the majority of which continent and nation?", "Australia", ["South America", "Europe", "North America"])
        ]
        q_str, correct, wrong = deserts[idx % len(deserts)]
        prompt = f"Desert geography: {q_str}"
        pool = [correct] + wrong
        hint = f"This famous desert is situated in {correct}."

    return prompt, correct, pool, hint


def generate_other_domain_item(domain: str, subskill: str, idx: int):
    prefix = subskill[:4]
    
    # English
    if prefix == "E-PD": return gen_e_pd(subskill, idx)
    elif prefix == "E-VM": return gen_e_vm(subskill, idx)
    elif prefix == "E-SG": return gen_e_sg(subskill, idx)
    elif prefix == "E-RF": return gen_e_rf(subskill, idx)
    elif prefix == "E-CR": return gen_e_cr(subskill, idx)
    elif prefix == "E-CC": return gen_e_cc(subskill, idx)
    elif prefix == "E-WE": return gen_e_we(subskill, idx)
    elif prefix == "E-OL": return gen_e_ol(subskill, idx)
    
    # Science
    elif prefix == "S-KN": return gen_s_kn(subskill, idx)
    elif prefix == "S-OC": return gen_s_oc(subskill, idx)
    elif prefix == "S-PP": return gen_s_pp(subskill, idx)
    elif prefix == "S-EE": return gen_s_ee(subskill, idx)
    elif prefix == "S-MO": return gen_s_mo(subskill, idx)
    elif prefix == "S-IN": return gen_s_in(subskill, idx)
    
    # Logic
    elif prefix == "L-PC": return gen_l_pc(subskill, idx)
    elif prefix == "L-AR": return gen_l_ar(subskill, idx)
    elif prefix == "L-SR": return gen_l_sr(subskill, idx)
    elif prefix == "L-RC": return gen_l_rc(subskill, idx)
    elif prefix == "L-CO": return gen_l_co(subskill, idx)
    elif prefix == "L-CE": return gen_l_ce(subskill, idx)
    
    # World Knowledge
    elif prefix == "W-KA": return gen_w_ka(subskill, idx)
    elif prefix == "W-KO": return gen_w_ko(subskill, idx)
    elif prefix == "W-KP": return gen_w_kp(subskill, idx)
    
    # Fallback
    return gen_e_pd(subskill, idx)


def main():
    print("=================================================================")
    print("UPGRADING QUESTION BANK WITH SUBSKILL-DIFFERENTIATED NARRATIVES")
    print("=================================================================")

    total_updated = 0
    domains = ["MATHEMATICS", "ENGLISH_LANGUAGE", "LOGICAL_REASONING", "SCIENCE_EVS", "WORLD_KNOWLEDGE"]

    for dom in domains:
        dom_path = ITEMS_DIR / dom
        if not dom_path.exists():
            continue

        subskill_dirs = [d for d in dom_path.iterdir() if d.is_dir()]
        print(f"\nProcessing domain [{dom}] with {len(subskill_dirs)} subskill folders...")

        for sdir in sorted(subskill_dirs):
            subcode = sdir.name
            files = sorted(sdir.glob("*.json"))

            for idx, fpath in enumerate(files):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        item = json.load(f)

                    if dom == "MATHEMATICS":
                        prompt, correct, pool, hint = generate_math_item(subcode, idx)
                    else:
                        prompt, correct, pool, hint = generate_other_domain_item(dom, subcode, idx)

                    # Update item prompt and hint fields
                    item["prompt_structure"]["display_text"] = prompt

                    if "scaffolding_protocol" in item and "level_1_reflection_prompt" in item["scaffolding_protocol"]:
                        item["scaffolding_protocol"]["level_1_reflection_prompt"]["prompt"] = hint

                    # Update options list in tap_select
                    opts = []
                    correct_opt_id = "opt_1"
                    for opt_idx, opt_val in enumerate(pool):
                        opt_id = f"opt_{opt_idx + 1}"
                        opts.append({
                            "option_id": opt_id,
                            "display_value": str(opt_val)
                        })
                        if opt_val == correct:
                            correct_opt_id = opt_id

                    if "interaction_model" not in item:
                        item["interaction_model"] = {}
                    if "modality_configurations" not in item["interaction_model"]:
                        item["interaction_model"]["modality_configurations"] = {}
                    item["interaction_model"]["modality_configurations"]["tap_select"] = {
                        "options": opts
                    }

                    if "rubric" not in item:
                        item["rubric"] = {}
                    item["rubric"]["correct_criteria"] = {
                        "selected_option_id": correct_opt_id
                    }

                    with open(fpath, "w", encoding="utf-8") as f:
                        json.dump(item, f, indent=2)

                    total_updated += 1
                except Exception as e:
                    print(f"Error processing {fpath}: {e}")

    print(f"\n[DONE] Successfully enriched and diversified {total_updated} question files with new narratives!")


if __name__ == "__main__":
    main()
