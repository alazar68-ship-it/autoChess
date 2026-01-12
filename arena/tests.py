from __future__ import annotations

import os
from django.test import TestCase
from django.conf import settings

from .services.fen import parse_fen_piece_placement, uci_move_highlight, is_insufficient_material
from .models import Game, EngineConfig, Side, StrengthMode, STARTPOS_FEN, GameStatus
from .services.game_loop import tick

class FenParsingTests(TestCase):
    def test_parse_startpos(self):
        board = parse_fen_piece_placement(STARTPOS_FEN)
        self.assertEqual(len(board), 8)
        self.assertEqual(len(board[0]), 8)

    def test_highlight(self):
        hl = uci_move_highlight("e2e4")
        self.assertIsNotNone(hl.from_sq)
        self.assertIsNotNone(hl.to_sq)

    def test_insufficient_material(self):
        self.assertTrue(is_insufficient_material("8/8/8/8/8/8/8/4K2k w - - 0 1"))
        self.assertFalse(is_insufficient_material(STARTPOS_FEN))

class IntegrationStockfishTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_10_ply_runs_if_engine_available(self):
        exe = getattr(settings, "AUTOCHESS_STOCKFISH_PATH", "stockfish")
        # Skip if binary not found on PATH and not an absolute path.
        if os.path.sep not in exe and os.name == "nt":
            # On Windows, stockfish on PATH is less likely; allow env override.
            if exe == "stockfish":
                self.skipTest("Stockfish nincs konfigurálva Windows-on.")
        if exe == "stockfish" and os.name != "nt":
            # Linux/mac: assume may exist; still might not
            pass

        g = Game.objects.create(status=GameStatus.RUNNING, fen=STARTPOS_FEN, move_interval_ms=0)
        EngineConfig.objects.create(game=g, side=Side.WHITE, strength_mode=StrengthMode.SKILL, strength_value=1, movetime_ms=50)
        EngineConfig.objects.create(game=g, side=Side.BLACK, strength_mode=StrengthMode.SKILL, strength_value=1, movetime_ms=50)

        # perform ticks
        for _ in range(10):
            tick(g.id)
            g.refresh_from_db()
            if g.status == GameStatus.FINISHED:
                break

        self.assertGreaterEqual(g.ply_count, 1)
