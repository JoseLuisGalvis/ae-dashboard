# ═══════════════════════════════════════════════════════
# app.py — Dashboard Estratégico AE TI 2026–2028
# Tecnología: Dash + Plotly + Bootstrap
# Ejecutar: python app.py  →  http://localhost:8070
# ═══════════════════════════════════════════════════════

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from data.kpis import AREAS, get_kpi_data, get_all_kpis, PERIODOS
from charts import grafica_evolucion, grafica_gauge, grafica_resumen_pilar, grafica_tendencia_multi

# ── App ─────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    ],
    suppress_callback_exceptions=True,
    title="Dashboard Estratégico AE — TI 2026-2028",
)

# ── Paleta BNA ─────────────────────────────────────────
BNA_AZUL        = "#005F87"
BNA_AZUL_DARK   = "#004466"
BNA_AZUL_LIGHT  = "#e6f2f7"
BNA_NARANJA     = "#ff7a00"
BNA_NARANJA_2   = "#ffb347"
BNA_NARANJA_BG  = "#fff4eb"
BNA_TEXT_DARK   = "#1a2e3b"
BNA_TEXT_MID    = "#4a6572"
BNA_TEXT_LIGHT  = "#718096"
BNA_BG          = "#f4f8fb"
BNA_WHITE       = "#ffffff"
BNA_BORDER      = "#dde8ef"

COLOR_META      = "#27ae60"
COLOR_PROGRESO  = "#f39c12"
COLOR_DEBAJO    = "#e74c3c"
COLOR_SIN_DATOS = "#94a3b8"

FONT = "'Inter', 'Helvetica Neue', Arial, sans-serif"


# ── Helpers de UI ────────────────────────────────────────

def badge_oti(texto):
    return html.Span(texto, style={
        "background": BNA_AZUL_LIGHT, "color": BNA_AZUL_DARK,
        "fontSize": "11px", "padding": "3px 10px", "borderRadius": "12px",
        "fontWeight": "500", "border": f"1px solid {BNA_AZUL}40",
    })


def card_kpi_mini(kpi, color_pilar):
    datos  = get_kpi_data(kpi["id"])
    ultimo = next((d for d in reversed(datos) if d["valor"] is not None), None)
    meta   = kpi.get("meta")
    um     = kpi.get("um", "")
    invertido = kpi.get("invertido", False)

    if ultimo and meta is not None and meta != 0:
        v = ultimo["valor"]
        pct = min(100, max(0, (1 - max(0, v - meta) / meta) * 100)) if invertido else min(100, (v / meta) * 100)
        if pct >= 90:   status, color_status = "En meta",     COLOR_META
        elif pct >= 70: status, color_status = "En progreso", COLOR_PROGRESO
        else:           status, color_status = "Por debajo",  COLOR_DEBAJO
        valor_display = f"{v:,.1f}" if isinstance(v, float) and v != int(v) else f"{v:,}"
    else:
        status, color_status, valor_display, pct = "Sin datos", COLOR_SIN_DATOS, "—", 0

    return html.Div([
        html.Div(style={"width": "4px", "background": color_status, "borderRadius": "4px 0 0 4px", "flexShrink": 0}),
        html.Div([
            html.Div(kpi["id"], style={"fontSize": "10px", "color": BNA_AZUL, "fontWeight": "600", "letterSpacing": "0.5px"}),
            html.Div(kpi["nombre"], style={"fontSize": "12px", "color": BNA_TEXT_DARK, "fontWeight": "500", "lineHeight": "1.3", "marginTop": "2px"}),
            html.Div([
                html.Span(f"{valor_display} {um}", style={"fontSize": "13px", "fontWeight": "700", "color": color_status}),
                html.Span(f"  meta: {kpi['meta_label']}", style={"fontSize": "10px", "color": BNA_TEXT_LIGHT, "marginLeft": "6px"}),
            ], style={"marginTop": "4px"}),
        ], style={"flex": 1, "padding": "0 10px"}),
    ], id={"type": "kpi-card", "kpi_id": kpi["id"]},
    n_clicks=0,
    style={
        "display": "flex", "alignItems": "stretch", "cursor": "pointer",
        "background": BNA_WHITE, "borderRadius": "8px", "padding": "10px 6px",
        "marginBottom": "6px", "border": f"1px solid {BNA_BORDER}",
        "transition": "box-shadow .15s, border-color .15s",
        "boxShadow": "0 2px 6px rgba(0,95,135,0.10)",
    })


