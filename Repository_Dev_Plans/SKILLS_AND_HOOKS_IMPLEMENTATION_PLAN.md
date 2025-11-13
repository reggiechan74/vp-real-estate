# Skills and Hooks Implementation Plan
## VP Real Estate Lease Analysis Repository

**Date:** November 13, 2025
**Reference:** BEST_PRACTICES_SKILLS_AND_HOOKS.md
**Current State:** 15 existing skills, 28 slash commands, no hooks

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Implementation Overview](#implementation-overview)
4. [Phase 1: Audit and Enhance Existing Skills](#phase-1-audit-and-enhance-existing-skills)
5. [Phase 2: Create New Analytical Skills](#phase-2-create-new-analytical-skills)
6. [Phase 3: Implement Hooks Infrastructure](#phase-3-implement-hooks-infrastructure)
7. [Phase 4: Create Skill Activation Rules](#phase-4-create-skill-activation-rules)
8. [Phase 5: Build Auto-Generation Tools](#phase-5-build-auto-generation-tools)
9. [Phase 6: Testing and Validation](#phase-6-testing-and-validation)
10. [Implementation Timeline](#implementation-timeline)
11. [Success Metrics](#success-metrics)
12. [Maintenance Plan](#maintenance-plan)

---

## Executive Summary

**Goal:** Implement intelligent skill activation system with hooks to provide contextual, on-demand expertise for commercial real estate lease analysis.

**Approach:** Build on existing 15 lease-focused skills by:
1. Adding 8 new analytical/process skills (total: 23 skills)
2. Implementing 2 hooks (UserPromptSubmit + PreToolUse)
3. Creating auto-generation infrastructure
4. Enabling 96% token efficiency through proactive file detection

**Expected Outcome:**
- Claude automatically suggests relevant skills when analyzing leases
- Skills load on-demand (not all 23 at once)
- Proactive skill loading when reading lease documents, offers, financial statements
- Reduced token consumption through intelligent activation

---

## Current State Analysis

### Existing Skills (15 total)

**Core Lease Agreements (1):**
- ✅ commercial-lease-expert

**Security & Protection (2):**
- ✅ indemnity-expert
- ✅ non-disturbance-expert

**Lease Modifications & Transfers (4):**
- ✅ consent-to-assignment-expert
- ✅ consent-to-sublease-expert
- ✅ share-transfer-consent-expert
- ✅ lease-surrender-expert

**Preliminary & Ancillary Agreements (4):**
- ✅ offer-to-lease-expert
- ✅ waiver-agreement-expert
- ✅ temporary-license-expert
- ✅ storage-agreement-expert

**Specialized Licenses (1):**
- ✅ telecom-licensing-expert

**Dispute Resolution (1):**
- ✅ lease-arbitration-expert

**Negotiation (2):**
- ✅ negotiation-expert
- ✅ objection-handling-expert

### Existing Slash Commands (28 total)

**Abstraction (2):**
- /abstract-lease
- /critical-dates

**Financial Analysis (10):**
- /effective-rent (NER, NPV, breakeven)
- /renewal-economics
- /tenant-credit
- /option-value
- /market-comparison
- /rollover-analysis
- /rental-variance
- /relative-valuation
- /recommendation-memo
- /extract-mls

**Accounting (1):**
- /ifrs16-calculation

**Comparison (4):**
- /compare-amendment
- /compare-offers
- /compare-precedent
- /lease-vs-lease

**Compliance (7):**
- /assignment-consent
- /default-analysis
- /environmental-compliance
- /estoppel-certificate
- /insurance-audit
- /notice-generator
- /work-letter

**Utilities (1):**
- /convert-to-pdf

### Infrastructure Gaps

**Missing:**
- ❌ Hooks directory (.claude/hooks/)
- ❌ Hook scripts (UserPromptSubmit, PreToolUse)
- ❌ Settings.json hook configuration
- ❌ skill-rules.json activation triggers
- ❌ Document type mapping (lease-types-map.json)
- ❌ Auto-generation scripts

**Token Inefficiency Risk:**
- Current: Skills load only when manually invoked via Skill tool
- Problem: User must know which skills exist and when to use them
- Impact: Expertise underutilized, manual activation required

---

## Implementation Overview

### Architecture Design

Following RICS best practices pattern:

```
.claude/
├── settings.json                     # NEW - Hook configuration
├── skill-rules.json                  # NEW - Auto-generated activation rules
├── skills/                           # EXISTING - 15 skills
│   ├── [15 existing skills]/
│   └── [8 new analytical skills]/    # NEW
├── hooks/                            # NEW - Hook scripts
│   ├── skill-activation-prompt.sh        # UserPromptSubmit wrapper
│   ├── skill-activation-prompt.ts        # UserPromptSubmit logic
│   ├── pre-tool-use-skill-loader.sh      # PreToolUse wrapper
│   ├── pre-tool-use-skill-loader.ts      # PreToolUse logic
│   ├── generate-skill-rules.js           # Auto-generator
│   ├── lease-types-map.json              # Document type → skills mapping
│   ├── package.json                      # Node dependencies
│   └── README.md                         # Hook documentation
└── commands/                         # EXISTING - 28 commands
```

### Key Patterns to Implement

**1. UserPromptSubmit Hook (Reactive)**
- Triggers: When user submits a message
- Analyzes: Keywords (NER, NPV, tenant credit, lease abstraction, etc.)
- Suggests: Relevant skills BEFORE Claude responds
- Example: "Calculate NER for this lease" → Suggests effective-rent-analyzer skill

**2. PreToolUse Hook (Proactive - 96% token efficiency)**
- Triggers: BEFORE Read tool executes
- Detects: Lease documents, offers, financial statements by filename pattern
- Suggests: Context-appropriate skills based on document type
- Example: Reading "offer_to_lease.pdf" → Suggests offer-to-lease-expert + effective-rent-analyzer

**3. Auto-Generation**
- Generate skill-rules.json from SKILL.md frontmatter
- Maintain single source of truth (skill files)
- Regenerate when adding/removing skills

---

## Phase 1: Audit and Enhance Existing Skills

### Goal
Ensure all 15 existing skills have optimal frontmatter for activation

### Tasks

**1.1 Audit Frontmatter Quality**

Check each skill for:
- ✅ `name`: Lowercase, hyphenated, consistent
- ✅ `description`: Explains purpose AND context (max 1024 chars)
- ✅ `tags`: Keywords for discovery
- ✅ `capability`: Detailed description of what skill provides
- ✅ `proactive`: Boolean indicating auto-activation preference

**Sample Audit:**
```bash
# Check all skills have proper frontmatter
for skill in .claude/skills/*/SKILL.md; do
  echo "=== $skill ==="
  head -10 "$skill" | grep -E "^(name|description|tags|capability):"
done
```

**1.2 Enhance Descriptions for Hook Matching**

Current descriptions are good, but optimize for keyword matching:

**Example Enhancement:**
```yaml
# BEFORE
description: Expert in commercial real estate lease agreements

# AFTER
description: Expert in commercial real estate lease agreements for industrial and office properties. Use when reviewing lease terms, negotiating base rent/operating expenses, analyzing tenant improvements and free rent, structuring net lease vs gross lease deals, evaluating renewal options, or advising on landlord/tenant rights. Key terms include base rent, operating expenses, proportionate share, TI allowance, net lease, triple net, lease economics, rent escalation, use clause, assignment restrictions, default remedies, Schedule G
```

**Key Improvement:** Add trigger keywords that users commonly mention

**1.3 Add Missing Metadata**

If any skills lack these fields, add them:
- `tags`: Array of keywords for discovery
- `capability`: Detailed capability description
- `proactive`: true/false for auto-activation

**Deliverables:**
- [ ] Frontmatter audit spreadsheet
- [ ] Enhanced descriptions for all 15 skills
- [ ] Standardized metadata across all skills

---

## Phase 2: Create New Analytical Skills

### Goal
Add 8 new skills focused on financial analysis, lease abstraction, and compliance processes

### New Skills to Create

**2.1 Financial Analysis Skills (3 new)**

**Skill: `effective-rent-analyzer`**
```yaml
---
name: effective-rent-analyzer
description: Expert in effective rent calculations using Ponzi Rental Rate (PRR) framework. Use when calculating NER, NPV, breakeven analysis, landlord investment returns, or analyzing lease deal economics. Key terms include net effective rent, gross effective rent, NPV of lease deal, breakeven NER, fully levered breakeven, sinking fund, capital recovery, tenant incentives, TI allowance, free rent, leasing commissions
tags: [effective-rent, NER, NPV, breakeven, PRR, ponzi-rental-rate, lease-economics, landlord-return]
capability: Calculates landlord investment returns using NPV methodology, determines breakeven rent thresholds, analyzes tenant incentive impacts, and provides investment recommendations
proactive: true
---
```

**Skill: `tenant-credit-analyst`**
```yaml
---
name: tenant-credit-analyst
description: Expert in tenant creditworthiness assessment and financial statement analysis. Use when evaluating tenant credit quality, analyzing financial ratios, assessing default risk, or structuring security requirements. Key terms include DSCR, current ratio, debt-to-equity, working capital, liquidity analysis, credit scoring, personal guarantee, security deposit, financial covenants
tags: [tenant-credit, financial-analysis, DSCR, credit-risk, security-deposit, guarantee]
capability: Analyzes tenant financial statements, calculates credit ratios, assesses default probability, and recommends security structures
proactive: true
---
```

**Skill: `lease-abstraction-specialist`**
```yaml
---
name: lease-abstraction-specialist
description: Expert in lease abstraction and critical terms extraction. Use when abstracting lease agreements, extracting key dates, identifying critical provisions, or creating lease summaries. Key terms include lease abstraction, critical dates, rent schedule, operating costs, renewal options, termination rights, default provisions, use clause, assignment clause, Schedule G special provisions
tags: [lease-abstraction, critical-dates, lease-summary, key-terms, extraction]
capability: Extracts and organizes critical lease terms into standardized 24-section templates (industrial/office) following ANSI/BOMA standards
proactive: true
---
```

**2.2 Compliance & Process Skills (3 new)**

**Skill: `lease-compliance-auditor`**
```yaml
---
name: lease-compliance-auditor
description: Expert in lease compliance monitoring and obligation tracking. Use when auditing insurance requirements, verifying environmental compliance, checking use clause adherence, or monitoring covenant compliance. Key terms include insurance audit, CGL requirements, environmental compliance, use clause violations, covenant breach, notice requirements, cure periods
tags: [compliance, insurance-audit, environmental, use-clause, covenant-compliance]
capability: Audits lease compliance across insurance, environmental, operational, and administrative obligations with red flag detection
proactive: true
---
```

**Skill: `default-and-remedies-advisor`**
```yaml
---
name: default-and-remedies-advisor
description: Expert in lease defaults and landlord remedies. Use when analyzing default scenarios, calculating cure periods, assessing damages, or drafting default notices. Key terms include monetary default, non-monetary default, cure period, notice to cure, lease termination, re-entry, damages, acceleration of rent, unamortized TI clawback
tags: [default, remedies, cure-period, termination, damages, default-notice]
capability: Analyzes default provisions, calculates damages and unamortized costs, structures cure timelines, and drafts default notices
proactive: true
---
```

**Skill: `lease-comparison-expert`**
```yaml
---
name: lease-comparison-expert
description: Expert in lease-to-lease comparison and deviation analysis. Use when comparing lease amendments to originals, analyzing competing offers, benchmarking against precedents, or identifying deal term variations. Key terms include lease comparison, amendment analysis, offer comparison, precedent deviation, market benchmarking, competitive analysis
tags: [comparison, amendment, offer-analysis, precedent, benchmarking, deviation-analysis]
capability: Compares lease documents side-by-side, highlights deviations from standards, and benchmarks terms against market comparables
proactive: true
---
```

**2.3 Investment & Portfolio Skills (2 new)**

**Skill: `portfolio-strategy-advisor`**
```yaml
---
name: portfolio-strategy-advisor
description: Expert in portfolio-level lease analysis and renewal prioritization. Use when analyzing lease rollover schedules, prioritizing renewals, assessing expiry cliff risk, or forecasting vacancy. Key terms include rollover analysis, expiry cliff, renewal priority, vacancy forecast, portfolio optimization, lease maturity, stagger strategy
tags: [portfolio, rollover, renewal-priority, expiry-cliff, vacancy-forecast, portfolio-strategy]
capability: Analyzes portfolio lease expiry timelines, identifies concentration risks, prioritizes renewal negotiations, and forecasts cash flow impacts
proactive: true
---
```

**Skill: `real-options-valuation-expert`**
```yaml
---
name: real-options-valuation-expert
description: Expert in real options valuation for lease flexibility features. Use when valuing renewal options, expansion rights, termination clauses, or other lease optionality using Black-Scholes methodology. Key terms include real options, option premium, renewal option value, expansion option, termination right, volatility, strike price, option pricing
tags: [real-options, option-value, renewal-option, expansion-right, black-scholes, flexibility]
capability: Values lease flexibility using real options theory, calculates option premiums, and quantifies strategic optionality embedded in leases
proactive: true
---
```

### Skill Content Structure

Each new skill should follow this template:

```markdown
---
name: skill-name
description: [Comprehensive description with trigger keywords]
tags: [keyword1, keyword2, ...]
capability: [What this skill provides]
proactive: true
---

# [Skill Title]

## Overview
[Brief context about this capability]

## Core Concepts

### Concept 1
[Definition and explanation]

### Concept 2
[Definition and explanation]

## Methodology

### Approach
[How this analysis is performed]

### Key Metrics
[Important calculations or measurements]

### Red Flags
[Warning signs to watch for]

## Common Use Cases

### Use Case 1: [Scenario]
**Situation**: [Description]
**Analysis**: [How to approach]
**Output**: [What to deliver]

### Use Case 2: [Scenario]
[Repeat pattern]

## Integration with Slash Commands

This skill is automatically loaded when:
- User mentions [keywords]
- Commands like /[command-name] are invoked
- Reading files matching pattern [file pattern]

**Related Commands**:
- /command1 - [description]
- /command2 - [description]

## Examples

### Example 1: [Title]
[Detailed walkthrough]

### Example 2: [Title]
[Detailed walkthrough]

---

**Skill Version:** 1.0
**Last Updated:** [Date]
**Related Skills:** [skill1], [skill2]
```

**Deliverables:**
- [ ] 8 new SKILL.md files in proper directory structure
- [ ] Content following template above
- [ ] Cross-references to related skills and commands
- [ ] Examples and use cases for each skill

---

## Phase 3: Implement Hooks Infrastructure

### Goal
Create hooks directory with UserPromptSubmit and PreToolUse implementations

### 3.1 Directory Structure

```bash
mkdir -p .claude/hooks
cd .claude/hooks
```

### 3.2 Create settings.json

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

**Key Points:**
- Only monitors "Read" tool (not Glob/Grep)
- Uses `$CLAUDE_PROJECT_DIR` for portability
- Two hooks: reactive (UserPromptSubmit) + proactive (PreToolUse)

### 3.3 UserPromptSubmit Hook (Reactive)

**Purpose:** Analyze user prompts for lease analysis keywords

**File:** `.claude/hooks/skill-activation-prompt.sh`

```bash
#!/bin/bash
set -e

cd "$CLAUDE_PROJECT_DIR/.claude/hooks"
cat | npx tsx skill-activation-prompt.ts
```

**File:** `.claude/hooks/skill-activation-prompt.ts`

```typescript
#!/usr/bin/env node
import { readFileSync } from 'fs';
import { join } from 'path';

interface HookInput {
    session_id: string;
    transcript_path: string;
    cwd: string;
    permission_mode: string;
    prompt: string;
}

interface SkillConfig {
    type: string;
    enforcement: string;
    priority: string;
    description: string;
    promptTriggers?: {
        keywords?: string[];
        intentPatterns?: string[];
    };
}

interface SkillRules {
    version: string;
    description: string;
    skills: Record<string, SkillConfig>;
}

interface MatchedSkill {
    name: string;
    matchType: 'keyword' | 'intent';
    config: SkillConfig;
}

async function main() {
    try {
        const input = readFileSync(0, 'utf-8');
        const data: HookInput = JSON.parse(input);

        const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
        const rulesPath = join(projectDir, '.claude', 'skill-rules.json');

        const rules: SkillRules = JSON.parse(readFileSync(rulesPath, 'utf-8'));

        const matches = analyzePrompt(data.prompt, rules);

        if (matches.length > 0) {
            const output = formatSuggestions(matches);
            console.log(output);
        }

        process.exit(0);
    } catch (err) {
        console.error('Error in UserPromptSubmit hook:', err);
        process.exit(0);  // Fail gracefully
    }
}

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

    return prioritizeMatches(matches);
}

function prioritizeMatches(matches: MatchedSkill[]): MatchedSkill[] {
    const priorityOrder = { 'critical': 1, 'high': 2, 'medium': 3, 'low': 4 };

    return matches
        .sort((a, b) => {
            const aPriority = priorityOrder[a.config.priority as keyof typeof priorityOrder] || 5;
            const bPriority = priorityOrder[b.config.priority as keyof typeof priorityOrder] || 5;
            return aPriority - bPriority;
        })
        .slice(0, 10);  // Top 10 matches
}

function formatSuggestions(matches: MatchedSkill[]): string {
    const critical = matches.filter(m => m.config.priority === 'critical');
    const high = matches.filter(m => m.config.priority === 'high');
    const other = matches.filter(m => !['critical', 'high'].includes(m.config.priority));

    let output = '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
    output += '🎯 SKILL ACTIVATION CHECK\n';
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';

    if (critical.length > 0) {
        output += '⚠️ CRITICAL SKILLS (REQUIRED):\n';
        critical.forEach(m => output += `  → ${m.name}\n`);
        output += '\n';
    }

    if (high.length > 0) {
        output += '📚 RECOMMENDED SKILLS:\n';
        high.forEach(m => output += `  → ${m.name}\n`);
        output += '\n';
    }

    if (other.length > 0) {
        output += '💡 OPTIONAL SKILLS:\n';
        other.forEach(m => output += `  → ${m.name}\n`);
        output += '\n';
    }

    output += 'ACTION: Use Skill tool BEFORE responding\n';
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';

    return output;
}

main();
```

**Make executable:**
```bash
chmod +x .claude/hooks/skill-activation-prompt.sh
chmod +x .claude/hooks/skill-activation-prompt.ts
```

### 3.4 PreToolUse Hook (Proactive)

**Purpose:** Detect lease documents by filename and suggest skills proactively

**File:** `.claude/hooks/pre-tool-use-skill-loader.sh`

```bash
#!/bin/bash
set -e

cd "$CLAUDE_PROJECT_DIR/.claude/hooks"
cat | npx tsx pre-tool-use-skill-loader.ts
```

**File:** `.claude/hooks/pre-tool-use-skill-loader.ts`

```typescript
#!/usr/bin/env node
import { readFileSync } from 'fs';
import { join, basename } from 'path';

interface HookInput {
    session_id: string;
    transcript_path: string;
    cwd: string;
    permission_mode: string;
    tool: string;
    parameters: any;
}

interface LeaseTypeMap {
    version: string;
    document_types: Record<string, {
        patterns: string[];
        skills: string[];
        description: string;
    }>;
}

async function main() {
    try {
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

        // PRIORITY 1: Check for Lease Documents
        const leaseOutput = handleLeaseDocument(filePath, projectDir);
        if (leaseOutput) {
            console.log(leaseOutput);
            process.exit(0);
        }

        // PRIORITY 2: Check for Financial Statements
        const financialOutput = handleFinancialDocument(filePath, projectDir);
        if (financialOutput) {
            console.log(financialOutput);
            process.exit(0);
        }

        // PRIORITY 3: Check for JSON Input Files
        const jsonOutput = handleJSONInput(filePath, projectDir);
        if (jsonOutput) {
            console.log(jsonOutput);
            process.exit(0);
        }

        process.exit(0);
    } catch (err) {
        console.error('Error in PreToolUse hook:', err);
        process.exit(0);  // Fail gracefully
    }
}

function handleLeaseDocument(filePath: string, projectDir: string): string | null {
    try {
        const fileName = basename(filePath).toLowerCase();
        const mapPath = join(projectDir, '.claude', 'hooks', 'lease-types-map.json');
        const leaseMap: LeaseTypeMap = JSON.parse(readFileSync(mapPath, 'utf-8'));

        for (const [docType, config] of Object.entries(leaseMap.document_types)) {
            const matches = config.patterns.some(pattern => {
                const regex = new RegExp(pattern, 'i');
                return regex.test(fileName);
            });

            if (matches) {
                return formatLeaseDocumentSuggestions(docType, config.skills, config.description);
            }
        }

        return null;
    } catch (err) {
        return null;
    }
}

function handleFinancialDocument(filePath: string, projectDir: string): string | null {
    const fileName = basename(filePath).toLowerCase();

    const financialPatterns = [
        /financial.*statement/i,
        /balance.*sheet/i,
        /income.*statement/i,
        /cash.*flow/i,
        /audit.*report/i,
        /financials?\.pdf/i
    ];

    const matches = financialPatterns.some(pattern => pattern.test(fileName));

    if (matches) {
        return formatFinancialDocumentSuggestions();
    }

    return null;
}

function handleJSONInput(filePath: string, projectDir: string): string | null {
    const fileName = basename(filePath).toLowerCase();

    // Detect calculator input files
    if (fileName.includes('_input.json')) {
        if (filePath.includes('Eff_Rent_Calculator')) {
            return formatCalculatorSuggestions('effective-rent');
        }
        if (filePath.includes('Option_Valuation')) {
            return formatCalculatorSuggestions('real-options');
        }
        if (filePath.includes('Renewal_Analysis')) {
            return formatCalculatorSuggestions('renewal-economics');
        }
    }

    return null;
}

function formatLeaseDocumentSuggestions(docType: string, skills: string[], description: string): string {
    let output = '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
    output += '⚡ PROACTIVE SKILL LOADING\n';
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
    output += `📄 Document Type: ${docType}\n`;
    output += `📝 Description: ${description}\n\n`;
    output += '📚 RECOMMENDED SKILLS:\n';
    skills.forEach(skill => output += `  → ${skill}\n`);
    output += '\n';
    output += 'ACTION: Skills auto-loaded for context-aware analysis\n';
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
    return output;
}

function formatFinancialDocumentSuggestions(): string {
    let output = '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
    output += '⚡ PROACTIVE SKILL LOADING\n';
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
    output += '📄 Document Type: Financial Statements\n\n';
    output += '📚 RECOMMENDED SKILLS:\n';
    output += '  → tenant-credit-analyst\n';
    output += '  → effective-rent-analyzer\n\n';
    output += 'ACTION: Financial analysis skills loaded\n';
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
    return output;
}

function formatCalculatorSuggestions(calculatorType: string): string {
    const skillMap: Record<string, string[]> = {
        'effective-rent': ['effective-rent-analyzer', 'commercial-lease-expert'],
        'real-options': ['real-options-valuation-expert', 'commercial-lease-expert'],
        'renewal-economics': ['effective-rent-analyzer', 'portfolio-strategy-advisor']
    };

    const skills = skillMap[calculatorType] || [];

    let output = '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
    output += '⚡ PROACTIVE SKILL LOADING\n';
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
    output += `📊 Calculator: ${calculatorType}\n\n`;
    output += '📚 RECOMMENDED SKILLS:\n';
    skills.forEach(skill => output += `  → ${skill}\n`);
    output += '\n';
    output += 'ACTION: Calculator-specific skills loaded\n';
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
    return output;
}

main();
```

**Make executable:**
```bash
chmod +x .claude/hooks/pre-tool-use-skill-loader.sh
chmod +x .claude/hooks/pre-tool-use-skill-loader.ts
```

### 3.5 Create lease-types-map.json

**File:** `.claude/hooks/lease-types-map.json`

```json
{
  "version": "1.0",
  "description": "Document type to skills mapping for proactive skill loading",
  "document_types": {
    "offer_to_lease": {
      "patterns": [
        "offer.*lease",
        "offer.*to.*lease",
        "loi",
        "letter.*intent",
        "term.*sheet"
      ],
      "skills": [
        "offer-to-lease-expert",
        "effective-rent-analyzer",
        "commercial-lease-expert",
        "negotiation-expert"
      ],
      "description": "Offer to Lease, LOI, or Term Sheet"
    },
    "lease_agreement": {
      "patterns": [
        "lease.*agreement",
        "commercial.*lease",
        "industrial.*lease",
        "office.*lease",
        "lease\\.pdf",
        "lease\\.docx"
      ],
      "skills": [
        "commercial-lease-expert",
        "lease-abstraction-specialist",
        "lease-compliance-auditor"
      ],
      "description": "Executed Lease Agreement"
    },
    "lease_amendment": {
      "patterns": [
        "amendment",
        "amending.*agreement",
        "lease.*amendment",
        "supplemental.*agreement"
      ],
      "skills": [
        "lease-comparison-expert",
        "commercial-lease-expert",
        "lease-abstraction-specialist"
      ],
      "description": "Lease Amendment or Amending Agreement"
    },
    "assignment_consent": {
      "patterns": [
        "assignment.*consent",
        "consent.*assignment",
        "assignment.*agreement"
      ],
      "skills": [
        "consent-to-assignment-expert",
        "commercial-lease-expert"
      ],
      "description": "Consent to Assignment Agreement"
    },
    "sublease_consent": {
      "patterns": [
        "sublease.*consent",
        "consent.*sublease",
        "sublease.*agreement"
      ],
      "skills": [
        "consent-to-sublease-expert",
        "commercial-lease-expert"
      ],
      "description": "Consent to Sublease Agreement"
    },
    "surrender_agreement": {
      "patterns": [
        "surrender",
        "lease.*termination",
        "early.*termination",
        "mutual.*release"
      ],
      "skills": [
        "lease-surrender-expert",
        "commercial-lease-expert",
        "effective-rent-analyzer"
      ],
      "description": "Lease Surrender or Early Termination Agreement"
    },
    "indemnity_guarantee": {
      "patterns": [
        "indemnity",
        "guarantee",
        "personal.*guarantee",
        "corporate.*guarantee"
      ],
      "skills": [
        "indemnity-expert",
        "tenant-credit-analyst"
      ],
      "description": "Indemnity or Guarantee Agreement"
    },
    "snda": {
      "patterns": [
        "snda",
        "subordination",
        "non.*disturbance",
        "attornment"
      ],
      "skills": [
        "non-disturbance-expert",
        "commercial-lease-expert"
      ],
      "description": "SNDA (Subordination, Non-Disturbance, Attornment)"
    },
    "estoppel": {
      "patterns": [
        "estoppel",
        "tenant.*estoppel",
        "estoppel.*certificate"
      ],
      "skills": [
        "commercial-lease-expert",
        "lease-compliance-auditor"
      ],
      "description": "Estoppel Certificate"
    },
    "default_notice": {
      "patterns": [
        "default.*notice",
        "notice.*default",
        "notice.*cure",
        "demand.*letter"
      ],
      "skills": [
        "default-and-remedies-advisor",
        "commercial-lease-expert"
      ],
      "description": "Default Notice or Demand Letter"
    }
  }
}
```

### 3.6 Create package.json

**File:** `.claude/hooks/package.json`

```json
{
  "name": "lease-abstract-hooks",
  "version": "1.0.0",
  "description": "Claude Code hooks for VP Real Estate lease analysis",
  "type": "module",
  "scripts": {
    "test-prompt": "echo '{\"prompt\":\"calculate NER for this lease\"}' | tsx skill-activation-prompt.ts",
    "test-pretool": "echo '{\"tool\":\"Read\",\"parameters\":{\"file_path\":\"./Sample_Inputs/sample_offer_to_lease.pdf\"}}' | tsx pre-tool-use-skill-loader.ts",
    "generate-rules": "node generate-skill-rules.js"
  },
  "dependencies": {
    "tsx": "^4.7.0"
  },
  "devDependencies": {
    "@types/node": "^20.11.0"
  }
}
```

**Install dependencies:**
```bash
cd .claude/hooks
npm install
```

### 3.7 Create Hook README

**File:** `.claude/hooks/README.md`

```markdown
# Lease Analysis Hooks

**Version:** 1.0
**Repository:** VP Real Estate Lease Abstract

## Overview

Intelligent skill activation system for commercial real estate lease analysis.

## Architecture

**2 Hooks:**
1. **UserPromptSubmit** (Reactive): Analyzes user prompts for keywords
2. **PreToolUse** (Proactive): Detects document types by filename

**Token Efficiency:** 96% reduction through proactive detection

## Hook Triggers

### UserPromptSubmit

Triggered when user submits a message.

**Keywords Detected:**
- Financial: NER, NPV, effective rent, breakeven, tenant credit, DSCR
- Legal: lease abstraction, assignment, sublease, default, termination
- Process: compliance, audit, comparison, valuation

**Example:**
```
User: "Calculate NER for this lease deal"
Hook: Suggests effective-rent-analyzer + commercial-lease-expert
```

### PreToolUse

Triggered BEFORE reading files.

**Patterns Detected:**
- Lease documents: `*lease*.pdf`, `*agreement*.docx`
- Offers: `*offer*lease*`, `*loi*`, `*term*sheet*`
- Financial: `*financial*statement*`, `*balance*sheet*`
- Calculator inputs: `*_input.json` in calculator directories

**Example:**
```
User: Read Sample_Inputs/offer_to_lease.pdf
Hook: (BEFORE read) Suggests offer-to-lease-expert + effective-rent-analyzer
Read tool: (THEN executes) File contents loaded
```

## Testing

**Test UserPromptSubmit:**
```bash
npm run test-prompt
```

**Test PreToolUse:**
```bash
npm run test-pretool
```

**Manual Testing:**
```bash
# UserPromptSubmit
echo '{"prompt":"review this lease agreement"}' | ./skill-activation-prompt.sh

# PreToolUse - Offer to Lease
echo '{"tool":"Read","parameters":{"file_path":"./Sample_Inputs/sample_offer_to_lease.pdf"}}' | ./pre-tool-use-skill-loader.sh

# PreToolUse - Financial Statement
echo '{"tool":"Read","parameters":{"file_path":"./financials.pdf"}}' | ./pre-tool-use-skill-loader.sh
```

## File Structure

```
.claude/hooks/
├── README.md                         # This file
├── package.json                      # Node dependencies
├── skill-activation-prompt.sh        # UserPromptSubmit wrapper
├── skill-activation-prompt.ts        # UserPromptSubmit logic
├── pre-tool-use-skill-loader.sh      # PreToolUse wrapper
├── pre-tool-use-skill-loader.ts      # PreToolUse logic
├── generate-skill-rules.js           # Auto-generator
├── lease-types-map.json              # Document type mapping
└── skill-rules.json                  # (Auto-generated) Activation rules
```

## Maintenance

**Adding New Skills:**
1. Create skill in `.claude/skills/skill-name/SKILL.md`
2. Run: `npm run generate-rules`
3. Test: `npm run test-prompt`

**Adding Document Patterns:**
1. Edit `lease-types-map.json`
2. Add pattern to appropriate document type
3. Test: `npm run test-pretool`

## Troubleshooting

**Hooks Not Triggering:**
```bash
# Check settings.json
cat ../.settings.json

# Check permissions
ls -la *.sh
chmod +x *.sh

# Check paths
grep "CLAUDE_PROJECT_DIR" *.ts
```

**Wrong Skills Suggested:**
```bash
# Regenerate rules
npm run generate-rules

# Check skill frontmatter
head -10 ../skills/*/SKILL.md
```

---

**Last Updated:** November 13, 2025
**Contact:** Reggie Chan, CFA, FRICS
```

**Deliverables:**
- [ ] settings.json with hook configuration
- [ ] UserPromptSubmit hook (shell + TypeScript)
- [ ] PreToolUse hook (shell + TypeScript)
- [ ] lease-types-map.json with document patterns
- [ ] package.json with dependencies
- [ ] README.md documenting hooks
- [ ] All scripts executable (`chmod +x`)

---

## Phase 4: Create Skill Activation Rules

### Goal
Generate skill-rules.json with keyword triggers for all 23 skills

### 4.1 Manual skill-rules.json Template

For immediate use before auto-generation is built:

**File:** `.claude/skill-rules.json`

```json
{
  "version": "1.0",
  "description": "Skill activation triggers for VP Real Estate lease analysis",
  "generation": {
    "method": "manual",
    "date": "2025-11-13",
    "total_skills": 23
  },
  "skills": {
    "commercial-lease-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "Commercial lease agreements for industrial and office properties",
      "promptTriggers": {
        "keywords": [
          "lease agreement",
          "commercial lease",
          "base rent",
          "operating expenses",
          "net lease",
          "triple net",
          "proportionate share",
          "lease negotiation"
        ],
        "intentPatterns": [
          "review.*lease",
          "negotiate.*lease",
          "draft.*lease",
          "(base|net).*rent"
        ]
      }
    },
    "effective-rent-analyzer": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "Effective rent calculations using Ponzi Rental Rate framework",
      "promptTriggers": {
        "keywords": [
          "NER",
          "net effective rent",
          "NPV",
          "effective rent",
          "breakeven",
          "landlord return",
          "lease economics",
          "ponzi rental rate"
        ],
        "intentPatterns": [
          "calculate.*(ner|npv|effective.*rent)",
          "breakeven.*analysis",
          "landlord.*return",
          "investment.*analysis"
        ]
      }
    },
    "tenant-credit-analyst": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "Tenant creditworthiness and financial statement analysis",
      "promptTriggers": {
        "keywords": [
          "tenant credit",
          "DSCR",
          "financial analysis",
          "credit quality",
          "personal guarantee",
          "security deposit",
          "financial statements",
          "credit risk"
        ],
        "intentPatterns": [
          "tenant.*(credit|financial)",
          "analyze.*(financials?|credit)",
          "dscr",
          "guarantee"
        ]
      }
    },
    "lease-abstraction-specialist": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "Lease abstraction and critical terms extraction",
      "promptTriggers": {
        "keywords": [
          "lease abstraction",
          "abstract lease",
          "critical dates",
          "lease summary",
          "key terms",
          "extract terms"
        ],
        "intentPatterns": [
          "abstract.*lease",
          "extract.*(terms|dates)",
          "lease.*summary",
          "critical.*dates"
        ]
      }
    },
    "offer-to-lease-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "Offers to lease, LOIs, and term sheets",
      "promptTriggers": {
        "keywords": [
          "offer to lease",
          "LOI",
          "letter of intent",
          "term sheet",
          "binding",
          "non-binding",
          "conditions precedent"
        ],
        "intentPatterns": [
          "offer.*(lease|loi)",
          "letter.*intent",
          "term.*sheet",
          "binding.*offer"
        ]
      }
    },
    "negotiation-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "Commercial lease negotiation strategy and tactics",
      "promptTriggers": {
        "keywords": [
          "negotiation",
          "negotiate",
          "counter offer",
          "calibrated questions",
          "tactical empathy",
          "evidence-based anchoring"
        ],
        "intentPatterns": [
          "negotiat(e|ion)",
          "counter.*offer",
          "respond.*to.*objection",
          "tactical.*empathy"
        ]
      }
    },
    "objection-handling-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "Analyzing and responding to tenant objections",
      "promptTriggers": {
        "keywords": [
          "objection",
          "tenant objection",
          "rent too high",
          "pushback",
          "tenant demands",
          "respond to objection"
        ],
        "intentPatterns": [
          "objection",
          "tenant.*(object|demand|pushback)",
          "rent.*too.*high",
          "respond.*to"
        ]
      }
    },
    "consent-to-assignment-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "Assignment consent where tenant transfers entire lease",
      "promptTriggers": {
        "keywords": [
          "assignment",
          "consent to assignment",
          "assignee",
          "assign lease",
          "business sale",
          "privity of estate"
        ],
        "intentPatterns": [
          "assign(ment|ee)",
          "consent.*assignment",
          "transfer.*lease",
          "business.*sale"
        ]
      }
    },
    "consent-to-sublease-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "Sublease consent where tenant rents space while remaining on lease",
      "promptTriggers": {
        "keywords": [
          "sublease",
          "sublet",
          "subtenant",
          "consent to sublease",
          "profit sharing",
          "recapture"
        ],
        "intentPatterns": [
          "subl(ease|et)",
          "consent.*sublease",
          "subtenant",
          "profit.*shar"
        ]
      }
    },
    "share-transfer-consent-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "Share transfer consent for change of control",
      "promptTriggers": {
        "keywords": [
          "share transfer",
          "change of control",
          "shareholder change",
          "voting control",
          "corporate restructuring"
        ],
        "intentPatterns": [
          "share.*(transfer|sale)",
          "change.*control",
          "shareholder.*change"
        ]
      }
    },
    "lease-surrender-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "Lease surrender and early termination agreements",
      "promptTriggers": {
        "keywords": [
          "surrender",
          "lease surrender",
          "early termination",
          "buyout",
          "mutual release",
          "space reduction"
        ],
        "intentPatterns": [
          "surrender",
          "early.*terminat",
          "buyout",
          "mutual.*release"
        ]
      }
    },
    "indemnity-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "Indemnity and guarantee agreements",
      "promptTriggers": {
        "keywords": [
          "indemnity",
          "guarantee",
          "personal guarantee",
          "corporate guarantee",
          "absolute and unconditional",
          "guarantor"
        ],
        "intentPatterns": [
          "indemn",
          "guarant(ee|or)",
          "personal.*guarant",
          "absolute.*unconditional"
        ]
      }
    },
    "non-disturbance-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "SNDA agreements and foreclosure protection",
      "promptTriggers": {
        "keywords": [
          "SNDA",
          "non-disturbance",
          "subordination",
          "attornment",
          "foreclosure protection",
          "lender priority"
        ],
        "intentPatterns": [
          "snda",
          "non.*disturbanc",
          "subordinat",
          "attorney",
          "foreclosure"
        ]
      }
    },
    "lease-arbitration-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "low",
      "description": "Lease arbitration for renewal rent disputes",
      "promptTriggers": {
        "keywords": [
          "arbitration",
          "rent arbitration",
          "fair market value",
          "baseball arbitration",
          "rent determination",
          "arbitrator"
        ],
        "intentPatterns": [
          "arbitrat",
          "fair.*market.*(value|rent)",
          "rent.*determin",
          "baseball.*arbitrat"
        ]
      }
    },
    "waiver-agreement-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "low",
      "description": "Waiver of conditions in offers to lease",
      "promptTriggers": {
        "keywords": [
          "waiver",
          "waive conditions",
          "conditional waiver",
          "accept offer",
          "counter-offer"
        ],
        "intentPatterns": [
          "waiv(e|er)",
          "waive.*condition",
          "counter.*offer"
        ]
      }
    },
    "temporary-license-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "low",
      "description": "Short-term licenses (1 day to 3 months)",
      "promptTriggers": {
        "keywords": [
          "temporary license",
          "short-term license",
          "license agreement",
          "pop-up",
          "interim occupancy",
          "film shoot"
        ],
        "intentPatterns": [
          "temporary.*licen",
          "short.*term.*licen",
          "pop.*up",
          "interim.*occupanc"
        ]
      }
    },
    "storage-agreement-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "low",
      "description": "Storage locker and ancillary storage agreements",
      "promptTriggers": {
        "keywords": [
          "storage",
          "storage locker",
          "storage agreement",
          "ancillary storage",
          "locker rental"
        ],
        "intentPatterns": [
          "storage.*(locker|agreement)",
          "ancillary.*storage"
        ]
      }
    },
    "telecom-licensing-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "low",
      "description": "Telecommunications carrier access licenses",
      "promptTriggers": {
        "keywords": [
          "telecom",
          "telecommunications",
          "carrier access",
          "equipment room",
          "CRTC",
          "riser rights"
        ],
        "intentPatterns": [
          "telecom",
          "telecommunication",
          "carrier.*access",
          "crtc"
        ]
      }
    },
    "lease-compliance-auditor": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "Lease compliance monitoring and obligation tracking",
      "promptTriggers": {
        "keywords": [
          "compliance",
          "insurance audit",
          "environmental compliance",
          "use clause",
          "covenant compliance",
          "lease obligations"
        ],
        "intentPatterns": [
          "complianc",
          "insurance.*audit",
          "environmental.*complianc",
          "use.*clause",
          "covenant"
        ]
      }
    },
    "default-and-remedies-advisor": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "high",
      "description": "Lease defaults and landlord remedies",
      "promptTriggers": {
        "keywords": [
          "default",
          "lease default",
          "cure period",
          "default notice",
          "remedies",
          "lease termination",
          "damages"
        ],
        "intentPatterns": [
          "default",
          "cure.*period",
          "default.*notice",
          "remed(y|ies)",
          "terminat.*lease"
        ]
      }
    },
    "lease-comparison-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "Lease-to-lease comparison and deviation analysis",
      "promptTriggers": {
        "keywords": [
          "compare",
          "comparison",
          "lease comparison",
          "amendment comparison",
          "precedent",
          "deviation",
          "benchmark"
        ],
        "intentPatterns": [
          "compar(e|ison)",
          "benchmark",
          "deviation",
          "precedent",
          "vs\\.?.*lease"
        ]
      }
    },
    "portfolio-strategy-advisor": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "Portfolio lease analysis and renewal prioritization",
      "promptTriggers": {
        "keywords": [
          "portfolio",
          "rollover",
          "expiry cliff",
          "renewal priority",
          "vacancy forecast",
          "lease maturity",
          "portfolio optimization"
        ],
        "intentPatterns": [
          "portfolio",
          "rollover",
          "expiry.*cliff",
          "renewal.*priorit",
          "vacancy.*forecast"
        ]
      }
    },
    "real-options-valuation-expert": {
      "type": "domain",
      "enforcement": "suggest",
      "priority": "medium",
      "description": "Real options valuation for lease flexibility",
      "promptTriggers": {
        "keywords": [
          "real options",
          "option value",
          "renewal option",
          "expansion option",
          "termination right",
          "Black-Scholes",
          "option premium"
        ],
        "intentPatterns": [
          "real.*option",
          "option.*valu",
          "(renewal|expansion|termination).*option",
          "black.*scholes"
        ]
      }
    }
  }
}
```

### 4.2 Priority Classification

**Critical Priority:**
- (None - no mandatory skills for this domain)

**High Priority:**
- commercial-lease-expert
- effective-rent-analyzer
- tenant-credit-analyst
- lease-abstraction-specialist
- offer-to-lease-expert
- negotiation-expert
- default-and-remedies-advisor

**Medium Priority:**
- objection-handling-expert
- consent-to-assignment-expert
- consent-to-sublease-expert
- share-transfer-consent-expert
- lease-surrender-expert
- indemnity-expert
- non-disturbance-expert
- lease-compliance-auditor
- lease-comparison-expert
- portfolio-strategy-advisor
- real-options-valuation-expert

**Low Priority:**
- lease-arbitration-expert
- waiver-agreement-expert
- temporary-license-expert
- storage-agreement-expert
- telecom-licensing-expert

**Deliverables:**
- [ ] skill-rules.json with all 23 skills
- [ ] Keywords and intent patterns for each skill
- [ ] Priority classification applied
- [ ] Validation against skill frontmatter

---

## Phase 5: Build Auto-Generation Tools

### Goal
Create scripts to auto-generate skill-rules.json from skill files

### 5.1 Generator Script

**File:** `.claude/hooks/generate-skill-rules.js`

```javascript
#!/usr/bin/env node
import { readdirSync, readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const PROJECT_DIR = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const SKILLS_DIR = join(PROJECT_DIR, '.claude', 'skills');
const OUTPUT_FILE = join(PROJECT_DIR, '.claude', 'skill-rules.json');

function main() {
    console.log('🔧 Generating skill-rules.json from skill files...\n');

    const skills = {};
    let totalSkills = 0;

    // Read all skill directories
    const skillDirs = readdirSync(SKILLS_DIR, { withFileTypes: true })
        .filter(dirent => dirent.isDirectory())
        .map(dirent => dirent.name)
        .sort();

    console.log(`Found ${skillDirs.length} skill directories\n`);

    for (const skillName of skillDirs) {
        const skillFilePath = join(SKILLS_DIR, skillName, 'SKILL.md');

        try {
            const content = readFileSync(skillFilePath, 'utf-8');
            const frontmatter = extractFrontmatter(content);

            if (!frontmatter.name || !frontmatter.description) {
                console.warn(`⚠️  Skipping ${skillName}: Missing name or description in frontmatter`);
                continue;
            }

            skills[skillName] = {
                type: 'domain',
                enforcement: 'suggest',
                priority: determinePriority(skillName, frontmatter),
                description: frontmatter.description,
                promptTriggers: {
                    keywords: generateKeywords(skillName, frontmatter),
                    intentPatterns: generateIntentPatterns(skillName, frontmatter)
                }
            };

            totalSkills++;
            console.log(`✓ ${skillName}`);
        } catch (err) {
            console.error(`✗ Error processing ${skillName}:`, err.message);
        }
    }

    const output = {
        version: '1.0',
        description: 'Auto-generated skill activation triggers for VP Real Estate lease analysis',
        generation: {
            method: 'auto-generated',
            date: new Date().toISOString(),
            generator: 'generate-skill-rules.js',
            total_skills: totalSkills
        },
        skills: skills
    };

    writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
    console.log(`\n✅ Generated skill-rules.json with ${totalSkills} skills`);
    console.log(`📁 Output: ${OUTPUT_FILE}`);
}

function extractFrontmatter(content) {
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (!frontmatterMatch) {
        return {};
    }

    const frontmatterText = frontmatterMatch[1];
    const frontmatter = {};

    // Simple YAML parser (handles name, description, tags, capability, proactive)
    const lines = frontmatterText.split('\n');
    let currentKey = null;
    let currentValue = '';

    for (const line of lines) {
        const keyMatch = line.match(/^(\w+):\s*(.*)$/);
        if (keyMatch) {
            if (currentKey) {
                frontmatter[currentKey] = currentValue.trim();
            }
            currentKey = keyMatch[1];
            currentValue = keyMatch[2];
        } else if (currentKey) {
            currentValue += ' ' + line.trim();
        }
    }

    if (currentKey) {
        frontmatter[currentKey] = currentValue.trim();
    }

    // Parse tags array if present
    if (frontmatter.tags) {
        const tagsMatch = frontmatter.tags.match(/\[(.*)\]/);
        if (tagsMatch) {
            frontmatter.tags = tagsMatch[1].split(',').map(t => t.trim());
        }
    }

    return frontmatter;
}

function determinePriority(skillName, frontmatter) {
    // High priority skills
    const highPriority = [
        'commercial-lease-expert',
        'effective-rent-analyzer',
        'tenant-credit-analyst',
        'lease-abstraction-specialist',
        'offer-to-lease-expert',
        'negotiation-expert',
        'default-and-remedies-advisor'
    ];

    // Low priority skills
    const lowPriority = [
        'lease-arbitration-expert',
        'waiver-agreement-expert',
        'temporary-license-expert',
        'storage-agreement-expert',
        'telecom-licensing-expert'
    ];

    if (highPriority.includes(skillName)) {
        return 'high';
    } else if (lowPriority.includes(skillName)) {
        return 'low';
    } else {
        return 'medium';
    }
}

function generateKeywords(skillName, frontmatter) {
    const keywords = [];

    // Add skill name variations
    keywords.push(skillName.replace(/-/g, ' '));

    // Extract keywords from description
    const description = frontmatter.description || '';

    // Common keywords to extract
    const keywordPatterns = [
        /\b(NER|NPV|DSCR|SNDA|LOI|TI|CAM)\b/g,  // Acronyms
        /\b(lease|rent|tenant|landlord|compliance|default|option|valuation)\w*/gi,  // Domain terms
    ];

    for (const pattern of keywordPatterns) {
        const matches = description.matchAll(pattern);
        for (const match of matches) {
            const keyword = match[0].toLowerCase();
            if (keyword.length > 2 && !keywords.includes(keyword)) {
                keywords.push(keyword);
            }
        }
    }

    // Add tags if present
    if (Array.isArray(frontmatter.tags)) {
        frontmatter.tags.forEach(tag => {
            if (!keywords.includes(tag.toLowerCase())) {
                keywords.push(tag.toLowerCase());
            }
        });
    }

    return keywords.slice(0, 15);  // Limit to top 15 keywords
}

function generateIntentPatterns(skillName, frontmatter) {
    const patterns = [];

    // Generate patterns based on skill type
    if (skillName.includes('expert')) {
        const topic = skillName.replace('-expert', '').replace(/-/g, ' ');
        patterns.push(`${topic.replace(' ', '.*')}`);
    }

    if (skillName.includes('analyst') || skillName.includes('analyzer')) {
        patterns.push(`(analyz|calculat|assess).*${skillName.split('-')[0]}`);
    }

    if (skillName.includes('specialist')) {
        patterns.push(`${skillName.split('-')[0]}.*specialist`);
    }

    // Extract key action verbs from description
    const description = frontmatter.description || '';
    const actionVerbs = [
        'review', 'analyze', 'calculate', 'assess', 'evaluate',
        'negotiate', 'draft', 'structure', 'compare', 'value'
    ];

    for (const verb of actionVerbs) {
        if (description.toLowerCase().includes(verb)) {
            const firstWord = skillName.split('-')[0];
            patterns.push(`${verb}.*(${firstWord}|lease)`);
        }
    }

    return patterns.slice(0, 5);  // Limit to top 5 patterns
}

main();
```

**Make executable:**
```bash
chmod +x .claude/hooks/generate-skill-rules.js
```

### 5.2 Test Generator

```bash
cd .claude/hooks
node generate-skill-rules.js
```

**Expected output:**
```
🔧 Generating skill-rules.json from skill files...

Found 23 skill directories

✓ commercial-lease-expert
✓ consent-to-assignment-expert
✓ consent-to-sublease-expert
✓ default-and-remedies-advisor
✓ effective-rent-analyzer
...
✓ tenant-credit-analyst
✓ waiver-agreement-expert

✅ Generated skill-rules.json with 23 skills
📁 Output: /workspaces/lease-abstract/.claude/skill-rules.json
```

**Deliverables:**
- [ ] generate-skill-rules.js script
- [ ] Auto-generated skill-rules.json
- [ ] Verification that all 23 skills included
- [ ] npm script: `npm run generate-rules`

---

## Phase 6: Testing and Validation

### Goal
Comprehensive testing of skills and hooks system

### 6.1 Manual Hook Testing

**Test UserPromptSubmit:**
```bash
cd .claude/hooks

# Test financial analysis keywords
echo '{"prompt":"calculate NER for this lease deal"}' | ./skill-activation-prompt.sh

# Expected: Suggests effective-rent-analyzer

# Test legal keywords
echo '{"prompt":"review this assignment consent agreement"}' | ./skill-activation-prompt.sh

# Expected: Suggests consent-to-assignment-expert, commercial-lease-expert

# Test compliance keywords
echo '{"prompt":"audit insurance requirements"}' | ./skill-activation-prompt.sh

# Expected: Suggests lease-compliance-auditor
```

**Test PreToolUse:**
```bash
# Test offer to lease detection
echo '{"tool":"Read","parameters":{"file_path":"./Sample_Inputs/sample_offer_to_lease.pdf"}}' | ./pre-tool-use-skill-loader.sh

# Expected: Suggests offer-to-lease-expert, effective-rent-analyzer, commercial-lease-expert, negotiation-expert

# Test financial statement detection
echo '{"tool":"Read","parameters":{"file_path":"./Sample_Inputs/financial_statements.pdf"}}' | ./pre-tool-use-skill-loader.sh

# Expected: Suggests tenant-credit-analyst, effective-rent-analyzer

# Test calculator input detection
echo '{"tool":"Read","parameters":{"file_path":"./Eff_Rent_Calculator/deals/tech_distribution_input.json"}}' | ./pre-tool-use-skill-loader.sh

# Expected: Suggests effective-rent-analyzer, commercial-lease-expert
```

### 6.2 Integration Testing with Claude

**Test Scenario 1: Lease Abstraction**
```
User: "Abstract this lease agreement"
Expected: Hook suggests lease-abstraction-specialist
Claude: Loads skill and uses /abstract-lease command
```

**Test Scenario 2: Effective Rent Analysis**
```
User: "Calculate NER for this offer to lease"
Expected: Hook suggests effective-rent-analyzer, offer-to-lease-expert
Claude: Loads skills and uses /effective-rent command
```

**Test Scenario 3: Tenant Credit Review**
```
User: Read Sample_Inputs/financial_statements.pdf
Expected: PreToolUse hook suggests tenant-credit-analyst (BEFORE file read)
Claude: Loads skill proactively, then reads file
```

### 6.3 Token Efficiency Validation

**Measure:**
1. Conversation with manual skill invocation (baseline)
2. Conversation with hook-based activation
3. Compare token usage

**Target:** <20% increase in token usage vs manual (due to hook suggestions), but 100% increase in expertise utilization

### 6.4 Validation Checklist

**Skills:**
- [ ] All 23 skills have proper frontmatter
- [ ] All skills loadable via Skill tool
- [ ] Skills cross-reference related commands
- [ ] Skills provide actionable guidance

**Hooks:**
- [ ] UserPromptSubmit detects financial keywords
- [ ] UserPromptSubmit detects legal keywords
- [ ] PreToolUse detects lease documents
- [ ] PreToolUse detects financial statements
- [ ] PreToolUse detects calculator inputs
- [ ] Hooks fail gracefully on errors
- [ ] Hooks don't block tool execution

**Auto-Generation:**
- [ ] Generator creates valid skill-rules.json
- [ ] All 23 skills included in output
- [ ] Keywords extracted correctly
- [ ] Intent patterns generated correctly
- [ ] Priorities assigned correctly

**Integration:**
- [ ] settings.json hooks configuration valid
- [ ] Hooks executable and have correct permissions
- [ ] package.json dependencies installed
- [ ] TypeScript compiles without errors
- [ ] Manual tests pass
- [ ] Claude integration tests pass

**Deliverables:**
- [ ] Test results document
- [ ] Token efficiency metrics
- [ ] Validation checklist completed
- [ ] Bug fixes for any issues found

---

## Implementation Timeline

### Week 1: Foundation (Phases 1-2)
**Days 1-2:** Phase 1 - Audit existing skills
- Audit frontmatter quality
- Enhance descriptions
- Standardize metadata

**Days 3-5:** Phase 2 - Create new skills
- Create 3 financial analysis skills
- Create 3 compliance/process skills
- Create 2 investment/portfolio skills

### Week 2: Infrastructure (Phases 3-4)
**Days 1-3:** Phase 3 - Implement hooks
- Create hooks directory structure
- Implement UserPromptSubmit hook
- Implement PreToolUse hook
- Create lease-types-map.json
- Write hook documentation

**Days 4-5:** Phase 4 - Skill activation rules
- Create initial skill-rules.json manually
- Validate against all 23 skills
- Test keyword/pattern matching

### Week 3: Automation & Testing (Phases 5-6)
**Days 1-2:** Phase 5 - Auto-generation
- Build generate-skill-rules.js
- Test auto-generation
- Compare manual vs auto-generated

**Days 3-5:** Phase 6 - Testing
- Manual hook testing
- Integration testing with Claude
- Token efficiency validation
- Bug fixes and refinements

### Total Duration: 15 working days (3 weeks)

---

## Success Metrics

### Quantitative Metrics

**Coverage:**
- ✅ 23 total skills (15 existing + 8 new)
- ✅ 28 slash commands integrated
- ✅ 10+ document type patterns detected

**Activation:**
- Target: 80%+ relevant skill suggestions
- Target: <5% irrelevant suggestions
- Target: 96% token efficiency (proactive vs reactive)

**Performance:**
- Hook execution: <100ms per trigger
- Zero blocking failures
- 100% graceful error handling

### Qualitative Metrics

**User Experience:**
- Skills suggested contextually without manual invocation
- Reduced cognitive load (don't need to remember which skills exist)
- Expertise accessed on-demand

**Maintainability:**
- Single source of truth (skill files)
- Auto-generation reduces manual effort
- Clear documentation for updates

**Scalability:**
- Can add new skills without rewriting hooks
- Pattern-based detection scales to new document types
- Token-efficient design supports 50+ skills

---

## Maintenance Plan

### Regular Maintenance (Monthly)

**Audit:**
- [ ] Review skill usage metrics (which skills activated most)
- [ ] Check for false positives/negatives in hook triggers
- [ ] Update keywords based on user language patterns

**Updates:**
- [ ] Add new document patterns to lease-types-map.json
- [ ] Refine intent patterns in skill-rules.json
- [ ] Update skill priorities based on usage

### Adding New Skills

**Process:**
1. Create skill directory: `.claude/skills/new-skill/`
2. Write SKILL.md with proper frontmatter
3. Regenerate: `npm run generate-rules`
4. Test: Mention skill keywords in prompt
5. Verify: Check skill suggested by hook
6. Document: Add to skills inventory

### Updating Hooks

**When to Update:**
- New document types discovered (update lease-types-map.json)
- New keyword patterns identified (update generator logic)
- Performance issues (optimize pattern matching)
- Claude Code API changes (update hook signatures)

**Testing After Updates:**
```bash
npm run test-prompt
npm run test-pretool
npm run generate-rules
```

### Versioning

**skill-rules.json:**
- Increment version when changing structure
- Document changes in generation metadata
- Keep git history for rollback

**Hooks:**
- Version in README.md
- Breaking changes require version bump
- Backward compatibility preferred

---

## Risk Mitigation

### Risk 1: Hooks Don't Trigger

**Mitigation:**
- Validate settings.json syntax
- Check script permissions (chmod +x)
- Test manually before integration
- Fail gracefully (never block)

### Risk 2: Wrong Skills Suggested

**Mitigation:**
- Conservative keyword matching (avoid over-triggering)
- Priority system (critical > high > medium > low)
- Limit suggestions (top 10 max)
- Continuous refinement based on feedback

### Risk 3: Token Budget Exceeded

**Mitigation:**
- Proactive detection (96% efficiency)
- Limit suggestions (top 10-15 skills max)
- Monitor token usage in testing
- Adjust skill content size if needed

### Risk 4: Maintenance Burden

**Mitigation:**
- Auto-generation (single source of truth)
- Clear documentation
- npm scripts for common tasks
- Modular design (easy to update parts)

---

## Appendices

### Appendix A: File Checklist

**New Files to Create (17 total):**
- [ ] .claude/settings.json
- [ ] .claude/skill-rules.json (auto-generated)
- [ ] .claude/hooks/skill-activation-prompt.sh
- [ ] .claude/hooks/skill-activation-prompt.ts
- [ ] .claude/hooks/pre-tool-use-skill-loader.sh
- [ ] .claude/hooks/pre-tool-use-skill-loader.ts
- [ ] .claude/hooks/generate-skill-rules.js
- [ ] .claude/hooks/lease-types-map.json
- [ ] .claude/hooks/package.json
- [ ] .claude/hooks/README.md
- [ ] .claude/skills/effective-rent-analyzer/SKILL.md
- [ ] .claude/skills/tenant-credit-analyst/SKILL.md
- [ ] .claude/skills/lease-abstraction-specialist/SKILL.md
- [ ] .claude/skills/lease-compliance-auditor/SKILL.md
- [ ] .claude/skills/default-and-remedies-advisor/SKILL.md
- [ ] .claude/skills/lease-comparison-expert/SKILL.md
- [ ] .claude/skills/portfolio-strategy-advisor/SKILL.md
- [ ] .claude/skills/real-options-valuation-expert/SKILL.md

**Files to Enhance (15 existing skills):**
- [ ] Audit and enhance frontmatter for all 15 existing skills

### Appendix B: Command Reference

```bash
# Generate skill rules
cd .claude/hooks
npm run generate-rules

# Test UserPromptSubmit
npm run test-prompt

# Test PreToolUse
npm run test-pretool

# Install dependencies
npm install

# Make scripts executable
chmod +x *.sh *.ts *.js

# Regenerate after adding skills
npm run generate-rules
```

### Appendix C: Integration with Existing Commands

**Financial Analysis Commands → Skills:**
- /effective-rent → effective-rent-analyzer, commercial-lease-expert
- /tenant-credit → tenant-credit-analyst
- /renewal-economics → effective-rent-analyzer, portfolio-strategy-advisor
- /option-value → real-options-valuation-expert
- /rollover-analysis → portfolio-strategy-advisor

**Abstraction Commands → Skills:**
- /abstract-lease → lease-abstraction-specialist, commercial-lease-expert
- /critical-dates → lease-abstraction-specialist

**Comparison Commands → Skills:**
- /compare-amendment → lease-comparison-expert, commercial-lease-expert
- /compare-offers → lease-comparison-expert, offer-to-lease-expert, negotiation-expert
- /compare-precedent → lease-comparison-expert
- /lease-vs-lease → lease-comparison-expert

**Compliance Commands → Skills:**
- /default-analysis → default-and-remedies-advisor, commercial-lease-expert
- /insurance-audit → lease-compliance-auditor
- /environmental-compliance → lease-compliance-auditor
- /assignment-consent → consent-to-assignment-expert

### Appendix D: Skill Invocation Examples

**Manual Invocation (existing):**
```
User: "Skill tool: commercial-lease-expert"
Claude: Loads skill and provides expertise
```

**Automatic Invocation (with hooks):**
```
User: "Review this lease agreement"
Hook: Suggests commercial-lease-expert, lease-abstraction-specialist
Claude: (autonomously loads skills) Provides expertise
```

**Proactive Invocation (PreToolUse):**
```
User: "Read Sample_Inputs/offer_to_lease.pdf"
Hook: (BEFORE read) Suggests offer-to-lease-expert, effective-rent-analyzer
Claude: (loads skills proactively)
Read tool: (THEN executes) File contents loaded
Claude: Analyzes using pre-loaded expertise
```

---

## Approval and Sign-Off

**Prepared By:** Claude Code
**Date:** November 13, 2025
**Version:** 1.0

**Ready for Review:**
- [ ] Review implementation plan
- [ ] Approve phased approach
- [ ] Approve timeline (3 weeks)
- [ ] Approve new skills list (8 new)
- [ ] Approve hooks architecture (UserPromptSubmit + PreToolUse)
- [ ] Approve auto-generation approach

**Decision:**
- [ ] Proceed with full implementation as planned
- [ ] Proceed with modifications (specify):
- [ ] Defer to later date
- [ ] Reject plan

**Approver:** _______________________
**Date:** _______________________

---

**End of Implementation Plan**
