from pydash.base.message import MessageKind
from pydash.player.parser import parse_mpd
from pydash.r2a.ir2a import IR2A
import time

class ProbeAndAdapt(IR2A):

    def __init__(self, id):
        super().__init__(id)
        self.parsed_mpd = None
        self.qi = []
        self.buffer_min = 10 
        self.buffer_max = 60  
        self.probing_rate = 0.14  
        self.safety_margin = 0.15 
        self.target_rate = 0 
        self.current_bitrate = 0 
        self.last_download_time = 0 

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()
        if self.qi:
            self.target_rate = min(self.qi)
            self.current_bitrate = self.target_rate
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        if self.qi:
            msg.add_quality_id(self.current_bitrate)
        else:
            msg.add_quality_id(min(self.qi)) 
        self.last_download_time = time.time() 
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        current_time = time.time()
        download_duration = current_time - self.last_download_time

        segment_size = msg.get_bit_length()

        throughput = (segment_size / download_duration) / 1000

        if throughput > self.current_bitrate + self.safety_margin:
            self.target_rate += self.probing_rate * self.current_bitrate
        else:
            self.target_rate -= self.probing_rate * (self.current_bitrate - throughput)

        self.current_bitrate = max(b for b in self.qi if b <= self.target_rate)

        self.send_up(msg)

    def initialize(self):
        super().initialize()
        self.last_download_time = time.time()

    def finalization(self):
        super().finalization()
