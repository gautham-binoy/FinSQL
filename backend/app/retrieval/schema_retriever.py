import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.database.models import SchemaCatalog, FinancialConcept, Company
from backend.app.retrieval.embeddings import get_embedding, cosine_similarity


class SchemaRetriever:
    """
    Retrieves only the minimal, relevant tables, columns, and financial concepts
    for a given question, preventing schema-dumping to the LLM.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def retrieve(
        self,
        question: str,
        detected_entities: Optional[List[str]] = None,
        detected_metrics: Optional[List[str]] = None,
        top_k: int = 10,
        similarity_threshold: float = 0.15
    ) -> Dict[str, Any]:
        """
        Performs hybrid semantic and concept-matching retrieval against SchemaCatalog.
        """
        detected_entities = detected_entities or []
        detected_metrics = detected_metrics or []

        q_embedding = get_embedding(question)

        catalog_items = self.db.query(SchemaCatalog).all()
        scored_items = []

        q_lower = question.lower()

        for item in catalog_items:
            # Semantic cosine similarity
            emb = json.loads(item.embedding_json) if item.embedding_json else []
            sim = cosine_similarity(q_embedding, emb) if emb else 0.0

            # Keyword and synonym boosting
            boost = 0.0
            
            # Boost if name directly matches
            if item.column_name and item.column_name.lower() in q_lower:
                boost += 0.25
            if item.concept_name and item.concept_name.lower() in q_lower:
                boost += 0.40
            
            # Boost if synonym matches
            for syn in item.synonyms:
                if syn.lower() in q_lower:
                    boost += 0.30
                    break

            # Boost if metric matches question analysis
            for m in detected_metrics:
                if item.concept_name and item.concept_name.lower() == m.lower():
                    boost += 0.50
                if item.column_name == "concept" or item.column_name == "value":
                    boost += 0.20

            # Boost company lookup columns if entities detected
            if detected_entities and item.table_name == "companies":
                if item.column_name in ["company_name", "ticker", "company_id"]:
                    boost += 0.35

            # Always ensure primary key / foreign key join columns have reasonable baseline relevance
            if item.column_name in ["company_id"]:
                boost += 0.20

            final_score = sim + boost

            scored_items.append({
                "id": item.id,
                "item_type": item.item_type,
                "table_name": item.table_name,
                "column_name": item.column_name,
                "concept_name": item.concept_name,
                "display_name": item.display_name,
                "description": item.description,
                "synonyms": item.synonyms,
                "sample_values": item.sample_values,
                "score": round(final_score, 4),
                "semantic_similarity": round(sim, 4),
            })

        # Sort by descending score
        scored_items.sort(key=lambda x: x["score"], reverse=True)

        # Select top K that meet threshold
        selected = [it for it in scored_items if it["score"] >= similarity_threshold][:top_k]

        # Extract distinct tables and concepts
        relevant_tables = sorted(list({it["table_name"] for it in selected if it["table_name"]}))
        relevant_concepts = sorted(list({it["concept_name"] for it in selected if it["concept_name"]}))

        # Generate structured text for LLM prompt
        prompt_schema_text = self._format_prompt_schema(selected, relevant_tables, relevant_concepts)

        return {
            "retrieved_items": selected,
            "relevant_tables": relevant_tables,
            "relevant_concepts": relevant_concepts,
            "prompt_schema_text": prompt_schema_text,
        }

    def _format_prompt_schema(
        self,
        items: List[Dict[str, Any]],
        tables: List[str],
        concepts: List[str]
    ) -> str:
        lines = []
        lines.append("### Retrieved Relevant Tables & Columns:")
        
        # Group by table
        tables_map: Dict[str, List[Dict[str, Any]]] = {}
        for item in items:
            t = item["table_name"] or "global"
            if t not in tables_map:
                tables_map[t] = []
            tables_map[t].append(item)

        for t_name, cols in tables_map.items():
            if t_name == "global":
                continue
            lines.append(f"\nTable `{t_name}`:")
            for col in cols:
                if col["item_type"] == "column":
                    lines.append(f"  - `{col['column_name']}`: {col['description']} (Sample: {col['sample_values']})")

        lines.append("\n### Table Relationships & Keys:")
        lines.append("- `companies.company_id` = `financial_facts.company_id` (INNER JOIN)")

        if concepts:
            lines.append("\n### Relevant Financial Concepts (exact values for `financial_facts.concept`):")
            for c in concepts:
                # Find matching concept description
                desc = next((it["description"] for it in items if it["concept_name"] == c), "")
                lines.append(f"- '{c}': {desc}")

        lines.append("\n### Key Financial Column Semantics:")
        lines.append("- `financial_facts.reporting_type`: Always filter `reporting_type = 'consolidated'` unless standalone is explicitly requested.")
        lines.append("- `financial_facts.is_restated`: Filter `is_restated = FALSE` unless historical restatements are requested.")
        lines.append("- `financial_facts.fiscal_period`: Filter `fiscal_period = 'FY'` for full annual fiscal years.")

        return "\n".join(lines)
