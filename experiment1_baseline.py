"""
Experiment 1: Channel Baseline

Tests basic LoRa communication without attacks.
Measures channel quality across different spreading factors and data rates.
"""

import matplotlib
import matplotlib.pyplot as plt
import time
import random
from typing import Dict

from lora_simulator import SimulatedLoRaNode, LoRaChannel

# ANSI Colors
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

# EU868 Data Rates
DATARATES = {
    "DR0": {"spreadingfactor": 12, "bandwidth": 125},
    "DR1": {"spreadingfactor": 11, "bandwidth": 125},
    "DR2": {"spreadingfactor": 10, "bandwidth": 125},
    "DR3": {"spreadingfactor":  9, "bandwidth": 125},
    "DR4": {"spreadingfactor":  8, "bandwidth": 125},
    "DR5": {"spreadingfactor":  7, "bandwidth": 125},
}

DEFAULT_CHANNEL = {
    'frequency': 868100000,
    'bandwidth': 125,
    'codingrate': 5,
    'invertiqtx': True,
    'invertiqrx': False,
    'explicitheader': True,
}


def single_message_test(spreading_factor: int = 12, payload_str: str = 'Secure Mobile Systems') -> dict:
    """
    Experiment 1.1: Single Message Test

    Tests one message at one spreading factor.
    Shows RSSI, SNR, and reception success.
    """
    log_info(f"=== Experiment 1.1: Single Message (SF{spreading_factor}) ===")

    # Setup
    channel = LoRaChannel()
    alice = SimulatedLoRaNode('alice', (0, 0), channel)
    bob = SimulatedLoRaNode('bob', (100, 0), channel)

    channel_config = {**DEFAULT_CHANNEL, 'spreadingfactor': spreading_factor}
    alice.set_lora_channel(**channel_config)
    bob.set_lora_channel(**channel_config)

    # Bob listens
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

    # Wait for reception
    time.sleep(0.5)

    # Check result
    recv_frame = bob.fetch_frame()
    bob.standby()
    channel.cleanup_old_frames(time.time())

    # Process
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
        log_warn("Try higher SF (lower DR) for longer range")

    return result


def channel_quality_test(num_rounds: int = 3, frame_len: int = 12,
                         frequency: int = 869525000, duty_cycle: float = 0.80) -> dict:
    """
    Experiment 1.2: Channel Quality Test

    Tests all data rates (DR0-DR5) with multiple rounds.
    Shows success/corruption/loss rates with visualization.
    """
    log_info("=== Experiment 1.2: Channel Quality by Data Rate ===")
    log_info(f"Testing {len(DATARATES)} data rates with {num_rounds} rounds each")

    # Setup
    channel = LoRaChannel()
    alice = SimulatedLoRaNode('alice', (0, 0), channel)
    bob = SimulatedLoRaNode('bob', (100, 0), channel)

    dr_labels = sorted(DATARATES.keys())
    count_recv = [0 for _ in dr_labels]
    count_lost = [0 for _ in dr_labels]
    count_corrupt = [0 for _ in dr_labels]

    # Create plot
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
    channel_base = {**DEFAULT_CHANNEL, "frequency": frequency}

    for round_num in range(num_rounds):
        log_info(f"Round {round_num + 1}/{num_rounds}")

        for drname, dridx in zip(dr_labels, range(len(dr_labels))):
            sf = DATARATES[drname]['spreadingfactor']
            log_debug(f"  Testing {drname} (SF{sf})")

            channel_config = {**channel_base, **DATARATES[drname]}
            alice.set_lora_channel(**channel_config)
            bob.set_lora_channel(**channel_config)

            bob.receive()
            time.sleep(0.1)

            # Random payload
            frm = [random.randint(0, 256) for _ in range(frame_len)]

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

            update_chart()

            # Duty cycle
            frm_duration = txend - txstart
            remaining = frm_duration / duty_cycle - frm_duration
            if remaining > 0:
                time.sleep(remaining)

            channel.cleanup_old_frames(time.time())

    # Results
    log_info("=== RESULTS ===")
    print(f"\n{'DR':<6} {'SF':<4} {'Received':<10} {'Corrupted':<12} {'Lost':<10} {'Success %':<10}")
    print("-" * 70)

    results = {}
    for drname, recv, corrupt, lost in zip(dr_labels, count_recv, count_corrupt, count_lost):
        sf = DATARATES[drname]['spreadingfactor']
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
    input("\nPress Enter to close plot...")
    plt.close()

    return results


def test_all_spreading_factors(payload_str: str = 'Secure Mobile Systems'):
    """
    Experiment 1.3: Test All Spreading Factors

    Runs single message test for SF7 through SF12.
    Shows how range improves with higher SF.
    """
    log_info("=== Testing All Spreading Factors (SF7-SF12) ===")

    results = []
    for sf in range(7, 13):
        result = single_message_test(spreading_factor=sf, payload_str=payload_str)
        results.append(result)
        time.sleep(0.5)

    # Summary
    log_info("\n=== SUMMARY ===")
    print(f"{'SF':<4} {'Status':<10} {'RSSI (dBm)':<12} {'SNR (dB)':<10} {'ToA (s)':<10}")
    print("-" * 50)

    for sf, result in zip(range(7, 13), results):
        status = "SUCCESS" if result['success'] else "FAILED"
        rssi = f"{result['rssi']}" if result['rssi'] is not None else "N/A"
        snr = f"{result['snr']}" if result['snr'] is not None else "N/A"
        toa = f"{result['time_on_air']:.3f}"

        color = Colors.GREEN if result['success'] else Colors.RED
        print(f"{color}{sf:<4} {status:<10} {rssi:<12} {snr:<10} {toa:<10}{Colors.RESET}")

    return results


if __name__ == "__main__":
    # If run directly, offer menu
    print("\nExperiment 1: Channel Baseline")
    print("1. Single message")
    print("2. Channel quality")
    print("3. All spreading factors")

    choice = input("\nChoice: ").strip()

    if choice == "1":
        single_message_test()
    elif choice == "2":
        channel_quality_test()
    elif choice == "3":
        test_all_spreading_factors()
    else:
        print("Invalid choice")
