import os
import json
import glob
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ITEMS_DIR = BASE_DIR / "question_bank" / "items" / "MATHEMATICS"

MATH_TEMPLATES = {
    "M-NQ": [
        {"prompt": "How many yellow ducklings are swimming in the pond?", "correct": "5", "options": ["3", "5", "7", "2"], "hint": "Count the cheerful yellow ducklings: 1, 2, 3, 4, 5!"},
        {"prompt": "Count the juicy red strawberries on the plate.", "correct": "4", "options": ["2", "4", "6", "1"], "hint": "Touch each sweet strawberry: 1, 2, 3, 4."},
        {"prompt": "How many busy honeybees are flying near the hive?", "correct": "3", "options": ["3", "5", "2", "6"], "hint": "Count the buzzing little bees: 1, 2, 3!"},
        {"prompt": "Count the golden acorns collected by the squirrel.", "correct": "6", "options": ["4", "6", "8", "3"], "hint": "Count each smooth acorn: 1, 2, 3, 4, 5, 6."},
        {"prompt": "How many colorful balloons are floating up high?", "correct": "7", "options": ["5", "7", "9", "4"], "hint": "Look up and count: 1, 2, 3, 4, 5, 6, 7 balloons!"},
        {"prompt": "Count the glowing starfish resting on the ocean floor.", "correct": "3", "options": ["1", "3", "5", "2"], "hint": "Count each five-pointed starfish: 1, 2, 3."},
        {"prompt": "How many fluttering butterflies are on the flowers?", "correct": "4", "options": ["2", "4", "5", "1"], "hint": "Count the gentle wings: 1, 2, 3, 4 butterflies."},
        {"prompt": "Count the warm cookies fresh out of the bakery oven.", "correct": "8", "options": ["6", "8", "10", "5"], "hint": "Count each yummy cookie: 1 through 8."},
        {"prompt": "How many shiny diamonds are inside the treasure chest?", "correct": "5", "options": ["3", "5", "6", "2"], "hint": "Count the sparkling blue diamonds: 1, 2, 3, 4, 5."},
        {"prompt": "Count the friendly little birds perched on the branch.", "correct": "2", "options": ["1", "2", "3", "4"], "hint": "Count the singing birds: 1, 2!"},
        {"prompt": "How many magical mushrooms are in the fairy circle?", "correct": "6", "options": ["4", "6", "7", "3"], "hint": "Count the red spotted mushrooms: 1, 2, 3, 4, 5, 6."},
        {"prompt": "Count the spiral seashells resting on the warm sand.", "correct": "5", "options": ["4", "5", "6", "3"], "hint": "Count the seaside treasures: 1, 2, 3, 4, 5."}
    ],
    "M-GS": [
        {"prompt": "Which shape has 3 straight sides and 3 corners?", "correct": "Triangle", "options": ["Triangle", "Square", "Circle", "Star"], "hint": "A triangle has 3 sides and 3 pointy corners!"},
        {"prompt": "Which shape is perfectly round like the full silver moon?", "correct": "Circle", "options": ["Circle", "Square", "Triangle", "Rectangle"], "hint": "A circle is curved and round with no sharp corners."},
        {"prompt": "Which shape has 4 equal straight sides like a gift box?", "correct": "Square", "options": ["Square", "Triangle", "Circle", "Oval"], "hint": "A square has four sides that are all the exact same length."},
        {"prompt": "Which shape has 2 long sides and 2 short sides like a doorway?", "correct": "Rectangle", "options": ["Rectangle", "Circle", "Square", "Star"], "hint": "A rectangle looks like a stretched square."},
        {"prompt": "Which shape has 5 bright points like a star in the night sky?", "correct": "Star", "options": ["Star", "Heart", "Circle", "Hexagon"], "hint": "A star has five shining points."},
        {"prompt": "Which smooth shape looks like a robin's speckled egg?", "correct": "Oval", "options": ["Oval", "Square", "Triangle", "Star"], "hint": "An oval is round and elongated like an egg."},
        {"prompt": "Which sweet shape is a symbol of love and kindness?", "correct": "Heart", "options": ["Heart", "Circle", "Square", "Diamond"], "hint": "A heart has two rounded lobes at the top and a point at the bottom."},
        {"prompt": "Which geometric shape has 6 sides like a honeycomb cell?", "correct": "Hexagon", "options": ["Hexagon", "Triangle", "Square", "Circle"], "hint": "Hexa- means six! Count the 6 straight sides."},
        {"prompt": "Which 3D solid rolls smoothly like a ball?", "correct": "Sphere", "options": ["Sphere", "Cube", "Cone", "Pyramid"], "hint": "A sphere is completely round in three dimensions."},
        {"prompt": "Which 3D solid has 6 square faces like a wooden toy block?", "correct": "Cube", "options": ["Cube", "Sphere", "Cylinder", "Cone"], "hint": "A cube has six flat square sides."}
    ],
    "M-ME": [
        {"prompt": "Which gentle animal is the TALLEST in the savannah?", "correct": "Giraffe", "options": ["Giraffe", "Lion", "Zebra", "Gazelle"], "hint": "A giraffe stretches its long neck high into acacia trees!"},
        {"prompt": "Which mighty creature is the HEAVIEST in the jungle?", "correct": "Elephant", "options": ["Elephant", "Monkey", "Parrot", "Fox"], "hint": "An elephant is enormous and weighs thousands of pounds."},
        {"prompt": "Which vehicle is the LONGEST on its tracks?", "correct": "Train", "options": ["Train", "Bicycle", "Car", "Scooter"], "hint": "A train has many cars linked together, making it very long."},
        {"prompt": "Which object is the LIGHTEST to pick up?", "correct": "Feather", "options": ["Feather", "Stone", "Brick", "Anvil"], "hint": "A bird's feather is light as air!"},
        {"prompt": "Which container holds the MOST water?", "correct": "Bathtub", "options": ["Bathtub", "Teacup", "Spoon", "Thimble"], "hint": "A big bathtub holds gallons and gallons of warm water."},
        {"prompt": "Which drawing tool is usually the SHORTEST?", "correct": "Crayon", "options": ["Crayon", "Meter Stick", "Walking Cane", "Flagpole"], "hint": "A crayon fits right into a child's hand."},
        {"prompt": "Which swift animal runs the FASTEST across land?", "correct": "Cheetah", "options": ["Cheetah", "Turtle", "Snail", "Sloth"], "hint": "Cheetahs can sprint as fast as a highway car!"},
        {"prompt": "Which season has the COLDEST freezing weather?", "correct": "Winter", "options": ["Winter", "Summer", "Spring", "Autumn"], "hint": "Snow and ice arrive during freezing winter days."},
        {"prompt": "Which building reaches TALLEST into the clouds?", "correct": "Skyscraper", "options": ["Skyscraper", "Doghouse", "Tent", "Cottage"], "hint": "A skyscraper has dozens of floors soaring toward the sky."},
        {"prompt": "Which tiny spoon holds the LEAST amount of sugar?", "correct": "Teaspoon", "options": ["Teaspoon", "Soup Ladle", "Bucket", "Big Bowl"], "hint": "A teaspoon is small for stirring a warm drink."}
    ],
    "M-PA": [
        {"prompt": "What comes next in the pattern: Red, Blue, Red, Blue...?", "correct": "Red", "options": ["Red", "Blue", "Green", "Yellow"], "hint": "Say the rhythm: Red, Blue, Red, Blue... next is Red!"},
        {"prompt": "What comes next in the pattern: Circle, Square, Circle, Square...?", "correct": "Circle", "options": ["Circle", "Square", "Triangle", "Star"], "hint": "Follow the turns: Circle then Square, Circle then... Circle!"},
        {"prompt": "What comes next: Sun, Moon, Sun, Moon...?", "correct": "Sun", "options": ["Sun", "Moon", "Cloud", "Rain"], "hint": "Day and night: Sun, Moon, Sun, Moon, Sun!"},
        {"prompt": "What comes next: Star, Star, Moon, Star, Star...?", "correct": "Moon", "options": ["Moon", "Star", "Sun", "Comet"], "hint": "Two stars, then a moon! Star, Star, Moon... Star, Star... Moon!"},
        {"prompt": "Complete the fruit pattern: Apple, Banana, Apple, Banana...?", "correct": "Apple", "options": ["Apple", "Banana", "Grape", "Orange"], "hint": "It alternates: Apple, Banana, Apple, Banana, Apple!"},
        {"prompt": "What comes next in size: Big, Small, Big, Small...?", "correct": "Big", "options": ["Big", "Small", "Tiny", "Giant"], "hint": "Big, Small, Big, Small, Big!"},
        {"prompt": "Complete the number sequence: 1, 2, 1, 2...?", "correct": "1", "options": ["1", "2", "3", "0"], "hint": "One, two, one, two, one!"},
        {"prompt": "What comes next in the direction pattern: Up, Down, Up, Down...?", "correct": "Up", "options": ["Up", "Down", "Left", "Right"], "hint": "Reach Up, crouch Down, reach Up, crouch Down... reach Up!"},
        {"prompt": "What shape finishes the sequence: Triangle, Circle, Triangle, Circle...?", "correct": "Triangle", "options": ["Triangle", "Circle", "Square", "Diamond"], "hint": "Triangle, Circle, Triangle, Circle, Triangle!"},
        {"prompt": "What comes next: Day, Night, Day, Night...?", "correct": "Day", "options": ["Day", "Night", "Dusk", "Dawn"], "hint": "Light, Dark, Light, Dark... Day arrives again!"}
    ],
    "M-OP": [
        {"prompt": "You have 2 shiny stars and find 1 more. How many stars in all?", "correct": "3", "options": ["3", "2", "4", "1"], "hint": "Put 2 and 1 together: 2 + 1 = 3 stars!"},
        {"prompt": "There are 3 little frogs on a lily pad, and 1 hops away. How many remain?", "correct": "2", "options": ["2", "3", "1", "4"], "hint": "Start with 3 and take away 1: 3 - 1 = 2 frogs left."},
        {"prompt": "You pick 2 red flowers and 2 yellow flowers. How many flowers together?", "correct": "4", "options": ["4", "3", "5", "2"], "hint": "Two plus two makes four: 2 + 2 = 4!"},
        {"prompt": "A hungry squirrel has 4 acorns and eats 2. How many are left?", "correct": "2", "options": ["2", "3", "1", "4"], "hint": "4 acorns minus 2 eaten acorns leaves 2."},
        {"prompt": "If you have 1 golden key and find 2 more, how many keys do you have?", "correct": "3", "options": ["3", "2", "4", "1"], "hint": "1 + 2 = 3 shiny golden keys!"},
        {"prompt": "3 bluebirds sit on a branch, and 2 more fly over. How many birds now?", "correct": "5", "options": ["5", "4", "6", "3"], "hint": "Count them up: 3 + 2 = 5 cheerful birds!"},
        {"prompt": "You have 5 sweet cookies and share 1 with a puppy. How many cookies are left?", "correct": "4", "options": ["4", "3", "5", "2"], "hint": "5 cookies minus 1 shared equals 4 cookies."},
        {"prompt": "1 shiny coin plus 1 shiny coin equals how many coins?", "correct": "2", "options": ["2", "1", "3", "4"], "hint": "Double it: 1 + 1 = 2 coins!"},
        {"prompt": "4 glowing crystals on a rock, 1 rolls into the stream. How many remain?", "correct": "3", "options": ["3", "4", "2", "1"], "hint": "4 take away 1 is 3 crystals."},
        {"prompt": "You have 3 blue balloons and blow up 3 pink balloons. How many in all?", "correct": "6", "options": ["6", "5", "7", "4"], "hint": "3 + 3 = 6 colorful balloons!"}
    ],
    "M-FR": [
        {"prompt": "If you slice an apple into 2 equal parts, what is each part called?", "correct": "One Half", "options": ["One Half", "One Whole", "One Quarter", "Zero"], "hint": "When split equally between 2, each piece is one half (1/2)."},
        {"prompt": "If 2 friends share 4 cookies equally, how many does each friend get?", "correct": "2", "options": ["2", "1", "3", "4"], "hint": "Share fairly: 2 for you and 2 for me!"},
        {"prompt": "If a round pizza is cut into 4 equal slices, what is each slice called?", "correct": "One Quarter", "options": ["One Quarter", "One Half", "One Whole", "Double"], "hint": "One of four equal pieces is called one quarter (1/4)."},
        {"prompt": "Does sharing equally mean everyone receives the SAME fair amount?", "correct": "Yes, Equal", "options": ["Yes, Equal", "No, Different", "Only One Gets It", "Nobody Knows"], "hint": "Equal sharing means everybody gets the exact same amount!"},
        {"prompt": "If 3 playful kittens share 6 fish treats equally, how many does each get?", "correct": "2", "options": ["2", "3", "1", "4"], "hint": "6 treats shared between 3 kittens gives 2 treats to each kitten."},
        {"prompt": "What fraction describes half of a tasty sandwich?", "correct": "1/2", "options": ["1/2", "1/4", "2/1", "1/1"], "hint": "One part out of two equal parts is written as 1/2."},
        {"prompt": "If you share 2 magic gems equally with a friend, how many do you each keep?", "correct": "1", "options": ["1", "2", "0", "3"], "hint": "One gem for your friend, one gem for you!"},
        {"prompt": "If a pie is still whole and has not been cut, how many whole pies is that?", "correct": "1 Whole", "options": ["1 Whole", "1 Half", "Zero", "2 Whole"], "hint": "An uncut pie is 1 complete whole!"}
    ],
    "M-DU": [
        {"prompt": "Which group of gems has MORE sparkling jewels?", "correct": "Left Group", "options": ["Left Group", "Right Group", "They are Equal"], "hint": "Count carefully! The left group has more sparkling gems."},
        {"prompt": "Which flower basket holds FEWER colorful blossoms?", "correct": "Right Basket", "options": ["Right Basket", "Left Basket", "They are Equal"], "hint": "Fewer means the smaller number of flowers."},
        {"prompt": "Which treasure chest contains MORE gold coins?", "correct": "Left Chest", "options": ["Left Chest", "Right Chest", "They are Equal"], "hint": "The left chest is overflowing with more coins!"},
        {"prompt": "Which bird nest holds FEWER speckled eggs?", "correct": "Right Nest", "options": ["Right Nest", "Left Nest", "They are Equal"], "hint": "Check which nest has less eggs to count."},
        {"prompt": "Which orchard tree has MORE red apples hanging on its branches?", "correct": "Left Tree", "options": ["Left Tree", "Right Tree", "They are Equal"], "hint": "The left tree has a larger harvest of apples."},
        {"prompt": "Which glass jar contains FEWER shiny marbles?", "correct": "Right Jar", "options": ["Right Jar", "Left Jar", "They are Equal"], "hint": "Look through the glass to see which has less marbles."},
        {"prompt": "Which balance scale shows an EQUAL weight on both pans?", "correct": "They are Equal", "options": ["They are Equal", "Left Pan", "Right Pan"], "hint": "When both sides balance evenly, they are equal!"},
        {"prompt": "Which farmer's cart carries MORE orange pumpkins?", "correct": "Left Cart", "options": ["Left Cart", "Right Cart", "They are Equal"], "hint": "The left cart is stacked high with more pumpkins."}
    ],
    "M-PS": [
        {"prompt": "A rabbit hops 2 steps forward, then 2 more steps. What number step is it on?", "correct": "Step 4", "options": ["Step 4", "Step 3", "Step 5", "Step 2"], "hint": "2 steps + 2 steps = Step 4!"},
        {"prompt": "You need 5 crystal keys to open the castle gate and have 3. How many more keys do you need?", "correct": "2", "options": ["2", "1", "3", "4"], "hint": "Count up from 3 to 5: 4, 5... you need 2 more keys!"},
        {"prompt": "There are 4 seats on a magic carpet and 3 fairies sit down. How many empty seats are left?", "correct": "1", "options": ["1", "2", "0", "3"], "hint": "4 total seats minus 3 fairies = 1 empty seat."},
        {"prompt": "A little gardener plants 3 flower seeds today and 3 tomorrow. How many seeds total?", "correct": "6", "options": ["6", "5", "7", "4"], "hint": "3 + 3 = 6 flower seeds planted in the soil."},
        {"prompt": "You have 6 toy cars and park 3 inside the garage. How many cars are parked outside?", "correct": "3", "options": ["3", "2", "4", "1"], "hint": "6 cars minus 3 inside = 3 outside."},
        {"prompt": "If a cute puppy has 4 paws, how many paws do 2 puppies have together?", "correct": "8", "options": ["8", "6", "10", "4"], "hint": "4 paws + 4 paws = 8 paws in all!"},
        {"prompt": "You want to wear a matching pair of boots. How many boots make a pair?", "correct": "2", "options": ["2", "1", "3", "4"], "hint": "A pair always means two: one for each foot!"},
        {"prompt": "A grandfather clock chimes at 3 o'clock. In 1 hour, what time will it chime?", "correct": "4 o'clock", "options": ["4 o'clock", "2 o'clock", "5 o'clock", "12 o'clock"], "hint": "Move the clock hand forward 1 hour: 3 + 1 = 4 o'clock!"}
    ]
}

