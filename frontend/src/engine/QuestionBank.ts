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
        }[];
      };
    };
  };
  options?: { id: string, text: string }[];
}

export class QuestionBank {
  private items: QuestionItem[] = [];

  constructor() {
    this.loadItems();
  }

  private loadItems() {
    // Dynamically load all JSONs from question_bank using Vite's glob import
    // Note: Since this is executed in the browser, the relative path must point to the root where question_bank resides during dev.
    // In production, we'd need to bundle this or fetch from an API.
    const modules = import.meta.glob('../../../question_bank/items/**/*.json', { eager: true });
    
    for (const path in modules) {
      const item = (modules[path] as any).default || modules[path];
      
      // Filter out mock items that are missing visual assets
      if (item.prompt_structure?.visual_assets && item.prompt_structure.visual_assets.length > 0) {
        this.items.push(item);
      }
    }
    console.log(`QuestionBank loaded ${this.items.length} fully populated items with visuals.`);
  }

  public getTask(
    domain_id: string,
    target_subskill_id?: string,
    cognitive_depth?: string
  ): QuestionItem | null {
    
    // Filter available items based on criteria
    let candidates = this.items.filter(item => item.domain_id === domain_id);
    
    if (target_subskill_id) {
      candidates = candidates.filter(item => item.target_subskill_id === target_subskill_id);
    }
    
    if (cognitive_depth) {
      candidates = candidates.filter(item => item.cognitive_depth === cognitive_depth);
    }

    if (candidates.length > 0) {
      // Pick a random candidate from the matching ones
      const randomIndex = Math.floor(Math.random() * candidates.length);
      return candidates[randomIndex];
    }

    // Fallback if no exact match (e.g. for mock data)
    const fallbackCandidates = this.items.filter(item => item.domain_id === domain_id);
    if (fallbackCandidates.length > 0) {
      return fallbackCandidates[Math.floor(Math.random() * fallbackCandidates.length)];
    }
    
    // Ultimate fallback to anything
    return this.items.length > 0 ? this.items[Math.floor(Math.random() * this.items.length)] : null;
  }
}
