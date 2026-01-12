from __future__ import annotations

from django import forms

from .models import Side, StrengthMode, EngineType


class NewGameForm(forms.Form):
    """Új meccs létrehozása - egyszerű UI paraméterekkel."""

    white_strength = forms.IntegerField(min_value=1, max_value=20, initial=10)
    black_strength = forms.IntegerField(min_value=1, max_value=20, initial=10)
    move_interval_ms = forms.IntegerField(min_value=200, max_value=5000, initial=600)
    preview_ms = forms.IntegerField(min_value=0, max_value=2000, initial=350, required=False)
    movetime_ms = forms.IntegerField(min_value=50, max_value=2000, initial=150)


class UpdateConfigForm(forms.Form):
    """Futó/állított meccs közbeni paraméter módosítás.

    Megjegyzés: PLAYER (ember) esetén a strength/movetime mezők nem relevánsak,
    ezért ezek nem kötelezőek.
    """

    side = forms.ChoiceField(choices=Side.choices)
    engine_type = forms.ChoiceField(choices=EngineType.choices)

    strength_mode = forms.ChoiceField(choices=StrengthMode.choices, required=False)
    strength_value = forms.IntegerField(min_value=1, max_value=3200, required=False)
    movetime_ms = forms.IntegerField(min_value=50, max_value=2000, required=False)

    def clean(self):
        cleaned = super().clean()
        engine_type = cleaned.get("engine_type")

        # PLAYER (ember) esetén a motor paraméterek nem számítanak.
        if engine_type == EngineType.PLAYER:
            return cleaned

        mode = cleaned.get("strength_mode")
        val = cleaned.get("strength_value")
        mt = cleaned.get("movetime_ms")

        if mode is None or val is None or mt is None:
            raise forms.ValidationError("Hiányzó motor paraméterek.")

        if mode == StrengthMode.SKILL and not (1 <= val <= 20):
            raise forms.ValidationError("Skill módban az erősség értéke 1 és 20 között kell legyen.")

        if mode == StrengthMode.ELO and not (800 <= val <= 3200):
            raise forms.ValidationError("Elo módban az erősség értéke 800 és 3200 között kell legyen.")

        return cleaned

        if mode == StrengthMode.SKILL and not (1 <= val <= 20):
            raise forms.ValidationError("Skill módban az erősség értéke 1 és 20 között kell legyen.")

        if mode == StrengthMode.ELO and not (800 <= val <= 3200):
            raise forms.ValidationError("Elo módban az erősség értéke 800 és 3200 között kell legyen.")

        return cleaned


class UpdateSpeedForm(forms.Form):
    """A megjelenítési sebesség (lépésköz + előnézet) állítása."""

    move_interval_ms = forms.IntegerField(min_value=200, max_value=5000, initial=600)
    preview_ms = forms.IntegerField(min_value=0, max_value=2000, initial=350, required=False)
