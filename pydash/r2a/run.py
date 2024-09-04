import json
from pydash.dash_client import DashClient  # Supondo que você tenha um cliente DASH disponível
from pydash.r2a.probe_and_adapt import ProbeAndAdapt

# Carregue as configurações do arquivo JSON
with open('C:/Users/giuli/OneDrive/Área de Trabalho/Unb/2024.1/Redes/Trabalho/Programação/pydash/dash_client.json', 'r') as f:
    config = json.load(f)

# Inicialize o algoritmo de adaptação com base na configuração
r2a_algorithm = None
if config["r2a_algorithm"] == "probe_and_adapt":
    r2a_algorithm = ProbeAndAdapt("probe_and_adapt_id")

# Crie e inicialize o cliente DASH
client = DashClient(
    buffering_until=config["buffering_until"],
    max_buffer_size=config["max_buffer_size"],
    playbak_step=config["playbak_step"],
    traffic_shaping_profile_interval=config["traffic_shaping_profile_interval"],
    traffic_shaping_profile_sequence=config["traffic_shaping_profile_sequence"],
    traffic_shaping_seed=config["traffic_shaping_seed"],
    url_mpd=config["url_mpd"],
    r2a_algorithm=r2a_algorithm
)

# Execute o cliente
client.run()
