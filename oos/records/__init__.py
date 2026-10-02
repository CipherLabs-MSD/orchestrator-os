"""OOS record substrate: schema validation, record store, append-only log (OOS-0003, ADR-0009).

Domain-neutral: it validates and persists structured records without knowing what they mean.
"""
from .errors import (ConcurrencyConflict, CorruptLogError, CorruptRecordError, DuplicateRecordError,
                     ImmutableRecordError, InvalidRecordId, LockTimeout, RecordNotFound, RecordStoreError,
                     RecordTooLarge, SchemaError, SchemaValidationError, UnknownRecordType,
                     UnsupportedSchemaVersion, ValidationIssue)
from .log import AppendLog, LogRead
from .schema import SUPPORTED_SCHEMA_KEYWORDS, SchemaRegistry, validate
from .store import Record, RecordStore, RecordType, check_identifier, load_record_types

__all__ = [
    "AppendLog", "LogRead", "Record", "RecordStore", "RecordType", "SchemaRegistry", "SUPPORTED_SCHEMA_KEYWORDS",
    "check_identifier", "load_record_types", "validate",
    "ConcurrencyConflict", "CorruptLogError", "CorruptRecordError", "DuplicateRecordError", "ImmutableRecordError",
    "InvalidRecordId", "LockTimeout", "RecordNotFound", "RecordStoreError", "RecordTooLarge", "SchemaError",
    "SchemaValidationError", "UnknownRecordType", "UnsupportedSchemaVersion", "ValidationIssue",
]
