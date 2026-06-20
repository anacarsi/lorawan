"""
Experiment 2: Simple Reactive Jammer

Mallory jams ALL LoRa frames she detects.
Tests how effective a simple reactive jammer is against different data rates.
"""

import matplotlib
try:
    import tkinter
    matplotlib.use('TkAgg')
except ImportError:
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
import time
import random
from lora_simulator import SimulatedLoRaNode, LoRaChannel

# Colors for logging
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'

def log_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} {msg}")

def log_warn(msg):
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {msg}")

def log_error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.RESET} {msg}")


class ReactiveJammer:
    """
    Simple reactive jammer - detects preamble and transmits noise.

    In real hardware, this would:
    1. Sniffer detects preamble
    2. Triggers jammer immediately
    3. Jammer transmits on same frequency/SF
    4. Corrupts the frame at Bob's receiver

    In simulation:
    - We detect when a frame is being transmitted
    - Create a jamming frame with random payload
    - Both reach Bob, causing collision/corruption
    """

    def __init__(self, jammer_node: SimulatedLoRaNode):
        self.jammer = jammer_node
        self.enabled = False
        self.jammed_count = 0

    def enable(self):
        """Enable the jammer"""
        self.enabled = True
        self.jammed_count = 0
        log_warn(f"{self.jammer.name} jammer ENABLED")

    def disable(self):
        """Disable the jammer"""
        self.enabled = False
        log_info(f"{self.jammer.name} jammer disabled (jammed {self.jammed_count} frames)")

    def jam_if_detected(self, channel: LoRaChannel, current_time: float):
        """Check if there's a frame to jam"""
        if not self.enabled:
            return

        # Look for frames currently being transmitted
        for frame in channel.frames_in_air:
            # Is this frame happening right now?
            if frame.start_time <= current_time <= frame.start_time + frame.duration:
                # Mallory is close to Bob, so she can detect Alice's signal
                # Calculate if Mallory can detect it
                dx = frame.tx_position[0] - self.jammer.position[0]
                dy = frame.tx_position[1] - self.jammer.position[1]
                distance = (dx**2 + dy**2)**0.5

                # Simple detection: if within 200m and not already jammed
                if distance < 200:
                    # Create jamming signal
                    # Reactive jammer transmits IMMEDIATELY when it detects preamble
                    # This means it overlaps with the original frame

                    # Jamming payload (random noise)
                    jam_payload = [random.randint(0, 255) for _ in range(20)]

                    # Create jamming frame
                    # Key: same SF and frequency as target!
                    jam_frame = type(frame)(
                        payload=jam_payload,
                        frequency=frame.frequency,
                        bandwidth=frame.bandwidth,
                        spreading_factor=frame.spreading_factor,
                        coding_rate=frame.coding_rate,
                        start_time=current_time,  # Start NOW
                        duration=0.1,  # Short burst is enough
                        tx_power=20,  # High power (Mallory is close to Bob)
                        tx_position=self.jammer.position
                    )

                    channel.add_frame(jam_frame)
                    self.jammed_count += 1
                    return True

        return False


