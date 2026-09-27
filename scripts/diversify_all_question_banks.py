#!/usr/bin/env python3
"""
scripts/diversify_all_question_banks.py

Massively diversifies question items across ALL 187 subskills in all 5 domains:
- MATHEMATICS (8 strands, 55 subskills)
- ENGLISH_LANGUAGE (8 strands, 53 subskills)
- SCIENCE_EVS (6 strands, 35 subskills)
- LOGICAL_REASONING (6 strands, 24 subskills)
- WORLD_KNOWLEDGE (3 strands, 20 subskills)

Features:
1. Subskill-level differentiation: Every generator derives `ss_id` and branches on `mod = (ss_id - 1) % N`
   where N >= strand subskill count, completely eliminating cross-subskill prompt/hint collisions.
2. Pedagogical coherence: All questions use natural, age-appropriate, sensible sentence structures
   (e.g., real sentence contexts for sight words; no absurd hieroglyph-in-space-station mashups).
3. Accurate Visual Assets:
   - For genuinely visual items (counting items in chests, geometry shapes, scientific tools/animals, landmarks),
     generates an exact matching SVG.
   - For verbal/text items (sight words, vocabulary, grammar, reading comprehension, logic conditionals),
     sets `representation_type = 'VERBAL'` and `visual_assets = []` so NO random images are displayed.
"""

import os
import sys
import glob
import json
import math
from pathlib import Path

# Import visual asset builders
sys.path.append(str(Path(__file__).resolve().parent))
from visual_asset_builder import (
    build_chest_counting_svg,
    build_polygon_svg,
    build_3d_shape_svg,
    build_analog_clock_svg,
    build_tool_svg,
    build_creature_or_entity_svg,
    build_landmark_svg
)

BASE_DIR = Path(__file__).resolve().parent.parent
ITEMS_DIR = BASE_DIR / "question_bank" / "items"
PUBLIC_SVG_DIR = BASE_DIR / "frontend" / "public" / "assets" / "svg"
DIST_SVG_DIR = BASE_DIR / "frontend" / "dist" / "assets" / "svg"

PUBLIC_SVG_DIR.mkdir(parents=True, exist_ok=True)
DIST_SVG_DIR.mkdir(parents=True, exist_ok=True)

