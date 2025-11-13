#!/usr/bin/env node
import { readdirSync, readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

// Get project root (parent of .claude/hooks)
const PROJECT_DIR = process.env.CLAUDE_PROJECT_DIR || join(process.cwd(), '..', '..');
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
        patterns.push(`${topic.replace(/ /g, '.*')}`);
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
