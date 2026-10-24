import os
import dash
from dash import dcc, html, Input, Output
import mysql.connector
import pandas as pd
import plotly.graph_objects as go

# Conexión a MySQL
DB_HOST = os.getenv("DB_HOST", "mysql")
DB_USER = os.getenv("DB_USER", "dash_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "DashDemo2026_local")
DB_NAME = os.getenv("DB_NAME", "agricultura")

# 1. Importar la tipografía "Plus Jakarta Sans" y "Inter" directamente de Google Fonts
GOOGLE_FONTS = (
    "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap"
)

app = dash.Dash(
    __name__,
    title="Crypto Monitor Pro",
    external_stylesheets=[GOOGLE_FONTS],
)
server = app.server

# Colores de identidad por moneda
CRYPTO_THEME = {
    "bitcoin": {"color": "#F7931A", "label": "Bitcoin (BTC)"},
    "ethereum": {"color": "#627EEA", "label": "Ethereum (ETH)"},
    "solana": {"color": "#14F195", "label": "Solana (SOL)"},
}

app.layout = html.Div(
    style={
        "backgroundColor": "#0d1117",
        "minHeight": "100vh",
        # 2. Definir la nueva tipografía como regla global
        "fontFamily": "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif",
        "padding": "30px",
        "color": "#e6edf3",
    },
    children=[
        # Encabezado
        html.Div(
            style={"textAlign": "center", "marginBottom": "28px"},
            children=[
                html.H1(
                    "Monitor de Criptomonedas en Vivo",
                    style={
                        "margin": "0",
                        "fontWeight": "700",
                        "fontSize": "2.1rem",
                        "letterSpacing": "-0.5px",
                    },
                ),
                html.P(
                    "Arquitectura Desacoplada: Docker + CoinGecko + MySQL 8.4 + Dash",
                    style={
                        "color": "#8b949e",
                        "marginTop": "8px",
                        "fontSize": "0.95rem",
                        "fontWeight": "500",
                    },
                ),
            ],
        ),
        # Tarjeta de Filtros
        html.Div(
            style={
                "maxWidth": "850px",
                "margin": "0 auto 20px auto",
                "backgroundColor": "#161b22",
                "padding": "18px 24px",
                "borderRadius": "12px",
                "border": "1px solid #30363d",
                "boxShadow": "0 8px 24px rgba(0,0,0,0.25)",
            },
            children=[
                html.Label(
                    "Selecciona el activo:",
                    style={
                        "fontWeight": "600",
                        "fontSize": "0.9rem",
                        "display": "block",
                        "marginBottom": "8px",
                        "color": "#c9d1d9",
                    },
                ),
                dcc.Dropdown(
                    id="crypto-selector",
                    options=[
                        {"label": "Bitcoin (BTC)", "value": "bitcoin"},
                        {"label": "Ethereum (ETH)", "value": "ethereum"},
                        {"label": "Solana (SOL)", "value": "solana"},
                    ],
                    value="bitcoin",
                    clearable=False,
                    style={
                        "color": "#161b22",
                        "fontFamily": "'Plus Jakarta Sans', sans-serif",
                        "fontWeight": "500",
                    },
                ),
            ],
        ),
        # Tarjeta principal del Gráfico
        html.Div(
            style={
                "maxWidth": "1100px",
                "margin": "0 auto",
                "backgroundColor": "#161b22",
                "padding": "24px",
                "borderRadius": "14px",
                "border": "1px solid #30363d",
                "boxShadow": "0 8px 24px rgba(0,0,0,0.3)",
            },
            children=[
                dcc.Graph(id="crypto-graph", config={"displayModeBar": False}),
                html.Div(
                    id="stats-footer",
                    style={
                        "textAlign": "center",
                        "marginTop": "16px",
                        "fontSize": "0.92rem",
                        "fontWeight": "500",
                        "letterSpacing": "0.2px",
                        "color": "#8b949e",
                        "borderTop": "1px solid #21262d",
                        "paddingTop": "14px",
                    },
                ),
            ],
        ),
        # Polling cada 10 segundos
        dcc.Interval(id="interval-component", interval=10 * 1000, n_intervals=0),
    ],
)


@app.callback(
    [Output("crypto-graph", "figure"), Output("stats-footer", "children")],
    [Input("crypto-selector", "value"), Input("interval-component", "n_intervals")],
)
def update_graph(selected_crypto, n):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
# 1. Traer los 500 registros MÁS RECIENTES (DESC)
        query = """
            SELECT fecha, precio_usd, volumen_24h, cambio_24h 
            FROM precios_crypto 
            WHERE criptomoneda = %s 
            ORDER BY fecha DESC 
            LIMIT 500
        """
        df = pd.read_sql(query, conn, params=[selected_crypto])
        conn.close()

        # 2. Reordenar de pasado a presente para que la gráfica avance hacia la derecha
        if not df.empty:
          df = df.sort_values("fecha").reset_index(drop=True)

          df["fecha"] = (pd.to_datetime(df["fecha"])
                         .dt.tz_localize("UTC")
                         .dt.tz_convert("America/Hermosillo")
          )
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161b22",
            plot_bgcolor="#161b22",
            font=dict(family="'Plus Jakarta Sans', sans-serif"),
            annotations=[
                {
                    "text": "Esperando lecturas de ingesta en la base de datos...",
                    "showarrow": False,
                    "font": {
                        "size": 15,
                        "color": "#8b949e",
                        "family": "'Plus Jakarta Sans', sans-serif",
                    },
                }
            ],
        )
        return fig, "Sin datos disponibles."

    theme = CRYPTO_THEME.get(selected_crypto, {"color": "#58a6ff", "label": selected_crypto})
    accent_color = theme["color"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["fecha"],
            y=df["precio_usd"],
            mode="lines",
            line=dict(color=accent_color, width=2.5),
            fill="tozeroy",
            fillcolor=f"rgba({int(accent_color[1:3], 16)}, {int(accent_color[3:5], 16)}, {int(accent_color[5:7], 16)}, 0.08)",
            hovertemplate="<b>Hora:</b> %{x|%H:%M:%S}<br><b>Precio:</b> $%{y:,.2f} USD<extra></extra>",
        )
    )

    # 3. Aplicar la misma fuente a los títulos y ejes del gráfico Plotly
    fig.update_layout(
        template="plotly_dark",
        font=dict(family="'Plus Jakarta Sans', sans-serif", color="#c9d1d9"),
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        margin=dict(l=40, r=30, t=35, b=40),
        title=dict(
            text=f"Histórico de Cotización: {theme['label']}",
            font=dict(size=17, color="#f0f6fc", family="'Plus Jakarta Sans', sans-serif"),
        ),
        xaxis=dict(
            gridcolor="#21262d",
            linecolor="#30363d",
            showgrid=True,
            tickfont=dict(family="'Plus Jakarta Sans', sans-serif", size=11),
        ),
        yaxis=dict(
            gridcolor="#21262d",
            linecolor="#30363d",
            showgrid=True,
            tickformat="$,.2f",
            tickfont=dict(family="'Plus Jakarta Sans', sans-serif", size=11),
        ),
    )

    precio_actual = df["precio_usd"].iloc[-1]
    ultima_fecha = pd.to_datetime(df["fecha"].iloc[-1]).strftime("%H:%M:%S")
    total_registros = len(df)

    footer_text = (
        f"Última consulta: {ultima_fecha}  •  "
        f"Precio Spot: ${precio_actual:,.2f} USD  •  "
        f"Muestras registradas: {total_registros}"
    )

    return fig, footer_text


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)