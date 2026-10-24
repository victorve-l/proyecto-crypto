import os
import logging
from datetime import datetime
import pandas as pd
import mysql.connector
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

app = Dash(__name__)
server = app.server
app.title = "Crypto Monitor Live"

app.layout = html.Div([
    html.H1("Monitor de Criptomonedas en Vivo", style={"textAlign": "center", "color": "#1f2937"}),
    html.P("Docker + Dash + MySQL + CoinGecko API · Actualización automática", style={"textAlign": "center", "color": "#4b5563"}),
    
    html.Div([
        html.Label("Selecciona la Criptomoneda:", style={"fontWeight": "bold", "marginBottom": "5px"}),
        dcc.Dropdown(
            id="selector-crypto",
            options=[
                {"label": "Bitcoin (BTC)", "value": "bitcoin"},
                {"label": "Ethereum (ETH)", "value": "ethereum"},
                {"label": "Solana (SOL)", "value": "solana"}
            ],
            value="bitcoin",
            clearable=False
        )
    ], style={"width": "50%", "margin": "0 auto 20px auto"}),

    dcc.Graph(id="grafica-precio"),
    html.P(id="estado-consulta", style={"textAlign": "center", "fontSize": "14px", "color": "#6b7280"}),
    
    # Consulta la base de datos automáticamente cada 10 segundos
    dcc.Interval(id="intervalo-reloj", interval=10_000, n_intervals=0)
], style={"maxWidth": "1000px", "margin": "30px auto", "padding": "20px", "fontFamily": "Segoe UI, sans-serif"})


def leer_datos(criptomoneda):
    conexion = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "mysql"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_USER", "dash_user"),
        password=os.environ.get("DB_PASSWORD", "DashDemo2026_local"),
        database=os.environ.get("DB_NAME", "agricultura"),
        connection_timeout=5
    )
    try:
        with conexion.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT fecha, precio_usd, volumen_24h, cambio_24h
                FROM precios_crypto
                WHERE criptomoneda = %s
                ORDER BY fecha ASC LIMIT 500
            """, (criptomoneda,))
            registros = cursor.fetchall()
    finally:
        conexion.close()

    if not registros:
        return pd.DataFrame()
    return pd.DataFrame(registros)


@app.callback(
    Output("grafica-precio", "figure"),
    Output("estado-consulta", "children"),
    Input("selector-crypto", "value"),
    Input("intervalo-reloj", "n_intervals")
)
def actualizar_grafica(crypto_seleccionada, _):
    try:
        df = leer_datos(crypto_seleccionada)
    except Exception as e:
        logging.exception("Fallo al conectar con MySQL")
        return px.line(title="Conectando con la base de datos..."), "Error de conexión."

    if df.empty:
        return px.line(title="Sin datos aún para esta criptomoneda"), "Esperando primer registro..."

    fig = px.line(
        df,
        x="fecha",
        y="precio_usd",
        markers=True,
        title=f"Histórico de Precio - {crypto_seleccionada.upper()} (USD)",
        labels={"fecha": "Hora de Registro", "precio_usd": "Precio (USD)"}
    )
    fig.update_layout(template="plotly_white")
    
    ultimo_precio = df["precio_usd"].iloc[-1]
    info = f"Última consulta: {datetime.now():%H:%M:%S} | Precio actual: ${ultimo_precio:,.2f} USD | Total de registros: {len(df)}"
    return fig, info


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)