def sidebar_pilar(pilar):
    oti_sections = []
    for oti in pilar["otis"]:
        kpi_cards = [card_kpi_mini(k, pilar["color"]) for k in oti["kpis"]]
        oti_sections.append(html.Div([
            html.Div(oti["nombre"], style={
                "fontSize": "11px", "fontWeight": "600", "color": BNA_AZUL,
                "textTransform": "uppercase", "letterSpacing": "0.6px",
                "padding": "10px 0 6px", "borderBottom": f"2px solid {BNA_AZUL}25",
                "marginBottom": "8px",
            }),
            *kpi_cards,
        ]))
    return html.Div(oti_sections, style={"padding": "0 4px"})


# ── Layout principal ─────────────────────────────────────
def make_pilar_tabs():
    tabs = []
    for p in AREAS:
        tabs.append(dcc.Tab(
            label=p["nombre"],
            value=p["id"],
            style={"fontFamily": FONT, "fontSize": "13px", "padding": "10px 16px", "color": BNA_TEXT_MID, "fontWeight": "500"},
            selected_style={
                "fontFamily": FONT, "fontSize": "13px", "padding": "10px 16px",
                "color": BNA_AZUL, "fontWeight": "700",
                "borderTop": f"3px solid {BNA_NARANJA}", "background": BNA_AZUL_LIGHT,
            },
        ))
    return tabs


app.layout = html.Div([
    # ── Header ───────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div([
                html.Img(src="/assets/logo_BNA.jpeg", style={"height": "42px", "marginRight": "12px"}),
                html.Div([html.Div("Banco de la Nación Argentina", style={"fontSize": "15px", "color": "rgba(255,255,255,0.85)", "textShadow": "0px 1px 2px rgba(0,0,0,0.6)"})])
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div([
                html.Div("Dashboard Estratégico AE", style={"fontWeight": "700", "fontSize": "18px", "color": "white", "textShadow": "0px 2px 4px rgba(0,0,0,0.7)"}),
                html.Div("Plan 2026 – 2028 · 2 Áreas · 2 Objetivos · 5 KPIs", style={"fontSize": "12px", "color": "rgba(255,255,255,0.8)"}),
            ], style={"marginLeft": "20px", "borderLeft": "2px solid rgba(255,255,255,0.3)", "paddingLeft": "20px"}),
        ], style={"display": "flex", "alignItems": "center"}),

        html.Div([
            html.Div("Último período: Q1-2026", style={"fontSize": "12px", "color": "rgba(255,255,255,0.85)"}),
            html.Div([
                html.Span("●", style={"color": "#2ecc71",  "marginRight": "4px"}), html.Span("En meta",     style={"marginRight": "12px"}),
                html.Span("●", style={"color": "#f39c12",  "marginRight": "4px"}), html.Span("En progreso", style={"marginRight": "12px"}),
                html.Span("●", style={"color": "#e74c3c",  "marginRight": "4px"}), html.Span("Por debajo",  style={"marginRight": "12px"}),
                html.Span("●", style={"color": "#f5f5f5",  "marginRight": "4px"}), html.Span("Sin Datos"),
            ], style={"fontSize": "11px", "color": "white", "marginTop": "4px"}),
        ], style={"textAlign": "right"}),
    ], style={
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "background": BNA_AZUL, "padding": "16px 28px",
        "boxShadow": "0 4px 12px rgba(0,0,0,0.25)",
        "borderBottom": "3px solid",
        "borderImage": f"linear-gradient(to right, {BNA_NARANJA}, {BNA_NARANJA_2}) 1",
        "fontFamily": FONT,
    }),

    # ── Tabs de AREAS ──────────────────────────────────
    html.Div([
        dcc.Tabs(id="tabs-pilar", value=AREAS[0]["id"], children=make_pilar_tabs(), style={"fontFamily": FONT}),
    ], style={"background": BNA_WHITE, "borderBottom": f"1px solid {BNA_BORDER}", "padding": "0 20px"}),

    # ── Body ─────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div(id="sidebar-content", style={"overflowY": "auto", "height": "100%", "padding": "16px 12px"}),
        ], style={
            "width": "300px", "flexShrink": 0, "background": BNA_WHITE,
            "borderRight": f"1px solid {BNA_BORDER}",
            "height": "calc(100vh - 120px)", "overflowY": "auto",
        }),
        html.Div([
            html.Div(id="main-content", style={"padding": "20px 24px"}),
        ], style={"flex": 1, "overflowY": "auto", "height": "calc(100vh - 120px)", "background": BNA_BG}),
    ], style={"display": "flex", "flex": 1}),

    dcc.Store(id="store-kpi-seleccionado", data=None),
    dcc.Store(id="store-pilar-seleccionado", data=AREAS[0]["id"]),
    dcc.Store(id="store-volver-clicks", data=0),

], style={"fontFamily": FONT, "background": BNA_BG, "minHeight": "100vh", "display": "flex", "flexDirection": "column"})


