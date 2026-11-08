"""
Unit tests for Mermaid, SQL, and Specification validators.
"""
import unittest

from system_design_agent.validators.mermaid_validator import MermaidValidator
from system_design_agent.validators.sql_validator import SQLValidator
from system_design_agent.models.spec import SystemDesignSpec
from system_design_agent.models.domain import (
    HLDSection,
    LLDSection,
    RequirementsSection,
    ResilienceSection,
    ScaffoldingSection,
)
from system_design_agent.validators.spec_validator import SpecValidator


class TestMermaidValidator(unittest.TestCase):
    def test_valid_graph_td(self):
        valid_md = """
```mermaid
graph TD
    A["Client App"] --> B["API Gateway"]
    B --> C[("PostgreSQL DB")]
```
        """
        is_valid, errors = MermaidValidator.validate_markdown(valid_md)
        self.assertTrue(is_valid, f"Expected valid mermaid, got errors: {errors}")

    def test_invalid_mismatched_brackets(self):
        invalid_md = """
```mermaid
graph TD
    A["Client App" --> B["API Gateway"]
```
        """
        is_valid, errors = MermaidValidator.validate_markdown(invalid_md)
        self.assertFalse(is_valid)
        self.assertTrue(any("Mismatched bracket" in err for err in errors))

    def test_unsupported_header(self):
        invalid_md = """
```mermaid
pie title Pets
    "Dogs" : 386
    "Cats" : 85
```
        """
        is_valid, errors = MermaidValidator.validate_markdown(invalid_md)
        self.assertFalse(is_valid)


class TestSQLValidator(unittest.TestCase):
    def test_valid_sql_ddl(self):
        valid_sql = """
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);
```
        """
        is_valid, errors = SQLValidator.validate_markdown(valid_sql)
        self.assertTrue(is_valid, f"Expected valid SQL, got errors: {errors}")

    def test_forbidden_placeholders_detected(self):
        lazy_sql = """
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    ...
);
CREATE INDEX idx_users_email ON users(email);
```
        """
        is_valid, errors = SQLValidator.validate_markdown(lazy_sql)
        self.assertFalse(is_valid)
        self.assertTrue(any("Forbidden placeholder" in err for err in errors))

    def test_missing_indexes(self):
        no_index_sql = """
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);
```
        """
        is_valid, errors = SQLValidator.validate_markdown(no_index_sql)
        self.assertFalse(is_valid)
        self.assertTrue(any("explicit indexes" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
