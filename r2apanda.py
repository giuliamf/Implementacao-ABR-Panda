"""
CIC0124 - Redes de Computadores - 2024.1
Projeto Final - Algoritmo PANDA
Autores:
    Giulia Moura Ferreira, 200018795
    João Vitor Vieira, 221022023

https://github.com/giuliamf/Implementacao-ABR-Panda
"""

from r2a.ir2a import IR2A
import time
import os
from pydash.player.parser import parse_mpd

import requests
import psutil
from xml.etree import ElementTree as ET
import matplotlib.pyplot as plt


# Função responsável por salvar gráficos de dados como throughput e bitrate.
# Ela cria um gráfico com base nos dados recebidos e salva na pasta ./results.
def save_graph(x_data, y_data, graph_name):
    print(f"Salvando gráfico: {graph_name}")
    print(f"x_data: {x_data}")
    print(f"y_data: {y_data}")

    if len(x_data) == 0 or len(y_data) == 0:
        # Se não houver dados suficientes, o gráfico não será criado.
        print(f"Nenhum dado disponível para {graph_name}, gráfico não será criado.")
        return

    if len(y_data) < len(x_data):
        # Se houver menos dados em y_data do que x_data, preenche com o último valor disponível.
        y_data.extend([y_data[-1] if y_data and y_data[-1] is not None else 0] * (len(x_data) - len(y_data)))

    # Configura e gera o gráfico com os dados fornecidos.
    plt.figure()
    plt.plot(x_data, y_data, marker='o', linestyle='-', label=graph_name)
    plt.title(f'{graph_name} over time')
    plt.xlabel('Time (s)')
    plt.ylabel(graph_name)
    plt.grid(True)
    file_path = os.path.abspath(os.path.join('results', f'{graph_name}.png'))

    # Garante que o diretório exista e salva o gráfico.
    if not os.path.exists('./results'):
        print("Diretório './results' não existe. Criando diretório.")
        os.makedirs('./results')

    plt.savefig(file_path)
    plt.close()
    print(f'Gráfico salvo em: {file_path}')