# ── Callbacks ────────────────────────────────────────────

@app.callback(
    Output("sidebar-content", "children"),
    Output("store-pilar-seleccionado", "data"),
    Input("tabs-pilar", "value"),
)
def actualizar_sidebar(pilar_id):
    pilar = next((p for p in AREAS if p["id"] == pilar_id), AREAS[0])
    header = html.Div([
        html.Div(pilar["nombre"], style={"fontWeight": "700", "fontSize": "15px", "color": BNA_AZUL}),
        html.Div(pilar["subtitulo"], style={"fontSize": "11px", "color": BNA_TEXT_MID, "marginTop": "2px", "lineHeight": "1.4"}),
    ], style={"marginBottom": "14px", "paddingBottom": "12px", "borderBottom": f"2px solid {BNA_NARANJA}"})
    return [header, sidebar_pilar(pilar)], pilar_id


@app.callback(
    Output("store-volver-clicks", "data"),
    Input("btn-volver", "n_clicks"),
    State("store-volver-clicks", "data"),
    prevent_initial_call=True,
)
def registrar_volver(n_clicks, prev):
    if n_clicks:
        return (prev or 0) + 1
    return prev or 0


# ─── FIX BUG 1: auto-jump al primer KPI ──────────────────
# Cuando Dash monta los kpi-card con n_clicks=0 dispara este callback
# aunque nadie hizo click. La corrección verifica que el n_clicks del
# card "triggereado" sea efectivamente > 0 antes de navegar.
@app.callback(
    Output("store-kpi-seleccionado", "data"),
    Input({"type": "kpi-card", "kpi_id": dash.ALL}, "n_clicks"),
    Input("tabs-pilar", "value"),
    Input("store-volver-clicks", "data"),
    State({"type": "kpi-card", "kpi_id": dash.ALL}, "id"),
    State("store-kpi-seleccionado", "data"),
    prevent_initial_call=True,
)
def gestionar_navegacion(n_clicks_list, pilar_tab, volver_count, ids, kpi_actual):
    import json
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]["prop_id"]

    # Cambio de pestaña → siempre volver a vista pilar
    if triggered_id == "tabs-pilar.value":
        return None

    # Click en "Volver" → resetear a vista pilar
    if triggered_id == "store-volver-clicks.data":
        return None

    # Click en card de KPI — solo si el card tiene n_clicks > 0
    try:
        prop = json.loads(triggered_id.rsplit(".", 1)[0])
        kpi_id = prop.get("kpi_id")
        if kpi_id:
            idx = next(
                (i for i, id_ in enumerate(ids) if id_.get("kpi_id") == kpi_id),
                None,
            )
            # Verificación clave: solo navegar si hubo un click real
            if idx is not None and n_clicks_list and (n_clicks_list[idx] or 0) > 0:
                return kpi_id
    except Exception:
        pass

    return dash.no_update


@app.callback(
    Output("main-content", "children"),
    Input("store-kpi-seleccionado", "data"),
    Input("tabs-pilar", "value"),
)
def actualizar_contenido(kpi_id, pilar_id):
    pilar = next((p for p in AREAS if p["id"] == pilar_id), AREAS[0])
    todos_kpis = [k for oti in pilar["otis"] for k in oti["kpis"]]

    if kpi_id:
        kpi = next((k for k in todos_kpis if k["id"] == kpi_id), None)
        if kpi:
            return vista_detalle_kpi(kpi, pilar)

    return vista_resumen_pilar(pilar)


# ── Vistas ───────────────────────────────────────────────

