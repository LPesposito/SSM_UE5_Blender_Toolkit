import os
import zipfile
import re

def get_version():
    """Extrai a string de versão do blender_manifest.toml"""
    manifest_path = os.path.join("scene_staticmesh_ue5_toolkit", "blender_manifest.toml")
    if not os.path.exists(manifest_path):
        print("Aviso: blender_manifest.toml não encontrado. Usando versão 'unknown'.")
        return "unknown"
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()
        # Procura por version = "x.x.x"
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(1)
    return "0.0.0"

def pack_addon():
    # Nome da pasta que contém o código do addon
    addon_folder = "scene_staticmesh_ue5_toolkit"
    version = get_version()
    output_filename = f"SSM_UE5_Blender_Toolkit_v{version}.zip"
    
    # Caminhos baseados na localização deste script
    root_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(root_dir, addon_folder)
    output_path = os.path.join(root_dir, output_filename)

    print(f"--- Iniciando Empacotamento v{version} ---")

    if not os.path.exists(source_path):
        print(f"ERRO: Pasta do addon '{addon_folder}' não encontrada em {root_dir}")
        return

    # Arquivos extras na raiz do dev que devem ir para a raiz do ZIP
    extra_files = ["README.md", "README.pt-br.md"]

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Adiciona READMEs
        for ef in extra_files:
            ef_path = os.path.join(root_dir, ef)
            if os.path.exists(ef_path):
                zipf.write(ef_path, ef)
                print(f"  [+] {ef}")

        for root, dirs, files in os.walk(source_path):
            # Remove pastas de cache da lista para não entrar no loop
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")
            
            for file in files:
                # Filtro de arquivos indesejados
                if file.endswith(('.pyc', '.pyo', '.DS_Store', '.git', '.gitignore')):
                    continue
                
                file_full_path = os.path.join(root, file)
                # O caminho dentro do zip deve incluir a pasta raiz do addon
                arcname = os.path.relpath(file_full_path, root_dir)
                zipf.write(file_full_path, arcname)
                print(f"  [+] {arcname}")

    print(f"\nSucesso! Arquivo gerado: {output_filename}")

if __name__ == "__main__":
    pack_addon()