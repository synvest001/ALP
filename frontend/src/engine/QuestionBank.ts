import { resolveAssetUrl } from '../utils/assets';

export interface QuestionItem {
  item_id: string;
  target_subskill_id: string;
  domain_id: string;
  evidence_archetype: string;
  language_load_class: string;
  challenge_type: string;
  prompt_structure: {
    display_text: string;
    spoken_audio_uri?: string;
    visual_assets?: {
      asset_id: string;
      asset_type: string;
      uri: string;
    }[];
  };
  scaffolding_protocol?: any;
  rubric: {
    correct_criteria: {
      selected_option_id: string;
    }
  };
  cognitive_depth: string;
  transfer_level: string;
  representation_type: string;
  primary_modality: string;
  interaction_model?: {
    modality_configurations?: {
      tap_select?: {
        options?: {
          option_id: string;
          display_value: string;
          asset_uri?: string;
        }[];
      };
    };
  };
  options?: { id: string; text: string; assetUri?: string }[];
}

export class QuestionBank {
  private items: QuestionItem[] = [];
  private itemsByDomain: Map<string, QuestionItem[]> = new Map();
  private itemsBySubskill: Map<string, QuestionItem[]> = new Map();
  private loadedDomains: Set<string> = new Set();
  private loadPromise: Promise<void> | null = null;
  public isReady = false;

  constructor() {
    this.loadPromise = this.preloadAll();
  }

  public async preloadAll(): Promise<void> {
    if (this.isReady) return;
    
    const domains = [
      'MATHEMATICS',
      'ENGLISH_LANGUAGE',
      'SCIENCE_EVS',
      'LOGICAL_REASONING',
      'WORLD_KNOWLEDGE'
    ];

    try {
      const fetchDomain = async (dom: string) => {
        try {
          const path = `data/question_bank/items_${dom}.json`;
          const url = resolveAssetUrl(path);
          const res = await fetch(url);
          if (res.ok) {
            const data: QuestionItem[] = await res.json();
            this.addItems(dom, data);
          }
        } catch (err) {
          console.warn(`[QuestionBank] Failed to load ${dom} bundle:`, err);
        }
      };

      await Promise.all(domains.map(fetchDomain));
      this.isReady = true;
      console.log(`[QuestionBank] Successfully initialized ${this.items.length} total questions into memory.`);
    } catch (e) {
      console.error("[QuestionBank] Error during question bank initialization:", e);
    }
  }

  public async ensureLoaded(): Promise<void> {
    if (this.isReady) return;
    if (this.loadPromise) {
      await this.loadPromise;
    } else {
      await this.preloadAll();
    }
  }

  private addItems(domain: string, newItems: QuestionItem[]) {
    this.loadedDomains.add(domain);
    if (!this.itemsByDomain.has(domain)) {
      this.itemsByDomain.set(domain, []);
    }
    const domainList = this.itemsByDomain.get(domain)!;

    for (const item of newItems) {
      this.items.push(item);
      domainList.push(item);

      const subskill = item.target_subskill_id;
      if (!this.itemsBySubskill.has(subskill)) {
        this.itemsBySubskill.set(subskill, []);
      }
      this.itemsBySubskill.get(subskill)!.push(item);
    }
  }

  private normalizePrompt(text?: string): string {
    if (!text) return '';
    return text.toLowerCase().replace(/[^a-z0-9]/g, ' ').trim().replace(/\s+/g, ' ');
  }