def vista_resumen_pilar(pilar):
    todos_kpis = [k for oti in pilar["otis"] for k in oti["kpis"]]
    en_meta = en_progreso = por_debajo = sin_datos = 0
    for kpi in todos_kpis:
        datos = get_kpi_data(kpi["id"])
        ultimo = next((d for d in reversed(datos) if d["valor"] is not None), None)
        meta = kpi.get("meta")
        if not ultimo or meta is None or meta == 0:
            sin_datos += 1; continue
        v, invertido = ultimo["valor"], kpi.get("invertido", False)
        pct = min(100, (1 - max(0, v - meta) / meta) * 100) if invertido else min(100, (v / meta) * 100)
        if pct >= 90:   en_meta += 1
        elif pct >= 70: en_progreso += 1
        else:           por_debajo += 1

    tarjetas_summary = html.Div([
        _metric_card("Total KPIs",  str(len(todos_kpis)), BNA_TEXT_DARK, BNA_AZUL_LIGHT),
        _metric_card("En meta",     str(en_meta),         "white",       COLOR_META),
        _metric_card("En progreso", str(en_progreso),     "white",       COLOR_PROGRESO),
        _metric_card("Por debajo",  str(por_debajo),      "white",       COLOR_DEBAJO),
        _metric_card("Sin datos",   str(sin_datos),       BNA_TEXT_MID,  "#e8ecf2"),
    ], style={"display": "flex", "gap": "12px", "marginBottom": "24px", "flexWrap": "wrap"})

    fig_resumen = grafica_resumen_pilar(pilar)

    oti_sections = []
    for oti in pilar["otis"]:
        kpis_con_datos = [k for k in oti["kpis"] if any(d["valor"] is not None for d in get_kpi_data(k["id"]))]

        # ── FIX BUG 2 (vista resumen) ────────────────────────
        # El nombre del KPI debajo del gauge se contiene en width fijo
        # igual al del gráfico; overflowWrap impide que desborde.
        gauges = html.Div([
            html.Div([
                dcc.Graph(
                    figure=grafica_gauge(k, BNA_AZUL),
                    config={"displayModeBar": False},
                    style={"width": "200px"},
                ),
                html.Div(
                    k["nombre"],
                    style={
                        "fontSize": "10px",
                        "color": BNA_TEXT_MID,
                        "textAlign": "center",
                        "width": "200px",
                        "lineHeight": "1.3",
                        "marginTop": "-5px",
                        "overflowWrap": "break-word",
                        "wordBreak": "break-word",
                        "padding": "0 4px",
                        "boxSizing": "border-box",
                    },
                ),
            ], style={"display": "flex", "flexDirection": "column", "alignItems": "center"})
            for k in kpis_con_datos
        ] if kpis_con_datos else [html.Div("Sin datos disponibles aún", style={"color": "#aaa", "fontSize": "12px", "padding": "10px"})],
        style={"display": "flex", "flexWrap": "wrap", "gap": "8px"})

        oti_sections.append(html.Div([
            html.Div([
                html.Div(oti["id"], style={"fontSize": "10px", "color": BNA_NARANJA, "fontWeight": "700", "letterSpacing": "0.5px"}),
                html.Div(oti["nombre"], style={"fontSize": "14px", "fontWeight": "600", "color": BNA_TEXT_DARK}),
                html.Div(f"{len(oti['kpis'])} KPIs", style={"fontSize": "11px", "color": BNA_TEXT_LIGHT}),
            ], style={"marginBottom": "12px"}),
            gauges,
        ], className="card-chart", style={
            "background": BNA_WHITE, "borderRadius": "12px", "padding": "16px 20px",
            "marginBottom": "14px", "border": f"1px solid {BNA_BORDER}",
            "boxShadow": "0 3px 12px rgba(0,95,135,0.10)",
        }))

    return html.Div([
        html.Div([
            html.Div(pilar["nombre"], style={"fontSize": "22px", "fontWeight": "700", "color": BNA_AZUL}),
            html.Div(pilar["subtitulo"], style={"fontSize": "13px", "color": BNA_TEXT_MID, "marginTop": "2px"}),
            html.Div("Seleccioná un KPI en el panel izquierdo para ver su detalle →", style={"fontSize": "11px", "color": BNA_TEXT_LIGHT, "marginTop": "6px"}),
        ], style={"marginBottom": "20px"}),
        tarjetas_summary,
        html.Div([
            html.Div("Avance hacia meta por KPI (Q1-2026)", style={"fontSize": "13px", "fontWeight": "600", "color": BNA_TEXT_DARK, "marginBottom": "8px"}),
            dcc.Graph(figure=fig_resumen, config={"displayModeBar": False}),
        ], className="card-chart", style={
            "background": BNA_WHITE, "borderRadius": "12px", "padding": "16px 20px",
            "marginBottom": "20px", "border": f"1px solid {BNA_BORDER}",
            "boxShadow": "0 3px 12px rgba(0,95,135,0.10)",
        }),
        html.Div(oti_sections),
    ])


