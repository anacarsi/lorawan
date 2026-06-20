"""
LoRa Physical Layer Simulator
Simulates realistic LoRa radio behavior including:
- Path loss and fading
- Time-on-air calculations
- Collision detection
- Jamming interference
"""

import time
import random
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class NodeState(Enum):
    STANDBY = "standby"
    TX = "transmitting"
    RX = "receiving"
    JAMMED = "jammed"


@dataclass
class LoRaFrame:
    """Represents a LoRa frame in the air"""
    payload: List[int]
    frequency: int
    bandwidth: int
    spreading_factor: int
    coding_rate: int
    start_time: float
    duration: float
    tx_power: int  # dBm
    tx_position: Tuple[float, float]  # (x, y) coordinates


@dataclass
class Position:
    """Physical position of a node"""
    x: float
    y: float
    name: str


class LoRaChannel:
    """Simulates the wireless channel - handles propagation and interference"""

    def __init__(self):
        self.frames_in_air: List[LoRaFrame] = []
        self.current_time = 0.0

    def calculate_path_loss(self, distance_m: float, frequency_hz: int) -> float:
        """
        Calculate path loss using log-distance model
        PL(d) = PL(d0) + 10*n*log10(d/d0) + X_sigma
        """
        if distance_m < 1:
            distance_m = 1

        # Path loss exponent (2.7-4 for urban, 2 for free space)
        n = 2.7

        # Reference distance
        d0 = 1.0  # meters

        # Free space path loss at d0
        pl_d0 = 20 * math.log10((4 * math.pi * d0 * frequency_hz) / 3e8)

        # Path loss at distance d
        path_loss = pl_d0 + 10 * n * math.log10(distance_m / d0)

        # Add shadowing (log-normal fading)
        shadowing_std = 3.0  # dB
        shadowing = random.gauss(0, shadowing_std)

        return path_loss + shadowing

    def calculate_rssi(self, frame: LoRaFrame, rx_position: Tuple[float, float]) -> float:
        """Calculate received signal strength"""
        # Calculate distance
        dx = frame.tx_position[0] - rx_position[0]
        dy = frame.tx_position[1] - rx_position[1]
        distance = math.sqrt(dx**2 + dy**2)

        # Path loss
        path_loss = self.calculate_path_loss(distance, frame.frequency)

        # RSSI = TX Power - Path Loss
        rssi = frame.tx_power - path_loss

        return rssi

    def calculate_snr(self, rssi: float, noise_floor: float = -120) -> float:
        """Calculate Signal-to-Noise Ratio"""
        # Noise floor depends on bandwidth
        # -174 dBm/Hz + 10*log10(BW)
        # For 125kHz: -174 + 10*log10(125000) ≈ -123 dBm

        return rssi - noise_floor

    def check_collision(self, frame1: LoRaFrame, frame2: LoRaFrame) -> bool:
        """
        Check if two frames collide.
        Frames collide if they overlap in time and have same SF and freq.
        """
        # Different SF/freq = orthogonal (no collision in ideal case)
        if frame1.spreading_factor != frame2.spreading_factor:
            return False
        if frame1.frequency != frame2.frequency:
            return False

        # Check time overlap
        f1_start = frame1.start_time
        f1_end = frame1.start_time + frame1.duration
        f2_start = frame2.start_time
        f2_end = frame2.start_time + frame2.duration

        return not (f1_end <= f2_start or f2_end <= f1_start)

    def add_frame(self, frame: LoRaFrame):
        """Add a frame to the channel"""
        self.frames_in_air.append(frame)

    def receive_frame(self, rx_position: Tuple[float, float], rx_sf: int,
                     rx_freq: int, rx_bw: int, current_time: float) -> Optional[Dict]:
        """
        Simulate reception at a receiver.
        Returns frame dict if successfully received, None otherwise.
        """
        # Find frames that match receiver config and are currently being transmitted
        matching_frames = [
            f for f in self.frames_in_air
            if f.spreading_factor == rx_sf
            and f.frequency == rx_freq
            and f.bandwidth == rx_bw
            and f.start_time <= current_time <= f.start_time + f.duration
        ]

        if not matching_frames:
            return None

        # Take the strongest frame (capture effect)
        best_frame = None
        best_rssi = -999

        for frame in matching_frames:
            rssi = self.calculate_rssi(frame, rx_position)
            if rssi > best_rssi:
                best_rssi = rssi
                best_frame = frame

        if best_frame is None:
            return None

        # Check if strong enough to receive (sensitivity depends on SF)
        sensitivity_map = {
            7: -123,
            8: -126,
            9: -129,
            10: -132,
            11: -134.5,
            12: -137
        }
        sensitivity = sensitivity_map.get(rx_sf, -120)

        if best_rssi < sensitivity:
            return None  # Too weak

        # Calculate SNR
        snr = self.calculate_snr(best_rssi)

        # Check for collisions
        collision = False
        for other_frame in matching_frames:
            if other_frame != best_frame:
                if self.check_collision(best_frame, other_frame):
                    collision = True
                    break

        # Determine if successfully decoded
        # SNR requirements for successful demodulation
        snr_required_map = {
            7: -7.5,
            8: -10,
            9: -12.5,
            10: -15,
            11: -17.5,
            12: -20
        }
        snr_required = snr_required_map.get(rx_sf, -10)

        payload = best_frame.payload
        crc_error = False

        if collision:
            # Collision - high probability of corruption
            if random.random() < 0.9:
                payload = [random.randint(0, 255) for _ in payload]
                crc_error = True

        elif snr < snr_required:
            # SNR too low - may corrupt
            if random.random() < 0.7:
                payload = [random.randint(0, 255) for _ in payload]
                crc_error = True

        return {
            'payload': payload,
            'rssi': int(best_rssi),
            'snr': int(snr),
            'crc_error': crc_error,
            'has_more': False,
            'frames_dropped': False,
            'time_valid_header': int(best_frame.start_time * 1e6),
            'time_rxdone': int((best_frame.start_time + best_frame.duration) * 1e6)
        }

    def cleanup_old_frames(self, current_time: float):
        """Remove frames that have finished transmitting"""
        self.frames_in_air = [
            f for f in self.frames_in_air
            if f.start_time + f.duration > current_time
        ]