NAMES = [
    "Alex", "Maya", "Leo", "Zara", "Liam", "Emma", "Noah", "Olivia",
    "Captain Orion", "Princess Luna", "Commander Zorg", "Dr. Nova"
]
COLORS = [
    "red", "blue", "green", "golden", "silver", "purple", "crystal", "emerald", "amber", "navy"
]
PLACES = [
    "the library", "the nature center", "the garden", "the observatory",
    "the workshop", "the museum", "the harbor", "the community center"
]
STORY_ITEMS = [
    "glowing crystals", "enchanted forest acorns", "ancient golden coins", "magic spellbooks", 
    "silver stars", "mermaid pearls", "robot gears", "ninja throwing stars", 
    "wizard wands", "treasure maps", "fossil stones", "hero badges"
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
        # M-NQ-01: Counting & Cardinality (VISUAL with chest)
        count = (idx % 12) + 5  # 5 to 16
        prompt = f"Explorer! Look inside the treasure chest. How many {item_name} are sparkling inside?"
        correct = str(count)
        pool = [str(count), str(max(1, count - 2)), str(count + 2), str(count + 3)]
        hint = f"Count each item carefully in the chest: there are exactly {count} {item_name}."
        svg = build_chest_counting_svg(item_name, count)
        return prompt, correct, pool, hint, "VISUAL", svg

    elif mod == 1:
        # M-NQ-02: Counting sequence / Successor (VERBAL)
        n = (idx % 15) + 10
        prompt = f"The launch countdown is at {n}. What number comes directly AFTER {n}?"
        correct = str(n + 1)
        pool = [str(n + 1), str(n - 1), str(n + 2), str(n)]
        hint = f"Count forward: ..., {n}, {n + 1}!"
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 2:
        # M-NQ-03: Magnitude comparison (Greater than) (VERBAL)
        a = (idx % 12) + 8
        b = a + (idx % 8) + 3
        prompt = f"Leo collected {b} coins, and Maya collected {a} coins. Which number is GREATER?"
        correct = str(b)
        pool = [str(b), str(a), "They have the same amount"]
        hint = f"{b} is a larger number than {a}."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 3:
        # M-NQ-04: Predecessor (Number before) (VERBAL)
        n = (idx % 12) + 15
        prompt = f"What number comes directly BEFORE {n} on the number line?"
        correct = str(n - 1)
        pool = [str(n - 1), str(n + 1), str(n - 2), str(n)]
        hint = f"Think backwards: the number directly before {n} is {n - 1}."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 4:
        # M-NQ-05: Place value / Tens and Ones (VERBAL)
        tens = (idx % 4) + 1
        ones = (idx % 9) + 1
        total = (tens * 10) + ones
        prompt = f"A bundle has {tens} tens and {ones} ones of craft sticks. What is the total number of sticks?"
        correct = str(total)
        pool = [str(total), str((tens+1)*10 + ones), str(tens*10 + ones + 2), str(total - 1)]
        hint = f"{tens} tens = {tens*10}. Add {ones} ones: {tens*10} + {ones} = {total}."
        return prompt, correct, pool, hint, "VERBAL", None

    else:
        # M-NQ-06: Missing intermediate number (VERBAL)
        a = (idx % 15) + 10
        mid = a + 1
        b = a + 2
        prompt = f"Look at the number sequence: {a}, ___, {b}. Which number is missing in the middle?"
        correct = str(mid)
        pool = [str(mid), str(mid + 2), str(max(1, a - 1)), str(b + 1)]
        hint = f"The number between {a} and {b} is {mid}."
        return prompt, correct, pool, hint, "VERBAL", None


def gen_m_op(subskill: str, idx: int):
    """Operations & Algebraic Thinking (M-OP: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6
    a = (idx % 8) + 5
    b = ((idx // 2) % 7) + 3
    total = a + b

    if mod == 0:
        # M-OP-01: Addition word problem
        prompt = f"Maya picked {a} red apples, and Leo picked {b} green apples. How many apples did they pick in all?"
        correct = str(total)
        pool = [str(total), str(max(1, total - 2)), str(total + 1), str(total + 3)]
        hint = f"Add the two groups: {a} + {b} = {total}."
    elif mod == 1:
        # M-OP-02: Subtraction word problem
        start = a + b + 4
        sub = b
        rem = start - sub
        prompt = f"There were {start} crayons in the art box. The students used {sub} crayons. How many crayons are left in the box?"
        correct = str(rem)
        pool = [str(rem), str(rem + 1), str(max(0, rem - 2)), str(rem + 2)]
        hint = f"Subtract: {start} - {sub} = {rem}."
    elif mod == 2:
        # M-OP-03: Doubling
        n = (idx % 8) + 4
        double_val = n * 2
        prompt = f"A recipe calls for {n} strawberries. If you DOUBLE the recipe, how many strawberries do you need?"
        correct = str(double_val)
        pool = [str(double_val), str(double_val - 2), str(double_val + 2), str(n + 3)]
        hint = f"Doubling means adding the number to itself: {n} + {n} = {double_val}."
    elif mod == 3:
        # M-OP-04: Combining groups
        items = ["blueberries", "sunflower seeds", "beads", "buttons"][idx % 4]
        prompt = f"Emma has {a} {items}, and Liam gives her {b} more {items}. How many {items} does Emma have altogether?"
        correct = str(total)
        pool = [str(total), str(total + 2), str(max(1, total - 1)), str(total + 4)]
        hint = f"Combine the amounts: {a} + {b} = {total} {items}."
    elif mod == 4:
        # M-OP-05: Missing addend
        req = total + 3
        missing = req - a
        prompt = f"Zara needs {req} building blocks to complete a tower. She already has {a} blocks. How many MORE blocks does she need?"
        correct = str(missing)
        pool = [str(missing), str(missing + 2), str(max(1, missing - 1)), str(req)]
        hint = f"Find the missing part: {req} - {a} = {missing} blocks needed."
    else:
        # M-OP-06: Equal groups / Multiplication foundation
        groups = (idx % 4) + 2
        per_grp = (idx % 3) + 2
        mult_total = groups * per_grp
        prompt = f"There are {groups} baskets, and each basket holds exactly {per_grp} oranges. How many oranges are there in total?"
        correct = str(mult_total)
        pool = [str(mult_total), str(mult_total + per_grp), str(max(1, mult_total - 2)), str(groups + per_grp)]
        hint = f"Count {groups} equal groups of {per_grp}: {groups} × {per_grp} = {mult_total} oranges."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_m_gs(subskill: str, idx: int):
    """Geometry & Spatial Sense (M-GS: 7 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 7

    if mod == 0:
        # M-GS-01: 2D polygon sides (VISUAL)
        shapes = [("Triangle", 3), ("Square", 4), ("Rectangle", 4), ("Hexagon", 6), ("Octagon", 8)]
        shape_name, sides = shapes[idx % len(shapes)]
        prompt = f"Look at the shape shown above. It is a {shape_name}. How many straight sides does it have?"
        correct = str(sides)
        pool = [str(sides), str(sides + 1), str(max(0, sides - 1)), "5" if sides != 5 else "7"]
        hint = f"A {shape_name} always has {sides} sides."
        svg = build_polygon_svg(shape_name, sides)
        return prompt, correct, pool, hint, "VISUAL", svg

    elif mod == 1:
        # M-GS-02: 3D shape identification (VISUAL)
        shapes_3d = ["Sphere", "Cube", "Cylinder", "Cone"]
        shape_3d = shapes_3d[idx % len(shapes_3d)]
        prompt = f"Look at the 3D solid shown above. Which geometric shape is it?"
        correct = shape_3d
        pool = [shape_3d, "Cube" if shape_3d != "Cube" else "Sphere", "Cone" if shape_3d != "Cone" else "Cylinder", "Pyramid"]
        hint = f"This 3D solid is a {shape_3d}."
        svg = build_3d_shape_svg(shape_3d)
        return prompt, correct, pool, hint, "VISUAL", svg

    elif mod == 2:
        # M-GS-03: Positional spatial relations (VERBAL)
        positions = [
            ("above", "flying high above the treetop"),
            ("below", "swimming deep below the wooden dock"),
            ("inside", "sitting safely inside the garden greenhouse"),
            ("behind", "standing directly behind the tall fence")
        ]
        pos_word, phrase = positions[idx % len(positions)]
        prompt = f"A bird is {phrase}. Which positional word describes where the bird is located?"
        correct = pos_word.capitalize()
        pool = [pos_word.capitalize(), "Across", "Underground", "Between"]
        hint = f"The clue word is '{pos_word}'."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 3:
        # M-GS-04: Polygon side properties (VISUAL)
        shapes = [("Triangle", 3), ("Hexagon", 6), ("Octagon", 8), ("Square", 4)]
        shape_name, sides = shapes[(idx + 1) % len(shapes)]
        prompt = f"Look at the polygon above. It has exactly {sides} straight sides. What is the name of this shape?"
        correct = shape_name
        pool = [shape_name, "Circle", "Triangle" if shape_name != "Triangle" else "Pentagon", "Star"]
        hint = f"A shape with {sides} straight sides is a {shape_name}."
        svg = build_polygon_svg(shape_name, sides)
        return prompt, correct, pool, hint, "VISUAL", svg

    elif mod == 4:
        # M-GS-05: Vertices / Corners (VISUAL)
        shapes_v = [("Triangle", 3), ("Square", 4), ("Pentagon", 5), ("Hexagon", 6)]
        s_name, v_count = shapes_v[idx % len(shapes_v)]
        prompt = f"Count the sharp corners (vertices) on the {s_name} shown above. How many vertices does it have?"
        correct = str(v_count)
        pool = [str(v_count), str(v_count + 1), str(max(1, v_count - 1)), "8" if v_count != 8 else "2"]
        hint = f"A {s_name} has exactly {v_count} corners (vertices)."
        svg = build_polygon_svg(s_name, v_count)
        return prompt, correct, pool, hint, "VISUAL", svg

    elif mod == 5:
        # M-GS-06: Symmetry (VERBAL)
        sym_items = [("butterfly", (idx % 4) + 2), ("leaf pattern", (idx % 5) + 3), ("robot face", (idx % 3) + 2)]
        s_item, dots = sym_items[idx % len(sym_items)]
        prompt = f"A {s_item} is symmetrical down its center line. If the left wing has {dots} spots, how many spots must be on the right wing to match?"
        correct = str(dots)
        pool = [str(dots), str(dots + 2), str(max(1, dots - 1)), str(dots * 2)]
        hint = f"Symmetry means both sides match identically: exactly {dots} spots."
        return prompt, correct, pool, hint, "VERBAL", None

    else:
        # M-GS-07: Composite shapes (VERBAL)
        comps = [
            ("a large rectangle", "2 equal squares", "Squares"),
            ("a hexagon", "6 identical small triangles", "Triangles"),
            ("a diamond shape", "2 matching triangles", "Triangles")
        ]
        c_whole, c_parts, shape_type = comps[idx % len(comps)]
        prompt = f"You can make {c_whole} by joining {c_parts} edge to edge. Which smaller shape is used?"
        correct = shape_type
        pool = [shape_type, "Circles", "Stars", "Spheres"]
        hint = f"{c_parts.capitalize()} combine to form the shape."
        return prompt, correct, pool, hint, "VERBAL", None


def gen_m_me(subskill: str, idx: int):
    """Measurement & Data (M-ME: 8 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 8

    if mod == 0:
        # M-ME-01: Time on analog clock (VISUAL)
        hour = (idx % 11) + 1
        prompt = f"Look at the clock shown above. What time does the clock display?"
        correct = f"{hour} o'clock"
        pool = [f"{hour} o'clock", f"{(hour % 12) + 1} o'clock", f"{max(1, hour - 1)} o'clock", "12 o'clock"]
        hint = f"The minute hand is on 12, and the hour hand points to {hour}: it is {hour} o'clock."
        svg = build_analog_clock_svg(hour)
        return prompt, correct, pool, hint, "VISUAL", svg

    elif mod == 1:
        # M-ME-02: Weight comparison (VERBAL)
        pairs = [
            ("A heavy stone boulder", "A fluffy bird feather", "HEAVIER"),
            ("A massive school bus", "A small skateboard", "HEAVIER"),
            ("A single drop of rain", "A bucket of water", "LIGHTER"),
            ("A paper airplane", "A steel locomotive train", "LIGHTER")
        ]
        obj1, obj2, qtype = pairs[idx % len(pairs)]
        prompt = f"Comparing weights: Which object is {qtype}: {obj1} or {obj2}?"
        correct = obj1
        pool = [obj1, obj2, "They weigh the exact same"]
        hint = f"{obj1} is {qtype.lower()}."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 2:
        # M-ME-03: Length comparison (VERBAL)
        pairs_len = [
            ("A garden hose", "A sewing needle", "LONGER"),
            ("A classroom hallway", "A wooden pencil", "LONGER"),
            ("A paperclip", "A baseball bat", "SHORTER"),
            ("A crayon", "A flagpole", "SHORTER")
        ]
        o1, o2, qtype = pairs_len[idx % len(pairs_len)]
        prompt = f"Comparing lengths: Which item is {qtype}: {o1} or {o2}?"
        correct = o1
        pool = [o1, o2, "They are identical in length"]
        hint = f"{o1} is {qtype.lower()}."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 3:
        # M-ME-04: Money addition and calculation (VERBAL)
        money_scenarios = [
            ("Rohan has two ₹10 coins. How much money does Rohan have in total?", "20 Rupees", ["20 Rupees", "12 Rupees", "10 Rupees", "30 Rupees"], "Two ₹10 coins equal 10 + 10 = 20 Rupees."),
            ("Priya has one ₹50 note and one ₹20 note. How much money does she have altogether?", "70 Rupees", ["70 Rupees", "30 Rupees", "50 Rupees", "60 Rupees"], "50 + 20 = 70 Rupees."),
            ("Ananya has three ₹5 coins in her piggy bank. How much money is that in total?", "15 Rupees", ["15 Rupees", "8 Rupees", "25 Rupees", "10 Rupees"], "Three ₹5 coins equal 5 + 5 + 5 = 15 Rupees."),
            ("A storybook costs ₹35. Aarav pays with a ₹50 note. How much change should Aarav receive?", "15 Rupees", ["15 Rupees", "25 Rupees", "10 Rupees", "20 Rupees"], "50 - 35 = 15 Rupees."),
            ("Maya has one ₹20 note and two ₹10 coins. What is the total value of her money?", "40 Rupees", ["40 Rupees", "30 Rupees", "50 Rupees", "22 Rupees"], "20 + 10 + 10 = 40 Rupees."),
            ("A toy car costs ₹18. Kabir pays with a ₹20 note. How much change should he get back?", "2 Rupees", ["2 Rupees", "5 Rupees", "8 Rupees", "12 Rupees"], "20 - 18 = 2 Rupees."),
            ("How many ₹5 coins do you need to equal the value of a ₹20 note?", "4 coins", ["4 coins", "2 coins", "5 coins", "10 coins"], "5 + 5 + 5 + 5 = 20, so 4 coins are needed."),
            ("A notebook costs ₹25 and an eraser costs ₹10. What is the total cost for both items?", "35 Rupees", ["35 Rupees", "15 Rupees", "40 Rupees", "30 Rupees"], "25 + 10 = 35 Rupees.")
        ]
        prompt, correct, pool, hint = money_scenarios[idx % len(money_scenarios)]
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 4:
        # M-ME-05: Liquid capacity (VERBAL)
        vessels = [
            ("A bathtub", "A teacup", "MORE"),
            ("A swimming pool", "A water glass", "MORE"),
            ("A teaspoon", "A large cooking pot", "LESS"),
            ("An eye dropper", "A water pitcher", "LESS")
        ]
        v1, v2, q = vessels[idx % len(vessels)]
        prompt = f"Comparing fluid capacity: Which container holds {q} liquid: {v1} or {v2}?"
        correct = v1
        pool = [v1, v2, "They hold the exact same volume"]
        hint = f"{v1} holds {q.lower()} liquid."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 5:
        # M-ME-06: Temperature comparison (VERBAL)
        temps = [
            ("A cup of hot cocoa", "A bowl of ice cream", "HOTTER"),
            ("A sunny summer afternoon", "A snowy winter morning", "HOTTER"),
            ("An ice cube in the freezer", "A warm bowl of soup", "COLDER"),
            ("A frosted icicle", "A campfire", "COLDER")
        ]
        t1, t2, q = temps[idx % len(temps)]
        prompt = f"Comparing temperatures: Which is {q}: {t1} or {t2}?"
        correct = t1
        pool = [t1, t2, "They have the same temperature"]
        hint = f"{t1} is {q.lower()}."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 6:
        # M-ME-07: Non-standard units (VERBAL)
        unit_scenarios = [
            ("A pencil is 6 paperclips long and an eraser is 2 paperclips long. How many paperclips LONGER is the pencil than the eraser?", "4 paperclips", ["4 paperclips", "8 paperclips", "2 paperclips", "3 paperclips"], "Subtract the eraser length: 6 - 2 = 4 paperclips."),
            ("A ribbon is 9 hand-spans long. You cut off 4 hand-spans. How many hand-spans long is the ribbon now?", "5 hand-spans", ["5 hand-spans", "13 hand-spans", "4 hand-spans", "6 hand-spans"], "Subtract: 9 - 4 = 5 hand-spans."),
            ("A toy train is 4 wooden blocks long. A second train is 5 blocks long. Connected together, how many blocks long are both trains?", "9 blocks", ["9 blocks", "8 blocks", "1 block", "10 blocks"], "Add the lengths: 4 + 5 = 9 blocks."),
            ("A notebook is 5 craft sticks long. The desk is 3 times as long as the notebook. How many craft sticks long is the desk?", "15 craft sticks", ["15 craft sticks", "8 craft sticks", "12 craft sticks", "18 craft sticks"], "Multiply: 5 × 3 = 15 craft sticks.")
        ]
        prompt, correct, pool, hint = unit_scenarios[idx % len(unit_scenarios)]
        return prompt, correct, pool, hint, "VERBAL", None

    else:
        # M-ME-08: Reading simple tally/chart data (VERBAL)
        data_sets = [
            ("apples", 8, "oranges", 5, "pears", 3),
            ("crayons", 12, "markers", 7, "pencils", 4),
            ("books", 15, "magazines", 10, "notebooks", 6)
        ]
        d1, c1, d2, c2, d3, c3 = data_sets[idx % len(data_sets)]
        prompt = f"A student counted items in class: {d1}: {c1}, {d2}: {c2}, {d3}: {c3}. Which item had the HIGHEST count?"
        correct = d1
        pool = [d1, d2, d3, "All are equal"]
        hint = f"{d1} has the largest count of {c1}."
        return prompt, correct, pool, hint, "VERBAL", None


def gen_m_pa(subskill: str, idx: int):
    """Patterns & Algebra (M-PA: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6

    if mod == 0:
        # M-PA-01: Repeating sequence next element (VERBAL)
        patterns = [
            ("Red, Blue, Green, Red, Blue, Green, Red, Blue", "Green", ["Green", "Red", "Blue", "Yellow"]),
            ("Triangle, Circle, Square, Triangle, Circle, Square, Triangle", "Circle", ["Circle", "Triangle", "Square", "Star"]),
            ("Up, Down, Left, Up, Down, Left, Up", "Down", ["Down", "Left", "Up", "Right"])
        ]
        pat_str, nxt, pool = patterns[idx % len(patterns)]
        prompt = f"Look at the repeating pattern: {pat_str}, ___? What comes next?"
        correct = nxt
        hint = f"The pattern repeats: '{nxt}' comes next."
    elif mod == 1:
        # M-PA-02: Skip counting (VERBAL)
        skip = [
            ("5, 10, 15, 20", "25", ["25", "30", "22", "26"]),
            ("2, 4, 6, 8", "10", ["10", "12", "9", "11"]),
            ("10, 20, 30, 40", "50", ["50", "60", "45", "55"])
        ]
        seq_str, nxt, pool = skip[idx % len(skip)]
        prompt = f"Follow the skip counting pattern: {seq_str}, ___? What number is next?"
        correct = nxt
        hint = f"Add the same amount each time to get {nxt}."
    elif mod == 2:
        # M-PA-03: Missing middle element (VERBAL)
        missing = [
            ("10, ___, 30, 40", "20", ["20", "15", "25", "35"]),
            ("4, 8, ___, 16", "12", ["12", "10", "14", "18"]),
            ("Circle, Triangle, ___, Circle, Triangle, Square", "Square", ["Square", "Circle", "Triangle", "Star"])
        ]
        seq_str, nxt, pool = missing[idx % len(missing)]
        prompt = f"Find the missing item in this sequence: {seq_str}"
        correct = nxt
        hint = "Look at the pattern before and after the blank."
    elif mod == 3:
        # M-PA-04: Growing number patterns (VERBAL)
        grow = [
            ("1, 2, 4, 8", "16", ["16", "12", "14", "20"]),
            ("3, 6, 9, 12", "15", ["15", "18", "14", "16"]),
            ("100, 90, 80, 70", "60", ["60", "50", "65", "55"])
        ]
        seq_str, nxt, pool = grow[idx % len(grow)]
        prompt = f"Identify the rule and complete the number sequence: {seq_str}, ___?"
        correct = nxt
        hint = f"Follow the consistent step to reach {nxt}."
    elif mod == 4:
        # M-PA-05: Pattern core / unit (VERBAL)
        cores = [
            ("Circle, Triangle, Circle, Triangle, Circle, Triangle", "Circle, Triangle", ["Circle, Triangle", "Circle, Circle", "Triangle, Triangle", "Square"]),
            ("Sun, Moon, Star, Sun, Moon, Star", "Sun, Moon, Star", ["Sun, Moon, Star", "Sun, Moon", "Star, Sun", "Moon, Star"])
        ]
        pat, core, pool = cores[idx % len(cores)]
        prompt = f"In the repeating sequence '{pat}', which group of shapes forms the repeating pattern unit?"
        correct = core
        hint = f"The repeating unit is '{core}'."
    else:
        # M-PA-06: Two-attribute sequence (VERBAL)
        two_attr = [
            ("Red Circle, Blue Square, Red Circle, Blue Square, Red Circle", "Blue Square", ["Blue Square", "Red Circle", "Red Square", "Blue Circle"]),
            ("Big Star, Small Moon, Big Star, Small Moon, Big Star", "Small Moon", ["Small Moon", "Big Star", "Big Moon", "Small Star"])
        ]
        seq, nxt, pool = two_attr[idx % len(two_attr)]
        prompt = f"Look at the sequence: {seq}, ___? What comes next?"
        correct = nxt
        hint = f"Both attributes alternate: '{nxt}' is next."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_m_fr(subskill: str, idx: int):
    """Fractions & Equal Sharing (M-FR: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6

    if mod == 0:
        # M-FR-01: Fair sharing division
        kids = (idx % 3) + 2
        per_kid = (idx % 4) + 2
        total_items = kids * per_kid
        items = ["strawberries", "cookies", "stickers", "crayons"][idx % 4]
        prompt = f"{total_items} {items} are shared equally among {kids} children. How many {items} does each child receive?"
        correct = f"{per_kid} {items}"
        pool = [f"{per_kid} {items}", f"{per_kid + 1} {items}", f"{max(1, per_kid - 1)} {items}", f"{total_items} {items}"]
        hint = f"Divide equally: {total_items} ÷ {kids} = {per_kid} {items} each."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 1:
        # M-FR-02: Concept of One-Half (1/2)
        half_scenarios = [
            ("A freshly baked pizza is cut into 2 equal slices. What fraction does 1 slice represent?", "One-half (1/2)", ["One-half (1/2)", "One-fourth (1/4)", "One whole", "Two-thirds"]),
            ("Maya has 10 crayons and gives HALF of them to Leo. How many crayons does Leo get?", "5 crayons", ["5 crayons", "2 crayons", "8 crayons", "10 crayons"]),
            ("There are 16 apples in a basket. If exactly half of them are red, how many red apples are there?", "8 apples", ["8 apples", "4 apples", "10 apples", "16 apples"]),
            ("A rectangle is folded down the center into 2 equal parts. What is each part called?", "One-half", ["One-half", "One-third", "One-fourth", "One whole"])
        ]
        prompt, correct, pool = half_scenarios[idx % len(half_scenarios)]
        return prompt, correct, pool, "Half means dividing into 2 equal parts.", "VERBAL", None

    elif mod == 2:
        # M-FR-03: Concept of One-Fourth / Quarter (1/4)
        fourth_scenarios = [
            ("A circular fruit pie is cut into 4 equal slices. What fraction does 1 slice represent?", "One-fourth (1/4)", ["One-fourth (1/4)", "One-half (1/2)", "One-third (1/3)", "One whole"]),
            ("A box contains 12 cupcakes. If one-fourth (1/4) of them have vanilla frosting, how many cupcakes have vanilla frosting?", "3 cupcakes", ["3 cupcakes", "4 cupcakes", "2 cupcakes", "6 cupcakes"]),
            ("There are 8 toy cars on a rug. What is one-fourth (1/4) of 8 toy cars?", "2 cars", ["2 cars", "4 cars", "1 car", "6 cars"]),
            ("A square sheet of paper is folded into 4 equal quarters. How many quarters make the whole paper?", "4 quarters", ["4 quarters", "2 quarters", "3 quarters", "8 quarters"])
        ]
        prompt, correct, pool = fourth_scenarios[idx % len(fourth_scenarios)]
        return prompt, correct, pool, "A quarter means dividing into 4 equal parts.", "VERBAL", None

    elif mod == 3:
        # M-FR-04: Concept of One-Third (1/3)
        third_scenarios = [
            ("A loaf of banana bread is cut into 3 equal slices. What fraction is 1 slice?", "One-third (1/3)", ["One-third (1/3)", "One-half (1/2)", "One-fourth (1/4)", "One whole"]),
            ("There are 9 butterflies in a garden. If one-third (1/3) of them are yellow, how many butterflies are yellow?", "3 butterflies", ["3 butterflies", "6 butterflies", "1 butterfly", "9 butterflies"]),
            ("A ribbon is 12 centimeters long. If you cut off one-third (1/3), how many centimeters is that piece?", "4 centimeters", ["4 centimeters", "3 centimeters", "6 centimeters", "2 centimeters"]),
            ("How many one-third (1/3) slices are needed to make 1 whole pie?", "3 slices", ["3 slices", "2 slices", "4 slices", "6 slices"])
        ]
        prompt, correct, pool = third_scenarios[idx % len(third_scenarios)]
        return prompt, correct, pool, "One-third means dividing into 3 equal parts.", "VERBAL", None

    elif mod == 4:
        # M-FR-05: Equal vs Unequal parts
        parts_scenarios = [
            ("Which option describes a shape divided into EQUAL parts?", "A sandwich cut into 2 matching halves of the exact same size", ["A sandwich cut into 2 matching halves of the exact same size", "A cookie broken into 1 giant piece and 3 tiny crumbs", "A ribbon cut randomly into uneven lengths", "A paper torn jaggedly"]),
            ("If a pancake is cut into 2 parts of DIFFERENT sizes, are the parts equal or unequal?", "Unequal parts", ["Unequal parts", "Equal halves", "Equal thirds", "Identical pieces"]),
            ("For a fraction like 1/2 or 1/4 to be fair and correct, what MUST be true about the pieces?", "All pieces must be the exact same size", ["All pieces must be the exact same size", "Pieces can be any random size", "One piece must always be larger", "Pieces must have different shapes"])
        ]
        prompt, correct, pool = parts_scenarios[idx % len(parts_scenarios)]
        return prompt, correct, pool, "Fractions always require parts to be exactly equal in size.", "VERBAL", None

    else:
        # M-FR-06: Combining fractions to make a whole
        whole_scenarios = [
            ("How many halves (1/2) are needed to make 1 whole unit?", "2 halves", ["2 halves", "4 halves", "1 half", "3 halves"]),
            ("How many one-fourth (1/4) slices are needed to form 1 complete whole circle?", "4 slices", ["4 slices", "2 slices", "3 slices", "8 slices"]),
            ("If you put 2 equal half-circles together along their flat edges, what shape do you make?", "1 whole circle", ["1 whole circle", "1 whole square", "1 half circle", "1 triangle"]),
            ("If you have two quarters (1/4 + 1/4) of a sandwich, that is equivalent to:", "One-half (1/2)", ["One-half (1/2)", "One whole", "One-third (1/3)", "Three-fourths (3/4)"])
        ]
        prompt, correct, pool = whole_scenarios[idx % len(whole_scenarios)]
        return prompt, correct, pool, "Fractions combine together to make larger parts or 1 whole.", "VERBAL", None


def gen_m_du(subskill: str, idx: int):
    """Data & Uncertainty (M-DU: 8 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 8
    colors = ["red", "blue", "green", "yellow", "purple", "orange", "silver", "gold"]
    c1 = colors[(ss_id - 1) % len(colors)]
    c2 = colors[ss_id % len(colors)]

    if mod == 0:
        prompt = f"A bag contains ONLY 10 {c1} marbles and 0 {c2} marbles. If you draw one without looking, what color will you definitely pull out?"
        correct = f"A {c1} marble"
        pool = [f"A {c1} marble", f"A {c2} marble", "Nothing at all", "A purple marble"]
        hint = f"There are only {c1} marbles in the bag, so it is 100% certain."
    elif mod == 1:
        prompt = f"A box contains 15 {c1} blocks and zero {c2} blocks. What is the chance of pulling out a {c2} block?"
        correct = "Impossible (0% chance)"
        pool = ["Impossible (0% chance)", "Certain (100% chance)", "Very likely", "50% chance"]
        hint = f"There are no {c2} blocks in the box, so it is impossible."
    elif mod == 2:
        prompt = f"A jar has 8 {c1} tokens and 2 {c2} tokens. Which color are you MORE LIKELY to pull out without looking?"
        correct = f"A {c1} token"
        pool = [f"A {c1} token", f"A {c2} token", "Both are equally likely"]
        hint = f"There are more {c1} tokens than {c2} tokens."
    elif mod == 3:
        prompt = "A coin has heads on one side and tails on the other side. When flipped, which result is expected?"
        correct = "Heads and tails are equally likely"
        pool = ["Heads and tails are equally likely", "Heads is guaranteed", "Tails is guaranteed", "Neither can happen"]
        hint = "A fair coin has a 50/50 equal chance of landing on heads or tails."
    elif mod == 4:
        prompt = f"A spinner has 9 {c1} sections and only 1 {c2} section. Which outcome is LEAST LIKELY when spun?"
        correct = f"Landing on {c2}"
        pool = [f"Landing on {c2}", f"Landing on {c1}", "Both are equally likely"]
        hint = f"{c2} covers the smallest part of the spinner."
    elif mod == 5:
        prompt = "In a reading log, a student drew four vertical tally marks crossed by one diagonal slash. How many books does that full tally bundle represent?"
        correct = "5"
        pool = ["5", "4", "10", "6"]
        hint = "A standard tally bundle represents 5 items."
    elif mod == 6:
        prompt = f"In a poll, 12 children voted for {c1} and 4 voted for {c2}. Is it TRUE that {c1} received more votes than {c2}?"
        correct = "True"
        pool = ["True", "False", "Cannot be determined"]
        hint = f"12 is greater than 4, so the statement is true."
    else:
        prompt = "The weather forecast predicts an 80% chance of sunshine tomorrow. What is the most reasonable expectation?"
        correct = "It is very likely to be sunny"
        pool = ["It is very likely to be sunny", "It is guaranteed to blizzard", "It is impossible for sun to appear", "It will definitely snow"]
        hint = "An 80% chance means an event is very likely."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_m_ps(subskill: str, idx: int):
    """Problem Solving & Modeling (M-PS: 8 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 8
    items = ["books", "markers", "notebooks", "pencils", "stickers", "art supplies", "lunchboxes", "crayons"]
    item = items[mod]

    if mod == 0:
        need = (idx % 10) + 15
        have = need - (idx % 6 + 4)
        diff = need - have
        prompt = f"The teacher needs {need} {item} for the classroom. She currently has {have}. How many MORE {item} does she need to collect?"
        correct = str(diff)
        pool = [str(diff), str(diff + 2), str(max(1, diff - 1)), str(need)]
        hint = f"Subtract what she has from what she needs: {need} - {have} = {diff}."
    elif mod == 1:
        members = (idx % 3) + 2
        each = (idx % 4) + 3
        total = members * each
        prompt = f"{members} students share {total} {item} equally among themselves. How many {item} does each student receive?"
        correct = str(each)
        pool = [str(each), str(each + 1), str(max(1, each - 2)), str(total)]
        hint = f"Divide equally: {total} ÷ {members} = {each}."
    elif mod == 2:
        start = (idx % 6) + 10
        found = (idx % 4) + 3
        spent = (idx % 3) + 2
        final = start + found - spent
        prompt = f"Liam had {start} {item}, received {found} more from his friend, and gave {spent} away. How many {item} does Liam have now?"
        correct = str(final)
        pool = [str(final), str(final + 2), str(max(1, final - 1)), str(start + found)]
        hint = f"{start} + {found} = {start+found}, minus {spent} = {final}."
    elif mod == 3:
        speed = (idx % 3) + 3
        hours = (idx % 3) + 2
        dist = speed * hours
        prompt = f"A cyclist rides at a steady speed of {speed} kilometers per hour. How many kilometers will they cover in {hours} hours?"
        correct = str(dist)
        pool = [str(dist), str(dist + speed), str(max(1, dist - 2)), str(speed + hours)]
        hint = f"Multiply speed by hours: {speed} × {hours} = {dist} kilometers."
    elif mod == 4:
        base = (idx % 8) + 6
        extra = (idx % 5) + 3
        total = base + extra
        prompt = f"Emma read {base} {item}. Noah read {extra} MORE {item} than Emma. How many {item} did Noah read?"
        correct = str(total)
        pool = [str(total), str(base), str(extra), str(total + extra)]
        hint = f"Add the extra amount: {base} + {extra} = {total}."
    elif mod == 5:
        start = (idx % 10) + 20
        cost = (idx % 8) + 6
        change = start - cost
        prompt = f"Maya had {start} Rupees and spent {cost} Rupees on a snack. How many Rupees does she have left?"
        correct = str(change)
        pool = [str(change), str(change + 2), str(max(1, change - 1)), str(start)]
        hint = f"Subtract the cost: {start} - {cost} = {change} Rupees."
    elif mod == 6:
        packs = (idx % 4) + 3
        per_pack = 5
        total = packs * per_pack
        prompt = f"A store packages {item} in packs of {per_pack}. If you buy {packs} full packs, how many {item} do you get altogether?"
        correct = str(total)
        pool = [str(total), str(total + 5), str(max(5, total - 5)), str(packs + 5)]
        hint = f"Count {packs} groups of {per_pack}: {total} {item}."
    else:
        count = (idx % 3) + 2
        price = (idx % 4) + 3
        total = count * price
        prompt = f"Notebooks cost {price} Rupees each. How much will {count} notebooks cost in total?"
        correct = str(total)
        pool = [str(total), str(total + price), str(max(1, total - 2)), str(count + price)]
        hint = f"Multiply: {count} × {price} = {total} Rupees."

    return prompt, correct, pool, hint, "VERBAL", None


# ----------------------------------------------------------------------
# ENGLISH LANGUAGE DIVERSIFICATION ENGINES (8 Strands)
# ----------------------------------------------------------------------

def gen_e_pd(subskill: str, idx: int):
    """Phonological Awareness & Decoding (E-PD: 6 subskills) - ALL VERBAL"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6

    if mod == 0:
        sounds = [("p", "Pencil", ["Water", "Table", "Window"]), ("b", "Broom", ["Carpet", "Chair", "Door"]), ("m", "Moon", ["Sun", "Cloud", "Star"]), ("c", "Cup", ["Plate", "Fork", "Spoon"])]
        s, correct, wrong = sounds[idx % len(sounds)]
        prompt = f"Which word begins with the /{s}/ sound?"
        pool = [correct] + wrong
        hint = f"'{correct}' begins with the sound /{s}/."
    elif mod == 1:
        ends = [("t", "Boat", ["Fish", "Water", "Sail"]), ("g", "Dog", ["Cat", "Bird", "Mouse"]), ("n", "Sun", ["Sky", "Star", "Cloud"]), ("k", "Book", ["Page", "Letter", "Word"])]
        s, correct, wrong = ends[idx % len(ends)]
        prompt = f"Which word ends with the /{s}/ sound?"
        pool = [correct] + wrong
        hint = f"'{correct}' ends with the /{s}/ sound."
    elif mod == 2:
        rhymes = [("star", "Far", ["Moon", "Sky", "Sun"]), ("cat", "Hat", ["Dog", "Bird", "Mouse"]), ("gold", "Bold", ["Coin", "Silver", "Ring"]), ("ring", "King", ["Crown", "Robe", "Castle"])]
        target, correct, wrong = rhymes[idx % len(rhymes)]
        prompt = f"Which word rhymes with '{target}'?"
        pool = [correct] + wrong
        hint = f"'{correct}' and '{target}' share the same ending sound."
    elif mod == 3:
        sylls = [("cat", "1", ["2", "3", "4"]), ("tiger", "2", ["1", "3", "4"]), ("elephant", "3", ["1", "2", "4"]), ("alligator", "4", ["2", "3", "5"])]
        word, correct, wrong = sylls[idx % len(sylls)]
        prompt = f"Clap out the syllables (beats) in the word '{word}'. How many syllables does it have?"
        pool = [correct] + wrong
        hint = f"The word '{word}' has {correct} syllables."
    elif mod == 4:
        blends = [("s - u - n", "Sun", ["Star", "Moon", "Sky"]), ("c - a - p", "Cap", ["Hat", "Cup", "Coat"]), ("f - i - sh", "Fish", ["Frog", "Bird", "Pond"]), ("b - a - t", "Bat", ["Ball", "Bird", "Cat"])]
        segmented, correct, wrong = blends[idx % len(blends)]
        prompt = f"Listen closely: /{segmented}/. What word do these sounds blend together to make?"
        pool = [correct] + wrong
        hint = f"Blending /{segmented}/ forms '{correct}'."
    else:
        vowels = [("short /a/", "Cat", ["Cake", "Car", "Boat"]), ("long /e/", "Tree", ["Bed", "Red", "Ten"]), ("short /i/", "Pin", ["Pine", "Pie", "Pen"]), ("long /o/", "Boat", ["Bat", "Box", "Bus"])]
        v_sound, correct, wrong = vowels[idx % len(vowels)]
        prompt = f"Which word contains the {v_sound} vowel sound?"
        pool = [correct] + wrong
        hint = f"'{correct}' contains the {v_sound} sound."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_e_vm(subskill: str, idx: int):
    """Vocabulary & Morphology (E-VM: 7 subskills) - ALL VERBAL"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 7

    if mod == 0:
        words = [("colossal", "Huge", ["Tiny", "Green", "Friendly"]), ("ancient", "Very old", ["New", "Shiny", "Broken"]), ("swift", "Fast", ["Slow", "Loud", "Heavy"]), ("fragile", "Easily broken", ["Strong", "Heavy", "Tall"])]
        word, correct, wrong = words[idx % len(words)]
        prompt = f"What is the meaning of the word '{word}'?"
        pool = [correct] + wrong
        hint = f"'{word}' means {correct.lower()}."
    elif mod == 1:
        syns = [("brave", "Courageous", ["Cowardly", "Sleepy", "Hungry"]), ("gleaming", "Shining", ["Dull", "Dark", "Dirty"]), ("clever", "Smart", ["Foolish", "Slow", "Heavy"]), ("furious", "Angry", ["Calm", "Peaceful", "Joyful"])]
        word, correct, wrong = syns[idx % len(syns)]
        prompt = f"Which word has the SAME meaning (synonym) as '{word}'?"
        pool = [correct] + wrong
        hint = f"'{correct}' means the same as '{word}'."
    elif mod == 2:
        ants = [("ancient", "Modern", ["Old", "Historic", "Dusty"]), ("gloomy", "Bright", ["Dark", "Cloudy", "Sad"]), ("fierce", "Gentle", ["Wild", "Mean", "Rough"]), ("hollow", "Solid", ["Empty", "Deep", "Curved"])]
        word, correct, wrong = ants[idx % len(ants)]
        prompt = f"Which word is the exact OPPOSITE (antonym) of '{word}'?"
        pool = [correct] + wrong
        hint = f"The opposite of '{word}' is '{correct}'."
    elif mod == 3:
        compounds = [("star", "fish", "Starfish", ["Starplanet", "Fishstar", "Starlight"]), ("sun", "flower", "Sunflower", ["Suncloud", "Flowerpower", "Sunbeam"]), ("butter", "fly", "Butterfly", ["Buttercup", "Flybutter", "Breadfly"])]
        w1, w2, correct, wrong = compounds[idx % len(compounds)]
        prompt = f"When you combine the words '{w1}' and '{w2}', what compound word is formed?"
        pool = [correct] + wrong
        hint = f"'{w1}' + '{w2}' = '{correct}'."
    elif mod == 4:
        affixes = [("un-", "happy", "Not happy", ["Very happy", "Always happy", "Extremely happy"]), ("re-", "build", "Build again", ["Never build", "Destroy", "Build first"]), ("pre-", "view", "View before", ["View after", "Never view", "View loud"])]
        pref, base, correct, wrong = affixes[idx % len(affixes)]
        prompt = f"What does the word '{pref}{base}' mean when you add the prefix '{pref}'?"
        pool = [correct] + wrong
        hint = f"The prefix '{pref}' means {correct.lower()}."
    elif mod == 5:
        contexts = [
            ("The thirsty travelers were *parched* after walking across the dry desert without any water.", "parched", "Extremely thirsty", ["Very cold", "Full of food", "Energetic"]),
            ("The kitten was *cautious* as it quietly tiptoed past the sleeping puppy.", "cautious", "Very careful", ["Noisy", "Angry", "Reckless"])
        ]
        sent, target, correct, wrong = contexts[idx % len(contexts)]
        prompt = f"Read the sentence: '{sent}' Using context clues, what does '{target}' mean?"
        pool = [correct] + wrong
        hint = f"The clues in the sentence show that '{target}' means {correct.lower()}."
    else:
        cats = [("fruits", "Apple", ["Carrot", "Potato", "Broccoli"]), ("musical instruments", "Guitar", ["Painting", "Hammer", "Book"]), ("vehicles", "Bicycle", ["Tree", "House", "Chair"])]
        cat, correct, wrong = cats[idx % len(cats)]
        prompt = f"Which of these belongs to the category of '{cat}'?"
        pool = [correct] + wrong
        hint = f"A {correct.lower()} is an example of {cat}."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_e_sg(subskill: str, idx: int):
    """Syntax & Grammar (E-SG: 5 subskills) - ALL VERBAL"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 5

    if mod == 0:
        n = (idx % 3) + 1
        if n == 1:
            correct, wrong = "The children played in the park.", ["The children in the park played.", "park in played children the The.", "Played the children park in."]
        elif n == 2:
            correct, wrong = "A gentle breeze blew the leaves.", ["Leaves the blew breeze gentle a.", "Blew breeze a gentle leaves the.", "A leaves gentle breeze the blew."]
        else:
            correct, wrong = "The teacher read a storybook.", ["Read a storybook the teacher.", "Teacher the a storybook read.", "A storybook read teacher the."]
        prompt = "Which sentence is written with the correct, natural word order?"
        pool = [correct] + wrong
        hint = "English sentences follow Subject + Verb + Object order."
    elif mod == 1:
        agreements = [
            ("The two dogs [barks / bark / barking] at the mail carrier.", "bark", ["barks", "barking", "barked"]),
            ("Emma [sing / sings / singing] a cheerful song.", "sings", ["sing", "singing", "sung"]),
            ("The students [listens / listen / listening] to the instructions.", "listen", ["listens", "listening", "listened"])
        ]
        sent, correct, wrong = agreements[idx % len(agreements)]
        prompt = f"Choose the correct verb to complete the sentence: '{sent}'"
        pool = [correct] + wrong
        hint = f"Singular subjects take singular verbs; plural subjects take plural verbs: '{correct}'."
    elif mod == 2:
        puncts = [
            ("Where did you put the library book?", ["where did you put the library book", "Where did you put the library book.", "Where did you put the library book!"]),
            ("The stars shine brightly tonight.", ["the stars shine brightly tonight", "The stars shine brightly tonight?", "the Stars shine brightly tonight."])
        ]
        correct, wrong = puncts[idx % len(puncts)]
        prompt = "Which sentence has correct capitalization and end punctuation?"
        pool = [correct] + wrong
        hint = "Sentences must start with a capital letter and end with the proper punctuation mark."
    elif mod == 3:
        pronouns = [
            ("Maya finished her drawing. ___ showed it to the class.", "She", ["He", "They", "It"]),
            ("Leo packed his backpack. ___ walked to school.", "He", ["She", "They", "It"]),
            ("The children worked together. ___ cleaned up the classroom.", "They", ["He", "She", "It"])
        ]
        sent, correct, wrong = pronouns[idx % len(pronouns)]
        prompt = f"Fill in the blank with the correct pronoun: '{sent}'"
        pool = [correct] + wrong
        hint = f"Use '{correct}' to match the antecedent."
    else:
        tenses = [
            ("Yesterday, Liam [walks / walked / will walk] to the library.", "walked", ["walks", "will walk", "walking"]),
            ("Right now, Maya [paints / painted / will paint] a colorful picture.", "paints", ["painted", "will paint", "painting"]),
            ("Tomorrow, our class [will visit / visited / visits] the science museum.", "will visit", ["visited", "visits", "visiting"])
        ]
        sent, correct, wrong = tenses[idx % len(tenses)]
        prompt = f"Choose the correct verb tense for the timeframe described: '{sent}'"
        pool = [correct] + wrong
        hint = f"The time clue determines the correct tense: '{correct}'."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_e_rf(subskill: str, idx: int):
    """Reading Foundations & Decoding (E-RF: 5 subskills) - ALL VERBAL"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 5

    if mod == 0:
        # E-RF-01: High-frequency sight words in authentic sentence context (NO HIEROGLYPHS!)
        sight_words = [
            ("Alex is a loyal ___ who is always ready to help.", "friend", ["friund", "friendz", "freind"]),
            ("We stayed inside the house ___ it was raining heavily.", "because", ["becuse", "becawse", "becausee"]),
            ("The birds flew back to ___ nest in the tall tree.", "their", ["thier", "theire", "ther"]),
            ("She ran as fast as she ___ across the playground.", "could", ["cood", "culd", "coudl"]),
            ("You ___ always wash your hands before eating lunch.", "should", ["shood", "shuld", "shoudl"]),
            ("What ___ you like to read for storytime today?", "would", ["wood", "wuld", "woudl"])
        ]
        sent, correct, wrong = sight_words[idx % len(sight_words)]
        prompt = f"Complete the sentence with the correct spelling: '{sent}' Which spelling is correct?"
        pool = [correct] + wrong
        hint = f"The correct spelling of the sight word is '{correct}'."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 1:
        # E-RF-02: Silent 'e' rule
        magic_e = [("hop", "hope", ["hop", "hopp", "hype"]), ("tap", "tape", ["tap", "tapp", "tep"]), ("pin", "pine", ["pin", "pinn", "pean"]), ("cub", "cube", ["cub", "cubb", "cobe"])]
        base, correct, wrong = magic_e[idx % len(magic_e)]
        prompt = f"When you add a silent 'e' to the word '{base}', what new word is formed?"
        pool = [correct] + wrong
        hint = f"Adding silent 'e' makes the vowel say its name: '{base}' becomes '{correct}'."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 2:
        # E-RF-03: Vowel digraphs
        digraphs = [("oa", "Boat", ["Bat", "Box", "Boot"]), ("ee", "Tree", ["Tray", "True", "Trip"]), ("ai", "Rain", ["Ran", "Run", "Rope"]), ("ea", "Leaf", ["Life", "Loaf", "Left"])]
        di, correct, wrong = digraphs[idx % len(digraphs)]
        prompt = f"Which word contains the vowel team '{di}' to make a long vowel sound?"
        pool = [correct] + wrong
        hint = f"'{correct}' uses the '{di}' vowel team."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 3:
        # E-RF-04: Consonant blends
        blends = [("bl-", "Blast", ["Fast", "Last", "Past"]), ("st-", "Star", ["Car", "Far", "Bar"]), ("gr-", "Green", ["Seen", "Bean", "Teen"]), ("fl-", "Flame", ["Name", "Game", "Same"])]
        bl, correct, wrong = blends[idx % len(blends)]
        prompt = f"Which word begins with the consonant blend '{bl}'?"
        pool = [correct] + wrong
        hint = f"'{correct}' begins with the '{bl}' blend."
        return prompt, correct, pool, hint, "VERBAL", None

    else:
        # E-RF-05: Word families
        families = [("-ight", "Knight", ["Night", "Sight", "Fight"], ["Knot", "Knee", "Knife"]), ("-all", "Ball", ["Call", "Fall", "Tall"], ["Bell", "Bull", "Bill"]), ("-ing", "Ring", ["Sing", "Wing", "King"], ["Rope", "Rake", "Rose"])]
        fam, correct, fam_words, wrong = families[idx % len(families)]
        prompt = f"Which word belongs to the '{fam}' word family?"
        pool = [correct] + wrong[:3]
        hint = f"'{correct}' ends with '{fam}'."
        return prompt, correct, pool, hint, "VERBAL", None


def gen_e_cr(subskill: str, idx: int):
    """Comprehension & Response (E-CR: 9 subskills) - ALL VERBAL (Grade 1 / Level 1)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 9

    if mod == 0:
        # Key details
        stories = [
            ("Maya has a little red wagon.", "What color is Maya's wagon?", "Red", ["Red", "Blue", "Green", "Yellow"]),
            ("Leo found a shiny golden key.", "What did Leo find?", "A golden key", ["A golden key", "A wooden stick", "A red ball", "A toy car"]),
            ("Emma brought an apple to school.", "What did Emma bring?", "An apple", ["An apple", "A banana", "A carrot", "An orange"])
        ]
        text, q, correct, pool = stories[idx % len(stories)]
        prompt = f"Read the sentence: '{text}' {q}"
        return prompt, correct, pool, f"The sentence says it is {correct.lower()}.", "VERBAL", None

    elif mod == 1:
        # Characters
        chars = [
            ("Leo planted sunflower seeds in the garden.", "Who planted the seeds?", "Leo", ["Leo", "A puppy", "The teacher", "A bird"]),
            ("Maya rode her bicycle to the park.", "Who rode the bicycle?", "Maya", ["Maya", "The cat", "A rabbit", "The driver"]),
            ("Noah read a funny book about dinosaurs.", "Who read the book?", "Noah", ["Noah", "A monkey", "The puppy", "A frog"])
        ]
        text, q, correct, pool = chars[idx % len(chars)]
        prompt = f"Read the sentence: '{text}' {q}"
        return prompt, correct, pool, f"{correct} is the character in the story.", "VERBAL", None

    elif mod == 2:
        # Setting
        settings = [
            ("Gentle waves washed over the warm, sandy beach.", "Where is this taking place?", "At the beach", ["At the beach", "In a cave", "At school", "In a forest"]),
            ("Tall pine trees grew all around as birds sang in the branches.", "Where is this scene?", "In the forest", ["In the forest", "At the airport", "In a pool", "In a store"]),
            ("Desks were lined in neat rows and books rested on the shelves.", "Where is this room?", "In a classroom", ["In a classroom", "In a garden", "In a kitchen", "On a farm"])
        ]
        text, q, correct, pool = settings[idx % len(settings)]
        prompt = f"Read the clue: '{text}' {q}"
        return prompt, correct, pool, f"The clues tell us this is {correct.lower()}.", "VERBAL", None

    elif mod == 3:
        # Main idea
        ideas = [
            ("Honeybees fly to blooming flowers to help new plants grow.", "What do bees help?", "Flowers grow", ["Flowers grow", "Cars drive", "Fish swim", "Beds sleep"]),
            ("Children put away the blocks and books together so the room was tidy.", "What were the children doing?", "Cleaning up", ["Cleaning up", "Sleeping", "Eating lunch", "Swimming"])
        ]
        text, q, correct, pool = ideas[idx % len(ideas)]
        prompt = f"Read the sentence: '{text}' {q}"
        return prompt, correct, pool, f"The main idea is {correct.lower()}.", "VERBAL", None

    elif mod == 4:
        # Cause and effect
        ce = [
            ("Because it started to rain, Emma opened her umbrella.", "Why did Emma open her umbrella?", "It started to rain", ["It started to rain", "It was sunny", "It was bedtime", "It was hot"]),
            ("Because the sun was so hot, the snowman began to melt.", "Why did the snowman melt?", "The sun was hot", ["The sun was hot", "It was freezing", "It was night", "It was windy"])
        ]
        text, q, correct, pool = ce[idx % len(ce)]
        prompt = f"Read: '{text}' {q}"
        return prompt, correct, pool, f"The cause was: {correct.lower()}.", "VERBAL", None

    elif mod == 5:
        # Sequence
        seqs = [
            ("First, Tom put on his socks. Next, he put on his shoes.", "What did Tom put on FIRST?", "Socks", ["Socks", "Shoes", "Hat", "Coat"]),
            ("First, Maya poured milk in a bowl. Next, she added cereal.", "What did Maya do FIRST?", "Poured milk", ["Poured milk", "Added cereal", "Ate lunch", "Washed dishes"])
        ]
        text, q, correct, pool = seqs[idx % len(seqs)]
        prompt = f"Read: '{text}' {q}"
        return prompt, correct, pool, f"The first step was {correct.lower()}.", "VERBAL", None

    elif mod == 6:
        # Problem
        probs = [
            ("The puppy was hungry and barked at its empty food bowl.", "What was the puppy's problem?", "It was hungry", ["It was hungry", "It was too full", "It was sleepy", "It was flying"]),
            ("Maya could not find her red crayon in the box.", "What was Maya's problem?", "Lost crayon", ["Lost crayon", "Broken shoes", "Too much food", "Rainy day"])
        ]
        text, q, correct, pool = probs[idx % len(probs)]
        prompt = f"Read: '{text}' {q}"
        return prompt, correct, pool, f"The problem is that {correct.lower()}.", "VERBAL", None

    elif mod == 7:
        # Solution
        sols = [
            ("The kitten was stuck in a low tree, so Dad helped it down.", "How was the kitten helped?", "Dad helped it down", ["Dad helped it down", "Dad walked away", "Dad climbed a roof", "Dad sang a song"]),
            ("Leo's pencil broke, so he sharpened it with a sharpener.", "How did Leo fix his pencil?", "Sharpened it", ["Sharpened it", "Threw it away", "Ate it", "Painted it"])
        ]
        text, q, correct, pool = sols[idx % len(sols)]
        prompt = f"Read: '{text}' {q}"
        return prompt, correct, pool, f"The solution was: {correct.lower()}.", "VERBAL", None

    else:
        # Feelings / Inferences
        feels = [
            ("Maya smiled and jumped with joy when she saw the puppy.", "How did Maya feel?", "Happy", ["Happy", "Sad", "Angry", "Sleepy"]),
            ("Leo lost his favorite toy and a tear rolled down his cheek.", "How did Leo feel?", "Sad", ["Sad", "Excited", "Cheerful", "Silly"])
        ]
        text, q, correct, pool = feels[idx % len(feels)]
        prompt = f"Read: '{text}' {q}"
        return prompt, correct, pool, f"The clue shows {correct.lower()}.", "VERBAL", None


def gen_e_cc(subskill: str, idx: int):
    """Creative & Composition (E-CC: 6 subskills) - ALL VERBAL (Grade 1 / Level 1)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6

    if mod == 0:
        endings = [
            ("Leo dropped his crayon under the desk, so he...", "picked it up", ["picked it up", "flew away", "took a nap", "ate his shoe"]),
            ("The puppy was thirsty, so Maya gave it...", "a bowl of water", ["a bowl of water", "a book", "a shoe", "a pencil"]),
            ("It started to rain outside, so the children...", "went indoors", ["went indoors", "turned invisible", "went to sleep", "planted trees"])
        ]
        start, correct, wrong = endings[idx % len(endings)]
        prompt = f"Choose the best ending to finish the sentence: '{start}'"
        pool = [correct] + wrong
        return prompt, correct, pool, "Pick the action that makes natural sense.", "VERBAL", None

    elif mod == 1:
        qs = [
            ("You found a lost puppy with a collar. What should you ask?", "Where is your home?", ["Where is your home?", "What time is dinner?", "Can you do math?", "How tall is a tree?"]),
            ("A classmate is crying on the bench. What is kind to ask?", "Are you okay?", ["Are you okay?", "Why are you loud?", "Can I have your lunch?", "Where is the bus?"])
        ]
        scen, correct, wrong = qs[idx % len(qs)]
        prompt = scen
        pool = [correct] + wrong
        return prompt, correct, pool, "Ask a helpful question.", "VERBAL", None

    elif mod == 2:
        starters = [
            ("Which is the best beginning for a story about a kitten?", "A little kitten found a soft ball of yarn.", ["A little kitten found a soft ball of yarn.", "Apples are red.", "Rain is wet.", "Desks are wooden."]),
            ("Which is the best beginning for a story about a spaceship?", "The shiny rocket blasted into the starry sky.", ["The shiny rocket blasted into the starry sky.", "Pencils have erasers.", "Cats like milk.", "The door closed."])
        ]
        prompt, correct, wrong = starters[idx % len(starters)]
        pool = [correct] + wrong
        return prompt, correct, pool, "A good story starter introduces the subject.", "VERBAL", None

    elif mod == 3:
        descs = [
            ("Which sentence describes a sweet red strawberry best?", "A sweet, juicy red berry.", ["A sweet, juicy red berry.", "It is a thing.", "Berries are round.", "Food is eaten."]),
            ("Which words describe a soft fluffy bunny best?", "A soft, fluffy little bunny.", ["A soft, fluffy little bunny.", "An animal with legs.", "Bunnies exist.", "Things that move."])
        ]
        prompt, correct, wrong = descs[idx % len(descs)]
        pool = [correct] + wrong
        return prompt, correct, pool, "Descriptive words help you picture the item.", "VERBAL", None

    elif mod == 4:
        talk = [
            ("What would a friendly dragon say to invite you to play?", "'Come play with me!'", ["'Come play with me!'", "'Be quiet.'", "'Books are rectangular.'", "'I am a rock.'"]),
            ("What does a cheerful bird seem to say in the morning?", "'Chirp chirp, wake up!'", ["'Chirp chirp, wake up!'", "'Go away.'", "'Pencils are sharp.'", "'Nighttime is here.'"])
        ]
        prompt, correct, wrong = talk[idx % len(talk)]
        pool = [correct] + wrong
        return prompt, correct, pool, "Dialogue should match the character's mood.", "VERBAL", None

    else:
        conns = [
            ("First we played tag. ___, we ate a healthy snack.", "Next", ["Next", "Yesterday", "Never", "Because"]),
            ("The sun came up, ___ the birds began to sing.", "and", ["and", "but", "or", "so"])
        ]
        sent, correct, wrong = conns[idx % len(conns)]
        prompt = f"Fill in the missing word: '{sent}'"
        pool = [correct] + wrong
        return prompt, correct, pool, f"'{correct}' connects the two events naturally.", "VERBAL", None


def gen_e_we(subskill: str, idx: int):
    """Written Expression & Editing (E-WE: 9 subskills) - ALL VERBAL (Grade 1 / Level 1)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 9

    if mod == 0:
        # Subject-verb agreement
        sents = [
            ("The cat is happy.", ["The cat are happy.", "Cat the is happy.", "The cat am happy."]),
            ("The dogs run fast.", ["The dogs runs fast.", "The dog run fast.", "Runs the dogs fast."]),
            ("We are ready.", ["We is ready.", "We am ready.", "Ready we is."])
        ]
        correct, wrong = sents[idx % len(sents)]
        prompt = "Which sentence is written correctly?"
        pool = [correct] + wrong
        return prompt, correct, pool, "Use words that match.", "VERBAL", None

    elif mod == 1:
        # Capitalization of names/days
        caps = [
            ("Which word should ALWAYS start with a capital letter?", "Monday", ["Monday", "happy", "tree", "apple"]),
            ("Which name is capitalized correctly?", "Emma", ["Emma", "emma", "eMma", "EMma"]),
            ("Which day of the week is capitalized correctly?", "Friday", ["Friday", "friday", "friDay", "fridaY"])
        ]
        prompt, correct, pool = caps[idx % len(caps)]
        return prompt, correct, pool, "Names and days always start with a capital letter.", "VERBAL", None

    elif mod == 2:
        # Punctuation marks
        puncts = [
            ("Which mark goes at the end of: 'Where is my dog___'?", "?", ["?", ".", "!", ","]),
            ("Which mark goes at the end of a statement: 'The cat is sleeping___'?", ".", [".", "?", "!", ","]),
            ("Which mark shows excitement: 'Look at that huge rainbow___'?", "!", ["!", ".", "?", ","])
        ]
        prompt, correct, pool = puncts[idx % len(puncts)]
        return prompt, correct, pool, "Questions end with a question mark (?).", "VERBAL", None

    elif mod == 3:
        # Simple plurals (-s)
        plurals = [
            ("What is the plural of 'dog'?", "dogs", ["dogs", "doges", "dogz", "dogies"]),
            ("What is the plural of 'cat'?", "cats", ["cats", "cates", "catz", "caties"]),
            ("What is the plural of 'bird'?", "birds", ["birds", "birdes", "birdz", "birdies"])
        ]
        prompt, correct, pool = plurals[idx % len(plurals)]
        return prompt, correct, pool, f"Add -s to make it plural: {correct}.", "VERBAL", None

    elif mod == 4:
        # Plurals with -es
        plurals_es = [
            ("What is the plural of 'box'?", "boxes", ["boxes", "boxs", "boxies", "boxen"]),
            ("What is the plural of 'fox'?", "foxes", ["foxes", "foxs", "foxies", "foxen"]),
            ("What is the plural of 'bus'?", "buses", ["buses", "buss", "busies", "busen"])
        ]
        prompt, correct, pool = plurals_es[idx % len(plurals_es)]
        return prompt, correct, pool, f"Words ending in x or s add -es: {correct}.", "VERBAL", None

    elif mod == 5:
        # Capital letter at start of sentence
        sents = [
            ("Which sentence starts with a capital letter and ends with a period?", "The sun is warm.", ["The sun is warm.", "the sun is warm.", "THE SUN IS WARM?", "sun the is warm."]),
            ("Which sentence is written correctly?", "We love to read.", ["We love to read.", "we love to read.", "WE LOVE TO READ?", "read we love to."])
        ]
        prompt, correct, pool = sents[idx % len(sents)]
        return prompt, correct, pool, "Sentences begin with a capital letter and end with a period.", "VERBAL", None

    elif mod == 6:
        # Describing words (Adjectives)
        adjs = [
            ("Which word describes the color of grass?", "Green", ["Green", "Run", "Tree", "From"]),
            ("Which word describes how a kitten feels?", "Soft", ["Soft", "Jump", "Walk", "Door"]),
            ("Which word describes an elephant?", "Huge", ["Huge", "Fly", "Eat", "Table"])
        ]
        prompt, correct, pool = adjs[idx % len(adjs)]
        return prompt, correct, pool, f"'{correct}' is a describing word.", "VERBAL", None

    elif mod == 7:
        # Connecting words (and, but)
        connects = [
            ("I like apples ___ I like oranges.", "and", ["and", "or", "so", "but"]),
            ("I ran fast, ___ I was not tired.", "but", ["but", "and", "or", "so"])
        ]
        sent, correct, wrong = connects[idx % len(connects)]
        prompt = f"Fill in the missing connecting word: '{sent}'"
        pool = [correct] + wrong
        return prompt, correct, pool, f"Use '{correct}' to connect the ideas.", "VERBAL", None

    else:
        # Grade 1 spelling
        spells = [
            ("Which word is spelled correctly?", "friend", ["friend", "frend", "frind", "frien"]),
            ("Which word is spelled correctly?", "little", ["little", "litel", "littel", "litul"]),
            ("Which word is spelled correctly?", "water", ["water", "watur", "watter", "wahtur"])
        ]
        prompt, correct, pool = spells[idx % len(spells)]
        return prompt, correct, pool, f"The correct spelling is '{correct}'.", "VERBAL", None


def gen_e_ol(subskill: str, idx: int):
    """Oral Language & Communication (E-OL: 6 subskills) - ALL VERBAL (Grade 1 / Level 1)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6

    if mod == 0:
        # E-OL-01: Greetings
        greetings = [
            ("Your teacher welcomes you in the morning. What do you say?", "Good morning!", ["Good morning!", "Goodbye!", "Go away", "Be quiet"]),
            ("You meet a new friend at the park. What is a friendly greeting?", "Hello, nice to meet you!", ["Hello, nice to meet you!", "Go away!", "Don't look at me", "Nothing"]),
            ("It is time to leave school at the end of the day. What do you say?", "See you tomorrow!", ["See you tomorrow!", "Never come back", "Be quiet", "Give me that"])
        ]
        prompt, correct, pool = greetings[idx % len(greetings)]
        return prompt, correct, pool, "We use kind words to greet others.", "VERBAL", None

    elif mod == 1:
        # E-OL-02: Apologies
        apologies = [
            ("You accidentally bump into a friend. What is the kind thing to say?", "I'm sorry!", ["I'm sorry!", "Move away!", "Not my fault!", "Watch out!"]),
            ("You accidentally drop a friend's crayon. What do you say?", "Sorry, let me help pick it up!", ["Sorry, let me help!", "You dropped it", "I don't care", "Whatever"]),
            ("You interrupted someone while they were speaking. What should you say?", "Excuse me, sorry!", ["Excuse me, sorry!", "Stop talking!", "Listen to me now!", "I don't care"])
        ]
        prompt, correct, pool = apologies[idx % len(apologies)]
        return prompt, correct, pool, "A kind apology says sorry politely.", "VERBAL", None

    elif mod == 2:
        # E-OL-03: Gratitude
        gratitude = [
            ("A classmate shares their crayons with you. What do you say?", "Thank you!", ["Thank you!", "Give me more!", "Took you long enough", "Nothing"]),
            ("Someone holds the door open for you. What is polite to say?", "Thank you so much!", ["Thank you so much!", "Close it!", "I didn't ask", "Hurry up"]),
            ("You receive a nice birthday gift. What do you say?", "Thank you, I love it!", ["Thank you, I love it!", "I wanted something else", "Take it back", "No"])
        ]
        prompt, correct, pool = gratitude[idx % len(gratitude)]
        return prompt, correct, pool, "Always say thank you when someone is kind.", "VERBAL", None

    elif mod == 3:
        # E-OL-04: Polite requests
        requests = [
            ("You want to borrow a blue crayon. How do you ask politely?", "May I please borrow that?", ["May I please borrow that?", "Give it to me!", "Mine now!", "Hand it over!"]),
            ("You need help tying your shoes. What do you ask?", "Could you please help me?", ["Could you please help me?", "Tie this now!", "Do it fast!", "You have to help me"]),
            ("You would like a drink of water. How do you ask nicely?", "May I get a drink, please?", ["May I get a drink, please?", "Give water now!", "I'm taking this", "Water!"])
        ]
        prompt, correct, pool = requests[idx % len(requests)]
        return prompt, correct, pool, "Use the magic word 'please' when asking for help.", "VERBAL", None

    elif mod == 4:
        # E-OL-05: Good listening habits
        listening = [
            ("When someone is speaking to you, what is the best way to listen?", "Look and listen quietly", ["Look and listen quietly", "Talk over them", "Cover your ears", "Walk away"]),
            ("How do you show that you are paying attention to storytime?", "Sit quietly and listen", ["Sit quietly and listen", "Shout across the room", "Play with toys", "Run around"]),
            ("If you did not hear what someone said, what should you say politely?", "Could you please repeat that?", ["Could you please repeat that?", "Why did you yell?", "I wasn't listening", "Whatever"])
        ]
        prompt, correct, pool = listening[idx % len(listening)]
        return prompt, correct, pool, "Good listeners look at the speaker and listen quietly.", "VERBAL", None

    else:
        # E-OL-06: Welcoming and including others
        including = [
            ("A classmate is sitting alone at recess. What can you say to include them?", "Would you like to play with us?", ["Would you like to play?", "You can't play here", "Go away", "Leave us alone"]),
            ("A new student joins your class table. What is a welcoming thing to say?", "Welcome! You can sit with us.", ["Welcome! Sit with us.", "This table is full", "Go away", "No new kids"]),
            ("Your group needs one more player for a game. What do you say to a friend?", "Come join our game!", ["Come join our game!", "You're not good enough", "We don't want you", "Go away"])
        ]
        prompt, correct, pool = including[idx % len(including)]
        return prompt, correct, pool, "We use kind words to welcome and include everyone.", "VERBAL", None


# ----------------------------------------------------------------------
# SCIENCE & EVS DIVERSIFICATION ENGINES (6 Strands)
# ----------------------------------------------------------------------

def gen_s_kn(subskill: str, idx: int):
    """Knowledge of Scientific Concepts (S-KN: 11 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 11

    if mod == 0:
        prompt = "Which animal breathes underwater by taking in water through gills?"
        correct = "Shark"
        pool = ["Shark", "Dolphin", "Sea Turtle", "Penguin"]
        hint = "Fish and sharks use gills to breathe underwater."
        return prompt, correct, pool, hint, "VISUAL", build_creature_or_entity_svg("shark")
    elif mod == 1:
        prompt = "Look at the creature shown above. It has exactly eight legs. What is it?"
        correct = "Spider"
        pool = ["Spider", "Ant", "Beetle", "Butterfly"]
        hint = "Spiders have 8 legs."
        return prompt, correct, pool, hint, "VISUAL", build_creature_or_entity_svg("spider")
    elif mod == 2:
        prompt = "Look at the tree shown above. Which tree grows from a little acorn seed?"
        correct = "Oak tree"
        pool = ["Oak tree", "Pine tree", "Rose bush", "Sunflower"]
        hint = "Acorns grow into mighty oak trees."
        return prompt, correct, pool, hint, "VISUAL", build_creature_or_entity_svg("tree")
    elif mod == 3:
        prompt = "Which animal has feathers, wings, and can fly in the sky?"
        correct = "A Bird"
        pool = ["A Bird", "A Fish", "A Frog", "A Rabbit"]
        hint = "Birds have feathers and wings."
        return prompt, correct, pool, hint, "VERBAL", None
    elif mod == 4:
        prompt = "Which animal has dry scaly skin and crawls on sunny rocks?"
        correct = "A Lizard"
        pool = ["A Lizard", "A Frog", "A Trout", "A Hamster"]
        hint = "Lizards are reptiles with dry scales."
        return prompt, correct, pool, hint, "VERBAL", None
    elif mod == 5:
        prompt = "Which animal has warm fur, feeds milk to its babies, and can be a pet?"
        correct = "A Dog"
        pool = ["A Dog", "A Goldfish", "A Robin", "An Ant"]
        hint = "Dogs are mammals with fur."
        return prompt, correct, pool, hint, "VERBAL", None
    elif mod == 6:
        prompt = "Look at the body organ shown above. Which organ beats inside your chest to pump blood?"
        correct = "The Heart"
        pool = ["The Heart", "The Lungs", "The Stomach", "The Brain"]
        hint = "The heart pumps blood through your body."
        return prompt, correct, pool, hint, "VISUAL", build_creature_or_entity_svg("heart")
    elif mod == 7:
        prompt = "Look at the sky above. Which bright star gives light and warmth to Earth during the day?"
        correct = "The Sun"
        pool = ["The Sun", "The Moon", "Mars", "North Star"]
        hint = "The Sun is the star that warms our planet."
        return prompt, correct, pool, hint, "VISUAL", build_creature_or_entity_svg("sun")
    elif mod == 8:
        prompt = "What fluffy white shapes float high in the sky on a sunny day?"
        correct = "Clouds"
        pool = ["Clouds", "Rainbows", "Wind", "Lightning"]
        hint = "Clouds float in the sky."
        return prompt, correct, pool, hint, "VERBAL", None
    elif mod == 9:
        prompt = "What is an ancient stone footprint or bone of a dinosaur called?"
        correct = "A Fossil"
        pool = ["A Fossil", "A Crystal", "A Pebble", "A Gem"]
        hint = "Old bones preserved in stone are fossils."
        return prompt, correct, pool, hint, "VERBAL", None
    else:
        prompt = "What natural warmth and light from the sky gives Earth clean energy?"
        correct = "Sunlight"
        pool = ["Sunlight", "Coal", "Oil", "Gasoline"]
        hint = "Sunlight gives clean, natural energy."
        return prompt, correct, pool, hint, "VERBAL", None


def gen_s_oc(subskill: str, idx: int):
    """Observational Concepts (S-OC: 5 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 5

    if mod == 0:
        items = [("living", "A Maple Tree", ["A Granite Rock", "A Metal Bicycle", "A Plastic Bottle"]),
                 ("non-living", "A Silver Coin", ["A Flying Sparrow", "A Green Fern", "A Swimming Trout"])]
        cat, correct, wrong = items[idx % len(items)]
        prompt = f"Which of these items is classified as a {cat} thing?"
        pool = [correct] + wrong
        hint = f"{correct} is {cat}."
    elif mod == 1:
        prompts = [
            ("Which of these animals is classified as a mammal?", "Dolphin", ["Crocodile", "Tuna", "Eagle"]),
            ("Which of these animals is classified as an amphibian?", "Tree Frog", ["Lizard", "Robin", "Goldfish"])
        ]
        p_str, correct, wrong = prompts[idx % len(prompts)]
        prompt = p_str
        pool = [correct] + wrong
        hint = f"{correct} fits this classification."
    elif mod == 2:
        parts = [
            ("absorbs water and nutrients from the soil while anchoring the plant", "Roots", ["Leaves", "Flowers", "Stem"]),
            ("uses sunlight to make food for the plant through photosynthesis", "Leaves", ["Roots", "Bark", "Petals"])
        ]
        desc, correct, wrong = parts[idx % len(parts)]
        prompt = f"Which plant part {desc}?"
        pool = [correct] + wrong
        hint = f"The {correct.lower()} perform this function."
    elif mod == 3:
        materials = [
            ("natural material harvested from organic resources", "Timber wood", ["Synthetic plastic", "Nylon rope", "Polyester fabric"]),
            ("human-made synthetic material made in a factory", "Plastic container", ["Granite stone", "Cotton wool", "Clay soil"])
        ]
        desc, correct, wrong = materials[idx % len(materials)]
        prompt = f"Which item is a {desc}?"
        pool = [correct] + wrong
        hint = f"{correct} is an example."
    else:
        states = [
            ("solid with a definite shape and volume", "An ice cube", ["Liquid water", "Water vapor", "Helium gas"]),
            ("gas that expands to fill its container", "Steam vapor", ["A wooden block", "Liquid milk", "A metal coin"])
        ]
        desc, correct, wrong = states[idx % len(states)]
        prompt = f"Which specimen is a {desc}?"
        pool = [correct] + wrong
        hint = f"{correct} is an example of this state of matter."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_s_pp(subskill: str, idx: int):
    """Physical Properties (S-PP: 4 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 4

    if mod == 0:
        prompt = "When liquid water is placed into a cold freezer, what state of matter does it change into?"
        correct = "Solid (Ice)"
        pool = ["Solid (Ice)", "Gas (Steam)", "Plasma", "Liquid"]
        hint = "Water freezes at 0°C into solid ice."
        return prompt, correct, pool, hint, "VERBAL", None
    elif mod == 1:
        prompt = "When liquid water is heated on a stove until it boils, what does the liquid change into?"
        correct = "Gas (Water Vapor)"
        pool = ["Gas (Water Vapor)", "Solid (Ice)", "Liquid (Mercury)", "Plasma"]
        hint = "Boiling causes water to evaporate into water vapor gas."
        return prompt, correct, pool, hint, "VERBAL", None
    elif mod == 2:
        prompt = "When warm water vapor in the air touches a cold glass of lemonade, water droplets form on the outside. What is this process called?"
        correct = "Condensation"
        pool = ["Condensation", "Evaporation", "Freezing", "Melting"]
        hint = "Condensation happens when a gas cools down into a liquid."
        return prompt, correct, pool, hint, "VERBAL", None
    else:
        prompt = "Look at the horseshoe magnet shown above. Which object will be strongly ATTRACTED to this magnet?"
        correct = "An iron nail"
        pool = ["An iron nail", "A wooden stick", "A plastic ruler", "A rubber eraser"]
        hint = "Magnets attract ferromagnetic metals like iron and steel."
        return prompt, correct, pool, hint, "VISUAL", build_tool_svg("magnet")


def gen_s_ee(subskill: str, idx: int):
    """Earth & Environment (S-EE: 5 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 5

    if mod == 0:
        prompt = "Look at the animal shown above. Which desert animal stores fat in its humps to survive long journeys without food?"
        correct = "Camel"
        pool = ["Camel", "Polar Bear", "Penguin", "Chimpanzee"]
        hint = "Camels store fat in their humps for desert survival."
        return prompt, correct, pool, hint, "VISUAL", build_creature_or_entity_svg("camel")
    elif mod == 1:
        prompt = "Which animal has thick insulating blubber and dense feathers to thrive in freezing polar waters?"
        correct = "Penguin"
        pool = ["Penguin", "Camel", "Desert Lizard", "Giraffe"]
        hint = "Penguins are adapted for cold arctic/antarctic marine habitats."
        return prompt, correct, pool, hint, "VERBAL", None
    elif mod == 2:
        prompt = "In a tropical rainforest, which amphibian has suction-cup toe pads and bright skin for tree climbing?"
        correct = "Tree Frog"
        pool = ["Tree Frog", "Camel", "Polar Bear", "Wolf"]
        hint = "Tree frogs have specialized toe pads for climbing wet leaves."
        return prompt, correct, pool, hint, "VERBAL", None
    elif mod == 3:
        prompt = "Which ocean mammal must swim to the surface to breathe air through a blowhole on top of its head?"
        correct = "Dolphin"
        pool = ["Dolphin", "Clownfish", "Jellyfish", "Sea Anemone"]
        hint = "Dolphins are marine mammals that breathe air."
        return prompt, correct, pool, hint, "VERBAL", None
    else:
        prompt = "In autumn, how do deciduous trees adapt as the weather cools and days get shorter?"
        correct = "They shed their leaves"
        pool = ["They shed their leaves", "They grow bright flowers", "They double their height", "They produce new fruit"]
        hint = "Deciduous trees lose their leaves to conserve water in winter."
        return prompt, correct, pool, hint, "VERBAL", None


def gen_s_mo(subskill: str, idx: int):
    """Measurement & Observation in Science (S-MO: 4 subskills) - ALL VISUAL (Grade 1 / Level 1)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 4

    if mod == 0:
        prompt = "Look at the tool shown above. Which tool measures whether something is hot or cold?"
        correct = "Thermometer"
        pool = ["Thermometer", "Balance scale", "Measuring tape", "Clock"]
        hint = "A thermometer measures temperature."
        return prompt, correct, pool, hint, "VISUAL", build_tool_svg("thermometer")
    elif mod == 1:
        prompt = "Look at the tool shown above. Which tool is used to weigh objects?"
        correct = "Balance scale"
        pool = ["Balance scale", "Thermometer", "Ruler", "Telescope"]
        hint = "A balance scale weighs objects."
        return prompt, correct, pool, hint, "VISUAL", build_tool_svg("scale")
    elif mod == 2:
        prompt = "Look at the tool shown above. Which tool measures how long a pencil is?"
        correct = "Ruler"
        pool = ["Ruler", "Cup", "Thermometer", "Clock"]
        hint = "A ruler measures length."
        return prompt, correct, pool, hint, "VISUAL", build_tool_svg("ruler")
    else:
        prompt = "Look at the tool shown above. Which tool helps you see tiny things up close?"
        correct = "Microscope"
        pool = ["Microscope", "Telescope", "Sunglasses", "Camera"]
        hint = "A microscope makes tiny things look big."
        return prompt, correct, pool, hint, "VISUAL", build_tool_svg("microscope")


def gen_s_in(subskill: str, idx: int):
    """Scientific Inquiry & Experimentation (S-IN: 6 subskills) - ALL VERBAL (Grade 1 / Level 1)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6

    if mod == 0:
        prompt = "If you drop a light wooden cork into a bowl of water, what happens?"
        correct = "It floats on top"
        pool = ["It floats on top", "It sinks to the bottom", "It dissolves away", "It turns to stone"]
        hint = "Light wood floats on water."
    elif mod == 1:
        prompt = "What happens to an ice cube left outside in the warm sunshine?"
        correct = "It melts into water"
        pool = ["It melts into water", "It freezes into stone", "It grows bigger", "It catches fire"]
        hint = "Warm sunlight melts cold ice into water."
    elif mod == 2:
        prompt = "What color do you get when you mix red paint and yellow paint together?"
        correct = "Orange"
        pool = ["Orange", "Purple", "Green", "Black"]
        hint = "Red and yellow make orange."
    elif mod == 3:
        prompt = "What will a sunflower seed grow into if you plant it and water it?"
        correct = "A tall sunflower"
        pool = ["A tall sunflower", "An apple tree", "A stone", "A pumpkin"]
        hint = "Seeds grow into the plant they came from."
    elif mod == 4:
        prompt = "Which of your five senses tells you if an apple tastes sweet?"
        correct = "Taste"
        pool = ["Taste", "Hearing", "Sight", "Touch"]
        hint = "Your tongue gives you the sense of taste."
    else:
        prompt = "What should you do to stay safe when doing a science activity?"
        correct = "Listen to your teacher"
        pool = ["Listen to your teacher", "Run around the room", "Taste unknown things", "Touch hot objects"]
        hint = "Always follow teacher instructions for safety."

    return prompt, correct, pool, hint, "VERBAL", None


# ----------------------------------------------------------------------
# LOGICAL REASONING DIVERSIFICATION ENGINES (6 Strands)
# ----------------------------------------------------------------------

def gen_l_pc(subskill: str, idx: int):
    """Patterning & Classification (L-PC: 4 subskills) - ALL VERBAL"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 4

    if mod == 0:
        prompt = "Which of these vehicles does NOT belong with airplanes, helicopters, and gliders?"
        correct = "Submarine"
        pool = ["Submarine", "Airplane", "Helicopter", "Glider"]
        hint = "A submarine travels underwater, while the others fly in the air."
    elif mod == 1:
        prompt = "Look at this group of food: Apple, Banana, Orange, and Carrot. Which item is the odd one out?"
        correct = "Carrot"
        pool = ["Carrot", "Apple", "Banana", "Orange"]
        hint = "Carrot is a root vegetable, whereas the others are fruits."
    elif mod == 2:
        prompt = "Look at these four shapes: Triangle, Square, Hexagon, and Circle. Which shape does NOT belong with the polygons?"
        correct = "Circle"
        pool = ["Circle", "Triangle", "Square", "Hexagon"]
        hint = "A circle has a curved boundary, while polygons have straight sides."
    else:
        prompt = "Examine these tools: Iron hammer, Steel wrench, Copper pliers, and Wooden chair. Which item does NOT belong by material?"
        correct = "Wooden chair"
        pool = ["Wooden chair", "Iron hammer", "Steel wrench", "Copper pliers"]
        hint = "The chair is made of wood, while the tools are made of metal."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_l_ar(subskill: str, idx: int):
    """Analogical Reasoning (L-AR: 2 subskills) - ALL VERBAL"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 2

    if mod == 0:
        analogies = [
            ("Bird is to Sky as Fish is to...", "Water", ["Ground", "Space", "Tree"]),
            ("Car is to Road as Train is to...", "Tracks", ["Air", "Water", "Space"])
        ]
        prompt_str, correct, wrong = analogies[idx % len(analogies)]
        prompt = f"Complete the analogy: {prompt_str}"
        pool = [correct] + wrong
        hint = "Think about where each animal or vehicle moves."
    else:
        opp_analogies = [
            ("Fire is to Hot as Ice is to...", "Cold", ["Warm", "Bright", "Dark"]),
            ("Sun is to Day as Moon is to...", "Night", ["Morning", "Afternoon", "Noon"])
        ]
        prompt_str, correct, wrong = opp_analogies[idx % len(opp_analogies)]
        prompt = f"Complete the attribute analogy: {prompt_str}"
        pool = [correct] + wrong
        hint = "Identify the direct sensory property."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_l_sr(subskill: str, idx: int):
    """Spatial Reasoning (L-SR: 5 subskills) - ALL VERBAL"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 5

    if mod == 0:
        shapes = [("triangle", "3", ["4", "5", "6"]), ("square", "4", ["3", "5", "6"]), ("pentagon", "5", ["3", "4", "6"]), ("hexagon", "6", ["4", "5", "8"])]
        shape, correct, wrong = shapes[idx % len(shapes)]
        prompt = f"If you trace along the outer edge of a {shape}, how many straight sides do you trace?"
        pool = [correct] + wrong
        hint = f"A {shape} has exactly {correct} sides."
    elif mod == 1:
        prompt = "If an arrow pointing straight UP is rotated 90 degrees CLOCKWISE, which direction does it point now?"
        correct = "Pointing RIGHT"
        pool = ["Pointing RIGHT", "Pointing DOWN", "Pointing LEFT", "Pointing UP"]
        hint = "Clockwise turns like the hands of a clock."
    elif mod == 2:
        prompt = "A flat cardboard pattern of 6 connected squares in a cross shape is folded along its edges. What 3D solid is formed?"
        correct = "A Cube"
        pool = ["A Cube", "A Pyramid", "A Cylinder", "A Sphere"]
        hint = "A cross pattern of 6 squares folds into a closed 6-sided cube."
    elif mod == 3:
        prompt = "A cylinder stands upright on a table. If you look straight down at it from directly above (bird's-eye view), what 2D shape do you see?"
        correct = "A Circle"
        pool = ["A Circle", "A Rectangle", "A Triangle", "A Diamond"]
        hint = "Looking directly down onto an upright cylinder reveals its circular top."
    else:
        prompt = "A lowercase letter 'b' is held in front of a flat mirror. Which letter does its reflection most closely resemble?"
        correct = "Letter 'd'"
        pool = ["Letter 'd'", "Letter 'p'", "Letter 'q'", "Letter 'b'"]
        hint = "A vertical mirror reverses left and right: 'b' reflects into 'd'."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_l_rc(subskill: str, idx: int):
    """Relational & Comparative Logic (L-RC: 5 subskills) - ALL VERBAL"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 5

    if mod == 0:
        chains = [
            ("Elephant > Horse > Rabbit", "Rabbit", "SMALLEST", ["Elephant", "Horse", "They are equal"]),
            ("Sun > Earth > Moon", "Sun", "LARGEST", ["Earth", "Moon", "They are equal"])
        ]
        chain, correct, q, wrong = chains[idx % len(chains)]
        prompt = f"Look at the size chain: {chain}. Which one is the {q}?"
        pool = [correct] + wrong
        hint = f"{correct} is the {q.lower()}."
    elif mod == 1:
        w_chains = [
            ("A boulder is heavier than an anvil. An anvil is heavier than a hammer.", "The boulder", "HEAVIEST", ["The anvil", "The hammer", "All weigh the same"]),
            ("A coin is lighter than a textbook. A textbook is lighter than a backpack.", "The coin", "LIGHTEST", ["The textbook", "The backpack", "All weigh the same"])
        ]
        premise, correct, q, wrong = w_chains[idx % len(w_chains)]
        prompt = f"Comparative weight: {premise} Which item is the {q}?"
        pool = [correct] + wrong
        hint = f"{correct} is the {q.lower()}."
    elif mod == 2:
        heights = [
            ("Tower A is taller than Tower B. Tower B is taller than Tower C.", "Tower A", "TALLEST", ["Tower B", "Tower C", "All are equal"]),
            ("The oak is taller than the birch. The birch is taller than the shrub.", "The shrub", "SHORTEST", ["The oak", "The birch", "All are equal"])
        ]
        premise, correct, q, wrong = heights[idx % len(heights)]
        prompt = f"Height ranking: {premise} Which one is the {q}?"
        pool = [correct] + wrong
        hint = f"{correct} is the {q.lower()}."
    elif mod == 3:
        speeds = [
            ("A cheetah runs faster than a horse. A horse runs faster than a turtle.", "The cheetah", "FASTEST", ["The horse", "The turtle", "All run at the same speed"]),
            ("An airplane travels faster than a car. A car travels faster than a bicycle.", "The bicycle", "SLOWEST", ["The airplane", "The car", "All travel at the same speed"])
        ]
        premise, correct, q, wrong = speeds[idx % len(speeds)]
        prompt = f"Speed ranking: {premise} Which traveler is the {q}?"
        pool = [correct] + wrong
        hint = f"{correct} is the {q.lower()}."
    else:
        times = [
            ("Breakfast happens before lunch. Lunch happens before dinner.", "Breakfast", "FIRST", ["Lunch", "Dinner", "All happen at noon"]),
            ("Morning comes before afternoon. Afternoon comes before night.", "Night", "LAST", ["Morning", "Afternoon", "All happen at noon"])
        ]
        premise, correct, q, wrong = times[idx % len(times)]
        prompt = f"Timeline order: {premise} Which comes {q}?"
        pool = [correct] + wrong
        hint = f"{correct} comes {q.lower()}."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_l_co(subskill: str, idx: int):
    """Conditional Logic (L-CO: 4 subskills) - ALL VERBAL"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 4

    if mod == 0:
        conditions = [
            ("If it rains, the sidewalk gets wet. It is raining.", "The sidewalk gets wet", ["The sidewalk stays completely dry", "It begins to snow", "The sun is shining"]),
            ("If you flip the wall switch on, the ceiling lamp turns on. You flip the switch on.", "The ceiling lamp turns on", ["The door unlocks", "The room gets pitch black", "Music plays"])
        ]
        cond, correct, wrong = conditions[idx % len(conditions)]
        prompt = f"Logic rule: '{cond}' What must happen next?"
        pool = [correct] + wrong
        hint = f"By direct conditional logic: {correct.lower()}."
    elif mod == 1:
        negatives = [
            ("The lock opens ONLY IF the bronze key is used. The bronze key was NOT used.", "The lock stays closed", ["The lock swings open", "The door vanishes", "The key turns to gold"]),
            ("The flashlight works ONLY WHEN it has batteries inside. It has NO batteries inside.", "The flashlight does not work", ["The flashlight shines brightly", "The flashlight plays music", "The batteries appear"])
        ]
        premise, correct, wrong = negatives[idx % len(negatives)]
        prompt = f"Deductive rule: '{premise}' What conclusion is guaranteed?"
        pool = [correct] + wrong
        hint = "Because the required condition was not met, the outcome cannot occur."
    elif mod == 2:
        disj = [
            ("The library book is in EITHER the red backpack OR the blue backpack. The red backpack is completely empty.", "The book is in the blue backpack", ["The book is in the red backpack", "The book never existed", "Both backpacks are full"]),
            ("The school bus driver is EITHER on Bus 1 OR on Bus 2. She is NOT on Bus 1.", "She is on Bus 2", ["She is on Bus 1", "The bus has no driver", "She is on an airplane"])
        ]
        premise, correct, wrong = disj[idx % len(disj)]
        prompt = f"Either/Or reasoning: '{premise}' What must be true?"
        pool = [correct] + wrong
        hint = "When one option is eliminated, the other must be true."
    else:
        chains = [
            ("Rule 1: If the bell rings, the recess door unlocks. Rule 2: If the door unlocks, the children go outside. The bell rings.", "The children go outside", ["The door stays locked", "The children go to sleep", "Nothing happens"]),
            ("Rule 1: If the sun rises, the morning birds begin singing. Rule 2: If the birds sing, the rooster crows. The sun rises.", "The rooster crows", ["The sun sets", "It becomes nighttime", "The birds stay quiet"])
        ]
        premise, correct, wrong = chains[idx % len(chains)]
        prompt = f"Two-step deduction: '{premise}' What is the final outcome?"
        pool = [correct] + wrong
        hint = f"Chaining the rules shows: {correct.lower()}."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_l_ce(subskill: str, idx: int):
    """Cause & Effect Reasoning (L-CE: 4 subskills) - ALL VERBAL (Grade 1 / Level 1)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 4

    if mod == 0:
        prompt = "Why are there wet footprints on the floor?"
        correct = "Someone walked in from the rain"
        pool = ["Someone walked in from the rain", "Someone baked bread", "The room was dusty", "A lamp turned on"]
        hint = "Rain makes feet wet and muddy."
    elif mod == 1:
        prompt = "You see dark smoke rising into the air. What is the cause?"
        correct = "A campfire or fire"
        pool = ["A campfire or fire", "A rainbow", "A snowman melting", "A cold breeze"]
        hint = "Fire produces smoke."
    elif mod == 2:
        prompt = "Why did the ice cube melt into a puddle of water?"
        correct = "It was warm in the room"
        pool = ["It was warm in the room", "It got freezing cold", "It was nighttime", "It was kept in the freezer"]
        hint = "Warmth causes ice to melt."
    else:
        prompt = "Dark storm clouds fill the sky and lightning flashes. What will happen next?"
        correct = "It will rain"
        pool = ["It will rain", "The sun will be blazing hot", "Stars will appear", "Snow will melt"]
        hint = "Dark storm clouds bring rain."

    return prompt, correct, pool, hint, "VERBAL", None


# ----------------------------------------------------------------------
# WORLD KNOWLEDGE DIVERSIFICATION ENGINES (3 Strands)
# ----------------------------------------------------------------------

def gen_w_ka(subskill: str, idx: int):
    """Cultural Awareness & Traditions (W-KA: 8 subskills) - ALL VERBAL"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 8

    if mod == 0:
        culture = [("Sushi wrapped in crisp nori seaweed", "Japan", ["Italy", "Mexico", "India"]),
                   ("Pizza baked with tomato sauce and mozzarella cheese", "Italy", ["Japan", "Mexico", "India"]),
                   ("Tacos filled with beans, salsa, and tortillas", "Mexico", ["Japan", "Italy", "India"]),
                   ("Fragrant basmati rice served with curry and naan", "India", ["Japan", "Italy", "Mexico"])]
        food, correct, wrong = culture[idx % len(culture)]
        prompt = f"Which country did the traditional dish '{food}' originate from?"
        pool = [correct] + wrong
        hint = f"{food} is from {correct}."
    elif mod == 1:
        fests = [
            ("Diwali, the radiant Festival of Lights celebrated with clay lamps called diyas", "India", ["Brazil", "Norway", "Canada"]),
            ("Carnival, celebrated with vibrant samba music and colorful parades", "Brazil", ["Japan", "Egypt", "Iceland"]),
            ("Lunar New Year, celebrated with festive dragon dances and red envelopes", "China and East Asia", ["France", "Chile", "Australia"])
        ]
        fest, correct, wrong = fests[idx % len(fests)]
        prompt = f"In which country or region did the cultural celebration of {fest} originate?"
        pool = [correct] + wrong
        hint = f"This celebration originated in {correct}."
    elif mod == 2:
        instrs = [
            ("the sitar, a stringed musical instrument with resonant strings", "India", ["Scotland", "Australia", "Peru"]),
            ("the bagpipes, a wind instrument with an airtight bag and drone pipes", "Scotland", ["India", "Egypt", "Brazil"]),
            ("the didgeridoo, a long wooden wind instrument", "Australia", ["Norway", "Japan", "Mexico"])
        ]
        inst, correct, wrong = instrs[idx % len(instrs)]
        prompt = f"With which country or culture is {inst} traditionally associated?"
        pool = [correct] + wrong
        hint = f"This instrument is from {correct}."
    elif mod == 3:
        attire = [
            ("the Kimono, a graceful wrapped robe tied with a sash called an obi", "Japan", ["Scotland", "Mexico", "Egypt"]),
            ("the Kilt, a traditional pleated woolen knee-length garment", "Scotland", ["Japan", "India", "Nigeria"]),
            ("the Sari, an elegant drape of colorful woven fabric", "India", ["Norway", "Mexico", "Australia"])
        ]
        garment, correct, wrong = attire[idx % len(attire)]
        prompt = f"In which country or culture is {garment} traditionally worn?"
        pool = [correct] + wrong
        hint = f"This traditional clothing is from {correct}."
    elif mod == 4:
        greetings = [
            ("Bonjour", "French", ["Spanish", "German", "Japanese"]),
            ("Konnichiwa", "Japanese", ["French", "Italian", "Arabic"]),
            ("Namaste", "Hindi", ["Russian", "Portuguese", "Greek"]),
            ("Hola", "Spanish", ["German", "Japanese", "Swahili"])
        ]
        word, correct, wrong = greetings[idx % len(greetings)]
        prompt = f"A traveler greets you warmly by saying '{word}'! Which language are they speaking?"
        pool = [correct] + wrong
        hint = f"'{word}' is a greeting in {correct}."
    elif mod == 5:
        myths = [
            ("Anansi the clever spider who outsmarts larger animals", "West African folktales", ["Norse mythology", "Greek legends", "Inuit folklore"]),
            ("King Arthur and the Knights of the Round Table", "British legends", ["Chinese folklore", "Egyptian legends", "Aztec myths"]),
            ("The Monkey King (Sun Wukong) with magical shapeshifting abilities", "Chinese folklore", ["Celtic myths", "Mayan legends", "Roman myths"])
        ]
        legend, correct, wrong = myths[idx % len(myths)]
        prompt = f"Stories about {legend} originate from which storytelling tradition?"
        pool = [correct] + wrong
        hint = f"This famous story comes from {correct}."
    elif mod == 6:
        symbols = [
            ("The Maple Leaf is a prominent national symbol on the flag of:", "Canada", ["Australia", "Japan", "Brazil"]),
            ("The Kangaroo is an official national animal emblem of:", "Australia", ["Canada", "India", "Germany"]),
            ("The Bald Eagle is a national bird and symbol of:", "United States", ["France", "Mexico", "China"])
        ]
        q_sym, correct, wrong = symbols[idx % len(symbols)]
        prompt = f"National symbols: {q_sym}"
        pool = [correct] + wrong
        hint = f"This symbol represents {correct}."
    else:
        arch = [
            ("an Igloo built from blocks of packed snow for arctic shelter", "Inuit people of the Arctic", ["Bedouin nomads of the desert", "Gauchos of Argentina", "Maori of New Zealand"]),
            ("a Yurt (Ger), a circular felt-covered tent used on the steppes", "Nomadic peoples of Central Asia (Mongolia)", ["Inuit of the Arctic", "Polynesians of the Pacific", "Celts of Europe"]),
            ("a tiered Pagoda built as a sacred tower", "East Asia (China and Japan)", ["Ancient Rome", "Scandinavia", "Ancient Egypt"])
        ]
        struct, correct, wrong = arch[idx % len(arch)]
        prompt = f"Traditional architecture: Which culture or region historically developed {struct}?"
        pool = [correct] + wrong
        hint = f"This structure was created by {correct}."

    return prompt, correct, pool, hint, "VERBAL", None


def gen_w_ko(subskill: str, idx: int):
    """Community Helpers & Occupations (W-KO: 6 subskills) - ALL VERBAL (Grade 1 / Level 1)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6

    if mod == 0:
        helpers = [
            ("Who fixes leaky water pipes in a house?", "A Plumber", ["A Plumber", "A Baker", "A Dentist", "A Pilot"]),
            ("Who safely fixes broken lights and electrical wires?", "An Electrician", ["An Electrician", "A Plumber", "A Carpenter", "A Painter"])
        ]
        prompt, correct, pool = helpers[idx % len(helpers)]
        return prompt, correct, pool, f"{correct} helps fix this problem.", "VERBAL", None

    elif mod == 1:
        health = [
            ("Who checks and cleans your teeth to keep them healthy?", "A Dentist", ["A Dentist", "A Firefighter", "A Baker", "A Farmer"]),
            ("Who takes care of sick puppies and kittens?", "A Veterinarian", ["A Veterinarian", "A Chef", "A Pilot", "A Carpenter"]),
            ("Who helps you feel better when you are sick?", "A Doctor", ["A Doctor", "A Pilot", "A Baker", "A Sailor"])
        ]
        prompt, correct, pool = health[idx % len(health)]
        return prompt, correct, pool, f"{correct} helps take care of health.", "VERBAL", None

    elif mod == 2:
        safety = [
            ("Who puts out fires and keeps people safe in emergencies?", "Firefighters", ["Firefighters", "Librarians", "Bakers", "Mail carriers"]),
            ("Who helps direct street traffic and keeps neighborhoods safe?", "Police Officers", ["Police Officers", "Dentists", "Plumbers", "Chefs"])
        ]
        prompt, correct, pool = safety[idx % len(safety)]
        return prompt, correct, pool, f"{correct} keep our community safe.", "VERBAL", None

    elif mod == 3:
        edu = [
            ("Who helps you find storybooks in the library?", "A Librarian", ["A Librarian", "A Firefighter", "A Mechanic", "A Plumber"]),
            ("Who teaches children reading and math in school?", "A Teacher", ["A Teacher", "A Pilot", "A Chef", "A Dentist"])
        ]
        prompt, correct, pool = edu[idx % len(edu)]
        return prompt, correct, pool, f"{correct} helps us learn and read.", "VERBAL", None

    elif mod == 4:
        transit = [
            ("Who flies airplanes high in the sky?", "A Pilot", ["A Pilot", "A Train Conductor", "A Farmer", "A Doctor"]),
            ("Who safely drives the big yellow school bus?", "A Bus Driver", ["A Bus Driver", "A Pilot", "A Sailor", "A Baker"])
        ]
        prompt, correct, pool = transit[idx % len(transit)]
        return prompt, correct, pool, f"{correct} drives this vehicle.", "VERBAL", None

    else:
        agri = [
            ("Who grows vegetables, fruits, and grain on a farm?", "A Farmer", ["A Farmer", "A Carpenter", "A Plumber", "A Doctor"]),
            ("Who bakes fresh loaves of bread and tasty cookies?", "A Baker", ["A Baker", "A Doctor", "A Pilot", "A Mechanic"])
        ]
        prompt, correct, pool = agri[idx % len(agri)]
        return prompt, correct, pool, f"{correct} makes food for the community.", "VERBAL", None

    return prompt, correct, pool, hint, "VERBAL", None


def gen_w_kp(subskill: str, idx: int):
    """Geographic Places & Features (W-KP: 6 subskills)"""
    ss_id = int(subskill.split("-")[-1]) if "-" in subskill else 1
    mod = (ss_id - 1) % 6

    if mod == 0:
        geo = [("the ancient Pyramids of Giza", "Africa", ["Asia", "Europe", "South America"]),
               ("the Eiffel Tower in Paris", "Europe", ["Asia", "Africa", "South America"]),
               ("the Great Wall stretching across mountains", "Asia", ["Europe", "Africa", "South America"]),
               ("the ancient citadel of Machu Picchu", "South America", ["Europe", "Asia", "Africa"])]
        landmark, correct, wrong = geo[idx % len(geo)]
        prompt = f"Look at the landmark or site described: {landmark}. On which continent is it located?"
        pool = [correct] + wrong
        hint = f"{landmark} is located in {correct}."
        svg = build_landmark_svg(landmark)
        return prompt, correct, pool, hint, "VISUAL", svg

    elif mod == 1:
        oceans = [
            ("Which is the largest and deepest ocean on planet Earth?", "Pacific Ocean", ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"]),
            ("Which freezing cold ocean surrounds the North Pole?", "Arctic Ocean", ["Indian Ocean", "Atlantic Ocean", "Pacific Ocean"])
        ]
        q_str, correct, wrong = oceans[idx % len(oceans)]
        prompt = q_str
        pool = [correct] + wrong
        hint = f"The correct answer is the {correct}."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 2:
        mountains = [
            ("The Himalayas, home to Mount Everest (the highest mountain on Earth), are located on which continent?", "Asia", ["Europe", "North America", "Africa"]),
            ("The Andes, the longest continental mountain range in the world, are located in:", "South America", ["Africa", "Asia", "Europe"])
        ]
        q_str, correct, wrong = mountains[idx % len(mountains)]
        prompt = q_str
        pool = [correct] + wrong
        hint = f"This mountain system is located in {correct}."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 3:
        rivers = [
            ("The Nile River, historically recognized as one of the longest rivers on Earth, flows northward through:", "Africa", ["South America", "Europe", "Asia"]),
            ("The Amazon River, which carries the largest volume of water of any river, flows through:", "South America", ["Africa", "North America", "Europe"])
        ]
        q_str, correct, wrong = rivers[idx % len(rivers)]
        prompt = q_str
        pool = [correct] + wrong
        hint = f"This river flows through {correct}."
        return prompt, correct, pool, hint, "VERBAL", None

    elif mod == 4:
        coords = [
            ("What is the imaginary line circling the middle of Earth halfway between the North and South Poles called?", "The Equator", ["The Prime Meridian", "The Tropic of Cancer", "The Arctic Circle"]),
            ("What are the northernmost and southernmost points on Earth's rotational axis called?", "The North and South Poles", ["The Equators", "The Oceanic Ridges", "The Meridians"])
        ]
        q_str, correct, wrong = coords[idx % len(coords)]
        prompt = q_str
        pool = [correct] + wrong
        hint = f"The answer is {correct}."
        return prompt, correct, pool, hint, "VERBAL", None

    else:
        deserts = [
            ("The Sahara, the largest hot desert in the world, covers large parts of northern:", "Africa", ["Asia", "Australia", "Europe"]),
            ("The cold Gobi Desert stretches across northern China and southern:", "Mongolia (Asia)", ["Egypt (Africa)", "Chile (South America)", "Spain (Europe)"])
        ]
        q_str, correct, wrong = deserts[idx % len(deserts)]
        prompt = q_str
        pool = [correct] + wrong
        hint = f"This desert is in {correct}."
        return prompt, correct, pool, hint, "VERBAL", None


def generate_item_data(domain: str, subskill: str, idx: int):
    prefix = subskill[:4]
    
    # Mathematics
    if prefix == "M-NQ": return gen_m_nq(subskill, idx)
    elif prefix == "M-OP": return gen_m_op(subskill, idx)
    elif prefix == "M-GS": return gen_m_gs(subskill, idx)
    elif prefix == "M-ME": return gen_m_me(subskill, idx)
    elif prefix == "M-PA": return gen_m_pa(subskill, idx)
    elif prefix == "M-FR": return gen_m_fr(subskill, idx)
    elif prefix == "M-DU": return gen_m_du(subskill, idx)
    elif prefix == "M-PS": return gen_m_ps(subskill, idx)
    
    # English
    elif prefix == "E-PD": return gen_e_pd(subskill, idx)
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
    print("REGENERATING QUESTION BANK: PEDAGOGICAL COHERENCE & ACCURATE VISUALS")
    print("=================================================================")

    total_updated = 0
    total_svgs_written = 0
    domains = ["MATHEMATICS", "ENGLISH_LANGUAGE", "LOGICAL_REASONING", "SCIENCE_EVS", "WORLD_KNOWLEDGE"]

    for dom in domains:
        dom_path = ITEMS_DIR / dom
        if not dom_path.exists():
            continue

        subskill_dirs = [d for d in dom_path.iterdir() if d.is_dir()]
        print(f"\nProcessing domain [{dom}] with {len(subskill_dirs)} subskills...")

        for sdir in sorted(subskill_dirs):
            subcode = sdir.name
            files = sorted(sdir.glob("*.json"))

            for idx, fpath in enumerate(files):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        item = json.load(f)

                    prompt, correct, pool, hint, rep_type, svg_markup = generate_item_data(dom, subcode, idx)

                    # Update display text and hint
                    item["prompt_structure"]["display_text"] = prompt
                    if "scaffolding_protocol" in item and "level_1_reflection_prompt" in item["scaffolding_protocol"]:
                        item["scaffolding_protocol"]["level_1_reflection_prompt"]["prompt"] = hint

                    # Handle visual representation and SVGs
                    item["representation_type"] = rep_type
                    item_id = item.get("item_id", fpath.stem)

                    if rep_type == "VISUAL" and svg_markup:
                        rel_svg_uri = f"assets/svg/{item_id.lower()}_visual.svg"
                        item["prompt_structure"]["visual_assets"] = [
                            {
                                "asset_id": f"{item_id}_vis_1",
                                "asset_type": "DYNAMIC_SVG",
                                "uri": rel_svg_uri
                            }
                        ]
                        # Write SVG to both public and dist directories
                        for dest_dir in [PUBLIC_SVG_DIR, DIST_SVG_DIR]:
                            svg_dest = dest_dir / f"{item_id.lower()}_visual.svg"
                            with open(svg_dest, "w", encoding="utf-8") as s_fp:
                                s_fp.write(svg_markup)
                        total_svgs_written += 1
                    else:
                        # Purely verbal/text question: NO random image!
                        item["prompt_structure"]["visual_assets"] = []

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

    print(f"\n[DONE] Successfully updated {total_updated} question files!")
    print(f"Total authentic question SVGs generated & written: {total_svgs_written}")


if __name__ == "__main__":
    main()
