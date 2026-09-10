import { resolveAssetUrl } from '../utils/assets';

export interface SubskillNode {
  code: string;
  title: string;
  domain_id: string;
  strands?: string;
  progression: string[];
  requiredPrereqs: string[];
  stronglySupportive: string[];
}

const DOMAIN_ID_MAP: Record<string, string> = {
  '1': 'MATHEMATICS',
  '2': 'ENGLISH_LANGUAGE',
  '3': 'SCIENCE_EVS',
  '4': 'LOGICAL_REASONING',
  '5': 'WORLD_KNOWLEDGE'
};

const DOMAIN_FALLBACK_ENTRIES: Record<string, string[]> = {
  'MATHEMATICS': ['M-NQ-01', 'M-NQ-02', 'M-OP-01', 'M-GS-01', 'M-ME-01', 'M-PA-01', 'M-DU-01'],
  'ENGLISH_LANGUAGE': ['E-OL-01', 'E-PD-01', 'E-VM-01', 'E-SG-01', 'E-RF-01'],
  'SCIENCE_EVS': ['S-KN-01', 'S-OC-01', 'S-PP-01', 'S-EE-01'],
  'LOGICAL_REASONING': ['L-PC-01', 'L-AR-01', 'L-SR-01', 'L-RC-01'],
  'WORLD_KNOWLEDGE': ['W-KA-01', 'W-KO-01', 'W-KP-01']
};

export class CurriculumGraph {
  private nodes: Map<string, SubskillNode> = new Map();
  private domainNodes: Map<string, SubskillNode[]> = new Map();
  private loadPromise: Promise<void> | null = null;
  public isGraphLoaded = false;

  constructor() {
    this.loadPromise = this.initGraph();
  }

  public async ensureLoaded(): Promise<void> {
    if (this.isGraphLoaded) return;
    if (this.loadPromise) {
      await this.loadPromise;
    } else {
      this.loadPromise = this.initGraph();
      await this.loadPromise;
    }
  }

