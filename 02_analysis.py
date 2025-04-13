import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json

def analyze_covid_data(parquet_file):
    """Analisa dados de COVID-19 com tratamento robusto de erros"""
    try:
        df = pd.read_parquet(parquet_file)
        
        # Verificar colunas essenciais
        required_cols = ['Data', 'UF', 'Município', 'Casos_acumulados', 'Obitos_acumulados']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Colunas obrigatórias ausentes: {missing_cols}")

        # Converter groupby para observed=True (elimina warnings)
        groupby_params = {'observed': True}

        # Análise consolidada (com tratamento especial para dicts)
        analysis = {
            'periodo': {
                'inicio': df['Data'].min().strftime('%Y-%m-%d'),
                'fim': df['Data'].max().strftime('%Y-%m-%d')
            },
            'cobertura': {
                'estados': df['UF'].nunique(),
                'municipios': df['Município'].nunique()
            },
            'totais': {
                'casos': int(df['Casos_acumulados'].max()),
                'obitos': int(df['Obitos_acumulados'].max())
            },
            'top_municipios': {
                'casos': df.groupby(['UF', 'Município'], **groupby_params)['Casos_acumulados']
                         .max().nlargest(5).reset_index().to_dict('records'),
                'obitos': df.groupby(['UF', 'Município'], **groupby_params)['Obitos_acumulados']
                          .max().nlargest(5).reset_index().to_dict('records')
            },
            'metricas': {
                'taxa_mortalidade': round(df['Obitos_acumulados'].sum() / df['Casos_acumulados'].sum(), 4),
                'media_movel_casos': round(df['Novos_casos'].rolling(7).mean().iloc[-1], 1),
                'media_movel_obitos': round(df['Novos_obitos'].rolling(7).mean().iloc[-1], 1)
            }
        }

        return analysis

    except Exception as e:
        print(f"Erro na análise: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    try:
        base_dir = Path(__file__).parent.parent
        input_file = base_dir / "output" / "processed_data.parquet"
        
        if not input_file.exists():
            print(f"❌ Arquivo não encontrado: {input_file}", file=sys.stderr)
            print("Execute primeiro o script 01_data_processing.py", file=sys.stderr)
            sys.exit(1)
        
        analysis = analyze_covid_data(input_file)
        
        # Converter para JSON seguro
        def safe_serialize(obj):
            if isinstance(obj, (np.integer, np.floating)):
                return int(obj) if isinstance(obj, np.integer) else float(obj)
            raise TypeError(f"Type {type(obj)} not serializable")

        print("\n🔬 Análise COVID-19 - Resultados:")
        print(json.dumps(analysis, indent=2, default=safe_serialize, ensure_ascii=False))
        
        # Salvar análise
        output_file = base_dir / "output" / "analysis_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=safe_serialize, ensure_ascii=False)
        print(f"\n💾 Análise salva em: {output_file}")
        
    except Exception as e:
        print(f"❌ Erro fatal: {str(e)}", file=sys.stderr)
        sys.exit(1)