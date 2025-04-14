import pandas as pd
from pathlib import Path
import sys

def process_data(input_csv, output_parquet):
    """Processa dados de COVID-19 com tratamento robusto"""
    try:
        dtype = {
            'city': 'category',
            'city_ibge_code': 'string',
            'date': 'string',
            'estimated_population_2019': 'float32'
        }

        print("📊 Carregando dados...")
        df = pd.read_csv(input_csv, dtype=dtype, parse_dates=['date'])
        
        # Processamento principal
        df = df[df['place_type'] == 'city'].copy()
        df['new_confirmed'] = df['new_confirmed'].fillna(0).astype('int32')
        
        # Salvar dados processados
        output_path = Path(output_parquet)
        output_path.parent.mkdir(exist_ok=True)
        df.to_parquet(output_path, engine='pyarrow', compression='brotli')
        
        print(f"✅ Dados processados salvos em {output_path}")
        return True

    except Exception as e:
        print(f"❌ Erro: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    process_data(
        input_csv=base_dir / "data" / "caso_full.csv",
        output_parquet=base_dir / "output" / "processed_data.parquet"
    )