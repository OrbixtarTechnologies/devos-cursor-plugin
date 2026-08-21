# DevOS Operating Model

DevOS is designed around a simple loop:

**Understand → Plan → Delegate → Implement → Verify → Review → Ship**

## Escalation

- Small change: context → implement → verify.
- Multi-file feature: context → plan → implement → test/review.
- High-risk change: context → architecture + security → implement → independent review → release readiness.
- Difficult bug: reproduce → debugger → regression test → review.

## Evidence standard

Every meaningful completion report should distinguish:
- observed facts
- decisions made
- commands actually run
- results actually observed
- remaining uncertainty

## Non-destructive default

The system avoids history rewriting, destructive cleanup, secret exposure, and irreversible operations unless the user explicitly asks for them and the operation is properly scoped.