# Classe que implementa o algoritmo PANDA, herdando da interface IR2A.
# IR2A é a interface para implementar novos algoritmos ABR no pyDash.
class R2APanda(IR2A):

    # Inicializa variáveis relevantes para o controle do algoritmo ABR.
    def __init__(self, id):
        super().__init__(id)
        self.bitrate_data = []  # Armazena as taxas de bits usadas durante a execução.
        self.throughput_data = []  # Armazena os valores de throughput medidos.
        self.time_data = []  # Armazena os tempos de execução para gerar gráficos.
        self.qi = None  # Armazena os bitrates disponíveis, obtidos do arquivo MPD.
        self.parsed_mpd = None  # Armazena o MPD parseado.
        self.last_download_time = None  # Tempo do último download.
        self.current_bitrate = None  # Bitrate atual.
        self.target_rate = None  # Taxa alvo inicial do algoritmo.
        self.probing_rate = 0.14  # Taxa de sondagem inicial do PANDA.
        self.safety_margin = 0.15  # Margem de segurança do buffer.
        self.buffer_max = 60  # Tamanho máximo do buffer (segundos).
        self.buffer_min = 10  # Tamanho mínimo do buffer (segundos).
        self.traffic_shaping_interval = 0  # Intervalo de mudança de perfis de traffic shaping.
        self.traffic_shaping_time = 0  # Tempo de aplicação do perfil de traffic shaping.

    # Método inicial que coleta dados iniciais de throughput e salva gráficos.
    def initialize(self):
        print("Inicializando execução do algoritmo PANDA.")
        current_time = time.time()
        self.time_data.append(current_time)

        # Coleta os dados de throughput da rede utilizando a biblioteca psutil.
        net_io = psutil.net_io_counters()
        throughput = net_io.bytes_sent + net_io.bytes_recv

        # Inicializa com valores de throughput e bitrate.
        self.throughput_data.append(throughput / 1000)  # Em Kbps
        self.bitrate_data.append(self.target_rate if self.target_rate else 0)

        # Salva os gráficos iniciais.
        save_graph(self.time_data, self.throughput_data, 'Initial Throughput')
        save_graph(self.time_data, self.bitrate_data, 'Initial Bitrate')

    # Processa a resposta do arquivo XML (MPD), determinando os bitrates disponíveis.
    def handle_xml_response(self, msg):
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()  # Obtém os bitrates disponíveis (Quality Index).
        self.target_rate = min(self.qi)  # Define o bitrate inicial como o menor disponível.
        self.current_bitrate = self.target_rate

        # Atualiza o tempo e bitrate atual.
        self.time_data.append(time.time())
        self.bitrate_data.append(self.current_bitrate)

        print(f"Resposta XML processada. Bitrates disponíveis: {self.qi}")
        print(f"Taxa alvo inicial: {self.target_rate}")
        self.send_up(msg)  # Envia a mensagem para a camada superior (Player).

    # Lida com as requisições de tamanho de segmento.
    def handle_segment_size_request(self, msg):
        print("handle_segment_size_request foi chamado")
        time.sleep(1)  # Simula um pequeno atraso.
        self.last_download_time = time.time()
        self.time_data.append(self.last_download_time)

        # Sincroniza os dados de bitrate e tempo.
        self.bitrate_data.append(self.current_bitrate)

        # Define o bitrate para a solicitação e envia para a camada inferior.
        msg.add_quality_id(self.current_bitrate)
        self.send_down(msg)
        print(f"Solicitação de segmento com bitrate atual: {self.current_bitrate}")

        # Salva os gráficos após a requisição.
        save_graph(self.time_data, self.throughput_data, 'Pre-request Throughput')
        save_graph(self.time_data, self.bitrate_data, 'Pre-request Bitrate')

    # Processa a resposta do tamanho do segmento, calculando o throughput.
    def handle_segment_size_response(self, msg):
        current_time = time.time()
        download_duration = current_time - self.last_download_time
        segment_size = msg.get_payload_size()  # Obtém o tamanho do payload.

        # Calcula o throughput baseado no tamanho do segmento e no tempo de download.
        if download_duration > 0 and segment_size > 0:
            throughput = (segment_size / download_duration) / 1000
        else:
            throughput = 0

        # Atualiza os dados de tempo, throughput e bitrate.
        self.time_data.append(current_time)
        self.throughput_data.append(throughput)
        self.bitrate_data.append(self.current_bitrate if self.current_bitrate is not None else 0)

        # Verifica se os dados estão sincronizados.
        assert len(self.time_data) == len(self.throughput_data), "Descompasso entre time_data e throughput_data"
        assert len(self.time_data) == len(self.bitrate_data), "Descompasso entre time_data e bitrate_data"

        # Salva os gráficos de throughput e bitrate.
        save_graph(self.time_data, self.throughput_data, 'Throughput')
        save_graph(self.time_data, self.bitrate_data, 'Bitrate')

    # Faz requisição do arquivo XML (MPD).
    def handle_xml_request(self, msg):
        xml_url = msg.get_payload()
        print(f">>>> Requisição XML recebida: {xml_url}")

        # Verifica se a URL é válida e faz a requisição do MPD.
        if not xml_url.startswith("http"):
            print("Erro: O conteúdo recebido não é uma URL válida de XML.")
            return

        try:
            request_time = time.time()
            self.time_data.append(request_time)
            self.bitrate_data.append(self.current_bitrate if self.current_bitrate is not None else 0)

            # Faz a requisição HTTP e processa o conteúdo XML.
            response = requests.get(xml_url)
            response.raise_for_status()
            xml_content = response.text
            xml_tree = ET.fromstring(xml_content)

            for element in xml_tree:
                print(f"Tag: {element.tag}, Atributos: {element.attrib}, Texto: {element.text}")

            self.send_up(msg)  # Envia a resposta para a camada superior (Player).

        except requests.exceptions.RequestException as e:
            print(f"Erro ao fazer requisição HTTP: {e}")
        except ET.ParseError as e:
            print(f"Erro ao parsear o XML: {e}")

    # Finaliza a execução do algoritmo e salva os gráficos finais.
    def finalization(self):
        print("Finalizando execução do algoritmo PANDA.")
        final_time = time.time()
        self.time_data.append(final_time)
        self.bitrate_data.append(self.current_bitrate if self.current_bitrate is not None else 0)

        save_graph(self.time_data, self.throughput_data, 'Final Throughput')
        save_graph(self.time_data, self.bitrate_data, 'Final Bitrate')

    # Método principal para o gerenciamento de mensagens, definindo o fluxo do algoritmo.
    def handle_message(self, msg):
        msg_kind = msg.get_kind()
        print(f">>>> Tipo de mensagem recebida: {msg_kind}")