def get_category_for_subskill(code: str) -> str:
    prefix = code[:4] # e.g. 'M-NQ', 'M-GS', 'M-ME', 'M-PA', 'M-OP', 'M-FR', 'M-DU', 'M-PS'
    if prefix in MATH_TEMPLATES:
        return prefix
    return "M-NQ"

def main():
    print(f"Scanning math items in {ITEMS_DIR}...")
    files = glob.glob(str(ITEMS_DIR / "**" / "*.json"), recursive=True)
    print(f"Found {len(files)} math files to diversify.")

    updated_count = 0
    for idx, fpath in enumerate(files):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                item = json.load(f)

            subskill = item.get("target_subskill_id", "M-NQ-01")
            cat = get_category_for_subskill(subskill)
            template_pool = MATH_TEMPLATES.get(cat, MATH_TEMPLATES["M-NQ"])

            # Use deterministic cycle based on file index so every template is evenly distributed
            template = template_pool[idx % len(template_pool)]

            item["prompt_structure"]["display_text"] = template["prompt"]
            if "scaffolding_protocol" in item and "level_1_reflection_prompt" in item["scaffolding_protocol"]:
                item["scaffolding_protocol"]["level_1_reflection_prompt"]["prompt"] = template["hint"]

            # Set correct answer and options
            correct_val = template["correct"]
            distractors = [opt for opt in template["options"] if opt != correct_val]
            
            # Form 4 options (or 3 for comparison)
            all_opts = [correct_val] + distractors
            # Deterministic rotation based on index so correct answer is in different positions
            shift = idx % len(all_opts)
            all_opts = all_opts[shift:] + all_opts[:shift]

            correct_id = f"opt_{all_opts.index(correct_val) + 1}"
            
            opt_objs = [{"option_id": f"opt_{i+1}", "display_value": val} for i, val in enumerate(all_opts)]
            
            if "interaction_model" not in item:
                item["interaction_model"] = {}
            if "modality_configurations" not in item["interaction_model"]:
                item["interaction_model"]["modality_configurations"] = {}
            
            item["interaction_model"]["modality_configurations"]["tap_select"] = {
                "options": opt_objs
            }
            item["rubric"]["correct_criteria"]["selected_option_id"] = correct_id

            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(item, f, indent=2)

            updated_count += 1
        except Exception as e:
            print(f"Error processing {fpath}: {e}")

    print(f"Successfully diversified {updated_count} math items with authentic math questions!")

if __name__ == "__main__":
    main()
