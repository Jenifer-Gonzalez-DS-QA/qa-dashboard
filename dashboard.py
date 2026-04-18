"""
dashboard.py
Genera un dashboard HTML interactivo con métricas de calidad usando plotly.
"""

import os
import plotly.graph_objects as go
from analyzer import load_results, general_metrics, metrics_by_method, slowest_tests, failed_tests, trend_over_time

COLOR_PASS = "#00e5a0"
COLOR_FAIL = "#ff4d6d"
COLOR_BG = "#0d1117"
COLOR_CARD = "#161b22"
COLOR_BORDER = "#30363d"
COLOR_TEXT = "#e6edf3"
COLOR_MUTED = "#8b949e"
COLOR_ACCENT = "#58a6ff"
YELLOW = "#f0c060"
METHOD_COLORS = {
    "GET":    "#58a6ff",
    "POST":   "#00e5a0",
    "PUT":    "#ffa657",
    "PATCH":  "#d2a8ff",
    "DELETE": "#ff4d6d",
}


def _layout(**extra):
    base = dict(
        paper_bgcolor=COLOR_CARD,
        plot_bgcolor=COLOR_CARD,
        font=dict(family="'JetBrains Mono', monospace",
                  color=COLOR_TEXT, size=12),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    base.update(extra)
    return base


def build_dashboard(df):
    metrics = general_metrics(df)
    by_method = metrics_by_method(df)
    slow = slowest_tests(df, 5)
    failed = failed_tests(df)
    trend = trend_over_time(df)

    # ── Donut pass/fail ───────────────────────────────────────────────────────
    fig_donut = go.Figure(go.Pie(
        labels=["Pasaron", "Fallaron"],
        values=[metrics["passed"], metrics["failed"]],
        hole=0.72,
        marker=dict(colors=[COLOR_PASS, COLOR_FAIL],
                    line=dict(color=COLOR_BG, width=3)),
        textinfo="none",
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    ))
    fig_donut.update_layout(
        **_layout(height=280, showlegend=True,
                  legend=dict(orientation="h", y=-0.1)),
        annotations=[dict(text=f"<b>{metrics['pass_rate_pct']}%</b>",
                          x=0.5, y=0.5, font=dict(size=26, color=COLOR_PASS), showarrow=False)]
    )

    # ── Barras por método ─────────────────────────────────────────────────────
    bar_colors = [METHOD_COLORS.get(m, COLOR_ACCENT)
                  for m in by_method["method"]]
    fig_method = go.Figure(go.Bar(
        x=by_method["method"], y=by_method["pass_rate_pct"],
        marker=dict(color=bar_colors),
        text=by_method["pass_rate_pct"].astype(str) + "%",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Éxito: %{y}%<extra></extra>",
    ))
    fig_method.update_layout(**_layout(
        height=280,
        yaxis=dict(range=[0, 115], showgrid=True,
                   gridcolor=COLOR_BORDER, title="% Éxito"),
        xaxis=dict(title="Método HTTP"),
    ))

    # ── Barras horizontales: más lentas ───────────────────────────────────────
    fig_slow = go.Figure(go.Bar(
        y=slow["test_name"], x=slow["response_time_ms"],
        orientation="h",
        marker=dict(color=slow["response_time_ms"],
                    colorscale=[[0, COLOR_ACCENT], [1, COLOR_FAIL]]),
        text=slow["response_time_ms"].astype(str) + " ms",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x} ms<extra></extra>",
    ))
    fig_slow.update_layout(**_layout(
        height=300,
        xaxis=dict(title="Tiempo (ms)", showgrid=True, gridcolor=COLOR_BORDER),
        yaxis=dict(autorange="reversed"),
    ))

    # ── Tendencia en el tiempo ────────────────────────────────────────────────
    if len(trend) > 1:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend["run"], y=trend["pass_rate_pct"], mode="lines+markers",
            name="% Éxito", line=dict(color=COLOR_PASS, width=2.5),
            hovertemplate="<b>%{x}</b><br>Éxito: %{y}%<extra></extra>",
        ))
        fig_trend.add_trace(go.Scatter(
            x=trend["run"], y=trend["avg_time_ms"], mode="lines+markers",
            name="Tiempo prom (ms)", line=dict(color=COLOR_ACCENT, width=2, dash="dot"),
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Tiempo: %{y} ms<extra></extra>",
        ))
        fig_trend.update_layout(**_layout(
            height=280,
            yaxis=dict(title="% Éxito", showgrid=True,
                       gridcolor=COLOR_BORDER, range=[0, 110]),
            yaxis2=dict(title="Tiempo prom (ms)", overlaying="y",
                        side="right", showgrid=False),
            legend=dict(orientation="h", y=-0.2),
        ))
        trend_html = fig_trend.to_html(full_html=False, include_plotlyjs=False)
    else:
        trend_html = (f'<p style="color:{COLOR_MUTED};padding:40px;text-align:center">'
                      'Ejecuta python main.py más de una vez para ver tendencias.</p>')

    # ── Tabla de fallidas ─────────────────────────────────────────────────────
    if not failed.empty:
        rows = "".join(f"""<tr>
            <td>{r['test_name']}</td>
            <td><span class="badge method-{r['method'].lower()}">{r['method']}</span></td>
            <td style="color:{COLOR_FAIL}">{r['actual_status']}</td>
            <td>{r['expected_status']}</td>
            <td>{r['response_time_ms']} ms</td>
            <td style="color:{COLOR_MUTED};font-size:11px">{r.get('error', '')}</td>
        </tr>""" for _, r in failed.iterrows())
        failed_section = f"""
        <div class="section">
            <h2 class="section-title">⚠️ Pruebas Fallidas</h2>
            <div class="card"><table class="data-table">
                <thead><tr>
                    <th>Nombre</th><th>Método</th><th>Status Real</th>
                    <th>Esperado</th><th>Tiempo</th><th>Error</th>
                </tr></thead>
                <tbody>{rows}</tbody>
            </table></div>
        </div>"""
    else:
        failed_section = """
        <div class="section">
            <div class="card all-pass">✅ ¡Todas las pruebas pasaron exitosamente!</div>
        </div>"""

    # ── HTML ──────────────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>

