
# STRATOSYNC Unified Dependency Diagram v1.1

                ┌────────────────────────┐
                │   Core Orchestrator    │
                └────────────┬───────────┘
                             │
    ┌──────────────┬─────────┴─────────┬──────────────┐
    │              │                   │              │
Human Engine   Business Engine    Org Engine     Scenario Engine
    │              │                   │              │
    └──────────────┴──────────────┬────┴──────────────┘
                                   │
                           Alignment Engine
                                   │
                           Executive Synthesis
