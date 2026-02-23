from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Protocol, Any
import json
from pathlib import Path

@dataclass
class MarketDataPacket:
    # normalized market inputs for v1.0 market layer
    MVI: str = "中程度"
    IGM: str = "横ばい"
    CPI: str = "中圧"
    RFI: str = "中摩擦"
    # numeric layer (non-public) 0-4
    mvi_score: float = 2.0
    igm_score: float = 2.0
    cpi_score: float = 2.0
    rfi_score: float = 2.0
    sources: Optional[Dict[str, Any]] = None

class MarketProvider(Protocol):
    def fetch(self, query: Dict[str, Any]) -> MarketDataPacket: ...

class FileMarketProvider:
    """Offline provider. Reads a JSON file containing the MarketDataPacket fields."""
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def fetch(self, query: Dict[str, Any]) -> MarketDataPacket:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return MarketDataPacket(**data)

class StubProvider:
    """Placeholder for future API providers (FRED/WorldBank/OECD/Trends)."""
    def fetch(self, query: Dict[str, Any]) -> MarketDataPacket:
        # No network in this package by default. Return neutral packet.
        return MarketDataPacket(sources={"mode": "stub", "query": query})

def get_provider(kind: str, path: Optional[str] = None) -> MarketProvider:
    kind = (kind or "stub").lower()
    if kind == "file":
        if not path:
            raise ValueError("File provider requires path=...")
        return FileMarketProvider(path)
    return StubProvider()