def vista_detalle_kpi(kpi, pilar):
    datos = get_kpi_data(kpi["id"])
    fig_barras = grafica_evolucion(kpi, BNA_AZUL)
    fig_gauge  = grafica_gauge(kpi, BNA_AZUL)
    oti_nombre = next((oti["nombre"] for oti in pilar["otis"] if any(k["id"] == kpi["id"] for k in oti["kpis"])), "—")

    ficha_items = [
        ("Unidad de medida",     kpi.get("um", "—")),
        ("Meta",                 kpi.get("meta_label", "—")),
        ("Fuente",               kpi.get("fuente", "—")),
        ("Responsable",          kpi.get("responsable", "—")),
        ("Objetivo estratégico", oti_nombre),
        ("Área",                pilar["nombre"]),
    ]

    ficha = html.Div([
        html.Div([
            html.Div(label, style={"fontSize": "10px", "color": BNA_TEXT_LIGHT, "fontWeight": "600", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
            html.Div(valor, style={"fontSize": "12px", "color": BNA_TEXT_DARK, "marginTop": "2px", "fontWeight": "500"}),
        ], style={"padding": "10px 0", "borderBottom": f"1px solid {BNA_AZUL_LIGHT}"})
        for label, valor in ficha_items
    ], style={
        "background": BNA_WHITE, "borderRadius": "12px", "padding": "0 20px",
        "border": f"1px solid {BNA_BORDER}",
        "boxShadow": "0 3px 12px rgba(0,95,135,0.10)",
    })

    return html.Div([
        html.Div([
            html.Span("← Volver al resumen del Área", id="btn-volver", n_clicks=0, style={
                "cursor": "pointer", "fontSize": "12px", "color": BNA_AZUL,
                "fontWeight": "600", "padding": "4px 0",
            }),
        ], style={"marginBottom": "16px"}),

        html.Div([
            html.Div([
                html.Div(kpi["id"], style={"fontSize": "11px", "color": BNA_NARANJA, "fontWeight": "700", "letterSpacing": "0.5px", "marginBottom": "4px"}),
                html.Div(kpi["nombre"], style={"fontSize": "20px", "fontWeight": "700", "color": BNA_TEXT_DARK}),
                html.Div(badge_oti(oti_nombre), style={"marginTop": "6px"}),
            ]),
        ], style={"marginBottom": "20px"}),

        html.Div([
            # ── FIX BUG 2 (card Situación Actual) ───────────────
            # overflow:hidden recorta cualquier contenido del gauge que
            # exceda los 240 px del contenedor; style width:100% en el
            # Graph fuerza al chart a respetar el ancho disponible.
            html.Div([
                html.Div(
                    "Situación actual",
                    style={
                        "fontSize": "12px", "fontWeight": "600",
                        "color": BNA_TEXT_MID, "marginBottom": "8px",
                        "overflowWrap": "break-word",
                        "wordBreak": "break-word",
                    },
                ),
                dcc.Graph(
                    figure=fig_gauge,
                    config={"displayModeBar": False},
                    style={"width": "100%"},
                ),
            ], className="card-chart", style={
                "background": BNA_WHITE, "borderRadius": "12px", "padding": "16px",
                "border": f"1px solid {BNA_BORDER}",
                "width": "240px", "flexShrink": 0,
                "boxShadow": "0 3px 12px rgba(0,95,135,0.10)",
                "overflow": "hidden",
                "boxSizing": "border-box",
            }),
            html.Div([
                html.Div("Evolución trimestral 2025 → Q1-2026", style={"fontSize": "12px", "fontWeight": "600", "color": BNA_TEXT_MID, "marginBottom": "8px"}),
                dcc.Graph(figure=fig_barras, config={"displayModeBar": False, "responsive": True}),
            ], className="card-chart", style={
                "background": BNA_WHITE, "borderRadius": "12px", "padding": "16px",
                "border": f"1px solid {BNA_BORDER}", "flex": 1,
                "boxShadow": "0 3px 12px rgba(0,95,135,0.10)",
            }),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px", "alignItems": "flex-start"}),

        html.Div([
            html.Div("Ficha técnica del indicador", style={"fontSize": "13px", "fontWeight": "600", "color": BNA_TEXT_DARK, "marginBottom": "12px"}),
            ficha,
        ], style={"marginBottom": "16px"}),

        html.Div([
            html.Div("Datos históricos", style={"fontSize": "13px", "fontWeight": "600", "color": BNA_TEXT_DARK, "marginBottom": "12px"}),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Período",    style={"fontSize": "11px", "color": BNA_TEXT_LIGHT, "fontWeight": "600", "padding": "8px 16px", "textAlign": "left",   "borderBottom": f"2px solid {BNA_AZUL_LIGHT}"}),
                    html.Th("Valor real", style={"fontSize": "11px", "color": BNA_TEXT_LIGHT, "fontWeight": "600", "padding": "8px 16px", "textAlign": "right",  "borderBottom": f"2px solid {BNA_AZUL_LIGHT}"}),
                    html.Th("Meta",       style={"fontSize": "11px", "color": BNA_TEXT_LIGHT, "fontWeight": "600", "padding": "8px 16px", "textAlign": "right",  "borderBottom": f"2px solid {BNA_AZUL_LIGHT}"}),
                    html.Th("Estado",     style={"fontSize": "11px", "color": BNA_TEXT_LIGHT, "fontWeight": "600", "padding": "8px 16px", "textAlign": "center", "borderBottom": f"2px solid {BNA_AZUL_LIGHT}"}),
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(d["periodo"], style={"padding": "8px 16px", "fontSize": "12px", "color": BNA_TEXT_DARK}),
                        html.Td(
                            f"{d['valor']:,.2f}" if isinstance(d['valor'], float) and d['valor'] != int(d['valor']) else (f"{d['valor']:,}" if d['valor'] is not None else "—"),
                            style={"padding": "8px 16px", "fontSize": "12px", "fontWeight": "600", "color": BNA_AZUL_DARK, "textAlign": "right"}
                        ),
                        html.Td(str(kpi.get("meta", "—")), style={"padding": "8px 16px", "fontSize": "12px", "color": BNA_TEXT_MID, "textAlign": "right"}),
                        html.Td(_estado_badge(d["valor"], kpi.get("meta"), kpi.get("invertido", False)), style={"padding": "8px 16px", "textAlign": "center"}),
                    ], style={"borderBottom": f"1px solid {BNA_AZUL_LIGHT}", "transition": "background .1s"})
                    for d in datos
                ]),
            ], style={"width": "100%", "borderCollapse": "collapse"}),
        ], style={
            "background": BNA_WHITE, "borderRadius": "12px", "padding": "16px 20px",
            "border": f"1px solid {BNA_BORDER}",
            "boxShadow": "0 3px 12px rgba(0,95,135,0.10)",
        }),
    ])


