from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import chess
import chess.svg


# Színpaletta: python-chess docs/ példákhoz igazított "barna" tábla.
# (A világos/sötét mezők a mellékelt referencia képhez közelítenek.)
DEFAULT_COLORS = {
    "square light": "#f0d9b5",
    "square dark": "#b58863",
    # Utolsó lépés kiemelés (világos/sötét mezőn).
    "square light lastmove": "#f6f595",
    "square dark lastmove": "#bdc959",
    # Koordináták/margin nem kell, mert a saját keretünk adja.
    "margin": "#ffffff00",
    "coord": "#00000000",
    "inner border": "#00000000",
    "outer border": "#00000000",
}


def render_board_svg(fen: str, last_move_uci: str | None = None, *, size: int = 560) -> str:
    """Pozíció kirajzolása SVG-ként python-chess segítségével.

    - Nem használunk külső képfájlokat: a bábuk a python-chess `chess.svg` modulból jönnek.
    - A koordinátákat a template rajzolja (bal + alul), ezért `coordinates=False`.

    Args:
        fen: Aktuális FEN.
        last_move_uci: Utolsó lépés UCI-ben (pl. e2e4). Opcionális.
        size: SVG mérete pixelben (a CSS felülírhatja reszponzív módon).

    Returns:
        SVG markup string.
    """
    board = chess.Board(fen)

    lastmove = None
    if last_move_uci:
        try:
            lastmove = chess.Move.from_uci(last_move_uci)
        except ValueError:
            lastmove = None

    check_sq = None
    try:
        if board.is_check():
            # A soron lévő fél királya sakkban van.
            king_sq = board.king(board.turn)
            check_sq = king_sq
    except Exception:
        check_sq = None

    svg = chess.svg.board(
        board=board,
        size=size,
        coordinates=False,
        lastmove=lastmove,
        check=check_sq,
        colors=DEFAULT_COLORS,
        borders=False,
    )
    return svg
