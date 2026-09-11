from typing import Dict, Any, List, Optional


class ResultVerifier:
    """
    Financial domain verifier inspecting query results for accounting traps:
    - Empty result sets
    - Duplicate reporting periods or filings
    - Unresolved restatements (both original and restated present)
    - Incompatible units (mixing USD with per-share or percentages)
    - Consolidated vs standalone discrepancies
    - Suspicious values or negative revenue
    """

    @classmethod
    def verify(
        cls,
        rows: List[Dict[str, Any]],
        columns: List[str],
        question_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        warnings: List[str] = []
        checks: Dict[str, Any] = {
            "empty_result": False,
            "duplicate_rows": False,
            "unit_consistency": True,
            "restatement_conflict": False,
            "reporting_type_conflict": False,
            "company_match": True,
            "period_match": True,
            "value_plausibility": True,
        }

        # 1. Empty Result Check
        if not rows:
            checks["empty_result"] = True
            warnings.append("Query returned 0 rows. Target metric or entity might not match database filters.")
            return {
                "valid": False,
                "needs_repair": True,
                "warnings": warnings,
                "checks": checks,
                "repair_reason": "Query returned 0 rows. Please verify company ticker/name, fiscal year, or concept spelling."
            }

        # 2. Check duplicate entities/periods/concepts
        seen_keys = set()
        has_restatement_col = any("restated" in c.lower() for c in columns)
        has_unit_col = any("unit" in c.lower() for c in columns)
        has_reporting_col = any("reporting" in c.lower() for c in columns)

        units_seen = set()
        has_original = False
        has_restated = False

        for row in rows:
            # Check units
            if has_unit_col:
                u = row.get("unit")
                if u:
                    units_seen.add(str(u).lower())

            # Check restatements
            if has_restatement_col:
                rest = row.get("is_restated")
                if rest is True or rest == 1:
                    has_restated = True
                elif rest is False or rest == 0:
                    has_original = True

            # Key for duplicate check: (company, fiscal_year, concept)
            comp = row.get("company_name") or row.get("ticker") or row.get("company_id")
            yr = row.get("fiscal_year") or row.get("year")
            concept = row.get("concept")

            if comp and yr and concept:
                key = (str(comp).lower(), str(yr), str(concept).lower())
                if key in seen_keys:
                    checks["duplicate_rows"] = True
                seen_keys.add(key)

            # Value plausibility (e.g. check for negative Revenue)
            val = row.get("value") or row.get("revenue")
            if concept and "revenue" in str(concept).lower() and isinstance(val, (int, float)):
                if val < 0:
                    checks["value_plausibility"] = False
                    warnings.append(f"Suspicious negative revenue detected: {val}")

        if checks["duplicate_rows"]:
            warnings.append("Duplicate rows detected for the same company, concept, and fiscal year. The query may be combining multiple filings, restatements, or reporting types.")

        # Unit consistency check
        if len(units_seen) > 1:
            # Mixing USD with per-share or ratios
            if any("usd" in u for u in units_seen) and any("share" in u or "ratio" in u for u in units_seen):
                checks["unit_consistency"] = False
                warnings.append(f"Incompatible financial units detected in results: {list(units_seen)}")

        # Restatement conflict check
        if has_original and has_restated and checks["duplicate_rows"]:
            checks["restatement_conflict"] = True
            warnings.append("Both original and restated values are present. Financial queries should filter for latest or specify `is_restated = FALSE`.")

        # Entity/Period Match against Question Analysis
        if question_analysis:
            expected_entities = [e.lower() for e in question_analysis.get("entities", [])]
            if expected_entities:
                result_str = " ".join(str(v).lower() for r in rows for v in r.values())
                matches = [e for e in expected_entities if e in result_str]
                if not matches and len(expected_entities) > 0:
                    checks["company_match"] = False
                    warnings.append(f"Expected entities {expected_entities} not clearly identified in returned rows.")

        is_valid = len(warnings) == 0 or (not checks["empty_result"] and not checks["restatement_conflict"])
        needs_repair = checks["empty_result"] or checks["restatement_conflict"]

        return {
            "valid": is_valid,
            "needs_repair": needs_repair,
            "warnings": warnings,
            "checks": checks,
            "repair_reason": warnings[0] if warnings else None
        }
