"""Schema for Knowledge Base"""

import json
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class KnowledgeEntry(BaseModel):
    """Represents a single knowledge base entry."""

    name: str = Field(..., description="Name of the person/entity")
    summary: str = Field(..., description="Summary/description of the entry")
    category: Optional[str] = Field(default=None, description="Optional category")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, v):
        if not v or not v.strip():
            raise ValueError("Summary cannot be empty")
        return v.strip()

    def to_dict(self) -> dict[str, Optional[str]]:
        """Convert to dictionary representation."""
        return {"name": self.name, "summary": self.summary, "category": self.category}

    @classmethod
    def from_dict(cls, data: dict[str, Optional[str]]) -> "KnowledgeEntry":
        """Create KnowledgeEntry from dictionary."""
        return cls(
            name=data.get("name", ""),
            summary=data.get("summary", ""),
            category=data.get("category"),
        )

    def get_characters(self) -> set[str]:
        """
        Extract characters from the entry name for similarity matching.
        """
        return set(self.name.lower())


class KnowledgeBase(BaseModel):
    """Represents the entire knowledge base with search capabilities."""

    entries: list[KnowledgeEntry] = Field(
        default_factory=list, description="List of knowledge entries"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_json_file(cls, file_path: str) -> "KnowledgeBase":
        """Load knowledge base from JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        entries = []
        for entry_data in data.get("entries", []):
            entries.append(KnowledgeEntry.from_dict(entry_data))

        return cls(entries=entries)

    def to_json_file(self, file_path: str) -> None:
        """Save knowledge base to JSON file."""
        data = {"entries": [entry.to_dict() for entry in self.entries]}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def jaccard_similarity(self, set1: set, set2: set) -> float:
        """Calculate Jaccard similarity between two sets."""
        if not set1 and not set2:
            return 0.0
        return len(set1 & set2) / len(set1 | set2)

    def search(
        self, query: str, threshold: float = 0.1, max_results: int = 5
    ) -> list[tuple[KnowledgeEntry, float]]:
        """
        Search for entries using character-based Jaccard similarity.
        """
        query_characters = set(query.lower())

        results = []
        for entry in self.entries:
            entry_characters = entry.get_characters()
            similarity = self.jaccard_similarity(query_characters, entry_characters)
            if similarity >= threshold:
                results.append((entry, similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:max_results]

    def find_by_name(self, name: str) -> Optional[KnowledgeEntry]:
        """Find entry by exact name match (case-insensitive)."""
        name_lower = name.lower()
        for entry in self.entries:
            if entry.name.lower() == name_lower:
                return entry
        return None

    def find_by_partial_name(self, partial_name: str) -> list[KnowledgeEntry]:
        """Find entries by partial name match."""
        partial_lower = partial_name.lower()
        return [entry for entry in self.entries if partial_lower in entry.name.lower()]

    def add_entry(self, entry: KnowledgeEntry) -> None:
        """Add a new entry to the knowledge base."""
        self.entries.append(entry)

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)

    def __getitem__(self, index: int) -> KnowledgeEntry:
        return self.entries[index]
