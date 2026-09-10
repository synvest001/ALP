export interface CastlePart {
  partIndex: number;
  name: string;
  realmRequirement: string;
  description: string;
  svgElementId: string;
}

export const FAIRY_CASTLE_PARTS: CastlePart[] = [
  {
    partIndex: 1,
    name: 'Moonstone Foundation & Crystal Moat',
    realmRequirement: 'Magical Forest',
    description: 'Ancient glowing stones anchored into the living earth, surrounded by sparkling enchanted water.',
    svgElementId: 'castle-foundation'
  },
  {
    partIndex: 2,
    name: 'Amethyst Ramparts & Star Bastions',
    realmRequirement: 'Crystal Cave',
    description: 'Impenetrable purple crystal battlements that reflect starlight across the kingdom.',
    svgElementId: 'castle-walls'
  },
  {
    partIndex: 3,
    name: 'Grand Dragon Gate & Golden Drawbridge',
    realmRequirement: 'Dragon Castle',
    description: 'A gilded arched gateway carved with guardian dragon crests, welcoming noble learners.',
    svgElementId: 'castle-gate'
  },
  {
    partIndex: 4,
    name: 'Emerald Forest Tower (East Wing)',
    realmRequirement: 'Mushroom Village',
    description: 'A towering spire entwined with luminescent moss and floral balconies.',
    svgElementId: 'castle-tower-left'
  },
  {
    partIndex: 5,
    name: 'Sapphire Fairy Tower (West Wing)',
    realmRequirement: 'Pixie Hollow',
    description: 'A delicate spiraling turret topped with iridescent stained glass.',
    svgElementId: 'castle-tower-right'
  },
  {
    partIndex: 6,
    name: 'Royal Great Keep & Starlight Hall',
    realmRequirement: 'Whispering Woods',
    description: 'The monumental central castle keep where banquet tables and ancient storybooks reside.',
    svgElementId: 'castle-keep'
  },
  {
    partIndex: 7,
    name: 'Rose-Quartz Turrets & Conical Roofs',
    realmRequirement: 'Candy Canyon',
    description: 'Gleaming pink-violet tiled rooftops that sparkle like fine sugar crystals.',
    svgElementId: 'castle-roofs'
  },
  {
    partIndex: 8,
    name: 'Sun-Gear Celestial Spire & Banners',
    realmRequirement: 'Clockwork City',
    description: 'A majestic golden needle reaching toward the clouds, fluttering with royal silk crests.',
    svgElementId: 'castle-spire'
  },
  {
    partIndex: 9,
    name: 'Floating Cloud Gardens & Fairy Wings',
    realmRequirement: 'Cloud Kingdom',
    description: 'Weightless floating green terraces suspended by shimmering fairy wing magic.',
    svgElementId: 'castle-gardens'
  },
  {
    partIndex: 10,
    name: 'Prismatic Aurora Crown & Starlight Beacon',
    realmRequirement: 'Starlight Observatory',
    description: 'The crowning jewel of the realm! A pulsing supernova diamond bathing the realm in rainbow auroras.',
    svgElementId: 'castle-crown'
  }
];

export function getUnlockedCastlePartsCount(nodesCompleted: number, nodesPerMap: number = 5): number {
  const realmsCompleted = Math.floor(nodesCompleted / nodesPerMap);
  return Math.min(FAIRY_CASTLE_PARTS.length, realmsCompleted);
}

