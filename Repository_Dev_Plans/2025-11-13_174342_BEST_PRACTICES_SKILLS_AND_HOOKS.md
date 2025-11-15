# Best Practices Guide: Claude Code Skills and Hooks

## Table of Contents
1. [Overview](#overview)
2. [Conceptual Framework](#conceptual-framework)
3. [Skills Architecture](#skills-architecture)
4. [Hooks Architecture](#hooks-architecture)
5. [Integration Patterns](#integration-patterns)
6. [File Structure](#file-structure)
7. [Maintenance and Updates](#maintenance-and-updates)
8. [Lessons Learned](#lessons-learned)

---

## Overview

This guide documents best practices for implementing Claude Code skills and hooks using the RICS APC Assessment Pipeline as a reference implementation. The RICS system demonstrates how to structure 115+ domain-specific competencies as autonomous skills with intelligent activation through hooks.

**Key Success Factors:**
- Token-efficient skill architecture (skills load on-demand, not all at once)
- Autonomous skill activation based on context (Claude decides when to load)
- Proper file structure following Claude Code conventions
- Intelligent hook triggers for skill suggestions
- Maintainable, scalable system design

---

## Conceptual Framework

### The Problem Space

**Challenge:** Domain experts need AI assistance that:
- Understands specialized terminology and standards
- Provides contextually relevant guidance
- Scales to hundreds of domain topics
- Loads efficiently (doesn't consume unnecessary tokens)
- Activates autonomously when relevant

**RICS Example:** Assessors evaluate candidates across:
- 21 pathways (Commercial Real Estate, Building Surveying, etc.)
- 115 competencies (Inspection, Valuation, Ethics, etc.)
- 3 proficiency levels (L1 Knowledge, L2 Application, L3 Reasoned Advice)
- Each assessment requires loading only 8-12 relevant competencies

### The Solution Pattern

**Skills** provide domain knowledge:
- Each skill = one domain topic (e.g., "Inspection" competency)
- Contains definitions, assessment criteria, sample questions, red flags
- Claude loads autonomously when relevant to conversation

**Hooks** provide intelligent activation:
- Monitor user prompts for domain keywords/patterns
- Suggest relevant skills before Claude responds
- Create feedback loops (e.g., after reading a file, suggest related skills)

**Result:** Claude has access to deep domain expertise but only loads what's needed for the current context.

---

## Skills Architecture

### 1. Proper File Structure

**CRITICAL:** Skills must follow Claude Code's exact structure.

```
.claude/skills/
├── inspection/                    # Each skill in own directory
│   └── SKILL.md                  # Must be named "SKILL.md"
├── measurement/
│   └── SKILL.md
├── valuation/
│   └── SKILL.md
└── ethics-rules-of-conduct-and-professionalism/
    └── SKILL.md
```

**Common Mistake:** Don't do this:
```
❌ .claude/skills/inspection.md           # Wrong - flat file structure
❌ .claude/skills/inspection/skill.md     # Wrong - lowercase
❌ .claude/skills/inspection/README.md    # Wrong - different name
```

### 2. YAML Frontmatter Requirements

Every `SKILL.md` must start with YAML frontmatter:

```yaml
---
name: inspection
description: Inspection - RICS APC competency assessment guidance
---
```

**Frontmatter Rules:**
- `name`: lowercase letters, numbers, hyphens only (max 64 chars)
- `description`: Critical for discovery - explains what AND when to use (max 1024 chars)
- Optional: `allowed-tools` to restrict tool access (Read, Grep, Glob only for read-only skills)

**Best Practice Descriptions:**

```yaml
# ✅ Good - explains purpose AND context
description: "Inspection - RICS APC competency assessment guidance (project)"

# ❌ Bad - too vague
description: "Inspection competency"

# ✅ Good - indicates when to use
description: "Ethics, rules of conduct and professionalism - RICS APC mandatory L3 competency with interview focus on ethical dilemmas"
```

### 3. Skill Content Structure

**RICS Pattern (adapt to your domain):**

```markdown
---
name: inspection
description: Inspection - RICS APC competency assessment guidance
---

# Inspection

**Competency Slug**: `competency-inspection`

## Overview
[Brief context about this competency]

---

## Generic Definition

### Level 1: Knowledge and Understanding
**Definition**: [What this level requires]

### Level 2: Application of Knowledge
**Definition**: [What this level requires]

### Level 3: Reasoned Advice and Depth of Knowledge
**Definition**: [What this level requires]

---

## Pathway-Specific Assessment Guidance

**This competency appears in 5 pathway(s)**:

### Building Surveying

#### Level 3

**Expected Evidence**:
- [Specific examples of what candidates should demonstrate]

**Sample Questions**:
- "What are the different RICS Home Survey levels?"
- "Explain the purpose and content of a Schedule of Condition."

**Sufficient Response Indicators**:
- [What good answers look like]

**Red Flags**:
- [Warning signs of insufficient competence]

---

### Commercial Real Estate

[Repeat pattern for each pathway]

---

## Usage in Assessment Commands

This skill is automatically loaded when:
- The competency name is mentioned in candidate submissions
- Assessment commands reference this competency
- Assessors query about assessment criteria

---
```

### 4. Naming Conventions

**Skill Directory Names:**
- Use lowercase with hyphens
- Match the canonical name of your domain topic
- Be consistent across all skills

**RICS Examples:**
```
✅ inspection
✅ measurement
✅ valuation
✅ ethics-rules-of-conduct-and-professionalism
✅ communication-and-negotiation
✅ building-information-modelling-bim-management

❌ Inspection (uppercase)
❌ inspection_competency (underscores)
❌ inspect (abbreviated)
```

### 5. Token Efficiency

**Problem:** If Claude loads all 115 skills at once = token budget explosion

**Solution:** Skills are loaded on-demand
- User mentions "inspection" → Claude loads inspection skill
- User reads pathway guide → Hook suggests relevant skills
- Only 8-12 skills loaded per conversation (not all 115)

**Design Principle:** Each skill should be:
- **Self-contained:** All context within the skill file
- **Focused:** One domain topic per skill
- **Referenceable:** Can cite specific sections from other docs if needed

---

## Hooks Architecture

### 1. Hook Types

Claude Code supports multiple hook types. RICS uses two:

**UserPromptSubmit Hook:**
- Triggers: When user submits a message
- Purpose: Analyze prompt for domain keywords/patterns
- Output: Suggest skills BEFORE Claude responds
- Use Case: Reactive - responds to user mentions

**PreToolUse Hook:**
- Triggers: BEFORE Read tool executes (proactive)
- Purpose: Detect context files (assessment caches, pathway guides) and suggest skills
- Output: Suggest skills before file is read (96% token efficiency vs reactive)
- Use Case: Proactive - anticipates needs based on file being read

**Why PreToolUse over PostToolUse?**
- **Token Efficiency**: 96% reduction (1KB lookup vs 24KB file processing)
- **Proactive Loading**: Skills suggested before file read, not after
- **Candidate Context**: Can synchronously read assessment cache to detect candidate-specific competencies
- **Simpler Architecture**: Eliminates need for deduplication logic between hooks

### 2. Settings Configuration

**File:** `.claude/settings.json`

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/skill-activation-prompt.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-skill-loader.sh"
          }
        ]
      }
    ]
  }
}
```

**Key Elements:**
- `matcher`: Tool name pattern (regex) for filtering (PreToolUse only monitors "Read", not "Glob")
- `command`: Path to shell script using `$CLAUDE_PROJECT_DIR` variable
- `type`: "command" for shell scripts

**Design Choice: Why Only "Read"?**
- Assessment caches and pathway guides are always accessed via Read tool
- Glob tool returns file lists (no content to analyze proactively)
- Keeps hook execution focused and efficient

### 3. Hook Implementation Pattern

**Shell Wrapper Script:**
```bash
#!/bin/bash
set -e

cd "$CLAUDE_PROJECT_DIR/.claude/hooks"
cat | npx tsx pre-tool-use-skill-loader.ts
```

**Why This Pattern?**
- Shell script handles directory navigation
- TypeScript handles business logic
- Reads JSON from stdin, outputs text to stdout
- Error handling with `set -e`

**TypeScript Implementation (PreToolUse):**
```typescript
#!/usr/bin/env node
import { readFileSync } from 'fs';
import { join } from 'path';

interface HookInput {
    session_id: string;
    transcript_path: string;
    cwd: string;
    permission_mode: string;
    tool: string;              // Tool being invoked (Read, Write, etc.)
    parameters: any;           // Tool parameters (e.g., file_path)
}

async function main() {
    try {
        // Read input from stdin
        const input = readFileSync(0, 'utf-8');
        const data: HookInput = JSON.parse(input);

        // Only process Read tool
        if (data.tool !== 'Read') {
            process.exit(0);
        }

        const filePath = data.parameters.file_path;
        if (!filePath) {
            process.exit(0);
        }

        const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();

        // PRIORITY 1: Check for Assessment Cache
        if (filePath.endsWith('00_Assessment_Cache.json')) {
            const output = handleAssessmentCache(filePath);
            if (output) {
                console.log(output);
                process.exit(0);
            }
        }

        // PRIORITY 2: Check for Pathway Guide
        if (/ASSESSMENT_GUIDE|PATHWAY_SUMMARY|pathway_guide/i.test(filePath)) {
            const output = handlePathwayGuide(filePath, projectDir);
            if (output) {
                console.log(output);
                process.exit(0);
            }
        }

        process.exit(0);
    } catch (err) {
        // Fail silently - don't block tool execution
        console.error('Error:', err);
        process.exit(0);  // Exit 0, not 1 - hooks should never block
    }
}

main();
```

**Key Differences from UserPromptSubmit:**
- Input includes `tool` and `parameters` instead of `prompt`
- Can read files synchronously BEFORE main tool executes
- Two priority handlers: assessment cache (Priority 1) and pathway guides (Priority 2)
- Fail silently with `exit(0)` to never block tool execution

### 4. Skill Rules File

**Purpose:** Central configuration for skill matching

**Location:** `.claude/skill-rules.json`

```json
{
  "version": "1.0",
  "description": "Skill activation triggers",
  "skills": {
    "inspection": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "Inspection - RICS APC competency assessment guidance",
      "promptTriggers": {
        "keywords": [
          "inspection",
          "inspection competency",
          "building inspection",
          "property inspection"
        ],
        "intentPatterns": [
          "inspection.*?(L1|L2|L3|level|competency)",
          "(demonstrate|assess|evaluate|review).*?inspection",
          "inspection.*?(evidence|demonstration)"
        ]
      }
    },
    "ethics-rules-of-conduct-and-professionalism": {
      "type": "guardrail",
      "enforcement": "suggest",
      "priority": "critical",
      "description": "Ethics mandatory L3 competency",
      "promptTriggers": {
        "keywords": [
          "ethics",
          "professional conduct",
          "rules of conduct"
        ],
        "intentPatterns": [
          "ethics.*?(dilemma|conflict|breach)",
          "professional.*?(conduct|standards)"
        ]
      }
    }
  }
}
```

**Priority Levels:**
- `critical`: Must-have skills (e.g., Ethics L3)
- `high`: Core competencies, mandatory competencies
- `medium`: Optional/specialized competencies
- `low`: Rarely needed, trigger only on exact match

**Enforcement Types:**
- `suggest`: Show suggestion, don't block
- `warn`: Show warning, allow proceeding
- `block`: Require skill activation (guardrail)

### 5. Auto-Generation Pattern

**Generate skill-rules.json from skill files:**

```javascript
#!/usr/bin/env node
import { readdirSync, readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const CLAUDE_DIR = '/path/to/.claude';
const SKILLS_DIR = join(CLAUDE_DIR, 'skills');
const OUTPUT_FILE = join(CLAUDE_DIR, 'skill-rules.json');

function main() {
    const skills = {};

    // Read all skill directories
    const skillDirs = readdirSync(SKILLS_DIR, { withFileTypes: true })
        .filter(dirent => dirent.isDirectory())
        .map(dirent => dirent.name)
        .sort();

    for (const skillName of skillDirs) {
        const skillFilePath = join(SKILLS_DIR, skillName, 'SKILL.md');
        const content = readFileSync(skillFilePath, 'utf-8');

        skills[skillName] = {
            type: 'domain',
            enforcement: 'suggest',
            priority: determinePriority(skillName),
            description: extractDescription(skillName, content),
            promptTriggers: {
                keywords: generateKeywords(skillName),
                intentPatterns: generateIntentPatterns(skillName)
            }
        };
    }

    const output = {
        version: '1.0',
        description: 'Auto-generated skill activation triggers',
        skills: skills
    };

    writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
    console.log(`✅ Generated skill-rules.json with ${skillDirs.length} skills`);
}

main();
```

---

## Integration Patterns

### Pattern 1: Prompt Analysis (UserPromptSubmit)

**Use Case:** User asks about a domain topic

**Flow:**
1. User types: "Tell me about inspection competency for Level 3"
2. Hook triggers before Claude responds
3. Hook analyzes prompt for keywords ("inspection", "Level 3")
4. Hook outputs: "🎯 RECOMMENDED SKILLS: → inspection"
5. Claude sees suggestion and loads inspection skill autonomously
6. Claude responds with inspection competency details

**Implementation:**
```typescript
function analyzePrompt(prompt: string, rules: SkillRules): MatchedSkill[] {
    const lowerPrompt = prompt.toLowerCase();
    const matches: MatchedSkill[] = [];

    for (const [skillName, config] of Object.entries(rules.skills)) {
        // Keyword matching
        if (config.promptTriggers?.keywords) {
            const keywordMatch = config.promptTriggers.keywords.some(kw =>
                lowerPrompt.includes(kw.toLowerCase())
            );
            if (keywordMatch) {
                matches.push({ name: skillName, matchType: 'keyword', config });
                continue;
            }
        }

        // Intent pattern matching (regex)
        if (config.promptTriggers?.intentPatterns) {
            const intentMatch = config.promptTriggers.intentPatterns.some(pattern => {
                const regex = new RegExp(pattern, 'i');
                return regex.test(lowerPrompt);
            });
            if (intentMatch) {
                matches.push({ name: skillName, matchType: 'intent', config });
            }
        }
    }

    return matches;
}
```

### Pattern 2: Proactive File Context Detection (PreToolUse)

**Use Case:** User reads assessment cache or pathway guide

**Flow:**
1. User: `Read Candidates/Smith_John_Q1_2024/AI_Assessment/00_Assessment_Cache.json`
2. **PreToolUse hook triggers BEFORE read executes**
3. Hook detects filename pattern (`00_Assessment_Cache.json`)
4. Hook **synchronously reads cache file** (advantage: can read before main tool)
5. Hook extracts candidate-specific competencies: 18 declared (11 mandatory + 3 core + 4 optional)
6. Hook outputs: "⚡ PROACTIVE SKILL LOADING: John Smith, 18 competencies detected"
7. **Read tool then executes** (user's original request)
8. Claude sees suggestion and loads relevant skills proactively

**Token Efficiency:** 96% reduction vs reactive approach
- Reactive (PostToolUse): Process full 24KB file contents
- Proactive (PreToolUse): 1KB lookup in pathway-competencies-map.json

**Implementation (Priority 1: Assessment Cache):**
```typescript
function handleAssessmentCache(filePath: string): string | null {
    try {
        // ADVANTAGE: Can read file synchronously BEFORE main Read tool
        const cacheContent = readFileSync(filePath, 'utf-8');
        const cache: AssessmentCache = JSON.parse(cacheContent);

        // Extract metadata
        const candidateName = cache.metadata.candidate_name;
        const pathway = cache.metadata.pathway;

        // Extract and normalize competency names
        const mandatory = cache.competency_selection.mandatory
            .map(c => normalizeCompetencyName(c.name));
        const core = cache.competency_selection.core
            .map(c => normalizeCompetencyName(c.name));
        const optional = cache.competency_selection.optional
            .map(c => normalizeCompetencyName(c.name));

        return formatCandidateCompetencies(candidateName, pathway, {
            mandatory, core, optional
        });
    } catch (err) {
        return null;  // Fail gracefully
    }
}
```

**Implementation (Priority 2: Pathway Guides):**
```typescript
function handlePathwayGuide(filePath: string, projectDir: string): string | null {
    try {
        // Extract pathway from filename (e.g., "commercial_real_estate")
        const pathwayName = extractPathwayFromPath(filePath);
        if (!pathwayName) return null;

        // Load pathway competencies map (1KB lookup, not 24KB file read)
        const mapPath = join(projectDir, '.claude', 'hooks', 'pathway-competencies-map.json');
        const pathwayMap = JSON.parse(readFileSync(mapPath, 'utf-8'));

        // Get competencies for this pathway
        const pathwayData = pathwayMap.pathways[pathwayName];
        if (!pathwayData) return null;

        return formatPathwayCompetencies(pathwayName, {
            core: pathwayData.core,
            common_optional: pathwayData.common_optional,
            mandatory: pathwayMap.mandatory_all_pathways
        });
    } catch (err) {
        return null;
    }
}

function extractPathwayFromPath(filePath: string): string | null {
    const fileName = basename(filePath).toLowerCase();

    // Remove common suffixes to extract pathway name
    return fileName
        .replace(/_assessment_guide\.md$/i, '')
        .replace(/_pathway_summary\.md$/i, '')
        .replace(/_pathway_guide\.pdf$/i, '')
        .replace(/_(january|...|december)_\d{4}/i, '')
        .replace(/\.(md|pdf)$/i, '') || null;
}
```

### Pattern 3: Data File Architecture

**Challenge:** Balancing token efficiency with comprehensive coverage

**Solution:** Two complementary data files

**File 1: `skill-rules.json`** (Competency-Centric)
- Used by: UserPromptSubmit hook
- Purpose: Match user prompts to competencies
- Structure: 115 competencies → keywords + intent patterns
- Size: ~60KB
- Update frequency: Regenerated when skills change

**File 2: `pathway-competencies-map.json`** (Pathway-Centric)
- Used by: PreToolUse hook
- Purpose: Map pathways to competencies (O(1) lookup)
- Structure: 21 pathways → core + optional competencies
- Size: ~7KB
- Update frequency: Manual when RICS updates pathway requirements

**Why Two Files?**
- **Different access patterns**: UserPromptSubmit needs keyword matching, PreToolUse needs pathway lookup
- **Performance**: O(1) pathway lookup (1KB) vs O(n) file content analysis (24KB)
- **Maintenance**: skill-rules.json auto-generated, pathway-map manually curated
- **Separation of concerns**: Competency definitions vs pathway structure

**Example pathway-competencies-map.json:**
```json
{
  "version": "1.0",
  "pathways": {
    "commercial_real_estate": {
      "core": ["inspection", "measurement", "valuation"],
      "common_optional": ["landlord-and-tenant", "leasing-and-letting", ...]
    },
    "building_surveying": {
      "core": ["inspection", "measurement", "valuation"],
      "common_optional": ["conservation-and-restoration", ...]
    }
  },
  "mandatory_all_pathways": [
    "ethics-rules-of-conduct-and-professionalism",
    "client-care",
    ...
  ]
}
```

---

## File Structure

### Complete Directory Layout

```
project-root/
├── .claude/
│   ├── settings.json                    # Hook configuration (2 hooks)
│   ├── skill-rules.json                 # Skill activation rules (auto-generated)
│   ├── commands/                        # Slash commands
│   │   ├── Core_Pipeline/
│   │   │   ├── 01-initial-submission-review.md
│   │   │   └── [25 more commands]
│   │   ├── Preliminary_Review/
│   │   ├── QA_Commands/
│   │   └── Utilities/
│   ├── hooks/                           # Hook scripts
│   │   ├── skill-activation-prompt.sh      # UserPromptSubmit wrapper
│   │   ├── skill-activation-prompt.ts      # UserPromptSubmit logic
│   │   ├── pre-tool-use-skill-loader.sh    # PreToolUse wrapper
│   │   ├── pre-tool-use-skill-loader.ts    # PreToolUse logic
│   │   ├── generate-skill-rules.js         # Auto-generates skill-rules.json
│   │   ├── pathway-competencies-map.json   # Pathway → competencies mapping
│   │   ├── package.json                    # Node dependencies (tsx)
│   │   └── README.md                       # Hook documentation (v2.1)
│   └── skills/                          # 115 competency skills
│       ├── inspection/
│       │   └── SKILL.md
│       ├── measurement/
│       │   └── SKILL.md
│       ├── valuation/
│       │   └── SKILL.md
│       ├── ethics-rules-of-conduct-and-professionalism/
│       │   └── SKILL.md
│       └── [111 more skills]/
│           └── SKILL.md
├── RICS_APC_Assessment_Guides/          # Assessment guides reference skills
│   ├── commercial_real_estate_FEBRUARY_2024_ASSESSMENT_GUIDE.md
│   └── [20 more guides]
└── Candidates/                          # Working directories
    └── {LastName}_{FirstName}_{Period}/
        ├── Submission_Documents/
        └── AI_Assessment/
            ├── 00_Assessment_Cache.json # Proactively detected by PreToolUse
            ├── 01_Initial_Review/
            └── [other assessment outputs]
```

### File Path References

**CRITICAL:** All paths must use `$CLAUDE_PROJECT_DIR` environment variable

```typescript
// ✅ Correct - uses environment variable
const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const rulesPath = join(projectDir, '.claude', 'skill-rules.json');

// ❌ Wrong - hardcoded absolute path (breaks on different machines)
const rulesPath = '/workspaces/RICS-APC-prep/.claude/skill-rules.json';

// ❌ Wrong - relative path (breaks depending on cwd)
const rulesPath = '../../.claude/skill-rules.json';
```

**In settings.json:**
```json
{
  "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/skill-activation-prompt.sh"
}
```

---

## Maintenance and Updates

### 1. Adding New Skills

**Process:**
1. Create skill directory: `.claude/skills/new-competency/`
2. Create `SKILL.md` with proper frontmatter and content
3. Regenerate skill-rules.json: `node .claude/hooks/generate-skill-rules.js`
4. Test skill activation: Mention competency name in prompt
5. Verify: `Skill tool should recognize new-competency`

### 2. Updating Existing Skills

**Best Practice:**
- Edit skill content in `SKILL.md` directly
- No need to regenerate skill-rules.json unless changing name/description
- Skills reload on each invocation (changes take effect immediately)

### 3. Modifying Hook Logic

**Testing UserPromptSubmit Changes:**
```bash
# Test with sample user prompt
echo '{"prompt":"tell me about inspection","session_id":"test"}' | \
  .claude/hooks/skill-activation-prompt.sh
```

**Testing PreToolUse Changes:**
```bash
# Test assessment cache detection
echo '{"tool":"Read","parameters":{"file_path":"Candidates/Smith_John_Q1_2024/AI_Assessment/00_Assessment_Cache.json"}}' | \
  .claude/hooks/pre-tool-use-skill-loader.sh

# Test pathway guide detection
echo '{"tool":"Read","parameters":{"file_path":"RICS_APC_Assessment_Guides/building_surveying_ASSESSMENT_GUIDE.md"}}' | \
  .claude/hooks/pre-tool-use-skill-loader.sh
```

**Common Changes:**
- **UserPromptSubmit**: Add new keyword patterns → Update `generateKeywords()` in generator
- **UserPromptSubmit**: Add new intent patterns → Update `generateIntentPatterns()`
- **PreToolUse**: Add new file patterns → Update detection regex in handler functions
- **PreToolUse**: Add new pathways → Update `pathway-competencies-map.json`
- **Both**: Change priority logic → Update `getPriority()` function
- **Both**: Modify output format → Update `formatSuggestions()`

### 4. Versioning Strategy

**skill-rules.json versioning:**
```json
{
  "version": "1.0",
  "generation": {
    "generated": "2025-11-13T17:00:00Z",
    "generator": "generate-skill-rules.js",
    "total_skills": 115
  }
}
```

**Track changes:**
- Commit skill-rules.json to git
- Document breaking changes in hooks README
- Version hook scripts if making breaking changes

### 5. Performance Optimization

**Token Budget Management:**
- Average skill size: ~15-20KB
- Loading 10 skills = ~150-200KB
- Keep skills focused and concise
- Use references instead of duplicating content

**Hook Performance:**
- PreToolUse hooks run before every Read operation
- Must be extremely fast (don't delay tool execution)
- Use O(1) lookups (pathway map) not O(n) file analysis
- Fail gracefully (process.exit(0) on errors, never block)
- Set reasonable limits (show top 10-15 skills, not all matches)

**PreToolUse Optimization:**
- Only read assessment cache synchronously (small files, ~50-150KB)
- For pathway guides, use filename extraction + map lookup (1KB vs 24KB)
- Cache map files in memory if performance becomes critical
- Exit early if file pattern doesn't match (assessment cache or pathway guide)

---

## Lessons Learned

### Critical Mistakes to Avoid

**1. Wrong File Structure**
```
❌ .claude/skills/inspection.md           # Flat files don't work
✅ .claude/skills/inspection/SKILL.md     # Directory with SKILL.md required
```

**2. Wrong File Paths in Hooks**
```typescript
// ❌ Hardcoded paths break when skills directory restructured
const rulesPath = '/path/.claude/skills/skill-rules.json';

// ✅ Use environment variable and proper join
const projectDir = process.env.CLAUDE_PROJECT_DIR;
const rulesPath = join(projectDir, '.claude', 'skill-rules.json');
```

**3. Forgetting to Update All References**
When restructuring, update:
- Hook scripts (skill-rules.json paths)
- Generator script (output paths, file reading logic)
- Documentation (README, guides)
- Settings.json (if paths changed)

**4. Not Testing After Restructuring**
```bash
# Always test after major changes
node .claude/hooks/generate-skill-rules.js  # Regenerate
echo '{"prompt":"inspection"}' | .claude/hooks/skill-activation-prompt.sh  # Test
```

### Success Patterns

**1. Choose PreToolUse Over PostToolUse for Structured Content**
```
RICS v1.0 (Initial): PostToolUse (reactive)
- Hook triggered AFTER reading 24KB pathway guide
- Analyzed full file contents for skill references
- Required deduplication logic with UserPromptSubmit
- 3 hooks total (UserPromptSubmit + PreToolUse + PostToolUse)

RICS v2.1 (Simplified): PreToolUse (proactive)
- Hook triggers BEFORE reading pathway guide
- Extracts pathway from filename, does 1KB map lookup
- 96% token reduction (1KB vs 24KB)
- 2 hooks total (UserPromptSubmit + PreToolUse)
- No deduplication needed
```

**Key Insight:** For structured, known file types (assessment caches, pathway guides), proactive detection (PreToolUse) is superior to reactive analysis (PostToolUse). Use PostToolUse only for unstructured content where patterns can't be predicted.

**2. Auto-Generation Reduces Maintenance**
- Don't manually maintain skill-rules.json
- Generate from skill files (single source of truth)
- Run generator whenever adding/removing skills

**3. Fail Gracefully**
```typescript
// Don't break on errors - hooks should be invisible if they fail
try {
    // Hook logic
    process.exit(0);
} catch (err) {
    console.error('Error:', err);
    process.exit(0);  // Exit success so tool execution continues
}
```

**4. Clear Output Formatting**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 SKILL ACTIVATION CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ CRITICAL SKILLS (REQUIRED):
  → ethics-rules-of-conduct-and-professionalism

📚 RECOMMENDED SKILLS:
  → inspection
  → measurement
  → valuation

ACTION: Use Skill tool BEFORE responding
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**5. Priority-Based Suggestions**
- Critical skills: Must-have (ethics)
- High priority: Core competencies
- Medium priority: Optional competencies
- Limit output: Show top 10-15, not all matches

**6. Synchronous File Reading in PreToolUse**
- PreToolUse can read files before the main tool executes
- Use for small, structured files (assessment caches ~50-150KB)
- Extract metadata without processing full content
- Enables candidate-specific skill suggestions

### Scalability Insights

**RICS Scale:**
- 115 competency skills
- 21 pathway guides
- 26 slash commands
- ~500KB total skill content
- Typical conversation loads 8-12 skills (~120-180KB)

**Key to Scalability:**
- On-demand loading (not all skills at once)
- Intelligent activation (hooks suggest, Claude decides)
- Token-efficient skill design (reference, don't duplicate)
- Auto-generation reduces manual effort

---

## Quick Start Checklist

Setting up a similar system for your domain:

### Phase 1: Skills Setup
- [ ] Create `.claude/skills/` directory
- [ ] For each domain topic:
  - [ ] Create `topic-name/` subdirectory
  - [ ] Create `SKILL.md` with proper frontmatter
  - [ ] Write content following structure pattern
- [ ] Test skill invocation: `Skill tool: topic-name`
- [ ] Verify all skills loadable

### Phase 2: Hooks Setup
- [ ] Create `.claude/hooks/` directory
- [ ] Create hook scripts (shell + TypeScript)
- [ ] Create `skill-rules.json` (manually or via generator)
- [ ] Add hook configuration to `.claude/settings.json`
- [ ] Test hooks manually with sample input
- [ ] Verify hooks trigger on real usage

### Phase 3: Auto-Generation
- [ ] Write generator script (`generate-skill-rules.js`)
- [ ] Test generator produces valid skill-rules.json
- [ ] Document regeneration process in README
- [ ] Add to maintenance workflow

### Phase 4: Documentation
- [ ] Document file structure
- [ ] Document skill naming conventions
- [ ] Document hook trigger patterns
- [ ] Write maintenance guide
- [ ] Create troubleshooting section

### Phase 5: Testing
- [ ] Test skill activation on prompts
- [ ] Test hook suggestions with real files
- [ ] Verify token efficiency (not loading all skills)
- [ ] Test error handling (missing files, bad JSON)
- [ ] Verify cross-platform compatibility

---

## Troubleshooting

### Skills Not Loading

**Symptom:** `Skill tool: topic-name` returns "Unknown skill"

**Diagnosis:**
1. Check file structure: Is it `skills/topic-name/SKILL.md`?
2. Check YAML frontmatter: Does it have `name` and `description`?
3. Check name match: Does directory name match YAML `name` field?
4. Test: Can you read the file directly?

**Fix:**
```bash
# Verify structure
ls -la .claude/skills/topic-name/

# Check frontmatter
head -5 .claude/skills/topic-name/SKILL.md

# Test read
cat .claude/skills/topic-name/SKILL.md
```

### Hooks Not Triggering

**Symptom:** No skill suggestions appear when expected

**Diagnosis:**
1. Check settings.json: Are hooks configured?
2. Check hook script permissions: Are they executable?
3. Check skill-rules.json: Does it exist at correct path?
4. Test hook manually with sample input

**Fix:**
```bash
# Check settings
cat .claude/settings.json

# Make executable
chmod +x .claude/hooks/*.sh

# Test UserPromptSubmit manually
echo '{"prompt":"test inspection"}' | .claude/hooks/skill-activation-prompt.sh

# Test PreToolUse manually (assessment cache)
echo '{"tool":"Read","parameters":{"file_path":"./Candidates/Smith_John_Q1_2024/AI_Assessment/00_Assessment_Cache.json"}}' | .claude/hooks/pre-tool-use-skill-loader.sh

# Test PreToolUse manually (pathway guide)
echo '{"tool":"Read","parameters":{"file_path":"./RICS_APC_Assessment_Guides/commercial_real_estate_ASSESSMENT_GUIDE.md"}}' | .claude/hooks/pre-tool-use-skill-loader.sh

# Check paths in TypeScript
grep "skill-rules.json" .claude/hooks/*.ts
grep "pathway-competencies-map.json" .claude/hooks/*.ts
```

### Wrong File Paths After Restructuring

**Symptom:** Hooks error with "ENOENT: no such file"

**Diagnosis:**
1. Check all hardcoded paths in hook scripts
2. Check skill-rules.json location
3. Verify generator script outputs to correct location

**Fix:**
```bash
# Find all skill-rules.json references
grep -r "skill-rules.json" .claude/hooks/

# Verify location
ls -la .claude/skill-rules.json

# Check environment variable usage
grep "CLAUDE_PROJECT_DIR" .claude/hooks/*.ts
```

---

## Conclusion

The RICS APC implementation demonstrates that with proper architecture:
- **115 domain skills** can be managed efficiently
- **Token usage** stays reasonable through on-demand loading
- **Hooks** provide intelligent activation without user intervention
- **Maintenance** is streamlined through auto-generation
- **Scalability** is achieved through patterns, not manual effort

**Core Principles:**
1. Skills = knowledge repositories (on-demand loading)
2. Hooks = intelligent activation (context-aware suggestions)
3. Auto-generation = maintainability (single source of truth)
4. Proper structure = functionality (follow Claude Code conventions exactly)

**Next Steps:**
- Adapt this pattern to your domain
- Start small (10-20 skills) and scale up
- Test thoroughly at each phase
- Document your specific patterns

---

**Document Version:** 2.1
**Last Updated:** November 13, 2025
**Reference Implementation:** RICS APC Assessment Pipeline
**Skills Count:** 115 competencies
**Hooks Count:** 2 (UserPromptSubmit, PreToolUse)
**Architecture:** Simplified proactive detection (96% token efficiency)
**Key Features:** Assessment cache detection, pathway context, candidate-specific loading
