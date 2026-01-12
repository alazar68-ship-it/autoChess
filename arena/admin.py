from django.contrib import admin
from .models import Game, EngineConfig, Move, MatchRecord

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id","status","result","termination_reason","ply_count","move_interval_ms","started_at","finished_at")
    search_fields = ("id","result","termination_reason","status")

@admin.register(EngineConfig)
class EngineConfigAdmin(admin.ModelAdmin):
    list_display = ("id","game","side","engine_type","strength_mode","strength_value","movetime_ms")

@admin.register(Move)
class MoveAdmin(admin.ModelAdmin):
    list_display = ("id","game","ply_index","uci","is_check","created_at")

@admin.register(MatchRecord)
class MatchRecordAdmin(admin.ModelAdmin):
    list_display = ("id","game","result","termination_reason","finished_at")
