# ═══════════════════════════════════════════════════════
# charts.py — Gráficas Plotly para el Dashboard AE
# ═══════════════════════════════════════════════════════

import plotly.graph_objects as go
from data.kpis import PERIODOS, get_kpi_data

# Paleta alineada con identidad BNA
BNA_AZUL        = "#005F87"
BNA_NARANJA     = "#ff7a00"
COLOR_META_LINE = "#e05c2a"
COLOR_GRID      = "#e6f2f7"
FONT_FAMILY     = "'Inter', Helvetica Neue, Arial, sans-serif"

# 🎨 Barras cálidas alineadas al acento naranja del navbar
COLOR_BARRA_OK   = "#ff8c42"   # Naranja cálido → en meta
COLOR_BARRA_FAIL = "#f4a261"   # Naranja-terracota cálido → por debajo


def _layout_base(titulo="", alto=320):
    return dict(
        title=dict(text=titulo, font=dict(size=13, color="#1a2e3b", family=FONT_FAMILY), x=0, xanchor="left", pad=dict(l=4, b=8)),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family=FONT_FAMILY, color="#1a2e3b"),
        height=alto,
        margin=dict(l=50, r=20, t=50, b=50),
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(gridcolor=COLOR_GRID, gridwidth=0.5, tickfont=dict(size=11), showline=False, zeroline=False),
        showlegend=False,
        hoverlabel=dict(bgcolor="white", bordercolor="#dde8ef", font_size=12, font_color="#1a2e3b"),
    )


def grafica_evolucion(kpi, color_pilar):
    """Gráfica de barras con línea de meta para un KPI."""
    datos     = get_kpi_data(kpi["id"])
    periodos  = [d["periodo"] for d in datos if d["valor"] is not None]
    valores   = [d["valor"]   for d in datos if d["valor"] is not None]
    meta      = kpi.get("meta")
    invertido = kpi.get("invertido", False)
    um        = kpi.get("um", "")

    fig = go.Figure()

    if not valores:
        fig.add_annotation(text="Sin datos disponibles", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=14, color="#aaa"))
        fig.update_layout(**_layout_base(kpi["nombre"]))
        return fig

    # 🎨 Color cálido: naranja si alcanza meta, terracota si no
    if meta is not None:
        if invertido:
            bar_colors = [COLOR_BARRA_OK if v <= meta else COLOR_BARRA_FAIL for v in valores]
        else:
            bar_colors = [COLOR_BARRA_OK if v >= meta else COLOR_BARRA_FAIL for v in valores]
    else:
        bar_colors = [COLOR_BARRA_OK] * len(valores)

    fig.add_trace(go.Bar(
        x=periodos, y=valores,
        marker_color=bar_colors,
        marker_line_width=0,
        text=[f"{v:,.1f}" if isinstance(v, float) and v != int(v) else f"{v:,}" for v in valores],
        textposition="outside",
        textfont=dict(size=11, color="#1a2e3b"),
        hovertemplate=f"<b>%{{x}}</b><br>Valor: %{{y}} {um}<extra></extra>",
        name="Valor real",
    ))

    if meta is not None:
        fig.add_hline(
            y=meta, line_dash="dash", line_color=COLOR_META_LINE, line_width=1.5,
            annotation_text=f"Meta: {meta} {um}",
            annotation_position="top right",
            annotation_font_size=10,
            annotation_font_color=COLOR_META_LINE,
        )

    layout = _layout_base(kpi["nombre"])
    layout["yaxis"]["title"] = dict(text=um, font=dict(size=11))
    fig.update_layout(**layout)
    return fig


def grafica_gauge(kpi, color_pilar):
    """Gauge de cumplimiento del último período."""
    datos     = get_kpi_data(kpi["id"])
    ultimo    = next((d for d in reversed(datos) if d["valor"] is not None), None)
    meta      = kpi.get("meta")
    um        = kpi.get("um", "")
    invertido = kpi.get("invertido", False)

    if not ultimo or meta is None:
        fig = go.Figure()
        fig.add_annotation(text="Sin datos", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=12, color="#aaa"))
        fig.update_layout(height=220, paper_bgcolor="white", margin=dict(l=10, r=10, t=30, b=10))
        return fig

    valor = ultimo["valor"]
    if invertido:
        pct = min(100, max(0, (1 - (valor - meta) / meta) * 100)) if meta > 0 and valor > 0 else 100
    else:
        pct = min(100, (valor / meta) * 100) if meta > 0 else 100

    if pct >= 90:   color_gauge = "#27ae60"
    elif pct >= 70: color_gauge = "#f39c12"
    else:           color_gauge = "#e74c3c"

    # ── ancho explícito ────────────────────────────────────
    # La card "Situación actual" tiene 240 px con 16 px de padding →
    # interior = 208 px. Con autosize=False + width=208 el SVG se genera
    # a ese tamaño nativo y no se comprime por CSS.
    GAUGE_W = 208  # px = 240 card – 2×16 padding

    # ── suffix corto ────────────────────────────────────────
    # El campo `um` puede ser muy largo (ej: "% reducción lead time").
    # Usarlo completo como suffix del número lo hace desbordar el SVG.
    # Solución: mostrar solo la primera "palabra" (ej: "%", "días", "pts").
    # El um completo ya aparece en la ficha técnica y en el eje del gauge.
    um_suffix = um.split()[0] if um else ""

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor,
        number=dict(suffix=f" {um_suffix}", font=dict(size=15, color="#1a2e3b")),
        delta=dict(
            reference=meta,
            increasing=dict(color="#27ae60" if not invertido else "#e74c3c"),
            decreasing=dict(color="#e74c3c" if not invertido else "#27ae60"),
            font=dict(size=11),
        ),
        gauge=dict(
            axis=dict(
                range=[0, max(meta * 1.3, valor * 1.2)] if not invertido else [0, valor * 1.5],
                tickfont=dict(size=8),   # ticks más pequeños para no solapar
            ),
            bar=dict(color=color_gauge, thickness=0.6),
            bgcolor="white",
            borderwidth=0,
            steps=[
                dict(range=[0, meta * 0.7 if not invertido else meta * 1.3], color="#fde8e8"),
                dict(range=[meta * 0.7 if not invertido else meta * 1.3, meta * 0.9 if not invertido else meta * 1.1], color="#fef3cd"),
                dict(range=[meta * 0.9 if not invertido else meta * 1.1, meta * 1.3 if not invertido else 0], color="#e8f8ee"),
            ] if meta > 0 else [],
            threshold=dict(line=dict(color=COLOR_META_LINE, width=2), thickness=0.75, value=meta),
        ),
        title=dict(text=f"<b>{ultimo['periodo']}</b>", font=dict(size=10, color="#888")),
    ))
    fig.update_layout(
        height=220,
        width=GAUGE_W,       # ← renderiza a 208 px nativos, sin compresión CSS
        autosize=False,      # ← impide que Plotly use su ancho por defecto
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=28, b=8),
        font=dict(family=FONT_FAMILY),
    )
    return fig