<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>QA Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">
<style>
,::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:{COLOR_BG};--card:{COLOR_CARD};--border:{COLOR_BORDER};--text:{COLOR_TEXT};--muted:{COLOR_MUTED};--pass:{COLOR_PASS};--fail:{COLOR_FAIL};--accent:{COLOR_ACCENT}}}
body{{background:var(--bg);color:var(--text);font-family:'JetBrains Mono',monospace;padding-bottom:60px}}
.header{{background:linear-gradient(135deg,#0d1117,#161b22);border-bottom:1px solid var(--border);padding:32px 48px}}
.header-label{{font-size:11px;letter-spacing:3px;color:var(--pass);text-transform:uppercase;margin-bottom:8px}}
.header-title{{font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800}}
.header-title span{{color:var(--pass)}}
.header-sub{{margin-top:10px;font-size:12px;color:var(--muted)}}
.container{{max-width:1200px;margin:0 auto;padding:0 32px}}
.section{{margin-top:40px}}
.section-title{{font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;letter-spacing:1px;color:var(--muted);text-transform:uppercase;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid var(--border)}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:20px;transition:border-color .2s}}
.card:hover{{border-color:rgba(88,166,255,.3)}}
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px}}
.kpi-card{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:20px 18px;position:relative;overflow:hidden;transition:transform .2s}}
.kpi-card:hover{{transform:translateY(-2px)}}
.kpi-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--kpi-color,var(--accent))}}
.kpi-label{{font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-bottom:10px}}
.kpi-value{{font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:var(--kpi-color,var(--text));line-height:1}}
.kpi-unit{{font-size:12px;color:var(--muted);margin-top:4px}}
.charts-2col{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.data-table{{width:100%;border-collapse:collapse;font-size:12px}}
.data-table th{{text-align:left;padding:10px 12px;color:var(--muted);font-size:10px;letter-spacing:1px;text-transform:uppercase;border-bottom:1px solid var(--border)}}
.data-table td{{padding:10px 12px;border-bottom:1px solid rgba(48,54,61,.5)}}
.badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600}}
.method-get{{background:rgba(88,166,255,.15);color:#58a6ff}}
.method-post{{background:rgba(0,229,160,.15);color:#00e5a0}}
.method-put{{background:rgba(255,166,87,.15);color:#ffa657}}
.method-patch{{background:rgba(210,168,255,.15);color:#d2a8ff}}
.method-delete{{background:rgba(255,77,109,.15);color:#ff4d6d}}
.all-pass{{text-align:center;padding:32px;color:var(--pass);font-family:'Syne',sans-serif;font-size:1.1rem}}
@media(max-width:768px){{.charts-2col{{grid-template-columns:1fr}}.header{{padding:24px 20px}}.container{{padding:0 16px}}}}
</style>
</head>
<body>
<div class="header">
  <div class="header-label">QA · Automation · Dashboard</div>
  <h1 class="header-title">Quality <span>Metrics</span></h1>
  <p class="header-sub">API: jsonplaceholder.typicode.com &nbsp;·&nbsp; Sin registro ni API key &nbsp;·&nbsp; {metrics['total_tests']} pruebas &nbsp;·&nbsp; Python + Pandas + Plotly</p>
</div>
<div class="container">
  <div class="section">
    <h2 class="section-title">📊 Indicadores Clave</h2>
    <div class="kpi-grid">
      <div class="kpi-card" style="--kpi-color:{COLOR_PASS}"><div class="kpi-label">Tasa de Éxito</div><div class="kpi-value">{metrics['pass_rate_pct']}</div><div class="kpi-unit">%</div></div>
      <div class="kpi-card" style="--kpi-color:{COLOR_PASS}"><div class="kpi-label">Pasaron</div><div class="kpi-value">{metrics['passed']}</div><div class="kpi-unit">pruebas OK</div></div>
      <div class="kpi-card" style="--kpi-color:{COLOR_FAIL}"><div class="kpi-label">Fallaron</div><div class="kpi-value">{metrics['failed']}</div><div class="kpi-unit">con error</div></div>
      <div class="kpi-card" style="--kpi-color:{COLOR_ACCENT}"><div class="kpi-label">Tiempo Prom.</div><div class="kpi-value">{metrics['avg_time_ms']}</div><div class="kpi-unit">ms</div></div>
      <div class="kpi-card" style="--kpi-color:#ffa657"><div class="kpi-label">Tiempo Máx.</div><div class="kpi-value">{metrics['max_time_ms']}</div><div class="kpi-unit">ms</div></div>
      <div class="kpi-card" style="--kpi-color:#d2a8ff"><div class="kpi-label">Tiempo Mín.</div><div class="kpi-value">{metrics['min_time_ms']}</div><div class="kpi-unit">ms</div></div>
    </div>
  </div>
  <div class="section">
    <h2 class="section-title">📈 Distribución de Resultados</h2>
    <div class="charts-2col">
      <div class="card">{fig_donut.to_html(full_html=False, include_plotlyjs=False)}</div>
      <div class="card">{fig_method.to_html(full_html=False, include_plotlyjs=False)}</div>
    </div>
  </div>
  <div class="section">
    <h2 class="section-title">🐢 Top 5 Pruebas más Lentas</h2>
    <div class="card">{fig_slow.to_html(full_html=False, include_plotlyjs=False)}</div>
  </div>
  <div class="section">
    <h2 class="section-title">📉 Tendencia en el Tiempo</h2>
    <div class="card">{trend_html}</div>
  </div>
  {failed_section}
</div>
</body>
</html>"""

    os.makedirs("reports", exist_ok=True)
    output = "reports/dashboard.html"
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Dashboard generado: {output}")
    return output


if __name__ == "__main__":
    df = load_results()
    build_dashboard(df)
