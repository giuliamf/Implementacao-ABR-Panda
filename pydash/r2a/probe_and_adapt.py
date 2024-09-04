from pydash.base.message import MessageKind
from pydash.player.parser import parse_mpd
from pydash.r2a.ir2a import IR2A


class ProbeAndAdapt(IR2A):

    def __init__(self, id):
        super().__init__(id)
        self.parsed_mpd = None
        self.qi = []

    def handle_xml_request(self, msg):
        # Encaminha a solicitação XML para o módulo abaixo na hierarquia
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # Processa a resposta XML e armazena informações de qualidade
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()
        # Encaminha a mensagem para o módulo acima na hierarquia
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # Escolhe a qualidade média baseada nas informações do MPD
        if self.qi:
            qualidade_media = self.qi[len(self.qi) // 2]
            msg.add_quality_id(qualidade_media)
        else:
            # Caso não haja informação, pode adicionar um comportamento padrão
            msg.add_quality_id(0)  # Exemplo: define qualidade mínima
        # Encaminha a solicitação com a qualidade escolhida para o módulo abaixo
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        # Aqui você pode implementar o cálculo da taxa de transferência, se necessário
        # Encaminha a resposta para o módulo acima na hierarquia
        self.send_up(msg)

    def initialize(self):
        # Inicializa o módulo e qualquer configuração adicional necessária
        super().initialize()

    def finalization(self):
        # Finaliza o módulo e libera recursos, se necessário
        super().finalization()
