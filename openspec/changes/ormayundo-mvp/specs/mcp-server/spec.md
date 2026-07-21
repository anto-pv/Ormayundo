## ADDED Requirements

### Requirement: MCP memory tools

The system SHALL expose the memory engine over the Model Context Protocol as two
tools: `remember` (accepts text, ingests it into the graph) and `recall` (accepts a
query, returns connected facts as text). The server SHALL operate against a
configurable database path.

#### Scenario: remember ingests text

- **WHEN** an MCP client calls `remember` with a block of text
- **THEN** the text is ingested into the graph and the tool reports success

#### Scenario: recall returns memory

- **WHEN** an MCP client calls `recall` with a query after prior `remember` calls
- **THEN** the tool returns the connected facts relevant to the query

#### Scenario: Shared persistent store

- **WHEN** the server restarts and `recall` is called
- **THEN** memories written before the restart are still returned
