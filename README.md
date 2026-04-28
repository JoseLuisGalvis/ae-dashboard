# Dashboard Estratégico AE

Aplicación web local construida con **Dash + Plotly**.  
2 Áreas · 2 Objetivos Estratégicos (OTIs) · 5 KPIs · Datos Q1-2025 → Q1-2026

---

## Instalación (una sola vez)

```bash
# 1. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Instalar dependencias
pip install -r requirements.txt
```

---

## Ejecución

```bash
python app.py
```

Abrí el navegador en: **http://localhost:8070**

---

## Estructura del proyecto

```
bna_dashboard/
│
├── app.py               ← App principal (layout + callbacks)
├── charts.py            ← Gráficas Plotly (barras, gauge, resumen)
├── requirements.txt     ← Dependencias Python
├── README.md            ← Este archivo
│
└── data/
    ├── __init__.py
    └── kpis.py          ← 6 pilares, 22 OTIs, 43 KPIs + datos históricos
```

---

## Cómo actualizar los datos

Abrí `data/kpis.py` y buscá el diccionario `KPI_HISTORICO`.  
Cada KPI tiene 5 valores: `[Q1-2025, Q2-2025, Q3-2025, Q4-2025, Q1-2026]`.

```python
"KPI-SW-01": [8, 14, 21, 29, 35],   # ← modificá estos valores
```

Guardá el archivo y recargá el navegador (F5). No hace falta reiniciar el servidor.

---

## Cómo agregar un nuevo período (ej: Q2-2026)

1. En `data/kpis.py`, agregá `"Q2-2026"` al final de la lista `PERIODOS`
2. Agregá el nuevo valor al final de cada lista en `KPI_HISTORICO`
3. Guardá y recargá

---

## Tecnologías

| Librería       | Uso                    |
| -------------- | ---------------------- |
| Dash 2.x       | Framework web reactivo |
| Plotly 5.x     | Gráficas interactivas  |
| Dash Bootstrap | Grid y estilos base    |
| Pandas         | Manipulación de datos  |

---

## Próximos pasos sugeridos

- Conectar a Excel real: usar `pandas.read_excel()` en `data/kpis.py`
- Agregar export a PDF con `kaleido`
- Agregar filtro por responsable o fuente
- Deploy en servidor interno con `gunicorn app:server`
