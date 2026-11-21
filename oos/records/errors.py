"""Explicit, structured errors for the record substrate. Callers can catch the base class."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationIssue:
    """One schema violation: where, which rule, what happened."""

    path: str
    keyword: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


class RecordStoreError(Exception):
    """Base class for every record-substrate error."""


class SchemaError(RecordStoreError):
    """A schema itself is unusable (unknown keyword, missing version, unreadable)."""


class SchemaValidationError(RecordStoreError):
    def __init__(self, what: str, issues: list[ValidationIssue]):
        self.what = what
        self.issues = list(issues)
        super().__init__(f"{what}: {len(self.issues)} schema violation(s): " + "; ".join(map(str, self.issues[:5])))


class UnknownRecordType(RecordStoreError):
    pass


class InvalidRecordId(RecordStoreError):
    pass


class DuplicateRecordError(RecordStoreError):
    pass


class RecordNotFound(RecordStoreError):
    pass


class ImmutableRecordError(RecordStoreError):
    """The record type is append-only: change it by superseding, never by replacing."""


class ConcurrencyConflict(RecordStoreError):
    def __init__(self, record: str, expected: int, actual: int):
        self.expected, self.actual = expected, actual
        super().__init__(f"{record}: expected revision {expected}, found {actual}")


class RecordTooLarge(RecordStoreError):
    pass


class CorruptRecordError(RecordStoreError):
    def __init__(self, location: str, reason: str):
        self.location, self.reason = location, reason
        super().__init__(f"{location}: corrupt record ({reason})")


class UnsupportedSchemaVersion(RecordStoreError):
    def __init__(self, location: str, found: int, supported: int, reason: str):
        self.found, self.supported = found, supported
        super().__init__(f"{location}: schema version {found} {reason} (current {supported})")


class LockTimeout(RecordStoreError):
    pass


class CorruptLogError(RecordStoreError):
    def __init__(self, location: str, line_no: int, reason: str):
        self.location, self.line_no, self.reason = location, line_no, reason
        super().__init__(f"{location}:{line_no}: corrupt log entry ({reason})")