class SimulatedLoRaNode:
    """Simulates a LoRa node with realistic physics"""

    def __init__(self, name: str, position: Tuple[float, float], channel: LoRaChannel):
        self.name = name
        self.position = position
        self.channel = channel
        self.state = NodeState.STANDBY
        self.config = {}
        self.rx_buffer = []
        self.tx_power = 14  # dBm (default)
        self.rx_start_time = 0.0
        self.sniffer_enabled = False
        self.jammer_config = {}

    def standby(self):
        """Enter standby mode"""
        self.state = NodeState.STANDBY
        self.sniffer_enabled = False

    def set_lora_channel(self, **kwargs):
        """Configure LoRa channel parameters"""
        self.config = kwargs

    def calculate_time_on_air(self, payload_len: int) -> float:
        """
        Calculate LoRa time-on-air using the formula.
        Returns time in seconds.
        """
        sf = self.config.get('spreadingfactor', 7)
        bw = self.config.get('bandwidth', 125) * 1000  # Convert to Hz
        cr = self.config.get('codingrate', 5)
        explicit_header = self.config.get('explicitheader', True)

        # Preamble symbols (typically 8)
        n_preamble = 8

        # Symbol duration
        T_sym = (2 ** sf) / bw

        # Preamble time
        T_preamble = (n_preamble + 4.25) * T_sym

        # Payload symbol count
        H = 0 if explicit_header else 1
        DE = 1 if sf >= 11 else 0  # Low data rate optimization
        payload_symb_nb = 8 + max(
            math.ceil((8 * payload_len - 4 * sf + 28 + 16 - 20 * H) / (4 * (sf - 2 * DE))) * (cr),
            0
        )

        # Payload time
        T_payload = payload_symb_nb * T_sym

        return T_preamble + T_payload

    def transmit_frame(self, payload: List[int], blocking: bool = True):
        """Transmit a frame"""
        current_time = time.time()

        # Calculate time on air
        toa = self.calculate_time_on_air(len(payload))

        # Create frame
        frame = LoRaFrame(
            payload=payload,
            frequency=self.config.get('frequency', 868100000),
            bandwidth=self.config.get('bandwidth', 125),
            spreading_factor=self.config.get('spreadingfactor', 7),
            coding_rate=self.config.get('codingrate', 5),
            start_time=current_time,
            duration=toa,
            tx_power=self.tx_power,
            tx_position=self.position
        )

        # Add to channel
        self.channel.add_frame(frame)

        # If blocking, wait for transmission to complete
        if blocking:
            time.sleep(toa)

        return True

    def receive(self):
        """Enter receive mode"""
        self.state = NodeState.RX
        self.rx_start_time = time.time()

    def fetch_frame(self) -> Optional[Dict]:
        """Fetch received frame from buffer"""
        # Try to receive from channel if in RX mode
        current_time = time.time()

        if self.state == NodeState.RX:
            # Look for frames that ended recently
            for frame in self.channel.frames_in_air:
                frame_end = frame.start_time + frame.duration
                # Check if frame just ended (within last second)
                if frame_end <= current_time and current_time - frame_end < 2.0:
                    # Check if it matches our config
                    if (frame.spreading_factor == self.config.get('spreadingfactor', 7) and
                        frame.frequency == self.config.get('frequency', 868100000) and
                        frame.bandwidth == self.config.get('bandwidth', 125)):

                        received = self.channel.receive_frame(
                            self.position,
                            frame.spreading_factor,
                            frame.frequency,
                            frame.bandwidth,
                            frame_end - 0.001  # Sample just before end
                        )

                        if received and received not in self.rx_buffer:
                            self.rx_buffer.append(received)

        # Return from buffer
        if self.rx_buffer:
            return self.rx_buffer.pop(0)

        return None

    def enable_sniffer(self, action: str = "internal", pattern: List[int] = None,
                      mask: List[int] = None):
        """Enable sniffer/jammer mode"""
        self.sniffer_enabled = True
        self.jammer_config = {
            'action': action,
            'pattern': pattern,
            'mask': mask
        }

    def set_jammer_payload_length(self, length: int):
        """Set jammer payload length"""
        self.jammer_config['payload_length'] = length

    def set_preamble_length(self, length: int):
        """Set preamble length"""
        self.config['preamble_length'] = length

    def set_txcrc(self, enabled: bool):
        """Enable/disable TX CRC"""
        self.config['txcrc'] = enabled
