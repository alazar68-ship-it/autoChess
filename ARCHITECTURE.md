# Architecture

## Overview

The system is intentionally "server-driven UI" (HTMX): the server renders HTML fragments and the browser swaps them into place.

Core concepts:
- **Game**: persisted state of a match (FEN, status, result, next action time).
- **EngineConfig**: per-side engine settings (strength + think-time).
- **Move**: per-ply records, including FEN after the ply.
- **MatchRecord**: denormalized summary for dashboards/history.

## State machine

- CONFIGURED → RUNNING → PAUSED → RUNNING → FINISHED

The `tick` endpoint:
- runs inside a DB transaction,
- acquires a row lock (`select_for_update()`),
- may or may not advance one ply depending on `next_action_at`.

## Engine integration

An engine is accessed via UCI. MVP assumes Stockfish.

There are two logical roles:
- **Mover engine** (per side): provides `bestmove` for current position.
- **Arbiter** (Stockfish): updates FEN via `position ... moves ...` + `d`, and provides:
  - `Fen:` line (new position),
  - `Checkers:` line (in-check detection),
  - `Key:` line (position key for repetition detection).

Note: Stockfish's `d` command is not part of the UCI standard, but is widely available in Stockfish builds.

## Concurrency model

This MVP assumes a single Django worker process (typical dev / simple deployment).
If you scale to multiple workers, per-process engine pools must be reconsidered (e.g., Celery/Redis worker model).
