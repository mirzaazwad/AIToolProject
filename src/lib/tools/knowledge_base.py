"""Knowledge Base Tool"""

import os
from typing import Optional

from ...data.schemas.tools.knowledge_base import \
    KnowledgeBase as knowledge_baseSchema
from ...data.schemas.tools.knowledge_base import KnowledgeEntry
from ..errors.tools.knowledge_base import (InsertionError, LoadingError,
                                           QueryError, RetrievalError)
from .base import Action


class KnowledgeBase(Action):
    """Knowledge base tool with character-based Jaccard similarity search."""

    def __init__(self, knowledge_base_file_path: Optional[str] = None):
        """
        Initialize knowledge base.

        Args:
            knowledge_base_file_path: Path to the knowledge base JSON file
        """
        if knowledge_base_file_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(os.path.dirname(current_dir))
            self.knowledge_base_file_path = os.path.join(
                src_dir, "data", "knowledge_base.json"
            )
        else:
            self.knowledge_base_file_path = knowledge_base_file_path
        self._load_knowledge_base()

    def _load_knowledge_base(self) -> None:
        """Load the knowledge base from file."""
        try:
            if os.path.exists(self.knowledge_base_file_path):
                self.knowledge_base = knowledge_baseSchema.from_json_file(
                    self.knowledge_base_file_path
                )
            else:
                self.knowledge_base = knowledge_baseSchema(entries=[])
                print(
                    f"Warning: Knowledge base file {self.knowledge_base_file_path} not found. Created empty knowledge_base."
                )
        except Exception as e:
            self.knowledge_base = knowledge_baseSchema(entries=[])
            raise LoadingError(f"Error loading knowledge base: {str(e)}")

    def execute(self, args: dict) -> KnowledgeEntry:
        """
        Execute knowledge base search and return only the summary.

        Args:
            args: Dictionary containing 'query' key with search term

        Returns:
            String with summary only or error message
        """
        if "query" not in args:
            raise QueryError("'query' parameter is required for knowledge base search")

        query = args["query"]
        if not query or not isinstance(query, str):
            raise QueryError("Query must be a non-empty string")
        search_result = self.search(query)
        most_relevant_entry = search_result[0] if search_result else None
        if not most_relevant_entry:
            raise RetrievalError(f"No entries found for query: '{query}'")
        return most_relevant_entry

    def search(
        self, query: str, threshold: float = 0.75, max_results: int = 1
    ) -> list[KnowledgeEntry]:
        """
        Search knowledge base using character-based Jaccard similarity.

        Args:
            query: Search query string
            threshold: Minimum similarity threshold (default: 0.75)
            max_results: Maximum number of results to return (default: 1)

        Returns:
            Dict with {"entry": name, "summary": summary} or error string
        """
        if not query.strip():
            raise QueryError("Empty query provided")

        results = self.knowledge_base.search(
            query, threshold=threshold, max_results=max_results
        )

        if not results:
            raise RetrievalError(f"No entries found for query: '{query}'")

        entries: list[KnowledgeEntry] = []
        for entry, _ in results:
            entries.append(entry)

        if len(entries) > 0:
            return entries

        raise RetrievalError(f"No entries found for query: '{query}'")

    def get_entry_count(self) -> int:
        """Get total number of entries in knowledge base."""
        return len(self.knowledge_base)

    def get_all_entries(self) -> list[dict[str, str]]:
        """Get formatted list of all entries."""
        if not self.knowledge_base.entries:
            return []

        entries = []
        for entry in self.knowledge_base.entries:
            entries.append({"entry": entry.name, "summary": entry.summary})

        return entries

    def add_entry(self, name: str, summary: str, category: Optional[str] = None):
        """
        Add a new entry to the knowledge base.

        Args:
            name: Name of the person/entity
            summary: Description/summary
            category: Optional category

        Returns:
            Success/error message
        """
        try:
            if self.knowledge_base.find_by_name(name):
                raise InsertionError(f"Entry '{name}' already exists in knowledge base")
            new_entry = KnowledgeEntry(name=name, summary=summary, category=category)
            self.knowledge_base.add_entry(new_entry)
            self.knowledge_base.to_json_file(self.knowledge_base_file_path)

            print(f"Successfully added entry for '{name}'")

        except Exception as e:
            raise InsertionError(f"Error adding entry: {str(e)}")
