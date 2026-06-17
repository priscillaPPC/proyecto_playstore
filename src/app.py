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
    df = pd.read_sql_query("SELECT * FROM aplicaciones", conn)
    conn.close()
    return df

# Cargamos los datos limpios de la base de datos
df_apps = cargar_datos_desde_sql()

# 2. DISEÑO VISUAL DE LA PÁGINA 
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': '#f4f6f9'}, children=[
    
    # Título principal llamativo
    html.Div(style={'textAlign': 'center', 'padding': '15px', 'backgroundColor': '#2c3e50', 'color': 'white', 'borderRadius': '8px'}, children=[
        html.H1("Google Play Store - Sistema de Soporte de Decisiones", style={'margin': '0'}),
        html.P("Solución Operativa Automatizada | Priscilla Pereira & Gabriel Palma", style={'margin': '5px 0 0 0'})
    ]),
    
    html.Br(),
    
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
                    options=[{'label': cat, 'value': cat} for cat in sorted(df_apps['category'].unique())],
                    value='GAME', # Valor inicial por defecto
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
                    min=int(df_apps['size'].min()),
                    max=int(df_apps['size'].max()),
                    value=int(df_apps['size'].max()),
                    marks={i: f'{i}MB' for i in range(0, int(df_apps['size'].max())+1, 20)},
                    step=5
                ),
                
                html.Br(),
                # Aquí se dibujará el gráfico técnico dinámicamente
                dcc.Graph(id='grafico-dinamico-tecnico')
            ])
        ])
    ])
])

# 3. INTERACTIVIDAD (Callbacks: Conectan los filtros con los gráficos)

# Lógica interactiva para la pestaña Ejecutiva
@app.callback(
    Output('grafico-dinamico-ejecutivo', 'figure'),
    Input('selector-categoria-ejecutivo', 'value')
)
def actualizar_grafico_ejecutivo(categoria_seleccionada):
    # Filtramos la base de datos por la categoría que el usuario elija en la web
    df_filtrado = df_apps[df_apps['category'] == categoria_seleccionada]
    
    # Tomamos las 10 apps con más opiniones para ver las dominantes
    top_apps = df_filtrado.sort_values(by="reviews", ascending=False).head(10)
    
    # Creamos un gráfico interactivo de barras con Plotly Express
    fig = px.bar(
        top_apps, 
        x="app", 
        y="reviews", 
        color="rating",
        title=f"Top 10 Aplicaciones Líderes en {categoria_seleccionada} por Reseñas",
        labels={"app": "Nombre de la App", "reviews": "Número de Reseñas", "rating": "Calificación"},
        color_continuous_scale="Viridis"
    )
    fig.update_layout(xaxis_tickangle=-45) # Inclinar nombres para que se lean bien
    return fig

# Lógica interactiva para la pestaña Técnica
@app.callback(
    Output('grafico-dinamico-tecnico', 'figure'),
    Input('slider-tamano-tecnico', 'value')
)
def actualizar_grafico_tecnico(tamano_maximo):
    # Filtramos las apps que pesen menos o igual que lo que diga la barra deslizante
    df_filtrado = df_apps[df_apps['size'] <= tamano_maximo]
    
    # Tomamos una muestra aleatoria de máximo 1000 registros para que el gráfico cargue rápido
    df_muestra = df_filtrado.sample(min(1000, len(df_filtrado)))
    
    # Creamos un gráfico de dispersión (Scatter Plot) interactivo
    fig = px.scatter(
        df_muestra,
        x="size",
        y="rating",
        color="is_popular",
        hover_name="app",
        title=f"Distribución Operativa de Apps (Filtro: menor a {tamano_maximo} MB)",
        labels={"size": "Tamaño del Archivo (MB)", "rating": "Calificación (Rating)", "is_popular": "Popularidad (1=Sí)"},
        color_continuous_scale=["#e74c3c", "#2ecc71"] # Rojo para no populares, Verde para populares
    )
    return fig

# 4. Encendemos el servidor web local
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)