## ADDED Requirements

### Requirement: Installable Claude plugin

The system SHALL provide a Claude plugin that registers the Ormayundo MCP server so
that installing the plugin makes the `remember` and `recall` tools available to the
agent. The plugin SHALL document the single required credential (`ANTHROPIC_API_KEY`)
and the configurable database path.

#### Scenario: Plugin exposes memory tools

- **WHEN** the plugin is installed and Claude is started
- **THEN** the `remember` and `recall` tools are available to the agent

#### Scenario: Documented configuration

- **WHEN** a user reads the plugin's setup instructions
- **THEN** they learn the required `ANTHROPIC_API_KEY` env var and how to set the
  database path
