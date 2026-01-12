from __future__ import annotations

from django.db import models
from django.utils import timezone

class Side(models.TextChoices):
    WHITE = "WHITE", "White"
    BLACK = "BLACK", "Black"

class GameStatus(models.TextChoices):
    CONFIGURED = "CONFIGURED", "Configured"
    RUNNING = "RUNNING", "Running"
    PAUSED = "PAUSED", "Paused"
    FINISHED = "FINISHED", "Finished"

class TerminationReason(models.TextChoices):
    CHECKMATE = "CHECKMATE", "Checkmate"
    STALEMATE = "STALEMATE", "Stalemate"
    REPETITION = "REPETITION", "Threefold repetition"
    FIFTY_MOVE = "FIFTY_MOVE", "Fifty-move rule"
    INSUFFICIENT = "INSUFFICIENT", "Insufficient material"
    RESIGN = "RESIGN", "Forfeit / engine error"
    MAX_PLIES = "MAX_PLIES", "Max plies reached"
    UNKNOWN = "UNKNOWN", "Unknown"

class StrengthMode(models.TextChoices):
    SKILL = "SKILL", "Skill (1-20)"
    ELO = "ELO", "Elo (UCI_Elo)"

class EngineType(models.TextChoices):
    STOCKFISH = "STOCKFISH", "Stockfish (UCI)"
    PYCHESS = "PYCHESS", "PyChess (python-chess minimax)"
    PLAYER = "PLAYER", "Játékos"

STARTPOS_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

class Game(models.Model):
    """Egy automata meccs állapota és metaadatai."""

    status = models.CharField(max_length=16, choices=GameStatus.choices, default=GameStatus.CONFIGURED)
    fen = models.TextField(default=STARTPOS_FEN)

    side_to_move = models.CharField(max_length=5, default="w")  # 'w' or 'b' from FEN
    ply_count = models.PositiveIntegerField(default=0)

    move_interval_ms = models.PositiveIntegerField(default=500)
    preview_ms = models.PositiveIntegerField(default=350)
    next_action_at = models.DateTimeField(null=True, blank=True)

    last_move_uci = models.CharField(max_length=8, blank=True, default="")
    last_move_san = models.CharField(max_length=16, blank=True, default="")

    # Move preview (two-phase tick): first highlight the planned move, then apply it on the next tick.
    pending_move_uci = models.CharField(max_length=8, blank=True, default="")
    pending_move_set_at = models.DateTimeField(null=True, blank=True)

    # UI: játékos kijelölések (emberi lépéshez)
    ui_selected_from = models.CharField(max_length=2, blank=True, default="")
    ui_selected_to = models.CharField(max_length=2, blank=True, default="")

    # Tick concurrency guard (helps avoid double-tick / sqlite lock bursts on demos)
    tick_lock = models.BooleanField(default=False)
    tick_lock_at = models.DateTimeField(null=True, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    result = models.CharField(max_length=7, blank=True, default="")  # 1-0 | 0-1 | 1/2-1/2
    termination_reason = models.CharField(max_length=16, choices=TerminationReason.choices, blank=True, default="")

    initial_position_key = models.CharField(max_length=64, blank=True, default="")  # Stockfish 'Key:' for start position.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_started(self) -> None:
        """Megjelöli a meccset futónak és inicializálja az időzítést."""
        now = timezone.now()
        if self.started_at is None:
            self.started_at = now
        self.status = GameStatus.RUNNING
        self.next_action_at = now

    def mark_paused(self) -> None:
        """Megállítja a futást, de nem zárja le a meccset."""
        self.status = GameStatus.PAUSED
        # Cancel any pending preview move so a paused game never "jumps" on resume.
        self.pending_move_uci = ""
        self.pending_move_set_at = None

    def mark_finished(self, *, result: str, reason: str) -> None:
        """Lezárja a meccset."""
        self.status = GameStatus.FINISHED
        # Clear preview state
        self.pending_move_uci = ""
        self.pending_move_set_at = None
        self.result = result
        self.termination_reason = reason
        self.finished_at = timezone.now()

class EngineConfig(models.Model):
    """Egy oldal motor-konfigurációja (MVP: Stockfish)."""

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="engines")
    side = models.CharField(max_length=5, choices=Side.choices)

    engine_type = models.CharField(max_length=16, choices=EngineType.choices, default=EngineType.STOCKFISH)
    strength_mode = models.CharField(max_length=8, choices=StrengthMode.choices, default=StrengthMode.SKILL)
    strength_value = models.PositiveIntegerField(default=10)  # skill 1..20 or elo value

    movetime_ms = models.PositiveIntegerField(default=150)
    uci_options = models.JSONField(blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("game", "side")]

class Move(models.Model):
    """Egy fél-lépés (ply) rekordja."""

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="moves")
    ply_index = models.PositiveIntegerField()

    uci = models.CharField(max_length=8)
    san = models.CharField(max_length=16, blank=True, default="")

    fen_after = models.TextField()
    position_key_after = models.CharField(max_length=64, blank=True, default="")
    is_check = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("game", "ply_index")]
        ordering = ["ply_index"]

class MatchRecord(models.Model):
    """Lezárt meccsek összefoglaló sora a dashboardhoz."""

    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name="match_record")

    result = models.CharField(max_length=7)
    termination_reason = models.CharField(max_length=16)

    white_strength_mode = models.CharField(max_length=8)
    white_strength_value = models.PositiveIntegerField()
    black_strength_mode = models.CharField(max_length=8)
    black_strength_value = models.PositiveIntegerField()
    move_interval_ms = models.PositiveIntegerField()

    pgn = models.TextField(blank=True, default="")  # Not fully supported without SAN; kept for future.

    finished_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
