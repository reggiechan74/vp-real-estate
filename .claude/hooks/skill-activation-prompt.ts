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
        output += '⚠️  CRITICAL SKILLS (REQUIRED):\n';
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
