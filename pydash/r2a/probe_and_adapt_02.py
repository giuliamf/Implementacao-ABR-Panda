from pydash.base.message import MessageKind
from pydash.player.parser import parse_mpd
from pydash.r2a.ir2a import IR2A
import time

class ProbeAndAdapt(IR2A):

    def __init__(self, id):
        super().__init__(id)
        self.parsed_mpd = None
        self.qi = []
        self.buffer_min = 10  # Buffer mínimo em segundos
        self.buffer_max = 60  # Buffer máximo em segundos
        self.probing_rate = 0.14  # Taxa de sonda
        self.safety_margin = 0.15  # Margem de segurança para buffer
        self.target_rate = 0  # Taxa alvo inicial
        self.current_bitrate = 0  # Bitrate inicial
        self.last_download_time = 0  # Tempo da última requisição

    def handle_xml_request(self, msg):
        # Encaminha a solicitação XML para o módulo abaixo na hierarquia
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # Processa a resposta XML e armazena informações de qualidade
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()
        # Inicializa a taxa de bitrate com a menor qualidade disponível
        if self.qi:
            self.target_rate = min(self.qi)
            self.current_bitrate = self.target_rate
        # Encaminha a mensagem para o módulo acima na hierarquia
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # Define a qualidade com base na taxa de throughput medida
        if self.qi:
            msg.add_quality_id(self.current_bitrate)
        else:
            msg.add_quality_id(min(self.qi))  # Caso sem informação, usa qualidade mínima
        self.last_download_time = time.time()  # Marca o tempo de início do download
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        # Calcula o throughput com base no tempo de download
        current_time = time.time()
        download_duration = current_time - self.last_download_time

        # Tamanho do segmento em bits
        segment_size = msg.get_bit_length()

        # Throughput medido (em kbps)
        throughput = (segment_size / download_duration) / 1000

        # Adapta a taxa de bitrate com base no throughput
        if throughput > self.current_bitrate + self.safety_margin:
            # Aumenta a taxa de bitrate
            self.target_rate += self.probing_rate * self.current_bitrate
        else:
            # Reduz a taxa de bitrate em caso de congestionamento
            self.target_rate -= self.probing_rate * (self.current_bitrate - throughput)

        # Seleciona o bitrate mais próximo disponível
        self.current_bitrate = max(b for b in self.qi if b <= self.target_rate)

        # Encaminha a resposta para o módulo acima
        self.send_up(msg)

    def initialize(self):
        # Inicializa o módulo e configura os parâmetros
        super().initialize()
        self.last_download_time = time.time()

    def finalization(self):
        # Finaliza o módulo e libera recursos, se necessário
        super().finalization()
