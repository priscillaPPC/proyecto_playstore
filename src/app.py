import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from database import obtener_conexion

# 1. Inicializamos la aplicación web de Dash
app = dash.Dash(__name__, title="Play Store Analytics")

def cargar_datos_desde_sql():
    """Conecta a la base de datos SQL que llenamos con el ETL y extrae los datos."""
    conn = obtener_conexion()
    # Leemos la tabla. Si hay un error (ej. tabla no existe), devolvemos un DataFrame vacío
    try:
        df = pd.read_sql_query("SELECT * FROM aplicaciones", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

# Cargamos los datos limpios de la base de datos
df_apps = cargar_datos_desde_sql()

# --- PROGRAMACIÓN DEFENSIVA ---
# Si el DataFrame está vacío, asignamos valores por defecto para que la app no colapse
if df_apps.empty:
    min_size = 0
    max_size = 100
    categorias_disponibles = ['Sin Datos']
else:
    min_size = int(df_apps['size'].min())
    max_size = int(df_apps['size'].max())
    categorias_disponibles = sorted(df_apps['category'].unique())

# 2. DISEÑO VISUAL DE LA PÁGINA 
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': '#f4f6f9'}, children=[
    
    # Título principal llamativo
    html.Div(style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#2c3e50', 'color': 'white', 'borderRadius': '8px'}, children=[
        html.H1("Google Play Store - Sistema de Soporte de Decisiones", style={'margin': '0'}),
        html.P("Solución Operativa Automatizada | Priscilla Pereira & Gabriel Palma", style={'margin': '5px 0 0 0'})
    ]),
    
    html.Br(),

    # =========================================================================
    # NUEVO: TARJETAS DE KPI (Scorecards)
    # =========================================================================
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px', 'gap': '15px'}, children=[
        
        # Tarjeta 1: Total Apps
        html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0px 2px 4px rgba(0,0,0,0.05)', 'textAlign': 'center'}, children=[
            html.H6("Total Aplicaciones", style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '14px'}),
            html.H2(id="kpi-total-apps", style={'margin': '5px 0 0 0', 'color': '#2c3e50', 'fontWeight': 'bold'})
        ]),
        
        # Tarjeta 2: Rating Promedio
        html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0px 2px 4px rgba(0,0,0,0.05)', 'textAlign': 'center'}, children=[
            html.H6("Rating Promedio", style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '14px'}),
            html.H2(id="kpi-avg-rating", style={'margin': '5px 0 0 0', 'color': '#f39c12', 'fontWeight': 'bold'})
        ]),
        
        # Tarjeta 3: Descargas Totales
        html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0px 2px 4px rgba(0,0,0,0.05)', 'textAlign': 'center'}, children=[
            html.H6("Descargas Totales", style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '14px'}),
            html.H2(id="kpi-total-installs", style={'margin': '5px 0 0 0', 'color': '#27ae60', 'fontWeight': 'bold'})
        ]),

        # Tarjeta 4: % Apps Populares
        html.Div(style={'flex': '1', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0px 2px 4px rgba(0,0,0,0.05)', 'textAlign': 'center'}, children=[
            html.H6("Tasa de Popularidad", style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '14px'}),
            html.H2(id="kpi-pct-popular", style={'margin': '5px 0 0 0', 'color': '#2980b9', 'fontWeight': 'bold'})
        ])
    ]),
    # =========================================================================
    
    # Sistema de Pestañas
    dcc.Tabs(id="pestanas-audiencia", value='tab-ejecutivo', children=[
        
        # --- PESTAÑA 1: VISTA DE NEGOCIO / EJECUTIVA ---
        dcc.Tab(label='📈 Vista Ejecutiva (Valor de Negocio)', value='tab-ejecutivo', children=[
            html.Div(style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '0 0 8px 8px', 'boxShadow': '0px 4px 6px rgba(0,0,0,0.1)'}, children=[
                html.H3("Métricas Estratégicas de Mercado", style={'color': '#2c3e50'}),
                html.P("Filtro diseñado para Directores de Producto e Inversores que buscan nichos rentables."),
                
                # Menú desplegable interactivo
                html.Label("Selecciona una Categoría de Apps:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='selector-categoria-ejecutivo',
                    options=[{'label': cat, 'value': cat} for cat in categorias_disponibles],
                    value=categorias_disponibles[0] if categorias_disponibles else None, 
                    clearable=False
                ),
                
                html.Br(),
                # Aquí se dibujará el gráfico dinámicamente
                dcc.Graph(id='grafico-dinamico-ejecutivo')
            ])
        ]),
        
        # --- PESTAÑA 2: VISTA TÉCNICA (Analistas / Científicos de Datos) ---
        dcc.Tab(label='🔬 Vista Técnica (Espacio de Características)', value='tab-tecnico', children=[
            html.Div(style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '0 0 8px 8px', 'boxShadow': '0px 4px 6px rgba(0,0,0,0.1)'}, children=[
                html.H3("Distribución y Densidad de Variables", style={'color': '#2c3e50'}),
                html.P("Herramienta para ingenieros de software que evalúa el peso físico de los archivos frente a las valoraciones."),
                
                # Barra deslizante interactiva
                html.Label("Filtrar por Tamaño Máximo Permitido (MB):", style={'fontWeight': 'bold'}),
                dcc.Slider(
                    id='slider-tamano-tecnico',
                    min=min_size,
                    max=max_size,
                    value=max_size,
                    marks={i: f'{i}MB' for i in range(min_size, max_size+1, 20)} if max_size > min_size else {0: '0MB'},
                    step=5
                ),
                
                html.Br(),
                # Aquí se dibujará el gráfico técnico dinámicamente
                dcc.Graph(id='grafico-dinamico-tecnico')
            ])
        ])
    ])
])