def simple_jammer_experiment(num_rounds: int = 2, frame_lengths: list = [1, 3, 12],
                             frequency: int = 869525000, duty_cycle: float = 0.80):
    """
    Experiment 2: Simple Reactive Jammer

    Tests effectiveness of a reactive jammer across:
    - Different frame lengths
    - Different spreading factors
    """

    log_info("=== Experiment 2: Simple Reactive Jammer ===")
    log_info("Mallory will jam all detected frames")

    # Setup
    channel = LoRaChannel()
    alice = SimulatedLoRaNode('alice', (0, 0), channel)
    bob = SimulatedLoRaNode('bob', (100, 0), channel)
    mallory = SimulatedLoRaNode('mallory', (100, 5), channel)  # Close to Bob!

    jammer = ReactiveJammer(mallory)

    # Test subset of data rates
    datarates = {
        "DR0": {"spreadingfactor": 12, "bandwidth": 125},
        "DR2": {"spreadingfactor": 10, "bandwidth": 125},
        "DR5": {"spreadingfactor":  7, "bandwidth": 125},
    }

    default_channel = {
        'frequency': frequency,
        'bandwidth': 125,
        'codingrate': 5,
        'invertiqtx': True,
        'invertiqrx': False,
        'explicitheader': True,
    }

    # Results for each frame length
    all_results = {}

    for frame_len in frame_lengths:
        log_info(f"\n--- Testing Frame Length: {frame_len} bytes ---")

        dr_labels = sorted(datarates.keys())
        count_recv = [0 for _ in dr_labels]
        count_jammed = [0 for _ in dr_labels]
        count_lost = [0 for _ in dr_labels]

        # Create plot
        fig, ax = plt.subplots(figsize=(8, 5))
        bar_width = 0.6

        x_pos = list(range(len(dr_labels)))
        bar_recv = ax.bar(x_pos, count_recv, bar_width, label='Received', color='#2ecc71')
        bar_jammed = ax.bar(x_pos, count_jammed, bar_width, bottom=count_recv,
                           label='Jammed', color='#e67e22')
        bar_lost = ax.bar(x_pos, count_lost, bar_width,
                         bottom=[r+j for r,j in zip(count_recv, count_jammed)],
                         label='Lost', color='#e74c3c')

        ax.set_xticks(x_pos)
        ax.set_xticklabels(dr_labels)
        ax.set_ylim([0, num_rounds + 1])
        ax.set_ylabel('Number of Frames')
        ax.set_xlabel('Data Rate')
        ax.set_title(f'Jamming Effectiveness (Frame Length: {frame_len}B)')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.ion()
        plt.show()

        def update_chart():
            for i in range(len(dr_labels)):
                bar_recv[i].set_height(count_recv[i])
                bar_jammed[i].set_height(count_jammed[i])
                bar_jammed[i].set_y(count_recv[i])
                bar_lost[i].set_height(count_lost[i])
                bar_lost[i].set_y(count_recv[i] + count_jammed[i])
            fig.canvas.draw()
            fig.canvas.flush_events()

        # Run experiments
        for round_num in range(num_rounds):
            log_info(f"Round {round_num + 1}/{num_rounds}")

            for drname, dridx in zip(dr_labels, range(len(dr_labels))):
                sf = datarates[drname]['spreadingfactor']

                # Configure channel
                channel_config = {**default_channel, **datarates[drname]}
                alice.set_lora_channel(**channel_config)
                bob.set_lora_channel(**channel_config)
                mallory.set_lora_channel(**channel_config)

                # Enable jammer
                jammer.enable()

                # Bob receives
                bob.receive()
                time.sleep(0.1)

                # Alice transmits
                payload = [random.randint(0, 256) for _ in range(frame_len)]

                tx_start = time.time()
                alice.transmit_frame(payload, blocking=False)  # Non-blocking!

                # Jammer reacts during transmission
                time.sleep(0.05)  # Give time for preamble detection
                jammer.jam_if_detected(channel, time.time())

                # Wait for transmission to complete
                time.sleep(2.0)

                # Check result
                recv_frame = bob.fetch_frame()
                bob.standby()
                jammer.disable()

                tx_end = time.time()

                if recv_frame is not None:
                    if recv_frame['payload'] == payload and not recv_frame['crc_error']:
                        count_recv[dridx] += 1
                        log_success(f"  {drname}: Received (jammer failed!)")
                    else:
                        count_jammed[dridx] += 1
                        log_warn(f"  {drname}: Jammed/Corrupted")
                else:
                    count_lost[dridx] += 1
                    log_error(f"  {drname}: Lost")

                update_chart()

                # Duty cycle
                frm_duration = tx_end - tx_start
                remaining = frm_duration / duty_cycle - frm_duration
                if remaining > 0:
                    time.sleep(remaining)

                channel.cleanup_old_frames(time.time())

        # Results summary
        log_info(f"\n=== Results for Frame Length {frame_len}B ===")
        print(f"{'DR':<6} {'SF':<4} {'Received':<10} {'Jammed':<10} {'Lost':<10} {'Jam %':<10}")
        print("-" * 60)

        for drname, recv, jammed, lost in zip(dr_labels, count_recv, count_jammed, count_lost):
            sf = datarates[drname]['spreadingfactor']
            total = num_rounds
            jam_rate = (jammed / total) * 100 if total > 0 else 0

            color = Colors.RED if jam_rate >= 70 else Colors.YELLOW if jam_rate >= 40 else Colors.GREEN
            print(f"{color}{drname:<6} {sf:<4} {recv:<10} {jammed:<10} {lost:<10} {jam_rate:>6.1f}%{Colors.RESET}")

        all_results[frame_len] = {
            'received': count_recv,
            'jammed': count_jammed,
            'lost': count_lost
        }

        plt.ioff()
        plt.savefig(f'jammer_experiment_frame{frame_len}.png', dpi=150, bbox_inches='tight')
        log_info(f"Plot saved as jammer_experiment_frame{frame_len}.png")

        input("\nPress Enter to continue to next frame length...")
        plt.close()

    return all_results


if __name__ == "__main__":
    print("\n" + "="*70)
    log_info("Experiment 2: Simple Reactive Jammer")
    log_info("Mallory (5m from Bob) will jam Alice's transmissions (100m away)")
    print("="*70 + "\n")

    simple_jammer_experiment(num_rounds=2, frame_lengths=[1, 3, 12])

    log_info("\nExperiment complete!")
