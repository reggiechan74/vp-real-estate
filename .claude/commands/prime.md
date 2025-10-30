---
description: Load Claude Code documentation into context
---

# Prime Command - Load Documentation

This command loads Claude Code documentation into context. You can specify a specific topic or load all documentation.

## Usage

- `/prime` - Load all documentation (default)
- `/prime [topic]` - Load specific topic documentation

## Available Topics

## Getting Started

**TOPIC: overview**
- Claude Code overview and features
- URLs:
  - https://docs.claude.com/en/docs/claude-code/overview
  - https://docs.claude.com/en/docs/intro

**TOPIC: getting-started**
- Quickstart, common workflows, and web interface
- URLs:
  - https://docs.claude.com/en/docs/claude-code/quickstart
  - https://docs.claude.com/en/docs/claude-code/common-workflows
  - https://docs.claude.com/en/docs/claude-code/claude-code-on-the-web

## Build with Claude Code

**TOPIC: sub-agents**
- Sub-agents and task delegation
- URLs:
  - https://docs.claude.com/en/docs/claude-code/sub-agents

**TOPIC: plugins**
- Claude Code plugins and plugin marketplaces
- URLs:
  - https://docs.claude.com/en/docs/claude-code/plugins
  - https://docs.claude.com/en/docs/claude-code/plugin-marketplaces

**TOPIC: agent-skills**
- Agent Skills overview, quickstart, and best practices
- URLs:
  - https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
  - https://docs.claude.com/en/docs/agents-and-tools/agent-skills/quickstart
  - https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
  - https://docs.claude.com/en/docs/claude-code/skills

**TOPIC: output-styles**
- Custom output styles
- URLs:
  - https://docs.claude.com/en/docs/claude-code/output-styles

**TOPIC: hooks**
- Hooks system and hooks guide
- URLs:
  - https://docs.claude.com/en/docs/claude-code/hooks
  - https://docs.claude.com/en/docs/claude-code/hooks-guide

**TOPIC: headless**
- Headless mode for Claude Code
- URLs:
  - https://docs.claude.com/en/docs/claude-code/headless

**TOPIC: ci-cd**
- GitHub Actions and GitLab CI/CD integration
- URLs:
  - https://docs.claude.com/en/docs/claude-code/github-actions
  - https://docs.claude.com/en/docs/claude-code/gitlab-ci-cd

**TOPIC: mcp**
- Model Context Protocol (MCP)
- URLs:
  - https://docs.claude.com/en/docs/mcp
  - https://docs.claude.com/en/docs/claude-code/mcp

**TOPIC: troubleshooting**
- Troubleshooting guide
- URLs:
  - https://docs.claude.com/en/docs/claude-code/troubleshooting

## Deployment

**TOPIC: deployment**
- Third-party integrations, Amazon Bedrock, and Google Vertex AI
- URLs:
  - https://docs.claude.com/en/docs/claude-code/third-party-integrations
  - https://docs.claude.com/en/docs/claude-code/amazon-bedrock
  - https://docs.claude.com/en/docs/claude-code/google-vertex-ai

## Administration

**TOPIC: administration**
- Identity and Access Management, monitoring, costs, and analytics
- URLs:
  - https://docs.claude.com/en/docs/claude-code/iam
  - https://docs.claude.com/en/docs/claude-code/monitoring-usage
  - https://docs.claude.com/en/docs/claude-code/costs
  - https://docs.claude.com/en/docs/claude-code/analytics

## Configuration

**TOPIC: configuration**
- Settings, terminal, model, memory, statusline, installation, security, and data usage
- URLs:
  - https://docs.claude.com/en/docs/claude-code/settings
  - https://docs.claude.com/en/docs/claude-code/terminal-config
  - https://docs.claude.com/en/docs/claude-code/model-config
  - https://docs.claude.com/en/docs/claude-code/memory
  - https://docs.claude.com/en/docs/claude-code/statusline
  - https://docs.claude.com/en/docs/claude-code/setup
  - https://docs.claude.com/en/docs/claude-code/security
  - https://docs.claude.com/en/docs/claude-code/data-usage

**TOPIC: ide**
- IDE integrations (VS Code and JetBrains)
- URLs:
  - https://docs.claude.com/en/docs/claude-code/vs-code
  - https://docs.claude.com/en/docs/claude-code/jetbrains

## Reference

**TOPIC: cli-reference**
- CLI commands, options, and reference
- URLs:
  - https://docs.claude.com/en/docs/claude-code/cli-reference
  - https://docs.claude.com/en/docs/claude-code/settings#tools-available-to-claude

**TOPIC: reference**
- Interactive mode, checkpointing, and plugins reference
- URLs:
  - https://docs.claude.com/en/docs/claude-code/interactive-mode
  - https://docs.claude.com/en/docs/claude-code/checkpointing
  - https://docs.claude.com/en/docs/claude-code/plugins-reference

**TOPIC: slash-commands**
- Creating and using custom slash commands
- URLs:
  - https://docs.claude.com/en/docs/claude-code/slash-commands

## Additional Resources

**TOPIC: tools**
- Text editor tools and tool use
- URLs:
  - https://docs.claude.com/en/docs/agents-and-tools/tool-use/text-editor-tool

---

## Processing Instructions

Based on the argument provided (or lack thereof), determine which URLs to fetch:

1. **If no argument or "all"**: Fetch ALL URLs from all topics
2. **If specific topic provided**: Fetch only URLs for that topic
3. **If invalid topic**: List available topics and ask user to specify

Use WebFetch tool to load each URL with the prompt: "Extract all documentation content, including examples, code snippets, and usage instructions"

**Example commands:**
- `/prime` → loads all documentation
- `/prime slash-commands` → loads only slash commands documentation
- `/prime hooks` → loads only hooks documentation
- `/prime mcp` → loads only MCP documentation
