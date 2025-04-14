from pathlib import Path
import shutil

def create_portable_dashboard(output_dir):
    """Cria versão portátil do dashboard"""
    try:
        visuals_dir = Path(output_dir) / "visuals"
        dashboard_file = visuals_dir / "dashboard.html"
        
        if not dashboard_file.exists():
            raise FileNotFoundError("Arquivo dashboard.html não encontrado")
        
        # Criar pacote portátil
        portable_dir = Path(output_dir) / "portable_dashboard"
        portable_dir.mkdir(exist_ok=True)
        
        # Copiar arquivos necessários
        shutil.copy2(dashboard_file, portable_dir / "covid_dashboard.html")
        
        print(f"✅ Dashboard portátil criado em: {portable_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar versão portátil: {str(e)}")
        return False

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    create_portable_dashboard(base_dir / "output")