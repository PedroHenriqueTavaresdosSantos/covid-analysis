import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

def generate_visualizations(parquet_path, output_dir):
    """Gera visualizações corrigidas para dados COVID-19 Brasil"""
    try:
        # Carregar dados
        df = pd.read_parquet(parquet_path)
        
        # 1. Pré-processamento dos dados para o mapa
        uf_data = df.groupby(['UF', 'Semana_epidemiologica'], observed=True).agg({
            'Obitos_acumulados': 'max',
            'Populacao_estimada': 'first'
        }).reset_index()
        
        # Remover linhas com valores NaN
        uf_data = uf_data.dropna(subset=['Populacao_estimada', 'Obitos_acumulados'])
        
        # Calcular óbitos por 100k habitantes
        uf_data['Obitos_por_100k'] = (uf_data['Obitos_acumulados'] / 
                                     (uf_data['Populacao_estimada'] / 100000)).round(1)
        
        # 2. Mapa de calor corrigido
        fig_map = px.choropleth(
            uf_data,
            locations='UF',
            color='Obitos_por_100k',
            animation_frame='Semana_epidemiologica',
            scope='south america',
            title='Óbitos por 100k habitantes por UF',
            color_continuous_scale='OrRd',
            range_color=(0, uf_data['Obitos_por_100k'].quantile(0.9)),
            locationmode='ISO-3',
            labels={'Obitos_por_100k': 'Óbitos/100k hab.'}
        )
        
        # Ajustar o layout do mapa para focar no Brasil
        fig_map.update_geos(
            visible=False,
            resolution=50,
            showcountries=True,
            countrycolor="Black",
            showsubunits=True,
            subunitcolor="Blue"
        )
        
        # 3. Evolução temporal (média móvel 7 dias)
        daily_data = df.groupby('Data').agg({
            'Novos_casos': 'sum',
            'Novos_obitos': 'sum'
        }).rolling(7).mean().reset_index()
        
        fig_temporal = make_subplots(specs=[[{"secondary_y": False}]])
        fig_temporal.add_trace(
            go.Scatter(
                x=daily_data['Data'],
                y=daily_data['Novos_casos'],
                name='Casos (média 7 dias)',
                line=dict(color='#1f77b4'))
        )
        fig_temporal.add_trace(
            go.Scatter(
                x=daily_data['Data'],
                y=daily_data['Novos_obitos'],
                name='Óbitos (média 7 dias)',
                line=dict(color='#d62728'))
        )
        fig_temporal.update_layout(
            title='Evolução Temporal - Média Móvel 7 Dias',
            xaxis_title='Data',
            yaxis_title='Número de Casos/Óbitos',
            hovermode='x unified'
        )
        
        # 4. Top municípios
        top_cities = df.groupby(['UF', 'Município'], observed=True).agg({
            'Obitos_acumulados': 'max',
            'Populacao_estimada': 'first'
        }).nlargest(15, 'Obitos_acumulados').reset_index()
        
        top_cities['Obitos_por_100k'] = (top_cities['Obitos_acumulados'] / 
                                       (top_cities['Populacao_estimada'] / 100000)).round(1)
        
        fig_top = px.bar(
            top_cities,
            x='Município',
            y='Obitos_acumulados',
            color='UF',
            title='Top 15 Municípios por Óbitos Acumulados',
            hover_data=['Obitos_por_100k', 'Populacao_estimada'],
            labels={
                'Obitos_acumulados': 'Óbitos totais',
                'Obitos_por_100k': 'Óbitos por 100k hab.'
            }
        )
        
        # Salvar visualizações
        output_path = Path(output_dir) / "visuals"
        output_path.mkdir(parents=True, exist_ok=True)
        
        fig_map.write_html(output_path / 'mapa_uf.html')
        fig_temporal.write_html(output_path / 'evolucao_temporal.html')
        fig_top.write_html(output_path / 'top_municipios.html')
        
        print(f"✅ Visualizações salvas em: {output_path}")

    except Exception as e:
        print(f"❌ Erro na geração de visualizações: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    try:
        base_dir = Path(__file__).parent.parent
        input_file = base_dir / "output" / "processed_data.parquet"
        output_dir = base_dir / "output"
        
        if not input_file.exists():
            print(f"❌ Arquivo de entrada não encontrado: {input_file}", file=sys.stderr)
            sys.exit(1)
            
        generate_visualizations(input_file, output_dir)
        
    except Exception as e:
        print(f"❌ Erro fatal: {str(e)}", file=sys.stderr)
        sys.exit(1)