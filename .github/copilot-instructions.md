# Copilot Instructions for VS Code Custom Agents Project

# Project Name Guidelines

* [Product Vision and Goals](../project/PRODUCT.md): Understand the high-level vision and objectives of the product to ensure alignment with business goals.
* [System Architecture and Design Principles](../project/ARCHITECTURE.md): Overall system architecture, design patterns, and design principles that guide the development process.
* [Contributing Guidelines](../project/CONTRIBUTING.md): Overview of the project's contributing guidelines and collaboration practices.
* [Implementation Plan](../project/PLAN.md): Step-by-step implementation plan outlining phases, milestones, and deliverables.

Suggest to update these documents if you find any incomplete or conflicting information during your work.

## Project Overview

This is a VS Code custom chat agents workspace using the `chatagent` format. The project defines personality-driven AI agents with specific tools and behavioral patterns.

## Architecture

- **Agent Definitions**: All agents live in `.github/agents/` as `.agent.md` files
- **Format**: Each agent uses the `chatagent` markdown code fence with YAML frontmatter
- **Purpose**: Create specialized AI assistants with distinct personalities and capabilities

## Agent File Structure

Each agent file (`.agent.md`) follows this pattern:

```yaml
---
description: "Brief description of agent's role and expertise"
tools: ['tool1', 'tool2']
handoffs:
  - label: Agent Name
    agent: 'agent-id'
    prompt: Context to pass when handing off to this agent
---
Instructions defining personality, language, and behavior
```

**Note:** The `.agent.md` files should NOT include ` ```chatagent ` code fences. The file extension itself identifies them as agent files.

**Key Components:**
- `description`: Concise summary of agent's persona and capabilities (used in UI)
- `tools`: Array of VS Code tools the agent can access (e.g., `runTasks`, `search`, `runSubagent`, `runCommands`, `edit`)
- `handoffs`: Array of other agents this agent can transfer work to, with:
  - `label`: Display name for the handoff option
  - `agent`: The agent ID to hand off to
  - `prompt`: Context message sent to the receiving agent explaining the handoff
- Instructions body: Detailed behavioral guidelines, language requirements, personality traits, and handoff decision criteria

## Naming Conventions

- Agent filenames can include spaces (e.g., `john english.agent.md`)
- Use descriptive names that reflect the agent's persona
- Always use `.agent.md` extension

## Existing Agents

### Orchestrator Agent

1. **jefe de la banda.agent.md**: The Chief orchestrator who coordinates the specialized team
   - Tools: `runTasks`, `search`, `runSubagent`
   - Handoffs: `gato`, `john english`, `pedro picapiedra`
   - Focus: Strategic coordination, task delegation, team management
   - Role: Analyzes problems, divides work, and delegates to specialists

### Specialist Agents (Work under Chief's coordination)

2. **gato.agent.md**: Spanish-speaking (Andalusian) Strategic Analyst
   - Tools: `search`, `runSubagent`
   - Handoffs: `jefe de la banda`
   - Focus: Code analysis, strategy design, pattern recognition, research
   - Role: The team's brain - analyzes and designs intelligent approaches

3. **john english.agent.md**: British Writer and Documentalist
   - Tools: `edit`
   - Handoffs: `jefe de la banda`
   - Focus: File creation/editing, documentation, refined writing
   - Role: The team's pen - writes and edits with sophistication

4. **pedro picapiedra.agent.md**: Spanish-speaking Practical Executor
   - Tools: `runCommands`
   - Handoffs: `jefe de la banda`
   - Focus: Command execution, testing, practical implementation
   - Role: The team's hands - executes and tests with enthusiasm

## Team Collaboration Model

The agents work in an **orchestrated hierarchy**:

```
                    ┌─────────────────────┐
                    │  Jefe de la Banda   │
                    │   (Orchestrator)    │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
         ┌────────┐      ┌──────────┐    ┌──────────┐
         │  Gato  │      │   John   │    │  Pedro   │
         │Analyst │      │  Writer  │    │ Executor │
         └────────┘      └──────────┘    └──────────┘
```

**Workflow Pattern:**
1. **Chief** receives request and creates strategy
2. **Chief** delegates to specialists:
   - **Gato** for analysis and strategic planning
   - **John** for writing and editing files
   - **Pedro** for executing commands and testing
3. **Specialists** complete their tasks and report back to Chief
4. **Chief** synthesizes results and coordinates next steps

**Complementary Specializations:**
- **Gato**: Thinks and plans (like addition/subtraction - finding patterns)
- **John**: Writes and documents (like multiplication - creating from templates)
- **Pedro**: Executes and tests (like division - breaking down into actions)

## Creating New Agents

When adding new agents:
1. Create `.agent.md` file in `.github/agents/`
2. Define clear, specific personality and expertise
3. Select appropriate tools based on agent's intended functions
4. Write instructions in the voice/style the agent should use
5. Include language requirements if agent should speak non-English
6. Configure handoffs to other agents when collaboration is needed
7. Include clear criteria in instructions for when to hand off to other agents

## Tool Selection Guide

- `runTasks`: For agents that manage workflows and task execution
- `search`: For research-oriented agents
- `runSubagent`: For agents that coordinate with other agents
- `runCommands`: For agents that execute terminal commands
- `edit`: For agents that modify files

## Testing

After creating/modifying an agent, test by invoking it in VS Code's chat interface to ensure personality and capabilities work as expected.
