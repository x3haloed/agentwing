# INC-218: duplicated tenant revenue
After onboarding a second tenant, the revenue export multiplied some invoices
and attributed them to the wrong tenant. Inspect data/, jobs/, and docs/runbook.md.
FINDINGS.json must contain cause (plain English), evidence (at least two relevant
repository file paths), and corrected_totals (same mapping as revenue.json).
Repair the general bug rather than special-casing this incident's customer ids.
