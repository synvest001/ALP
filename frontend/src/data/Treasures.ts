export interface Treasure {
  id: string;
  name: string;
  realm: string;
  rarity: 'Rare' | 'Epic' | 'Legendary' | 'Mythic';
  color: string;
  description: string;
  svg: string;
}

export const GRAND_TREASURES: Treasure[] = [
  {
    id: 'emerald_dragon',
    name: 'Emerald Dragon of Eldoria',
    realm: 'Magical Forest',
    rarity: 'Mythic',
    color: 'linear-gradient(135deg, #10b981, #047857)',
    description: 'A playful forest dragon blessed by the ancient trees. Its emerald scales glow when true bravery is shown.',
    svg: `<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="dragonGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#34d399" stop-opacity="0.9"/>
          <stop offset="60%" stop-color="#059669" stop-opacity="0.6"/>
          <stop offset="100%" stop-color="#064e3b" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="dragonScale" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#6ee7b7"/>
          <stop offset="50%" stop-color="#10b981"/>
          <stop offset="100%" stop-color="#047857"/>
        </linearGradient>
        <linearGradient id="goldHorn" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#fde047"/>
          <stop offset="100%" stop-color="#d97706"/>
        </linearGradient>
      </defs>
      <circle cx="60" cy="60" r="54" fill="url(#dragonGlow)"/>
      <!-- Body & Tail -->
      <path d="M 60,35 C 75,35 88,48 85,68 C 82,85 66,95 50,92 C 38,90 28,78 32,64 C 34,58 40,55 45,58 C 48,60 48,66 45,70 C 42,75 48,82 56,82 C 65,82 72,75 72,64 C 72,50 62,45 54,48" 
            fill="none" stroke="url(#dragonScale)" stroke-width="12" stroke-linecap="round"/>
      <!-- Wing -->
      <path d="M 60,54 Q 85,30 92,48 Q 80,56 70,62 Z" fill="#34d399" opacity="0.85" stroke="#047857" stroke-width="2"/>
      <!-- Head -->
      <path d="M 52,38 C 45,34 40,28 35,32 C 30,36 34,44 42,46 C 48,48 54,44 52,38 Z" fill="url(#dragonScale)" stroke="#047857" stroke-width="2"/>
      <!-- Horns -->
      <path d="M 48,34 Q 52,20 60,18 Q 54,26 50,33 Z" fill="url(#goldHorn)"/>
      <path d="M 44,32 Q 44,18 50,17 Q 46,24 44,31 Z" fill="url(#goldHorn)"/>
      <!-- Eye -->
      <circle cx="40" cy="35" r="3" fill="#fef08a"/>
      <circle cx="39.5" cy="35" r="1.5" fill="#1e293b"/>
      <!-- Sparkles -->
      <polygon points="85,25 87,30 92,32 87,34 85,39 83,34 78,32 83,30" fill="#fef08a"/>
      <polygon points="25,70 26,73 29,74 26,75 25,78 24,75 21,74 24,73" fill="#6ee7b7"/>
    </svg>`
  },
  {
    id: 'crystal_heart',
    name: 'Heart of the Crystal Grotto',
    realm: 'Crystal Cave',
    rarity: 'Legendary',
    color: 'linear-gradient(135deg, #a855f7, #6366f1)',
    description: 'A radiant prism gem carved from deep subterranean crystals. It reflects every color of the enchanted aurora.',
    svg: `<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="crystalGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#c084fc" stop-opacity="0.9"/>
          <stop offset="70%" stop-color="#818cf8" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#4f46e5" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="gemFacet1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#e0e7ff"/>
          <stop offset="100%" stop-color="#a855f7"/>
        </linearGradient>
        <linearGradient id="gemFacet2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#c084fc"/>
          <stop offset="100%" stop-color="#6366f1"/>
        </linearGradient>
        <linearGradient id="gemFacet3" x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#818cf8"/>
          <stop offset="100%" stop-color="#3b82f6"/>
        </linearGradient>
      </defs>
      <circle cx="60" cy="60" r="54" fill="url(#crystalGlow)"/>
      <!-- Gem Body (Heart/Diamond Facets) -->
      <polygon points="60,20 85,42 60,98 35,42" fill="url(#gemFacet2)" stroke="#e0e7ff" stroke-width="2.5"/>
      <polygon points="60,20 75,42 60,98" fill="url(#gemFacet1)"/>
      <polygon points="60,20 45,42 60,98" fill="url(#gemFacet3)" opacity="0.9"/>
      <!-- Top Crown Facets -->
      <polygon points="60,20 75,42 85,42" fill="#f5d0fe" opacity="0.8"/>
      <polygon points="60,20 45,42 35,42" fill="#c7d2fe" opacity="0.8"/>
      <!-- Shimmer Highlight -->
      <polygon points="60,26 68,42 60,65 52,42" fill="#ffffff" opacity="0.6"/>
      <!-- Sparkles -->
      <polygon points="90,28 92,34 98,36 92,38 90,44 88,38 82,36 88,34" fill="#ffffff"/>
      <polygon points="28,75 29,78 32,79 29,80 28,83 27,80 24,79 27,78" fill="#f5d0fe"/>
    </svg>`
  },
  {
    id: 'sun_crown',
    name: 'Crown of the Sun King',
    realm: 'Dragon Castle',
    rarity: 'Mythic',
    color: 'linear-gradient(135deg, #f59e0b, #ef4444)',
    description: 'Forged in royal dragonfire, this gleaming golden tiara pulses with warm starlight and steadfast authority.',
    svg: `<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#fef08a" stop-opacity="0.85"/>
          <stop offset="60%" stop-color="#f59e0b" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#b45309" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="goldCrown" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#fef08a"/>
          <stop offset="50%" stop-color="#f59e0b"/>
          <stop offset="100%" stop-color="#b45309"/>
        </linearGradient>
      </defs>
      <circle cx="60" cy="60" r="54" fill="url(#sunGlow)"/>
      <!-- Crown Base -->
      <path d="M 25,75 Q 60,85 95,75 L 98,62 Q 60,72 22,62 Z" fill="url(#goldCrown)" stroke="#78350f" stroke-width="2"/>
      <!-- Crown Peaks -->
      <polygon points="22,62 32,38 42,66" fill="url(#goldCrown)" stroke="#78350f" stroke-width="1.5"/>
      <polygon points="98,62 88,38 78,66" fill="url(#goldCrown)" stroke="#78350f" stroke-width="1.5"/>
      <polygon points="40,66 60,25 80,66" fill="url(#goldCrown)" stroke="#78350f" stroke-width="2"/>
      <!-- Rubies -->
      <circle cx="60" cy="42" r="6" fill="#ef4444" stroke="#7f1d1d" stroke-width="1.5"/>
      <circle cx="58" cy="40" r="2" fill="#fca5a5"/>
      <circle cx="33" cy="50" r="4" fill="#3b82f6" stroke="#1e3a8a" stroke-width="1.5"/>
      <circle cx="87" cy="50" r="4" fill="#3b82f6" stroke="#1e3a8a" stroke-width="1.5"/>
      <!-- Jewels on Band -->
      <circle cx="60" cy="74" r="3.5" fill="#ef4444"/>
      <circle cx="45" cy="73" r="3" fill="#10b981"/>
      <circle cx="75" cy="73" r="3" fill="#10b981"/>
      <!-- Sparkle -->
      <polygon points="60,12 62,17 67,19 62,21 60,26 58,21 53,19 58,17" fill="#ffffff"/>
    </svg>`
  },
  {
    id: 'luminous_shroom',
    name: 'Bioluminescent Fairy Cap',
    realm: 'Mushroom Village',
    rarity: 'Rare',
    color: 'linear-gradient(135deg, #ec4899, #8b5cf6)',
    description: 'A magical mushroom that glows under moonlight. Woodland pixies use it to illuminate nighttime garden tea parties.',
    svg: `<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="shroomGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#f472b6" stop-opacity="0.8"/>
          <stop offset="70%" stop-color="#a855f7" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="#581c87" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="shroomCap" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#fb7185"/>
          <stop offset="60%" stop-color="#e11d48"/>
          <stop offset="100%" stop-color="#881337"/>
        </linearGradient>
      </defs>
      <circle cx="60" cy="60" r="54" fill="url(#shroomGlow)"/>
      <!-- Stem -->
      <path d="M 52,65 Q 48,92 60,94 Q 72,92 68,65 Z" fill="#fdf4ff" stroke="#c084fc" stroke-width="2"/>
      <ellipse cx="60" cy="65" rx="14" ry="4" fill="#fae8ff"/>
      <!-- Cap -->
      <path d="M 22,65 C 22,35 98,35 98,65 C 98,70 22,70 22,65 Z" fill="url(#shroomCap)" stroke="#4c0519" stroke-width="2.5"/>
      <!-- Glowing Dots -->
      <circle cx="45" cy="46" r="6" fill="#fef08a" opacity="0.9"/>
      <circle cx="70" cy="44" r="7" fill="#fef08a" opacity="0.9"/>
      <circle cx="34" cy="56" r="4.5" fill="#fef08a" opacity="0.9"/>
      <circle cx="84" cy="58" r="5" fill="#fef08a" opacity="0.9"/>
      <circle cx="58" cy="55" r="4" fill="#fef08a" opacity="0.9"/>
      <!-- Spore Sparkles -->
      <circle cx="48" cy="85" r="2" fill="#fef08a"/>
      <circle cx="72" cy="82" r="1.5" fill="#fef08a"/>
      <polygon points="90,32 92,36 96,37 92,38 90,42 88,38 84,37 88,36" fill="#fdf4ff"/>
    </svg>`
  },
  {
    id: 'pixie_locket',
    name: 'Prismatic Pixie Locket',
    realm: 'Pixie Hollow',
    rarity: 'Legendary',
    color: 'linear-gradient(135deg, #06b6d4, #3b82f6)',
    description: 'An enchanted silver medallion with gossamer dragonfly wings that flutter softly whenever friends share kindness.',
    svg: `<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="pixieGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#67e8f9" stop-opacity="0.9"/>
          <stop offset="70%" stop-color="#3b82f6" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="#1e3a8a" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <circle cx="60" cy="60" r="54" fill="url(#pixieGlow)"/>
      <!-- Wings -->
      <path d="M 60,60 C 20,25 15,65 52,65 Z" fill="#a5f3fc" opacity="0.75" stroke="#0891b2" stroke-width="1.5"/>
      <path d="M 60,60 C 100,25 105,65 68,65 Z" fill="#a5f3fc" opacity="0.75" stroke="#0891b2" stroke-width="1.5"/>
      <path d="M 60,64 C 30,80 32,95 56,70 Z" fill="#cffafe" opacity="0.65" stroke="#0891b2" stroke-width="1.5"/>
      <path d="M 60,64 C 90,80 88,95 64,70 Z" fill="#cffafe" opacity="0.65" stroke="#0891b2" stroke-width="1.5"/>
      <!-- Locket Center -->
      <circle cx="60" cy="62" r="18" fill="#f8fafc" stroke="#0284c7" stroke-width="3"/>
      <circle cx="60" cy="62" r="13" fill="#06b6d4"/>
      <polygon points="60,52 64,59 71,60 66,65 67,72 60,68 53,72 54,65 49,60 56,59" fill="#fef08a"/>
      <!-- Chain Ring -->
      <circle cx="60" cy="40" r="5" fill="none" stroke="#0284c7" stroke-width="2.5"/>
    </svg>`
  },
  {
    id: 'whispering_tome',
    name: 'Tome of Whispering Stars',
    realm: 'Whispering Woods',
    rarity: 'Legendary',
    color: 'linear-gradient(135deg, #8b5cf6, #3b82f6)',
    description: 'An ancient velvet grimoire that hums with gentle lullabies. Its pages automatically reveal the secrets of constellations.',
    svg: `<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="tomeGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#c4b5fd" stop-opacity="0.8"/>
          <stop offset="70%" stop-color="#6366f1" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="#312e81" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <circle cx="60" cy="60" r="54" fill="url(#tomeGlow)"/>
      <!-- Open Book -->
      <path d="M 60,40 Q 40,36 22,44 L 25,82 Q 42,74 60,78 Z" fill="#fdf4ff" stroke="#4338ca" stroke-width="2"/>
      <path d="M 60,40 Q 80,36 98,44 L 95,82 Q 78,74 60,78 Z" fill="#fdf4ff" stroke="#4338ca" stroke-width="2"/>
      <!-- Book Cover Spine -->
      <path d="M 20,44 Q 40,34 60,38 Q 80,34 100,44 L 97,85 Q 78,75 60,79 Q 42,75 23,85 Z" fill="#4c1d95" opacity="0.9" stroke="#312e81" stroke-width="2.5"/>
      <!-- Pages Overlay -->
      <path d="M 60,40 Q 42,37 25,44 L 27,80 Q 44,73 60,77 Z" fill="#ffffff"/>
      <path d="M 60,40 Q 78,37 95,44 L 93,80 Q 76,73 60,77 Z" fill="#ffffff"/>
      <!-- Magic Star on Page -->
      <polygon points="42,56 44,60 48,61 45,64 46,68 42,66 38,68 39,64 36,61 40,60" fill="#facc15"/>
      <line x1="32" y1="50" x2="52" y2="50" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round"/>
      <line x1="68" y1="50" x2="88" y2="50" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round"/>
      <line x1="68" y1="58" x2="84" y2="58" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round"/>
      <line x1="68" y1="66" x2="88" y2="66" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round"/>
      <!-- Floating Sparkles -->
      <circle cx="60" cy="28" r="3" fill="#fef08a"/>
      <polygon points="76,22 78,26 82,27 78,28 76,32 74,28 70,27 74,26" fill="#fef08a"/>
    </svg>`
  },
  {
    id: 'rainbow_candy_gem',
    name: 'The Rainbow Swirl Jewel',
    realm: 'Candy Canyon',
    rarity: 'Rare',
    color: 'linear-gradient(135deg, #f43f5e, #facc15)',
    description: 'A confection gemstone spun from sweet sugar rainbows and sparkling dew. It smells delightfully of strawberries.',
    svg: `<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="candyGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#fda4af" stop-opacity="0.9"/>
          <stop offset="60%" stop-color="#f43f5e" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="#be123c" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <circle cx="60" cy="60" r="54" fill="url(#candyGlow)"/>
      <!-- Lollipop / Candy Swirl -->
      <circle cx="60" cy="55" r="28" fill="#f43f5e" stroke="#ffe4e6" stroke-width="3"/>
      <path d="M 60,55 M 60,31 A 24,24 0 0,1 84,55 A 16,16 0 0,1 68,71 A 8,8 0 0,1 60,63" fill="none" stroke="#fef08a" stroke-width="5" stroke-linecap="round"/>
      <path d="M 60,55 M 36,55 A 24,24 0 0,1 60,31 A 16,16 0 0,1 76,47 A 8,8 0 0,1 68,55" fill="none" stroke="#67e8f9" stroke-width="4" stroke-linecap="round"/>
      <!-- Stick -->
      <path d="M 57,82 L 53,105 Q 60,108 67,105 L 63,82 Z" fill="#ffffff" stroke="#cbd5e1" stroke-width="2"/>
      <!-- Ribbon Bow -->
      <polygon points="52,82 40,76 44,88" fill="#ec4899"/>
      <polygon points="68,82 80,76 76,88" fill="#ec4899"/>
      <circle cx="60" cy="82" r="4" fill="#fbbf24"/>
    </svg>`
  },
  {
    id: 'chrono_watch',
    name: 'Chrono-Gilded Pocket Watch',
    realm: 'Clockwork City',
    rarity: 'Legendary',
    color: 'linear-gradient(135deg, #eab308, #b45309)',
    description: 'A celestial timepiece designed by master tinkers. Its golden hands move to the rhythm of curious learners solving puzzles.',
    svg: `<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="watchGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#fef08a" stop-opacity="0.8"/>
          <stop offset="70%" stop-color="#eab308" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="#713f12" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <circle cx="60" cy="60" r="54" fill="url(#watchGlow)"/>
      <!-- Winding Ring -->
      <circle cx="60" cy="22" r="9" fill="none" stroke="#eab308" stroke-width="3"/>
      <rect x="57" y="28" width="6" height="6" rx="2" fill="#ca8a04"/>
      <!-- Outer Casing -->
      <circle cx="60" cy="64" r="32" fill="#ca8a04" stroke="#713f12" stroke-width="2.5"/>
      <circle cx="60" cy="64" r="28" fill="#fefce8" stroke="#ca8a04" stroke-width="2"/>
      <!-- Gears Inside -->
      <circle cx="60" cy="64" r="18" fill="none" stroke="#fde047" stroke-dasharray="4,3" stroke-width="2"/>
      <!-- Clock Hands -->
      <line x1="60" y1="64" x2="60" y2="44" stroke="#1e293b" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="60" y1="64" x2="74" y2="60" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>
      <circle cx="60" cy="64" r="3" fill="#1e293b"/>
      <!-- Roman Dial Ticks -->
      <circle cx="60" cy="40" r="1.5" fill="#854d0e"/>
      <circle cx="84" cy="64" r="1.5" fill="#854d0e"/>
      <circle cx="60" cy="88" r="1.5" fill="#854d0e"/>
      <circle cx="36" cy="64" r="1.5" fill="#854d0e"/>
    </svg>`
  },
  {
    id: 'phoenix_feather',
    name: 'Feather of the Astral Phoenix',
    realm: 'Cloud Kingdom',
    rarity: 'Mythic',
    color: 'linear-gradient(135deg, #f97316, #ec4899)',
    description: 'A majestic feather gifted by the mythical cloud bird. It radiates soothing warmth and whispers words of encouragement.',
    svg: `<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="phoenixGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#fdba74" stop-opacity="0.9"/>
          <stop offset="60%" stop-color="#f97316" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#9a3412" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <circle cx="60" cy="60" r="54" fill="url(#phoenixGlow)"/>
      <!-- Feather Plume -->
      <path d="M 35,95 C 45,70 50,45 85,25 C 75,45 80,65 55,90 Z" fill="#ea580c" stroke="#c2410c" stroke-width="2"/>
      <path d="M 40,88 C 48,68 52,48 80,32 C 72,48 74,65 55,85 Z" fill="#f97316"/>
      <path d="M 45,80 C 50,65 55,50 75,40 C 68,52 70,64 56,78 Z" fill="#fbbf24"/>
      <!-- Shaft -->
      <path d="M 30,102 Q 52,65 86,24" fill="none" stroke="#fff7ed" stroke-width="2.5" stroke-linecap="round"/>
      <!-- Embers -->
      <circle cx="82" cy="18" r="2.5" fill="#fef08a"/>
      <circle cx="92" cy="30" r="2" fill="#fdba74"/>
      <circle cx="68" cy="18" r="1.5" fill="#f97316"/>
      <polygon points="85,38 87,41 90,42 87,43 85,46 83,43 80,42 83,41" fill="#fef08a"/>
    </svg>`
  },
  {
    id: 'starlight_scepter',
    name: 'Starlight Scepter of Mastery',
    realm: 'Starlight Observatory',
    rarity: 'Mythic',
    color: 'linear-gradient(135deg, #38bdf8, #818cf8)',
    description: 'The supreme wand of knowledge. Crowned with a miniature glowing star, it lights up the path across every magical kingdom.',
    svg: `<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="scepterGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#bae6fd" stop-opacity="0.95"/>
          <stop offset="60%" stop-color="#38bdf8" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#0284c7" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <circle cx="60" cy="60" r="54" fill="url(#scepterGlow)"/>
      <!-- Scepter Staff -->
      <line x1="32" y1="98" x2="68" y2="42" stroke="#e2e8f0" stroke-width="6" stroke-linecap="round"/>
      <line x1="32" y1="98" x2="68" y2="42" stroke="#0284c7" stroke-width="2" stroke-linecap="round"/>
      <circle cx="30" cy="100" r="5" fill="#facc15" stroke="#ca8a04" stroke-width="1.5"/>
      <!-- Crown Top -->
      <circle cx="72" cy="36" r="14" fill="#38bdf8" stroke="#f0f9ff" stroke-width="2"/>
      <!-- Glowing Star -->
      <polygon points="72,18 75,28 85,31 77,38 78,48 72,42 66,48 67,38 59,31 69,28" fill="#fef08a" stroke="#eab308" stroke-width="1.5"/>
      <circle cx="72" cy="35" r="4" fill="#ffffff"/>
      <!-- Orbiting Rings -->
      <ellipse cx="72" cy="36" rx="20" ry="6" fill="none" stroke="#bae6fd" stroke-width="1.5" transform="rotate(-30 72 36)"/>
    </svg>`
  }
];
