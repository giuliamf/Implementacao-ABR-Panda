from pydash.r2a import IR2A
import time

class R2APanda(IR2A):
    def initialize(self):
        self.buffer_min = 10  # Tempo mínimo de buffer em segundos
        self.buffer_max = 60  # Tempo máximo de buffer em segundos
        self.probing_rate = 0.14  # Taxa de sonda para aumento de taxa de bit
        self.safety_margin = 0.15  # Margem de segurança para evitar buffer underrun
        self.target_rate = min(self.qi)  # Inicializamos com a menor taxa de bit
        self.current_bitrate = self.target_rate
        self.last_download_time = time.time()

    def handle_xml_response(self, msg):
        # Extrai o conteúdo do arquivo MPD e a lista de qualidades
        from pydash.player.parser import parse_mpd
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # Define a qualidade baseada na taxa de throughput medida
        msg.add_quality_id(self.current_bitrate)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        # Calcula o throughput real com base no tempo de download
        current_time = time.time()
        download_duration = current_time - self.last_download_time
        self.last_download_time = current_time
        
        # Tamanho do segmento em bits
        segment_size = msg.get_bit_length()
        
        # Throughput medido (em kbps)
        throughput = (segment_size / download_duration) / 1000
        
        # Adapta a taxa de bit com base no throughput
        if throughput > self.current_bitrate + self.safety_margin:
            self.target_rate += self.probing_rate * self.current_bitrate
        else:
            self.target_rate -= self.probing_rate * (self.current_bitrate - throughput)

        # Define o bitrate mais próximo disponível
        self.current_bitrate = max(b for b in self.qi if b <= self.target_rate)
        
        self.send_up(msg)

    def finalization(self):
        print("Finalizando execução do algoritmo PANDA.")
