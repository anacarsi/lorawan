"""
LoRaWAN Security Experiments - SIMULATION VERSION
Uses realistic physical layer simulation of LoRa radio behavior.
"""

import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for interactive plots
import matplotlib.pyplot as plt

import time
import random
from typing import Dict, List

from lora_simulator import SimulatedLoRaNode, LoRaChannel

# ANSI Color codes for logging
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

def log_debug(msg):
    print(f"{Colors.MAGENTA}[DEBUG]{Colors.RESET} {msg}")


# ============================================================================
# SIMULATION SETUP
# ============================================================================

log_info("Initializing LoRa Physical Layer Simulator")
log_info("This simulates realistic radio propagation, collisions, and interference")

# Create shared wireless channel
channel = LoRaChannel()

# Node positions (in meters)
# Alice is in lecture hall (0, 0)
# Bob and Mallory are in office building 100m away
POSITIONS = {
    'alice': (0, 0),
    'bob': (100, 0),
    'mallory': (100, 5)
}

# Create simulated nodes
alice = SimulatedLoRaNode('alice', POSITIONS['alice'], channel)
bob = SimulatedLoRaNode('bob', POSITIONS['bob'], channel)
mallory = SimulatedLoRaNode('mallory', POSITIONS['mallory'], channel)

all_nodes = [alice, bob, mallory]
node_names = ["alice", "bob", "mallory"]

log_info(f"Created 3 nodes: {', '.join(node_names)}")
log_info(f"Distance Alice->Bob: 100m, Distance Bob->Mallory: 5m")

for node in all_nodes:
    node.standby()

# Default channel configuration
default_channel = {
    'frequency': 868100000,  # Hz
    'bandwidth': 125,  # kHz
    'spreadingfactor': 7,
    'syncword': 18,
    'codingrate': 5,
    'invertiqtx': True,
    'invertiqrx': False,
    'explicitheader': True,
}

# EU868 Data Rates
datarates = {
    "DR0": {"spreadingfactor": 12, "bandwidth": 125},
    "DR1": {"spreadingfactor": 11, "bandwidth": 125},
    "DR2": {"spreadingfactor": 10, "bandwidth": 125},
    "DR3": {"spreadingfactor":  9, "bandwidth": 125},
    "DR4": {"spreadingfactor":  8, "bandwidth": 125},
    "DR5": {"spreadingfactor":  7, "bandwidth": 125},
}


# ============================================================================
# EXPERIMENT 1.1: Single Message
# ============================================================================

def first_experiment(spreading_factor: int = 12, payload_str: str = 'Secure Mobile Systems') -> dict:
    """
    Experiment 1.1: Single Message Test
    Tests basic LoRa communication with realistic physics simulation.
    """
    log_info(f"=== Experiment 1.1: Single Message (SF{spreading_factor}) ===")

    channel_config = {**default_channel, 'spreadingfactor': spreading_factor}

    # Configure nodes
    for node in all_nodes:
        node.standby()
        node.set_lora_channel(**channel_config)

    # Bob starts receiving
    bob.receive()
    log_info("Bob is now receiving...")
    time.sleep(0.1)

    # Alice transmits
    payload = [ord(c) for c in payload_str]
    log_info(f"Alice transmitting: '{payload_str}'")

    tx_start = time.time()
    alice.transmit_frame(payload, blocking=True)
    tx_duration = time.time() - tx_start

    log_info(f"Frame transmitted (time-on-air: {tx_duration:.3f}s)")

    # Wait for Bob to process
    time.sleep(0.5)

    # Check what Bob received
    recv_frame = bob.fetch_frame()
    bob.standby()

    # Cleanup
    channel.cleanup_old_frames(time.time())

    # Process results
    result = {
        'success': False,
        'transmitted': payload_str,
        'received': None,
        'rssi': None,
        'snr': None,
        'crc_error': None,
        'time_on_air': tx_duration
    }

    if recv_frame is not None:
        received_str = "".join([chr(b) for b in recv_frame['payload']])
        result['received'] = received_str
        result['rssi'] = recv_frame['rssi']
        result['snr'] = recv_frame['snr']
        result['crc_error'] = recv_frame.get('crc_error', False)
        result['success'] = (received_str == payload_str) and not result['crc_error']

        log_info(f"Frame received: '{received_str}'")
        log_info(f"  RSSI: {result['rssi']} dBm")
        log_info(f"  SNR: {result['snr']} dB")
        log_info(f"  CRC Error: {result['crc_error']}")

        if result['success']:
            log_success("Message received correctly!")
        else:
            log_error("Message corrupted")
    else:
        log_error("No frame received by Bob")

    return result


# ============================================================================
# EXPERIMENT 1.2: Channel Quality
# ============================================================================