# 3. INTERACTIVIDAD (Callbacks: Conectan los filtros con los gráficos y KPIs)

# Lógica interactiva para la pestaña Ejecutiva (Gráfico + 4 KPIs)
@app.callback(
    [Output('grafico-dinamico-ejecutivo', 'figure'),
     Output('kpi-total-apps', 'children'),
     Output('kpi-avg-rating', 'children'),
     Output('kpi-total-installs', 'children'),
     Output('kpi-pct-popular', 'children')],
    Input('selector-categoria-ejecutivo', 'value')
)
def actualizar_panel_ejecutivo(categoria_seleccionada):
    if df_apps.empty or not categoria_seleccionada:
        return px.bar(title="Sin datos disponibles"), "0", "0 ⭐", "0", "0%"

    # Filtramos la base de datos
    df_filtrado = df_apps[df_apps['category'] == categoria_seleccionada]
    
    # --- CÁLCULO DE KPIs ---
    total_apps = len(df_filtrado)
    avg_rating = round(df_filtrado['rating'].mean(), 2) if total_apps > 0 else 0
    total_installs = df_filtrado['installs'].sum()
    
    pct_popular = 0
    if total_apps > 0:
        pct_popular = round((df_filtrado['is_popular'].sum() / total_apps) * 100, 1)
    
    # Formatear números grandes (Descargas)
    if total_installs >= 1_000_000_000:
        installs_str = f"{round(total_installs / 1_000_000_000, 1)}B"
    elif total_installs >= 1_000_000:
        installs_str = f"{round(total_installs / 1_000_000, 1)}M"
    else:
        installs_str = f"{total_installs:,}"

    # --- CREACIÓN DEL GRÁFICO ---
    top_apps = df_filtrado.sort_values(by="reviews", ascending=False).head(10)
    fig = px.bar(
        top_apps, 
        x="app", 
        y="reviews", 
        color="rating",
        title=f"Top 10 Apps en {categoria_seleccionada} por Reseñas",
        labels={"app": "Nombre de la App", "reviews": "Número de Reseñas", "rating": "Calificación"},
        color_continuous_scale="Viridis"
    )
    fig.update_layout(xaxis_tickangle=-45)
    
    # Devolvemos el gráfico y los 4 valores de texto para las tarjetas
    return fig, f"{total_apps:,}", f"{avg_rating} ⭐", installs_str, f"{pct_popular}%"

# Lógica interactiva para la pestaña Técnica
@app.callback(
    Output('grafico-dinamico-tecnico', 'figure'),
    Input('slider-tamano-tecnico', 'value')
)
def actualizar_grafico_tecnico(tamano_maximo):
    if df_apps.empty:
        return px.scatter(title="Sin datos disponibles")

    # Filtramos las apps
    df_filtrado = df_apps[df_apps['size'] <= tamano_maximo]
    df_muestra = df_filtrado.sample(min(1000, len(df_filtrado)))
    
    fig = px.scatter(
        df_muestra,
        x="size",
        y="rating",
        color="is_popular",
        hover_name="app",
        title=f"Distribución Operativa de Apps (Filtro: menor a {tamano_maximo} MB)",
        labels={"size": "Tamaño (MB)", "rating": "Calificación", "is_popular": "Popularidad (1=Sí)"},
        color_continuous_scale=["#e74c3c", "#2ecc71"] 
    )
    return fig

# 4. Encendemos el servidor web local
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)