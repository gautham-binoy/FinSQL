from typing import Dict, Any, List, Set, Optional
import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


ALLOWED_TABLES: Set[str] = {
    "companies",
    "financial_facts",
    "financial_concepts",
    "schema_catalog"
}

FORBIDDEN_EXPRESSION_TYPES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.TruncateTable,
    exp.Command,
    exp.Pragma,
)


class SQLValidator:
    """
    AST-based SQL validator using SQLGlot to guarantee strict read-only safety,
    table whitelisting, cartesian join detection, and syntax correctness.
    """

    @classmethod
    def validate(cls, sql: str) -> Dict[str, Any]:
        """
        Validates the SQL query AST. Returns structured validation metadata.
        """
        if not sql or not sql.strip():
            return {
                "valid": False,
                "reason": "Empty SQL query.",
                "error_type": "SYNTAX_ERROR",
                "ast_tables": [],
                "ast_columns": [],
                "has_limit": False
            }

        cleaned_sql = sql.strip().rstrip(";")

        # 1. Multi-statement injection check
        if ";" in cleaned_sql:
            # Check if there are truly multiple executable statements
            try:
                parsed_statements = sqlglot.parse(cleaned_sql, read="postgres")
                if len(parsed_statements) > 1:
                    return {
                        "valid": False,
                        "reason": "Multiple SQL statements detected. Only a single read-only statement is permitted.",
                        "error_type": "MULTI_STATEMENT",
                        "ast_tables": [],
                        "ast_columns": [],
                        "has_limit": False
                    }
            except Exception:
                pass

        # 2. AST Parsing with SQLGlot
        try:
            expression = sqlglot.parse_one(cleaned_sql, read="postgres")
        except ParseError as pe:
            # Try generic SQL parser if postgres dialect failed
            try:
                expression = sqlglot.parse_one(cleaned_sql)
            except Exception as e:
                return {
                    "valid": False,
                    "reason": f"SQLGlot parser error: {str(pe)}",
                    "error_type": "SYNTAX_ERROR",
                    "ast_tables": [],
                    "ast_columns": [],
                    "has_limit": False
                }

        if expression is None:
            return {
                "valid": False,
                "reason": "Failed to generate SQL AST.",
                "error_type": "SYNTAX_ERROR",
                "ast_tables": [],
                "ast_columns": [],
                "has_limit": False
            }

        # 3. Read-Only check: Top-level statement MUST be SELECT or CTE (WITH ... SELECT)
        if not isinstance(expression, (exp.Select, exp.Union)):
            return {
                "valid": False,
                "reason": f"Only SELECT statements are permitted. Found: {expression.key.upper()}",
                "error_type": "DANGEROUS_OPERATION",
                "ast_tables": [],
                "ast_columns": [],
                "has_limit": False
            }

        # 4. AST Traversal: Reject any mutation or DDL sub-expressions
        for forbidden_type in FORBIDDEN_EXPRESSION_TYPES:
            for node in expression.find_all(forbidden_type):
                return {
                    "valid": False,
                    "reason": f"Mutation or DDL operation '{node.key.upper()}' is strictly prohibited.",
                    "error_type": "DANGEROUS_OPERATION",
                    "ast_tables": [],
                    "ast_columns": [],
                    "has_limit": False
                }

        # Collect CTE aliases so they aren't rejected as unknown tables
        cte_aliases: Set[str] = set()
        for cte in expression.find_all(exp.CTE):
            alias = cte.alias_or_name or cte.alias
            if alias:
                cte_aliases.add(str(alias).lower())

        # 5. Table Whitelist Check
        referenced_tables: List[str] = []
        for table_node in expression.find_all(exp.Table):
            t_name = table_node.name.lower()
            if t_name in cte_aliases:
                continue
            referenced_tables.append(t_name)
            if t_name not in ALLOWED_TABLES:
                return {
                    "valid": False,
                    "reason": f"Access to table '{t_name}' is not permitted. Allowed tables: {sorted(list(ALLOWED_TABLES))}",
                    "error_type": "UNAPPROVED_TABLE",
                    "ast_tables": referenced_tables,
                    "ast_columns": [],
                    "has_limit": False
                }

        # 6. Cartesian Join Detection
        joins = expression.args.get("joins") or []
        for join in joins:
            if join.kind and "CROSS" in join.kind.upper():
                # Allow cross join only if explicitly intentional, but warn
                pass
            # If JOIN without ON condition or WHERE condition
            if join.this and not join.args.get("on") and not join.args.get("using"):
                # Could be a comma-separated cartesian product
                where_clause = expression.args.get("where")
                if not where_clause:
                    return {
                        "valid": False,
                        "reason": "Potential Cartesian product detected: JOIN without ON/USING or WHERE matching clause.",
                        "error_type": "CARTESIAN_JOIN",
                        "ast_tables": referenced_tables,
                        "ast_columns": [],
                        "has_limit": False
                    }

        # 7. Collect extracted columns
        columns_found: List[str] = []
        for col_node in expression.find_all(exp.Column):
            columns_found.append(col_node.name)

        has_limit = expression.args.get("limit") is not None

        return {
            "valid": True,
            "reason": "Query is valid, read-only, and accesses approved tables.",
            "error_type": None,
            "ast_tables": list(set(referenced_tables)),
            "ast_columns": list(set(columns_found)),
            "has_limit": has_limit,
        }
