export interface LearnerSkillProfile {
  id: string;
  name: string;
  dueEvents: {
    type: 'RETRIEVAL' | 'REMEDIATION_BRANCH_1';
    target_subskill_id: string;
    domain_id: string;
    phase_context: string;
    task_function_type: string;
  }[];
  // 14-day rolling actuals (percentages 0-100)
  trailing14DayDomainActuals: Record<string, number>;
  trailing14DayFunctionActuals: Record<string, number>;
  // Capability profile for Workstream 7 later
  modality_capabilities: {
    permitted: string[];
    restricted: string[];
  }
}

export const MockProfile: LearnerSkillProfile = {
  id: "student_001",
  name: "Leo",
  // Mock some due events (e.g. a retrieval checkpoint that's due)
  dueEvents: [
    {
      type: 'RETRIEVAL',
      target_subskill_id: 'M-OP-05', // Math Domain
      domain_id: 'MATHEMATICS',
      phase_context: 'PHASE_C',
      task_function_type: 'RETRIEVAL'
    }
  ],
  // Mock actuals - let's make Math underrepresented so the engine prioritizes it
  trailing14DayDomainActuals: {
    'MATHEMATICS': 20, // Target 30-40, deficit = 10
    'ENGLISH_LANGUAGE': 40, // Target 25-35, over by 5
    'SCIENCE_EVS_WORLD_KNOWLEDGE': 25, // Target 15-25, at ceiling
    'LOGICAL_REASONING': 15 // Target 10-20, within range
  },
  trailing14DayFunctionActuals: {
    'FOCUSED_CORE': 20, // Target 25-35, deficit = 5
    'RETRIEVAL': 30, // Target 15-25, over by 5
    'CONSOLIDATION': 20, // Target 15-25, within range
    'STRATEGIC_REASONING': 20, // Target 15-25, within range
    'CREATIVE_TRANSFER': 10 // Target 10-20, within range
  },
  modality_capabilities: {
    permitted: ["TAP_SELECT", "SPOKEN_DICTATED"],
    restricted: ["HANDWRITTEN_STYLUS"]
  }
};
