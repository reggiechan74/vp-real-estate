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

interface AgentMatch {
    name: 'adam' | 'reggie-chan-vp' | 'dennis';
    displayName: string;
    role: string;
    model: 'haiku' | 'sonnet' | 'opus';
}

async function main() {
    try {
        const input = readFileSync(0, 'utf-8');
        const data: HookInput = JSON.parse(input);

        // First check for agent invocation
        const agentMatch = detectAgent(data.prompt);
        if (agentMatch) {
            const output = formatAgentSuggestion(agentMatch);
            console.log(output);
            process.exit(0);
        }

        // If no agent detected, proceed with skill matching
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

function detectAgent(prompt: string): AgentMatch | null {
    const lowerPrompt = prompt.toLowerCase();

    // Agent detection patterns
    const agents = [
        {
            name: 'adam' as const,
            displayName: 'Adam',
            role: 'Senior Analyst',
            model: 'haiku' as const,
            patterns: [
                /^adam[,:\s]/i,           // "Adam," or "Adam:" or "Adam "
                /\bhey\s+adam\b/i,        // "hey adam"
                /\bask\s+adam\b/i,        // "ask adam"
                /\badam\s+can\s+you\b/i,  // "adam can you"
                /\badam\s+what\b/i,       // "adam what"
                /\badam\s+please\b/i,     // "adam please"
            ]
        },
        {
            name: 'reggie-chan-vp' as const,
            displayName: 'Reggie',
            role: 'VP of Leasing and Asset Management',
            model: 'sonnet' as const,
            patterns: [
                /^reggie[,:\s]/i,
                /\bhey\s+reggie\b/i,
                /\bask\s+reggie\b/i,
                /\breggie\s+can\s+you\b/i,
                /\breggie\s+what\b/i,
                /\breggie\s+please\b/i,
            ]
        },
        {
            name: 'dennis' as const,
            displayName: 'Dennis',
            role: 'Strategic Advisor',
            model: 'opus' as const,
            patterns: [
                /^dennis[,:\s]/i,
                /\bhey\s+dennis\b/i,
                /\bask\s+dennis\b/i,
                /\bdennis\s+can\s+you\b/i,
                /\bdennis\s+what\b/i,
                /\bdennis\s+please\b/i,
            ]
        }
    ];

    // Check each agent's patterns
    for (const agent of agents) {
        const matched = agent.patterns.some(pattern => pattern.test(prompt));
        if (matched) {
            return {
                name: agent.name,
                displayName: agent.displayName,
                role: agent.role,
                model: agent.model
            };
        }
    }

    return null;
}

function formatAgentSuggestion(agent: AgentMatch): string {
    // Define signature requirements for each agent
    const signatures: Record<string, string> = {
        'dennis': '**— Dennis**\n*Strategic Advisor | 36+ years institutional real estate experience*',
        'reggie-chan-vp': '**— Reggie, VP Real Estate**',
        'adam': '**— Adam | Senior Analyst**'
    };

    let output = '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
    output += '👤 AGENT ACTIVATION DETECTED\n';
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';
    output += `🎯 AGENT REQUESTED: ${agent.displayName}\n`;
    output += `📋 Role: ${agent.role}\n`;
    output += `🤖 Model: ${agent.model}\n\n`;
    output += `ACTION: Use Task tool with subagent_type="${agent.name}"\n`;
    output += `⚠️  IMPORTANT: Pass through ${agent.displayName}'s response UNFILTERED\n`;
    output += `✍️  SIGNATURE REQUIRED:\n\n${signatures[agent.name]}\n\n`;
    output += `⚠️  CRITICAL: Verify the agent's response ends with their signature.\n`;
    output += `    If missing, DO NOT add it yourself - the agent must include it.\n`;
    output += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
    return output;
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
