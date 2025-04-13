import pandas as pd
import numpy as np
from pathlib import Path
import sys

def process_data(input_csv, output_parquet):
    """Processa dados de COVID-19 com tratamento robusto de valores ausentes"""
    try:
        # Configuração de tipos para eficiência
        dtype = {
            'city': 'category',
            'city_ibge_code': 'str',
            'epidemiological_week': 'str',
            'estimated_population': 'float64',  # Alterado para float
            'estimated_population_2019': 'float64',  # Alterado para float
            'is_last': 'bool',
            'is_repeated': 'bool',
            'last_available_confirmed': 'int64',
            'last_available_confirmed_per_100k_inhabitants': 'float64',
            'last_available_death_rate': 'float64',
            'last_available_deaths': 'int64',
            'place_type': 'category',
            'state': 'category',
            'new_confirmed': 'float64',  # Alterado para float
            'new_deaths': 'float64'  # Alterado para float
        }

        # Carregar dados com tratamento especial para datas
        df = pd.read_csv(
            input_csv,
            sep=',',
            dtype=dtype,
            parse_dates=['date', 'last_available_date'],
            encoding='utf-8',
            na_values=['NA', 'NaN', 'null', '']
        )

        # Pré-processamento
        print("🔍 Processando dados...")
        
        # Tratamento de valores ausentes
        for col in ['new_confirmed', 'new_deaths']:
            df[col] = df[col].fillna(0).astype('int64')
        
        for col in ['estimated_population', 'estimated_population_2019']:
            df[col] = df[col].fillna(-1).astype('int64')  # -1 para população desconhecida

        # Filtrar apenas dados de cidades
        df = df[df['place_type'] == 'city'].copy()

        # Renomear colunas para português
        df = df.rename(columns={
            'city': 'Município',
            'state': 'UF',
            'date': 'Data',
            'epidemiological_week': 'Semana_epidemiologica',
            'new_confirmed': 'Novos_casos',
            'new_deaths': 'Novos_obitos',
            'last_available_confirmed': 'Casos_acumulados',
            'last_available_deaths': 'Obitos_acumulados',
            'estimated_population_2019': 'Populacao_estimada'
        })

        # Calcular campos derivados
        df['Taxa_mortalidade'] = np.where(
            df['Casos_acumulados'] > 0,
            df['Obitos_acumulados'] / df['Casos_acumulados'],
            0
        ).round(4)

        # Selecionar colunas relevantes
        cols_to_keep = [
            'Data', 'UF', 'Município', 'Semana_epidemiologica',
            'Novos_casos', 'Novos_obitos', 'Casos_acumulados',
            'Obitos_acumulados', 'Populacao_estimada', 'Taxa_mortalidade'
        ]
        df = df[cols_to_keep]

        # Salvar dados processados
        output_path = Path(output_parquet)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_parquet(
            output_path,
            engine='pyarrow',
            compression='snappy',
            index=False
        )
        
        print(f"✅ Dados processados salvos em {output_path}")
        print("\n📊 Estatísticas resumidas:")
        print(f"- Período: {df['Data'].min().date()} a {df['Data'].max().date()}")
        print(f"- Total municípios: {df['Município'].nunique()}")
        print(f"- Total casos acumulados: {df['Casos_acumulados'].max():,}")
        print(f"- Total óbitos acumulados: {df['Obitos_acumulados'].max():,}")

    except Exception as e:
        print(f"\n❌ Erro no processamento: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    try:
        base_dir = Path(__file__).parent.parent
        input_file = base_dir / "data" / "caso_full.csv"
        output_file = base_dir / "output" / "processed_data.parquet"
        
        print(f"📂 Processando arquivo: {input_file}")
        process_data(input_file, output_file)
        
    except Exception as e:
        print(f"❌ Erro fatal: {str(e)}", file=sys.stderr)
        sys.exit(1)