def channel_quality_experiment(num_rounds: int = 3, frame_len: int = 12,
                               frequency: int = 869525000, duty_cycle: float = 0.80) -> dict:
    """
    Experiment 1.2: Multiple Channels
    Test all data rates with realistic physics.
    """
    log_info("=== Experiment 1.2: Channel Quality by Data Rate ===")
    log_info(f"Testing {len(datarates)} data rates with {num_rounds} rounds each")

    dr_labels = sorted(datarates.keys())
    count_recv = [0 for _ in dr_labels]
    count_lost = [0 for _ in dr_labels]
    count_corrupt = [0 for _ in dr_labels]

    # Setup plot
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.6

    x_pos = list(range(len(dr_labels)))
    bar_recv = ax.bar(x_pos, count_recv, bar_width, label='Received', color='#2ecc71')
    bar_corrupt = ax.bar(x_pos, count_corrupt, bar_width, bottom=count_recv,
                         label='Corrupted', color='#f39c12')
    bar_lost = ax.bar(x_pos, count_lost, bar_width,
                     bottom=[r+c for r,c in zip(count_recv, count_corrupt)],
                     label='Lost', color='#e74c3c')

    ax.set_xticks(x_pos)
    ax.set_xticklabels(dr_labels)
    ax.set_ylim([0, num_rounds + 1])
    ax.set_ylabel('Number of Messages')
    ax.set_xlabel('Data Rate')
    ax.set_title(f'Channel Quality (Distance: 100m, Frame: {frame_len}B)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.ion()
    plt.show()

    def update_chart():
        for i in range(len(dr_labels)):
            bar_recv[i].set_height(count_recv[i])
            bar_corrupt[i].set_height(count_corrupt[i])
            bar_corrupt[i].set_y(count_recv[i])
            bar_lost[i].set_height(count_lost[i])
            bar_lost[i].set_y(count_recv[i] + count_corrupt[i])
        fig.canvas.draw()
        fig.canvas.flush_events()

    # Run experiment
    channel_base = {**default_channel, "frequency": frequency}

    for round_num in range(num_rounds):
        log_info(f"Round {round_num + 1}/{num_rounds}")

        for drname, dridx in zip(dr_labels, range(len(dr_labels))):
            sf = datarates[drname]['spreadingfactor']
            log_debug(f"  Testing {drname} (SF{sf})")

            channel_config = {**channel_base, **datarates[drname]}
            alice.set_lora_channel(**channel_config)
            bob.set_lora_channel(**channel_config)

            bob.receive()
            time.sleep(0.1)

            # Random payload
            frm = [random.randrange(0, 256) for _ in range(frame_len)]

            # Transmit
            txstart = time.time()
            alice.transmit_frame(frm, blocking=True)
            txend = time.time()

            # Wait for reception
            time.sleep(0.3)

            # Check result
            frm_rx = bob.fetch_frame()
            bob.standby()

            if frm_rx is not None:
                if frm_rx['payload'] == frm and not frm_rx['crc_error']:
                    count_recv[dridx] += 1
                    log_success(f"    {drname}: Received (RSSI: {frm_rx['rssi']}dBm)")
                else:
                    count_corrupt[dridx] += 1
                    log_warn(f"    {drname}: Corrupted")
            else:
                count_lost[dridx] += 1
                log_error(f"    {drname}: Lost")

            # Update visualization
            update_chart()

            # Respect duty cycle
            frm_duration = txend - txstart
            remaining = frm_duration / duty_cycle - frm_duration
            if remaining > 0:
                time.sleep(remaining)

            # Cleanup old frames
            channel.cleanup_old_frames(time.time())

    # Final summary
    log_info("=== RESULTS ===")
    print(f"\n{'DR':<6} {'SF':<4} {'Received':<10} {'Corrupted':<12} {'Lost':<10} {'Success %':<10}")
    print("-" * 70)

    results = {}
    for drname, recv, corrupt, lost in zip(dr_labels, count_recv, count_corrupt, count_lost):
        sf = datarates[drname]['spreadingfactor']
        total = num_rounds
        success_rate = (recv / total) * 100 if total > 0 else 0

        results[drname] = {
            'received': recv,
            'corrupted': corrupt,
            'lost': lost,
            'success_rate': success_rate
        }

        color = Colors.GREEN if success_rate >= 80 else Colors.YELLOW if success_rate >= 50 else Colors.RED
        print(f"{color}{drname:<6} {sf:<4} {recv:<10} {corrupt:<12} {lost:<10} {success_rate:>6.1f}%{Colors.RESET}")

    plt.ioff()
    plt.show(block=False)
    input("\nPress Enter to close plot and continue...")
    plt.close()

    return results


# ============================================================================
# MAIN MENU
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    log_info("LoRaWAN Security Experiments - REALISTIC SIMULATION")
    log_info("Simulates: Path loss, fading, collisions, time-on-air, SNR")
    print("="*70 + "\n")

    while True:
        print("\nSelect experiment:")
        print("  1. Single message (test one spreading factor)")
        print("  2. Channel quality (all data rates DR0-DR5)")
        print("  3. Exit")

        choice = input("\nChoice: ").strip()

        if choice == "1":
            sf_input = input("Enter spreading factor (7-12) [default: 12]: ").strip()
            sf = int(sf_input) if sf_input else 12
            if 7 <= sf <= 12:
                first_experiment(spreading_factor=sf)
            else:
                log_error("SF must be between 7 and 12")

        elif choice == "2":
            rounds_input = input("Enter number of rounds per DR [default: 3]: ").strip()
            rounds = int(rounds_input) if rounds_input else 3
            channel_quality_experiment(num_rounds=rounds)

        elif choice == "3":
            log_info("Exiting...")
            break

        else:
            log_error("Invalid choice")