export function renderFairyCastleSvg(unlockedCount: number, newlyBuiltIndex: number = -1): string {
  // Renders a grand vector illustration of the Fairy Castle
  // Parts with index <= unlockedCount are rendered fully colored and glowing.
  // Parts with index > unlockedCount are rendered as ethereal silhouettes with a gentle lock.
  // If newlyBuiltIndex > 0, that part gets a special pulse/glow animation!

  const isUnlocked = (idx: number) => idx <= unlockedCount;
  const isNew = (idx: number) => idx === newlyBuiltIndex;

  return `
  <svg viewBox="0 0 500 420" xmlns="http://www.w3.org/2000/svg" class="fairy-castle-svg">
    <defs>
      <!-- Gradients -->
      <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#1e1b4b"/>
        <stop offset="60%" stop-color="#4c1d95"/>
        <stop offset="100%" stop-color="#831843"/>
      </linearGradient>
      
      <linearGradient id="waterGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#0284c7"/>
        <stop offset="50%" stop-color="#38bdf8"/>
        <stop offset="100%" stop-color="#0284c7"/>
      </linearGradient>

      <linearGradient id="wallGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#f5d0fe"/>
        <stop offset="50%" stop-color="#c084fc"/>
        <stop offset="100%" stop-color="#7e22ce"/>
      </linearGradient>

      <linearGradient id="stoneGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#94a3b8"/>
        <stop offset="100%" stop-color="#475569"/>
      </linearGradient>

      <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#fef08a"/>
        <stop offset="50%" stop-color="#f59e0b"/>
        <stop offset="100%" stop-color="#b45309"/>
      </linearGradient>

      <linearGradient id="roofGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#f43f5e"/>
        <stop offset="50%" stop-color="#fb7185"/>
        <stop offset="100%" stop-color="#e11d48"/>
      </linearGradient>

      <radialGradient id="beaconGlow" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#fef08a" stop-opacity="1"/>
        <stop offset="40%" stop-color="#38bdf8" stop-opacity="0.8"/>
        <stop offset="80%" stop-color="#ec4899" stop-opacity="0.4"/>
        <stop offset="100%" stop-color="#a855f7" stop-opacity="0"/>
      </radialGradient>

      <filter id="partGlow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="5" result="blur"/>
        <feComposite in="SourceGraphic" in2="blur" operator="over"/>
      </filter>
    </defs>

    <!-- Sky Backdrop -->
    <rect width="500" height="420" rx="20" fill="url(#skyGrad)"/>

    <!-- Twinkling Background Stars -->
    <g fill="#ffffff" opacity="0.8">
      <circle cx="50" cy="40" r="1.5"/>
      <circle cx="120" cy="25" r="1"/>
      <circle cx="200" cy="50" r="2"/>
      <circle cx="380" cy="30" r="1.5"/>
      <circle cx="450" cy="60" r="1"/>
      <circle cx="420" cy="110" r="2"/>
      <circle cx="70" cy="120" r="1.5"/>
      <polygon points="160,20 162,24 166,25 162,26 160,30 158,26 154,25 158,24" fill="#fef08a"/>
      <polygon points="340,40 342,43 346,44 342,45 340,48 338,45 334,44 338,43" fill="#fef08a"/>
    </g>

    <!-- Floating Cloud Hills -->
    <path d="M 0,380 Q 120,330 250,360 Q 380,330 500,380 L 500,420 L 0,420 Z" fill="#1e1b4b" opacity="0.6"/>

    <!-- PART 1: Foundation & Moat -->
    <g id="castle-foundation" class="castle-part ${isUnlocked(1) ? 'unlocked' : 'locked'} ${isNew(1) ? 'newly-built' : ''}">
      ${isUnlocked(1) ? `
        <!-- Crystal Moat -->
        <path d="M 60,370 Q 250,395 440,370 Q 450,405 250,410 Q 50,405 60,370 Z" fill="url(#waterGrad)"/>
        <!-- Foundation Stones -->
        <path d="M 90,340 L 410,340 L 425,375 L 75,375 Z" fill="url(#stoneGrad)" stroke="#334155" stroke-width="2"/>
        <!-- Courtyard Tiles -->
        <line x1="140" y1="340" x2="135" y2="375" stroke="#cbd5e1" stroke-width="1.5" opacity="0.5"/>
        <line x1="200" y1="340" x2="195" y2="375" stroke="#cbd5e1" stroke-width="1.5" opacity="0.5"/>
        <line x1="300" y1="340" x2="305" y2="375" stroke="#cbd5e1" stroke-width="1.5" opacity="0.5"/>
        <line x1="360" y1="340" x2="365" y2="375" stroke="#cbd5e1" stroke-width="1.5" opacity="0.5"/>
      ` : `
        <path d="M 90,340 L 410,340 L 425,375 L 75,375 Z" fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.2)" stroke-dasharray="6,4"/>
      `}
    </g>

    <!-- PART 2: Amethyst Ramparts & Walls -->
    <g id="castle-walls" class="castle-part ${isUnlocked(2) ? 'unlocked' : 'locked'} ${isNew(2) ? 'newly-built' : ''}">
      ${isUnlocked(2) ? `
        <rect x="130" y="240" width="240" height="100" fill="url(#wallGrad)" stroke="#581c87" stroke-width="2.5"/>
        <!-- Battlements -->
        <rect x="130" y="228" width="25" height="15" fill="url(#wallGrad)" stroke="#581c87" stroke-width="1.5"/>
        <rect x="175" y="228" width="25" height="15" fill="url(#wallGrad)" stroke="#581c87" stroke-width="1.5"/>
        <rect x="220" y="228" width="25" height="15" fill="url(#wallGrad)" stroke="#581c87" stroke-width="1.5"/>
        <rect x="255" y="228" width="25" height="15" fill="url(#wallGrad)" stroke="#581c87" stroke-width="1.5"/>
        <rect x="300" y="228" width="25" height="15" fill="url(#wallGrad)" stroke="#581c87" stroke-width="1.5"/>
        <rect x="345" y="228" width="25" height="15" fill="url(#wallGrad)" stroke="#581c87" stroke-width="1.5"/>
      ` : `
        <rect x="130" y="240" width="240" height="100" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.2)" stroke-dasharray="6,4"/>
      `}
    </g>

    <!-- PART 3: Grand Gate & Drawbridge -->
    <g id="castle-gate" class="castle-part ${isUnlocked(3) ? 'unlocked' : 'locked'} ${isNew(3) ? 'newly-built' : ''}">
      ${isUnlocked(3) ? `
        <!-- Drawbridge -->
        <path d="M 220,340 L 220,380 L 280,380 L 280,340 Z" fill="url(#goldGrad)" stroke="#78350f" stroke-width="2"/>
        <!-- Archway -->
        <path d="M 215,340 L 215,280 Q 250,250 285,280 L 285,340 Z" fill="#2e1065" stroke="url(#goldGrad)" stroke-width="4"/>
        <path d="M 225,340 L 225,288 Q 250,268 275,288 L 275,340 Z" fill="#0f172a"/>
        <!-- Portcullis Grate -->
        <line x1="240" y1="275" x2="240" y2="340" stroke="#facc15" stroke-width="2"/>
        <line x1="250" y1="270" x2="250" y2="340" stroke="#facc15" stroke-width="2"/>
        <line x1="260" y1="275" x2="260" y2="340" stroke="#facc15" stroke-width="2"/>
        <line x1="225" y1="300" x2="275" y2="300" stroke="#facc15" stroke-width="2"/>
        <line x1="225" y1="320" x2="275" y2="320" stroke="#facc15" stroke-width="2"/>
      ` : `
        <path d="M 215,340 L 215,280 Q 250,250 285,280 L 285,340 Z" fill="none" stroke="rgba(255,255,255,0.2)" stroke-dasharray="4,3"/>
      `}
    </g>

    <!-- PART 4: Emerald East Tower (Left) -->
    <g id="castle-tower-left" class="castle-part ${isUnlocked(4) ? 'unlocked' : 'locked'} ${isNew(4) ? 'newly-built' : ''}">
      ${isUnlocked(4) ? `
        <rect x="90" y="160" width="55" height="180" fill="#059669" stroke="#064e3b" stroke-width="2.5"/>
        <rect x="85" y="145" width="65" height="18" fill="#10b981" stroke="#064e3b" stroke-width="2"/>
        <!-- Window -->
        <rect x="108" y="200" width="18" height="30" rx="9" fill="#fef08a" stroke="#064e3b" stroke-width="2"/>
      ` : `
        <rect x="90" y="160" width="55" height="180" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.15)" stroke-dasharray="6,4"/>
      `}
    </g>

    <!-- PART 5: Sapphire West Tower (Right) -->
    <g id="castle-tower-right" class="castle-part ${isUnlocked(5) ? 'unlocked' : 'locked'} ${isNew(5) ? 'newly-built' : ''}">
      ${isUnlocked(5) ? `
        <rect x="355" y="160" width="55" height="180" fill="#2563eb" stroke="#1e3a8a" stroke-width="2.5"/>
        <rect x="350" y="145" width="65" height="18" fill="#3b82f6" stroke="#1e3a8a" stroke-width="2"/>
        <!-- Window -->
        <rect x="374" y="200" width="18" height="30" rx="9" fill="#fef08a" stroke="#1e3a8a" stroke-width="2"/>
      ` : `
        <rect x="355" y="160" width="55" height="180" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.15)" stroke-dasharray="6,4"/>
      `}
    </g>

    <!-- PART 6: Royal Great Keep -->
    <g id="castle-keep" class="castle-part ${isUnlocked(6) ? 'unlocked' : 'locked'} ${isNew(6) ? 'newly-built' : ''}">
      ${isUnlocked(6) ? `
        <rect x="180" y="130" width="140" height="115" fill="url(#wallGrad)" stroke="#4c1d95" stroke-width="3"/>
        <!-- Stained Glass Rose Window -->
        <circle cx="250" cy="180" r="24" fill="#38bdf8" stroke="url(#goldGrad)" stroke-width="3"/>
        <circle cx="250" cy="180" r="14" fill="#f43f5e"/>
        <line x1="226" y1="180" x2="274" y2="180" stroke="#fef08a" stroke-width="2"/>
        <line x1="250" y1="156" x2="250" y2="204" stroke="#fef08a" stroke-width="2"/>
      ` : `
        <rect x="180" y="130" width="140" height="115" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.15)" stroke-dasharray="6,4"/>
      `}
    </g>

    <!-- PART 7: Conical Roofs & Turrets -->
    <g id="castle-roofs" class="castle-part ${isUnlocked(7) ? 'unlocked' : 'locked'} ${isNew(7) ? 'newly-built' : ''}">
      ${isUnlocked(7) ? `
        <!-- Left Roof -->
        <polygon points="80,145 117,70 155,145" fill="url(#roofGrad)" stroke="#881337" stroke-width="2.5"/>
        <!-- Right Roof -->
        <polygon points="345,145 382,70 420,145" fill="url(#roofGrad)" stroke="#881337" stroke-width="2.5"/>
        <!-- Keep Center Pediment -->
        <polygon points="175,130 250,75 325,130" fill="url(#roofGrad)" stroke="#881337" stroke-width="3"/>
      ` : `
        <polygon points="80,145 117,70 155,145" fill="none" stroke="rgba(255,255,255,0.2)" stroke-dasharray="4,3"/>
        <polygon points="345,145 382,70 420,145" fill="none" stroke="rgba(255,255,255,0.2)" stroke-dasharray="4,3"/>
        <polygon points="175,130 250,75 325,130" fill="none" stroke="rgba(255,255,255,0.2)" stroke-dasharray="4,3"/>
      `}
    </g>

    <!-- PART 8: Golden Spire & Banners -->
    <g id="castle-spire" class="castle-part ${isUnlocked(8) ? 'unlocked' : 'locked'} ${isNew(8) ? 'newly-built' : ''}">
      ${isUnlocked(8) ? `
        <!-- Central Golden Needle Spire -->
        <polygon points="244,75 250,15 256,75" fill="url(#goldGrad)" stroke="#78350f" stroke-width="2"/>
        <!-- Left Banner -->
        <line x1="117" y1="70" x2="117" y2="40" stroke="#f59e0b" stroke-width="2"/>
        <polygon points="117,40 145,50 117,60" fill="#f43f5e"/>
        <!-- Right Banner -->
        <line x1="382" y1="70" x2="382" y2="40" stroke="#f59e0b" stroke-width="2"/>
        <polygon points="382,40 410,50 382,60" fill="#3b82f6"/>
        <!-- Spire Flag -->
        <polygon points="250,15 285,25 250,35" fill="url(#goldGrad)" stroke="#78350f" stroke-width="1"/>
      ` : `
        <line x1="250" y1="75" x2="250" y2="15" stroke="rgba(255,255,255,0.2)" stroke-dasharray="4,3"/>
      `}
    </g>

    <!-- PART 9: Floating Gardens & Fairy Wings -->
    <g id="castle-gardens" class="castle-part ${isUnlocked(9) ? 'unlocked' : 'locked'} ${isNew(9) ? 'newly-built' : ''}">
      ${isUnlocked(9) ? `
        <!-- Floating Terraces -->
        <g opacity="0.9">
          <ellipse cx="60" cy="220" rx="35" ry="12" fill="#a7f3d0" stroke="#059669" stroke-width="2"/>
          <path d="M 35,220 Q 60,200 85,220" stroke="#10b981" stroke-width="3" fill="none"/>
          <ellipse cx="440" cy="220" rx="35" ry="12" fill="#a7f3d0" stroke="#059669" stroke-width="2"/>
          <path d="M 415,220 Q 440,200 465,220" stroke="#10b981" stroke-width="3" fill="none"/>
        </g>
        <!-- Shimmering Fairy Wings on Keep -->
        <path d="M 250,140 C 180,90 150,160 230,170 Z" fill="#bae6fd" opacity="0.75" filter="url(#partGlow)"/>
        <path d="M 250,140 C 320,90 350,160 270,170 Z" fill="#bae6fd" opacity="0.75" filter="url(#partGlow)"/>
      ` : `
        <ellipse cx="60" cy="220" rx="30" ry="10" fill="none" stroke="rgba(255,255,255,0.15)" stroke-dasharray="3,3"/>
        <ellipse cx="440" cy="220" rx="30" ry="10" fill="none" stroke="rgba(255,255,255,0.15)" stroke-dasharray="3,3"/>
      `}
    </g>

    <!-- PART 10: Prismatic Starlight Beacon & Crown -->
    <g id="castle-crown" class="castle-part ${isUnlocked(10) ? 'unlocked' : 'locked'} ${isNew(10) ? 'newly-built' : ''}">
      ${isUnlocked(10) ? `
        <!-- Giant Radiating Beacon Halo -->
        <circle cx="250" cy="15" r="45" fill="url(#beaconGlow)"/>
        <!-- Star Jewel -->
        <polygon points="250,0 255,10 266,13 257,20 259,31 250,25 241,31 243,20 234,13 245,10" 
                 fill="#ffffff" stroke="#facc15" stroke-width="2" filter="url(#partGlow)"/>
        <!-- Orbiting Stardust Rings -->
        <ellipse cx="250" cy="15" rx="55" ry="16" fill="none" stroke="#fde047" stroke-width="2" stroke-dasharray="12,6" opacity="0.8" transform="rotate(-15 250 15)"/>
        <ellipse cx="250" cy="15" rx="55" ry="16" fill="none" stroke="#38bdf8" stroke-width="2" stroke-dasharray="12,6" opacity="0.8" transform="rotate(25 250 15)"/>
      ` : `
        <circle cx="250" cy="15" r="10" fill="none" stroke="rgba(255,255,255,0.2)" stroke-dasharray="3,3"/>
      `}
    </g>

    <!-- Locked Overlay Badges / Progress Indicator -->
    <rect x="15" y="15" width="130" height="35" rx="10" fill="rgba(0,0,0,0.5)" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"/>
    <text x="25" y="38" font-family="'Comic Sans MS', sans-serif" font-size="14" font-weight="bold" fill="#facc15">
      🏰 ${unlockedCount}/10 Built
    </text>
  </svg>`;
}
