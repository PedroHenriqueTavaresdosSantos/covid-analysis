import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys
import json
import numpy as np

def save_interactive_html(fig, filename):
    """Salva gráfico como HTML interativo"""
    try:
        fig.write_html(
            filename,
            full_html=True,
            include_plotlyjs='cdn',
            config={'responsive': True}
        )
        print(f"✅ HTML salvo: {filename}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar HTML: {str(e)}")
        return False

def generate_visualizations(parquet_path, output_dir):
    try:
        # Carregar dados processados
        df = pd.read_parquet(parquet_path)
        
        # 1. Gráfico de Evolução Temporal
        daily_data = df.groupby('date').agg({
            'new_confirmed': 'sum',
            'new_deaths': 'sum'
        }).rolling(7).mean().reset_index()
        
        fig_temporal = go.Figure()
        fig_temporal.add_trace(go.Scatter(
            x=daily_data['date'], y=daily_data['new_confirmed'],
            name='Casos (média 7 dias)', line=dict(color='#1f77b4')))
        fig_temporal.add_trace(go.Scatter(
            x=daily_data['date'], y=daily_data['new_deaths'],
            name='Óbitos (média 7 dias)', line=dict(color='#d62728')))
        
        fig_temporal.update_layout(
            title='Evolução Temporal COVID-19',
            xaxis_title='Data',
            yaxis_title='Número de Casos/Óbitos'
        )

        # 2. Top 15 Municípios
        top_cities = df.groupby(['state', 'city']).agg({
            'last_available_deaths': 'max',
            'estimated_population_2019': 'first'
        }).nlargest(15, 'last_available_deaths').reset_index()
        
        fig_cities = px.bar(
            top_cities,
            x='last_available_deaths',
            y='city',
            color='state',
            orientation='h',
            title='Top 15 Municípios por Óbitos'
        )

        # 3. Combinar gráficos em um dashboard
        dashboard = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Evolução Temporal", "Top Municípios"),
            vertical_spacing=0.2
        )
        
        for trace in fig_temporal.data:
            dashboard.add_trace(trace, row=1, col=1)
            
        for trace in fig_cities.data:
            dashboard.add_trace(trace, row=2, col=1)
            
        dashboard.update_layout(height=900, showlegend=True)

        # Salvar dashboard completo
        output_path = Path(output_dir) / "visuals"
        output_path.mkdir(parents=True, exist_ok=True)
        
        save_interactive_html(dashboard, output_path / "dashboard.html")
        
        return True

    except Exception as e:
        print(f"❌ Erro: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    generate_visualizations(
        parquet_path=base_dir / "output" / "processed_data.parquet",
        output_dir=base_dir / "output"
    )