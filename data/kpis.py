# ═══════════════════════════════════════════════════════
# kpis.py — Estructura completa de AREAS, OTIs y KPIs
# AE KPI Dashboard 2026–2028
# ═══════════════════════════════════════════════════════

import os
import pandas as pd
from functools import lru_cache

_XLSX = os.path.join(os.path.dirname(__file__), "kpis.xlsx")


@lru_cache(maxsize=1)
def _cargar():
    """Lee el Excel una sola vez y devuelve (areas, periodos, historico)."""
    df_kpis = pd.read_excel(_XLSX, sheet_name="KPIs", dtype=str)
    df_hist = pd.read_excel(_XLSX, sheet_name="Histórico", dtype=str)
    df_areas = pd.read_excel(_XLSX, sheet_name="Áreas y OTIs", dtype=str)

    # ── Períodos: columnas del histórico que no son "KPI ID" ──
    periodos = [c for c in df_hist.columns if c != "KPI ID"]

    # ── Histórico: {kpi_id: [v1, v2, ...]} ───────────────────
    historico = {}
    for _, row in df_hist.iterrows():
        kid = row["KPI ID"].strip()
        if kid == "—":
            continue
        vals = []
        for p in periodos:
            raw = row.get(p, None)
            try:
                vals.append(float(raw) if raw not in (None, "nan", "—", "") else None)
            except (ValueError, TypeError):
                vals.append(None)
        historico[kid] = vals

    # ── Áreas con sus OTIs y KPIs ─────────────────────────────
    areas_dict = {}
    for _, r in df_areas.iterrows():
        aid = r["Área ID"].strip()
        if aid not in areas_dict:
            areas_dict[aid] = {
                "id": aid,
                "nombre": r["Área Nombre"].strip(),
                "subtitulo": r["Subtítulo"].strip(),
                "color": "#" + r["Color Hex"].strip().lstrip("#"),
                "color_bg": "#eef7fd" if aid == "ae" else "#e8f3fb",
                "otis": {},
            }
        oti_id = r["OTI ID"].strip()
        oti_nombre = r["OTI Nombre"].strip()
        if oti_id != "—" and oti_id not in areas_dict[aid]["otis"]:
            areas_dict[aid]["otis"][oti_id] = {
                "id": oti_id,
                "nombre": oti_nombre,
                "kpis": [],
            }

    # ── Insertar KPIs en sus OTIs ─────────────────────────────
    for _, r in df_kpis.iterrows():
        aid  = r["Área ID"].strip()
        oid  = r["OTI ID"].strip()
        if aid not in areas_dict or oid not in areas_dict[aid]["otis"]:
            continue
        try:
            meta = float(r["Meta"])
        except (ValueError, TypeError):
            meta = None
        kpi = {
            "id":          r["KPI ID"].strip(),
            "nombre":      r["KPI Nombre"].strip(),
            "um":          r["Unidad de Medida"].strip(),
            "meta":        meta,
            "meta_label":  r["Meta Label"].strip(),
            "fuente":      r["Fuente"].strip(),
            "responsable": r["Responsable"].strip(),
        }
        areas_dict[aid]["otis"][oid]["kpis"].append(kpi)

    # ── Convertir a listas (mantiene orden de inserción) ──────
    areas = []
    for a in areas_dict.values():
        a["otis"] = list(a["otis"].values())
        areas.append(a)

    return areas, periodos, historico


# ── API pública (idéntica a la anterior) ──────────────────────

def _data():
    return _cargar()


AREAS    = property(lambda self: _data()[0])   # acceso directo como lista
PERIODOS = property(lambda self: _data()[1])

# Para que las importaciones `from data.kpis import AREAS, PERIODOS` sigan
# funcionando igual que antes, los exponemos como variables de módulo:
_areas, _periodos, _historico = _cargar.__wrapped__() if hasattr(_cargar, "__wrapped__") else (None, None, None)

def _init():
    global AREAS, PERIODOS, _historico
    AREAS, PERIODOS, _historico = _cargar()

_init()


def get_kpi_data(kpi_id: str) -> list[dict]:
    """Devuelve [{periodo, valor}, ...] igual que antes."""
    valores = _historico.get(kpi_id, [None] * len(PERIODOS))
    return [{"periodo": p, "valor": v} for p, v in zip(PERIODOS, valores)]


def get_all_kpis() -> list[dict]:
    result = []
    for pilar in AREAS:
        for oti in pilar["otis"]:
            for kpi in oti["kpis"]:
                result.append({
                    **kpi,
                    "pilar_id":     pilar["id"],
                    "pilar_nombre": pilar["nombre"],
                    "oti_nombre":   oti["nombre"],
                })
    return result


def get_pilar_by_id(pilar_id: str):
    return next((p for p in AREAS if p["id"] == pilar_id), None)