  private async initGraph(): Promise<void> {
    try {
      const url = resolveAssetUrl('data/curriculum_map.json');
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        this.parseCurriculumMap(data);
        this.isGraphLoaded = true;
        console.log(`[CurriculumGraph] Loaded ${this.nodes.size} subskills across ${this.domainNodes.size} domains.`);
      } else {
        console.warn(`[CurriculumGraph] Failed to fetch curriculum map from ${url}: status ${res.status}`);
      }
    } catch (e) {
      console.warn("[CurriculumGraph] Could not fetch curriculum_map.json, using fallback entry points", e);
    }
  }

  private parseCurriculumMap(data: any) {
    const domains = data.domains || [];
    for (const d of domains) {
      const domainId = DOMAIN_ID_MAP[d.id] || d.title;
      if (!this.domainNodes.has(domainId)) {
        this.domainNodes.set(domainId, []);
      }

      for (const strand of (d.strands || [])) {
        for (const skill of (strand.skills || [])) {
          const code = skill.code;
          const title = skill.title;
          const progression = skill.progression || [];
          const prereqs = skill.prerequisites || {};

          const requiredRaw = prereqs.required || [];
          const requiredPrereqs: string[] = [];
          for (const item of requiredRaw) {
            if (typeof item === 'string') {
              if (item.toLowerCase().includes('none') || item.toLowerCase().includes('tbd')) continue;
              item.split(',').forEach(c => {
                const trimmed = c.trim();
                if (trimmed && !trimmed.toLowerCase().includes('none') && !trimmed.toLowerCase().includes('tbd')) {
                  requiredPrereqs.push(trimmed);
                }
              });
            }
          }

          const node: SubskillNode = {
            code,
            title,
            domain_id: domainId,
            strands: strand.title,
            progression,
            requiredPrereqs,
            stronglySupportive: prereqs.strongly_supportive || []
          };

          this.nodes.set(code, node);
          this.domainNodes.get(domainId)!.push(node);
        }
      }
    }
  }

  /**
   * Returns foundational entry points for each domain (skills with no required prerequisites
   * or foundational Phase A skills). Returns them randomized to prevent predictable question orders.
   */
  public getEntryPoints(domainId?: string): string[] {
    const entryPoints: string[] = [];
    const domains = domainId ? [domainId] : Array.from(this.domainNodes.keys());

    for (const d of domains) {
      const nodes = this.domainNodes.get(d) || [];
      // Foundational skills: no prerequisites OR Phase A progression
      let foundational = nodes.filter(n => n.requiredPrereqs.length === 0 || n.progression.includes('Phase A'));
      if (foundational.length === 0) {
        foundational = nodes;
      }
      
      // Shuffle to make the selection non-predictable across kids
      const shuffled = [...foundational].sort(() => Math.random() - 0.5);
      entryPoints.push(...shuffled.map(e => e.code));
    }

    if (entryPoints.length === 0) {
      if (domainId && DOMAIN_FALLBACK_ENTRIES[domainId]) {
        return [...DOMAIN_FALLBACK_ENTRIES[domainId]].sort(() => Math.random() - 0.5);
      }
      return ['M-NQ-01', 'M-NQ-02', 'M-OP-01', 'M-GS-01', 'E-OL-01', 'E-PD-01', 'S-KN-01', 'L-PC-01', 'W-KA-01'];
    }

    return entryPoints;
  }

  /**
   * Determines which subskills are currently unlocked given the set of secure subskills.
   * A subskill is unlocked if all of its required prerequisites are in the secure set,
   * or if it is a foundational Phase A/B skill.
   */
  public getUnlockedSubskills(secureCodes: Set<string>, domainId?: string): string[] {
    const unlocked: string[] = [];
    const domains = domainId ? [domainId] : Array.from(this.domainNodes.keys());

    for (const d of domains) {
      const nodes = this.domainNodes.get(d) || [];
      for (const node of nodes) {
        const isSatisfied = node.requiredPrereqs.every(req => secureCodes.has(req)) ||
                            node.progression.includes('Phase A');
        if (isSatisfied) {
          unlocked.push(node.code);
        }
      }
    }

    return unlocked;
  }

  /**
   * Returns next progressive subskills to introduce for a domain, randomized across
   * available candidate subskills so every child receives a unique, unpredictable sequence.
   */
  public getNextProgressiveSubskills(
    domainId: string,
    secureCodes: Set<string>,
    activeCodes: Set<string>,
    limit: number = 3
  ): string[] {
    const unlocked = this.getUnlockedSubskills(secureCodes, domainId);
    // Filter out already mastered or currently active
    const candidates = unlocked.filter(code => !secureCodes.has(code) && !activeCodes.has(code));
    if (candidates.length > 0) {
      // Randomize candidates so every session and every child gets a different mix
      const shuffled = [...candidates].sort(() => Math.random() - 0.5);
      return shuffled.slice(0, limit);
    }

    // Fallback: pick randomly from entry points
    const entries = this.getEntryPoints(domainId);
    const shuffledEntries = [...entries].sort(() => Math.random() - 0.5);
    return shuffledEntries.slice(0, limit);
  }

  public getNode(code: string): SubskillNode | undefined {
    return this.nodes.get(code);
  }

  public getDomainForSubskill(code: string): string {
    const node = this.nodes.get(code);
    if (node) return node.domain_id;
    if (code.startsWith('M-')) return 'MATHEMATICS';
    if (code.startsWith('E-')) return 'ENGLISH_LANGUAGE';
    if (code.startsWith('S-')) return 'SCIENCE_EVS';
    if (code.startsWith('L-')) return 'LOGICAL_REASONING';
    if (code.startsWith('W-')) return 'WORLD_KNOWLEDGE';
    return 'MATHEMATICS';
  }
}
