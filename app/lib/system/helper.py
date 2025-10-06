import sys
import subprocess

# Importar usando imports absolutos ou relativos dependendo do contexto
try:
    from ..config.config import VPN_NAME
except ImportError:
    # Quando rodando em modo desenvolvimento com PYTHONPATH apropriado
    from config.config import VPN_NAME

# ==============================================================================
# LÓGICA DO HELPER (EXECUTADO COMO ROOT)
# ==============================================================================
def run_helper_mode():
    """Lida com os comandos recebidos do processo principal da GUI."""
    def run_root_command(args):
        subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

    def get_status():
        result = subprocess.run(["ipsec", "statusall"], stdout=subprocess.PIPE, text=True, check=False)
        output = result.stdout.strip()
        if "ESTABLISHED" in output and VPN_NAME in output:
            return "STATUS: connected"
        return "STATUS: disconnected"

    # Loop para ler comandos do stdin
    for line in sys.stdin:
        command = line.strip()
        if command == "start":
            run_root_command(["systemctl", "start", "ipsec"])
            run_root_command(["ipsec", "up", VPN_NAME])
        elif command == "stop":
            run_root_command(["ipsec", "down", VPN_NAME])
        elif command == "restart":
            run_root_command(["systemctl", "restart", "ipsec"])
            run_root_command(["ipsec", "up", VPN_NAME])
        
        if command in ["start", "stop", "restart", "status"]:
            print(get_status())
        elif command == "quit":
            break
        else:
            print(f"ERROR: Unknown command '{command}'")
        
        # Garante que a saída seja enviada imediatamente
        sys.stdout.flush()
