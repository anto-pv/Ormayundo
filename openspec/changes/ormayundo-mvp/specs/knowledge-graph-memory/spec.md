## ADDED Requirements

### Requirement: SQLite graph store

The system SHALL persist the knowledge graph in a single SQLite file containing a
`nodes` table (unique entity name plus embedding) and an `edges` table (source,
relation, destination). The store SHALL support upserting a node by name, adding an
edge between two nodes, retrieving the nearest nodes to a query vector by cosine
similarity, and retrieving the neighbors of a node.

#### Scenario: Upsert is idempotent by name

- **WHEN** the same entity name is upserted twice
- **THEN** the store contains exactly one node for that name and reuses its id

#### Scenario: Round-trip triples

- **WHEN** triples are written and then queried back
- **THEN** the stored nodes and edges match what was written

#### Scenario: Nearest-node ranking

- **WHEN** the store is asked for the nearest nodes to a query vector
- **THEN** it returns nodes ordered by descending cosine similarity, limited to top-k

### Requirement: Text ingestion into the graph

The system SHALL accept arbitrary text, split it into chunks, extract
`(subject, relation, object)` triples from each chunk using the Claude API, embed
each distinct entity locally, and write the resulting nodes and edges to the store.

#### Scenario: Paragraph produces a graph

- **WHEN** a paragraph describing related entities is ingested
- **THEN** the store contains nodes for the entities and edges for their relations

#### Scenario: Extraction output is parsed safely

- **WHEN** the model returns triples
- **THEN** malformed or incomplete triples are skipped and valid ones are written

### Requirement: Semantic graph-hop recall

The system SHALL answer a natural-language query by embedding it, selecting the
nearest entity nodes, expanding 1–2 hops along edges, and returning the connected
subgraph formatted as readable text.

#### Scenario: Query returns connected facts

- **WHEN** a question is asked about a previously ingested topic
- **THEN** the system returns the relevant entities and the relations linking them

#### Scenario: No match returns empty result

- **WHEN** a query matches no entity nodes above threshold
- **THEN** the system returns an empty (not erroneous) result

### Requirement: Local embedding interface

The system SHALL compute embeddings through a single `embed(texts) -> vectors`
interface backed by a local `sentence-transformers` model, requiring no external
API key for embeddings.

#### Scenario: Embeddings need no network credential

- **WHEN** text is embedded
- **THEN** the operation succeeds without an embeddings API key

### Requirement: Configuration

The system SHALL read the Claude credential from `ANTHROPIC_API_KEY` and store the
graph at a configurable database path defaulting to `~/.ormayundo/memory.db`.

#### Scenario: Default database location

- **WHEN** no database path is provided
- **THEN** the engine uses `~/.ormayundo/memory.db`
