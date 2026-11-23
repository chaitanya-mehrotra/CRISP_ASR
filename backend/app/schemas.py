from typing import Literal

from pydantic import BaseModel, Field


class SourceRequest(BaseModel):
    source: str = Field(min_length=1, max_length=100_000)


class OutlineEntry(BaseModel):
    kind: str
    name: str | None
    line: int


class RuleInfo(BaseModel):
    id: str
    title: str
    severity: Literal["high", "medium"]
    risk: str
    fix: str
    example: str


class Finding(RuleInfo):
    call: str
    repairable: bool
    repair_mode: Literal["preview", "guided", "manual"]
    ast_chain: list[str]
    origin: str
    impact: str
    question: str
    line: int
    column: int
    end_line: int
    end_column: int


class ParseResult(BaseModel):
    node_count: int
    structure: dict[str, int]
    node_types: dict[str, int]
    top_level: list[str]
    outline: list[OutlineEntry]
    findings: list[Finding]


class RepairRequest(SourceRequest):
    rule_id: str = Field(min_length=1, max_length=12)
    line: int = Field(ge=1)
    column: int = Field(ge=1)


class ValidationChecks(BaseModel):
    syntax: bool
    compilation: bool
    rescan: bool


class RepairPreview(BaseModel):
    source: str
    line: int
    before: str
    after: str
    checks: ValidationChecks
    remaining_findings: int

    before_findings: int
    target_resolved: bool
    new_findings: int
    explanation: str


class RepairChange(BaseModel):
    line: int
    before: str
    after: str
    notes: list[str]


class BatchRepairPreview(BaseModel):
    source: str
    changes: list[RepairChange]
    checks: ValidationChecks
    before_findings: int
    remaining_findings: int
    target_resolved: bool
    new_findings: int
    repair_count: int
    deferred_count: int
    manual_findings: int
