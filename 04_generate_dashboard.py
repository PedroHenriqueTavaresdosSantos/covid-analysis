from dash import Dash, html, dcc
from pathlib import Path
from datetime import datetime
import base64

def create_dashboard():
    app = Dash(__name__)
    
    # Caminho absoluto para os gráficos
    base_path = Path(__file__).parent.parent / "output" / "visuals"
    
    # Função para carregar gráficos como iframe
    def load_graph_iframe(filename):
        file_path = base_path / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Carregar os gráficos diretamente
    mapa_html = load_graph_iframe('mapa_uf.html')
    evolucao_html = load_graph_iframe('evolucao_temporal.html')
    top_html = load_graph_iframe('top_municipios.html')

    # Layout do dashboard
    app.layout = html.Div([
        html.H1("Dashboard COVID-19 Brasil", style={'textAlign': 'center', 'color': '#1a3263'}),
        
        # Gráfico 1: Mapa
        html.Div([
            html.H3("Mapa de Óbitos por 100k Habitantes", style={'textAlign': 'center'}),
            html.Iframe(
                srcDoc=mapa_html,
                style={
                    'width': '100%',
                    'height': '600px',
                    'border': 'none'
                }
            )
        ], style={
            'margin': '20px',
            'border': '1px solid #ddd',
            'borderRadius': '5px',
            'padding': '15px'
        }),
        
        # Gráfico 2: Evolução Temporal
        html.Div([
            html.H3("Evolução Temporal", style={'textAlign': 'center'}),
            html.Iframe(
                srcDoc=evolucao_html,
                style={
                    'width': '100%',
                    'height': '500px',
                    'border': 'none'
                }
            )
        ], style={
            'margin': '20px',
            'border': '1px solid #ddd',
            'borderRadius': '5px',
            'padding': '15px'
        }),
        
        # Gráfico 3: Top Municípios
        html.Div([
            html.H3("Top Municípios por Óbitos", style={'textAlign': 'center'}),
            html.Iframe(
                srcDoc=top_html,
                style={
                    'width': '100%',
                    'height': '500px',
                    'border': 'none'
                }
            )
        ], style={
            'margin': '20px',
            'border': '1px solid #ddd',
            'borderRadius': '5px',
            'padding': '15px'
        }),
        
        # Rodapé
        html.Footer(
            [
                html.P(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
                html.P("Dados: Ministério da Saúde", style={'fontStyle': 'italic'})
            ],
            style={
                'textAlign': 'center',
                'marginTop': '30px',
                'padding': '20px',
                'backgroundColor': '#f8f9fa'
            }
        )
    ], style={'fontFamily': 'Arial, sans-serif'})

    return app

if __name__ == "__main__":
    # Verificar se os arquivos existem
    required_files = [
        "mapa_uf.html",
        "evolucao_temporal.html",
        "top_municipios.html"
    ]
    
    base_path = Path(__file__).parent.parent / "output" / "visuals"
    missing_files = [f for f in required_files if not (base_path / f).exists()]
    
    if missing_files:
        print(f"❌ Arquivos não encontrados: {missing_files}")
        print("Execute primeiro o script 03_generate_visualizations.py")
        exit(1)
    
    app = create_dashboard()
    app.run(debug=True, port=8050)