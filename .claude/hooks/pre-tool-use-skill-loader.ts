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