def grafica_resumen_pilar(pilar):
    """Barras horizontales de avance de todos los KPIs del pilar."""
    todas_las_etiquetas = []
    valores_norm = []

    for oti in pilar["otis"]:
        for kpi in oti["kpis"]:
            datos  = get_kpi_data(kpi["id"])
            ultimo = next((d for d in reversed(datos) if d["valor"] is not None), None)
            meta   = kpi.get("meta")
            if not ultimo or meta is None or meta == 0:
                continue
            invertido = kpi.get("invertido", False)
            v = ultimo["valor"]
            pct = min(100, max(0, (1 - max(0, v - meta) / meta) * 100)) if invertido else min(100, (v / meta) * 100)
            etiqueta = kpi["nombre"][:30] + "…" if len(kpi["nombre"]) > 30 else kpi["nombre"]
            todas_las_etiquetas.append(etiqueta)
            valores_norm.append(round(pct, 1))

    if not todas_las_etiquetas:
        fig = go.Figure()
        fig.add_annotation(text="Sin datos suficientes", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#aaa"))
        fig.update_layout(height=380, paper_bgcolor="white")
        return fig

    # 🎨 Colores cálidos para las barras del resumen
    colores_barras = []
    for v in valores_norm:
        if v >= 90:   colores_barras.append("#27ae60")
        elif v >= 70: colores_barras.append(BNA_NARANJA)
        else:         colores_barras.append("#e74c3c")

    fig = go.Figure(go.Bar(
        x=valores_norm,
        y=todas_las_etiquetas,
        orientation="h",
        marker_color=colores_barras,
        marker_line_width=0,
        text=[f"{v:.0f}%" for v in valores_norm],
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="<b>%{y}</b><br>Avance: %{x:.1f}%<extra></extra>",
    ))

    alto = max(300, len(todas_las_etiquetas) * 32 + 80)
    fig.update_layout(
        title=dict(text=f"Avance hacia meta — {pilar['nombre']} (Q1-2026)", font=dict(size=13), x=0, xanchor="left"),
        xaxis=dict(range=[0, 120], showgrid=True, gridcolor=COLOR_GRID, ticksuffix="%", tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=11), automargin=True),
        plot_bgcolor="white", paper_bgcolor="white",
        height=alto,
        margin=dict(l=10, r=60, t=50, b=30),
        font=dict(family=FONT_FAMILY),
        hoverlabel=dict(bgcolor="white", bordercolor="#dde8ef", font_size=12, font_color="#1a2e3b"),
        shapes=[dict(type="line", x0=100, x1=100, y0=-0.5, y1=len(todas_las_etiquetas) - 0.5,
                     line=dict(color=COLOR_META_LINE, width=1.5, dash="dash"))],
    )
    return fig


def grafica_tendencia_multi(kpis_ids, labels, color_pilar):
    """Gráfica de líneas multiKPI para comparar tendencias."""
    fig = go.Figure()
    colores = [BNA_AZUL, "#ff8c42", "#f39c12", "#27ae60", "#e74c3c", "#8e44ad"]

    for i, (kid, label) in enumerate(zip(kpis_ids, labels)):
        datos    = get_kpi_data(kid)
        periodos = [d["periodo"] for d in datos if d["valor"] is not None]
        valores  = [d["valor"]   for d in datos if d["valor"] is not None]
        if not valores:
            continue
        fig.add_trace(go.Scatter(
            x=periodos, y=valores, mode="lines+markers",
            name=label[:35],
            line=dict(color=colores[i % len(colores)], width=2),
            marker=dict(size=6),
            hovertemplate=f"<b>{label[:30]}</b><br>%{{x}}: %{{y}}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="Comparativa de tendencias", font=dict(size=13), x=0, xanchor="left"),
        plot_bgcolor="white", paper_bgcolor="white",
        height=300, margin=dict(l=50, r=20, t=50, b=50),
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(gridcolor=COLOR_GRID, tickfont=dict(size=11), zeroline=False),
        showlegend=True,
        legend=dict(font=dict(size=10), orientation="h", y=-0.25),
        font=dict(family=FONT_FAMILY),
    )
    return fig