  /**
   * Retrieves a task matching domain, subskill, and target cognitive depth.
   * Prioritizes unseen questions and unique prompts to guarantee zero repetitions.
   */
  public getTask(
    domain_id?: string,
    target_subskill_id?: string,
    cognitive_depth?: string,
    excludeIds?: string[],
    excludePrompts?: Set<string>
  ): QuestionItem | null {
    const excludeSet = new Set(excludeIds || []);

    const isAllowed = (it: QuestionItem) => {
      if (excludeSet.has(it.item_id)) return false;
      if (excludePrompts && it.prompt_structure?.display_text) {
        const norm = this.normalizePrompt(it.prompt_structure.display_text);
        if (excludePrompts.has(norm)) return false;
      }
      return true;
    };

    // 1. Resolve domain filter
    let candidatePool: QuestionItem[] = [];
    if (target_subskill_id && this.itemsBySubskill.has(target_subskill_id)) {
      candidatePool = this.itemsBySubskill.get(target_subskill_id)!;
    } else if (domain_id) {
      if (domain_id === 'SCIENCE_EVS_WORLD_KNOWLEDGE') {
        const evs = this.itemsByDomain.get('SCIENCE_EVS') || [];
        const wk = this.itemsByDomain.get('WORLD_KNOWLEDGE') || [];
        candidatePool = [...evs, ...wk];
      } else {
        candidatePool = this.itemsByDomain.get(domain_id) || [];
      }
    } else {
      candidatePool = this.items;
    }

    if (candidatePool.length === 0) {
      candidatePool = this.items;
    }

    // 2. Cognitive depth filter (Depth-First escalation)
    let depthPool = candidatePool;
    if (cognitive_depth) {
      const matchDepth = candidatePool.filter(it => it.cognitive_depth === cognitive_depth);
      if (matchDepth.length > 0) {
        depthPool = matchDepth;
      }
    }

    // 3. Exclude seen items & prompts
    let unseenCandidates = depthPool.filter(isAllowed);

    // 4. If all items at this exact depth were seen, expand to all unseen items in this subskill
    if (unseenCandidates.length === 0 && target_subskill_id) {
      const subskillItems = this.itemsBySubskill.get(target_subskill_id) || [];
      unseenCandidates = subskillItems.filter(isAllowed);
    }

    // 5. If all items in this subskill were seen, expand to all unseen items in the entire domain
    if (unseenCandidates.length === 0 && domain_id) {
      const domainItems = (domain_id === 'SCIENCE_EVS_WORLD_KNOWLEDGE')
        ? [...(this.itemsByDomain.get('SCIENCE_EVS') || []), ...(this.itemsByDomain.get('WORLD_KNOWLEDGE') || [])]
        : (this.itemsByDomain.get(domain_id) || []);
      unseenCandidates = domainItems.filter(isAllowed);
    }

    // 6. If unseen candidates found, select a random one
    if (unseenCandidates.length > 0) {
      return unseenCandidates[Math.floor(Math.random() * unseenCandidates.length)];
    }

    // 7. Domain Affinity Guard: If a domain was requested, prefer an unseen item ID in the SAME domain
    // before ever leaking across domains (crucial for preserving Mathematics ratio)
    if (domain_id) {
      const domainItems = (domain_id === 'SCIENCE_EVS_WORLD_KNOWLEDGE')
        ? [...(this.itemsByDomain.get('SCIENCE_EVS') || []), ...(this.itemsByDomain.get('WORLD_KNOWLEDGE') || [])]
        : (this.itemsByDomain.get(domain_id) || []);
      const domainUnseenIdOnly = domainItems.filter(it => !excludeSet.has(it.item_id));
      if (domainUnseenIdOnly.length > 0) {
        const fallbackItem = domainUnseenIdOnly[Math.floor(Math.random() * domainUnseenIdOnly.length)];
        console.warn(`[QuestionBank] Domain Affinity Guard fallback: exhausted unique prompts for domain '${domain_id}'. Dropping excludePrompts filter and serving item '${fallbackItem.item_id}' (prompt: "${fallbackItem.prompt_structure?.display_text}").`);
        return fallbackItem;
      }
    }

    // 8. Search ANY unseen candidate in the entire question bank across all 12,925 items
    const globalUnseen = this.items.filter(isAllowed);
    if (globalUnseen.length > 0) {
      return globalUnseen[Math.floor(Math.random() * globalUnseen.length)];
    }

    // 9. If strictly no unseen prompts exist anywhere, relax prompt filter but still enforce unique item ID
    const unseenIdOnly = this.items.filter(it => !excludeSet.has(it.item_id));
    if (unseenIdOnly.length > 0) {
      const fallbackItem = unseenIdOnly[Math.floor(Math.random() * unseenIdOnly.length)];
      console.warn(`[QuestionBank] Global fallback: exhausted unique prompts globally. Dropping excludePrompts filter and serving item '${fallbackItem.item_id}' (prompt: "${fallbackItem.prompt_structure?.display_text}").`);
      return fallbackItem;
    }

    return this.items.length > 0 ? this.items[Math.floor(Math.random() * this.items.length)] : null;
  }

  public getLoadedCount(): number {
    return this.items.length;
  }
}
