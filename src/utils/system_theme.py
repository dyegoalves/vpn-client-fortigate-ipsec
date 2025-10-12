import subprocess
import re

def get_system_color_scheme() -> str:
    """
    Detecta o esquema de cores do sistema (claro/escuro) usando gdbus.
    Retorna 'Dark' ou 'Light'.
    """
    command = [
        "gdbus",
        "call",
        "--session",
        "--dest",
        "org.freedesktop.portal.Desktop",
        "--object-path",
        "/org/freedesktop/portal/desktop",
        "--method",
        "org.freedesktop.portal.Settings.Read",
        "org.freedesktop.appearance",
        "color-scheme",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        # Espera uma saída como (<<uint32 1>>,) ou (<<uint32 0>>,) ou similar
        match = re.search(r'uint32 (\d+)', output)
        if match:
            value = int(match.group(1))
            # Assumindo 1 para Dark e 0 para Light com base em convenções comuns
            # e na sua saída de exemplo (<<uint32 1>>,) para tema escuro.
            return "Dark" if value == 1 else "Light"
        else:
            print(f"[WARNING] Não foi possível analisar a saída do gdbus: {output}")
            return "Light" # Retorno padrão para segurança
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Erro ao chamar gdbus: {e.stderr}")
        return "Light" # Retorno padrão em caso de erro
    except FileNotFoundError:
        print("[ERROR] Comando gdbus não encontrado. Certifique-se de que está instalado.")
        return "Light" # Retorno padrão se gdbus não estiver disponível

if __name__ == "__main__":
    print(f"Esquema de cores do sistema: {get_system_color_scheme()}")