def _estado_badge(valor, meta, invertido=False):
    if valor is None or meta is None:
        return html.Span("—", style={"fontSize": "11px", "color": "#ccc"})
    pct = 100 if meta == 0 else (min(100, max(0, (1 - max(0, valor - meta) / meta) * 100)) if invertido else min(100, (valor / meta) * 100))
    if pct >= 90:   txt, bg, fg = "En meta",    "#dcf5e7", "#1a7a4a"
    elif pct >= 70: txt, bg, fg = "Progreso",   "#fef3cd", "#7d5800"
    else:           txt, bg, fg = "Por debajo", "#fde8e8", "#a02020"
    return html.Span(txt, style={"fontSize": "10px", "fontWeight": "600", "padding": "3px 10px", "borderRadius": "10px", "background": bg, "color": fg})


def _metric_card(titulo, valor, color_texto, color_bg):
    return html.Div([
        html.Div(titulo, style={"fontSize": "10px", "fontWeight": "600", "opacity": "0.80", "textTransform": "uppercase", "letterSpacing": "0.5px"}),
        html.Div(valor, style={"fontSize": "26px", "fontWeight": "700", "marginTop": "4px"}),
    ], style={
        "background": color_bg, "color": color_texto, "borderRadius": "10px",
        "padding": "14px 18px", "minWidth": "90px",
        "boxShadow": "0 3px 12px rgba(0,95,135,0.13)",
    })


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8070)