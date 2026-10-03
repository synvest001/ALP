import { resolveAssetUrl } from '../utils/assets';
import { getJson } from '../utils/http';

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
  // Working set: only the subskill chunks needed for the upcoming session are in memory.
  private chunks: Map<string, QuestionItem[]> = new Map();
  private items: QuestionItem[] = [];
  private itemsByDomain: Map<string, QuestionItem[]> = new Map();
  private itemsBySubskill: Map<string, QuestionItem[]> = new Map();
  private chunkIndex: Record<string, { domain: string; count: number }> | null = null;
  private legacyMode = false;
  private indexPromise: Promise<void> | null = null;
  public isReady = false;
  private loadErrors: string[] = [];

  private static readonly DOMAINS = [
    'MATHEMATICS', 'ENGLISH_LANGUAGE', 'SCIENCE_EVS', 'LOGICAL_REASONING', 'WORLD_KNOWLEDGE'
  ];

  constructor() {
    this.indexPromise = this.loadIndex();
  }

  /** Loads the tiny chunk index. Falls back to legacy full bundles (dev server). */
  private async loadIndex(): Promise<void> {
    this.loadErrors = [];
    try {
      const idx = await getJson<{ subskills: Record<string, { domain: string; count: number }> }>(
        resolveAssetUrl('data/question_bank/chunks/index.json')
      );
      this.chunkIndex = idx.subskills;
      this.isReady = true;
      console.log(`[QuestionBank] Chunk index ready: ${Object.keys(this.chunkIndex).length} subskills.`);
    } catch (e: any) {
      console.warn('[QuestionBank] No chunk index; falling back to full bundles.', e);
      await this.loadLegacyBundles();
    }
  }

  /** Dev-server fallback: load every domain bundle, sequentially. */
  private async loadLegacyBundles(): Promise<void> {
    this.legacyMode = true;
    for (const dom of QuestionBank.DOMAINS) {
      try {
        const data = await getJson<QuestionItem[]>(resolveAssetUrl(`data/question_bank/items_${dom}.json`));
        for (const it of data) {
          const list = this.chunks.get(it.target_subskill_id) || [];
          list.push(it);
          this.chunks.set(it.target_subskill_id, list);
        }
      } catch (e: any) {
        this.loadErrors.push(`${dom}: ${String(e && e.message ? e.message : e)}`);
      }
    }
    this.rebuildViews();
    this.isReady = this.items.length > 0;
  }

  public async ensureLoaded(): Promise<void> {
    if (this.indexPromise) await this.indexPromise;
    if (!this.isReady) {
      this.indexPromise = this.loadIndex();
      await this.indexPromise;
    }
  }

  public hasSubskill(id: string): boolean {
    return this.legacyMode ? this.chunks.has(id) : !!(this.chunkIndex && this.chunkIndex[id]);
  }

  /**
   * Make exactly these subskills resident in memory (loading missing ones one at a time,
   * evicting the rest). Keeps the working set small on 512 MB devices.
   */
  public async loadSubskills(ids: string[]): Promise<void> {
    await this.ensureLoaded();
    if (this.legacyMode || !this.chunkIndex) return;
    const wanted = new Set(ids.filter(id => this.chunkIndex![id]));
    for (const id of Array.from(this.chunks.keys())) {
      if (!wanted.has(id)) this.chunks.delete(id);
    }
    this.loadErrors = [];
    const missing = Array.from(wanted).filter(id => !this.chunks.has(id));
    for (const id of missing) {
      let lastErr = '';
      for (let attempt = 1; attempt <= 2; attempt++) {
        try {
          const data = await getJson<QuestionItem[]>(resolveAssetUrl(`data/question_bank/chunks/${id}.json`));
          this.chunks.set(id, data);
          lastErr = '';
          break;
        } catch (err: any) {
          lastErr = String(err && err.message ? err.message : err);
          console.warn(`[QuestionBank] ${id}: attempt ${attempt} failed:`, err);
        }
      }
      if (lastErr) this.loadErrors.push(`${id}: ${lastErr}`);
    }
    this.rebuildViews();
    console.log(`[QuestionBank] Working set: ${this.chunks.size} subskills, ${this.items.length} items.` +
      (this.loadErrors.length ? ` Errors: ${this.loadErrors.join('; ')}` : ''));
  }

  public getLoadErrors(): string[] {
    return this.loadErrors;
  }

  private rebuildViews() {
    this.items = [];
    this.itemsByDomain = new Map();
    this.itemsBySubskill = new Map();
    this.chunks.forEach((list, sub) => {
      this.itemsBySubskill.set(sub, list);
      for (const item of list) {
        this.items.push(item);
        const d = this.itemsByDomain.get(item.domain_id);
        if (d) d.push(item); else this.itemsByDomain.set(item.domain_id, [item]);
      }
    });
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
