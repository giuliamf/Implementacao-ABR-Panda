from pydash.r2a.ir2a import IR2A

"""
Perguntas vão de cima para baixo (para o connection handler)
Respostas vão de baixo para cima (para o player)
"""


class IR2AMedia(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)

        self.vazoes = []
        self.qi = []
        pass

    def handle_xml_request(self, msg):
        self.send_down(msg)   # Pergunta

    def handle_xml_response(self, msg):

        print('>>>>>>>>>>>>> MENSAGEM!')
        print(msg.get_payload())

        self.send_up(msg)    # Resposta

    def handle_segment_size_request(self, msg):
        # Escolha da qualidade
        msg.add_quality_id(self.qi[2000])

        self.send_down(msg)    # Pergunta

    def handle_segment_size_response(self, msg):
        self.send_up(msg)      # Resposta

    def initialize(self):
        pass

    def finalization(self):
        pass
