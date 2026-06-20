# matplotlib widget

import matplotlib
import matplotlib.pyplot as plt
from IPython import display

import threading
import time
import traceback
import random
import sys

from chirpotle.context import tpy_from_context
from chirpotle.dissect.base import (
    DeviceSession,
    MType)
from chirpotle.dissect.v102 import (
    LoRaWANMessage_V1_0_2)
from chirpotle.tools import (
    Rx2Wormhole,
    DownlinkDelayedWormhole,
    seq_eq)

# ANSI Color codes for logging
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

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


tc, devices = tpy_from_context()

# Nodes in the lecture hall
alice = tc.nodes['lecture_hall']['alice']

# Nodes in the Cysec Building
bob     = tc.nodes['office']['bob']
mallory = tc.nodes['office']['mallory']

all_nodes = [alice, bob, mallory]
node_names = ["alice", "bob", "mallory"]
for node, name in zip(all_nodes, node_names):
    log_info(f"Sending {name} to standby")
    node.standby()


default_channel = {
    'frequency': 868100000, # Hz
    'bandwidth': 125, # kHz
    'spreadingfactor': 7,
    'syncword': 18, # private LoRa network
    'codingrate': 5, # 4/5 error coding
    'invertiqtx': True,
    'invertiqrx': False, # we invert this, so nodes can talk to each other instead to a Gateway (for now)
    'explicitheader': True, # frame contains header and length field
}

# LoRaWAN data rates according to EU868 regional specification
datarates = {
    "DR0": {"spreadingfactor": 12, "bandwidth": 125},
    "DR1": {"spreadingfactor": 11, "bandwidth": 125},
    "DR2": {"spreadingfactor": 10, "bandwidth": 125},
    "DR3": {"spreadingfactor":  9, "bandwidth": 125},
    "DR4": {"spreadingfactor":  8, "bandwidth": 125},
    "DR5": {"spreadingfactor":  7, "bandwidth": 125},
    # "DR6": {"spreadingfactor":  7, "bandwidth": 250}, # we limit experiments to DR0..5 only
}

def test_spreading_factors(payload_str: str = 'Secure Mobile Systems') -> None:
    """
    Test communication across all spreading factors (SF7-SF12).

    This demonstrates the tradeoff between range and speed:
    - SF7: Fastest, shortest range
    - SF12: Slowest, longest range

    Each step up in SF roughly doubles the transmission time but increases range.
    """
    log_info("=== Testing All Spreading Factors ===")
    log_info("SF7 = Fast/Short Range -> SF12 = Slow/Long Range")

    results = []
    for sf in range(7, 13):
        result = first_experiment(spreading_factor=sf, payload_str=payload_str)
        results.append(result)
        time.sleep(1)  # Brief pause between tests

    # Summary
    log_info("=== SUMMARY ===")
    print(f"{'SF':<4} {'Status':<10} {'RSSI (dBm)':<12} {'SNR (dB)':<10}")
    print("-" * 40)
    for sf, result in zip(range(7, 13), results):
        status = "SUCCESS" if result['success'] else "FAILED"
        rssi = f"{result['rssi']}" if result['rssi'] is not None else "N/A"
        snr = f"{result['snr']}" if result['snr'] is not None else "N/A"

        if result['success']:
            print(f"{Colors.GREEN}{sf:<4} {status:<10} {rssi:<12} {snr:<10}{Colors.RESET}")
        else:
            print(f"{Colors.RED}{sf:<4} {status:<10} {rssi:<12} {snr:<10}{Colors.RESET}")


def first_experiment(spreading_factor: int = 12, payload_str: str = 'Secure Mobile Systems') -> dict:
    """
    Experiment 1.1: Single Message Test

    Tests basic LoRa communication between Alice (transmitter) and Bob (receiver).
    Higher spreading factors provide longer range but slower transmission.

    Args:
        spreading_factor: LoRa SF (7-12). Higher = longer range, slower speed
        payload_str: Message to transmit

    Returns:
        dict with 'success', 'transmitted', 'received', 'rssi', 'snr'
    """
    log_info(f"=== Experiment 1.1: Single Message (SF{spreading_factor}) ===")

    # Create channel configuration with specified spreading factor
    channel = {**default_channel, 'spreadingfactor': spreading_factor}

    # Reset: Put all nodes into standby mode and configure the channel
    for node, name in zip(all_nodes, node_names):
        log_debug(f"Configuring {name} to standby with SF{spreading_factor}")
        node.standby()
        node.set_lora_channel(**channel)

    # Bob in the Cysec Building will receive the message
    bob.receive()
    log_info("Bob is now receiving...")
    time.sleep(0.5)  # Give Bob time to enter receive mode

    # Alice sends the message (blocking ensures transmission completes)
    log_info(f"Alice transmitting: '{payload_str}'")
    alice.transmit_frame([ord(c) for c in payload_str], blocking=True)
    log_info("Frame transmitted by Alice")

    # Wait for transmission to complete and Bob to process
    time.sleep(1)

    # Check what Bob received
    recv_frame = bob.fetch_frame()
    bob.standby()  # Put Bob back to standby after receiving

    # Process results
    result = {
        'success': False,
        'transmitted': payload_str,
        'received': None,
        'rssi': None,
        'snr': None,
        'crc_error': None
    }

    if recv_frame is not None:
        received_str = "".join([chr(b) for b in recv_frame['payload']])
        result['received'] = received_str
        result['rssi'] = recv_frame['rssi']
        result['snr'] = recv_frame['snr']
        result['crc_error'] = recv_frame.get('crc_error', False)
        result['success'] = (received_str == payload_str) and not result['crc_error']

        log_info(f"Frame received: '{received_str}'")
        log_info(f"  RSSI: {result['rssi']} dBm (signal strength)")
        log_info(f"  SNR: {result['snr']} dB (signal-to-noise ratio)")
        log_info(f"  CRC Error: {result['crc_error']}")

        if result['success']:
            log_success("Message received correctly!")
        else:
            log_error(f"MISMATCH: Expected '{payload_str}' but got '{received_str}'")
    else:
        log_error("No frame received by Bob")
        log_warn("Possible causes:")
        log_warn("  - Signal too weak (increase SF or reduce distance)")
        log_warn("  - Nodes not synchronized")
        log_warn("  - Interference on the channel")

    return result


def channel_quality_experiment(num_rounds: int = 2, frame_len: int = 12,
                               frequency: int = 869525000, duty_cycle: float = 0.80) -> dict:
    """
    Experiment 1.2: Multiple Channels

    Test multiple data rates (DR0-DR5) to evaluate channel quality.
    Measures received, lost, and corrupted frames for each data rate.

    Args:
        num_rounds: Number of test rounds per data rate
        frame_len: Length of random test frames in bytes
        frequency: Transmission frequency in Hz
        duty_cycle: Maximum allowed duty cycle (0.80 = 80%)

    Returns:
        dict with results per data rate
    """
    log_info("=== Experiment 1.2: Multiple Channels ===")
    log_info(f"Testing {len(datarates)} data rates with {num_rounds} rounds each")
    log_info(f"Frame length: {frame_len} bytes, Frequency: {frequency} Hz")

    # Use the data rates to get labels for the plot
    dr_labels = sorted(datarates.keys())

    # Received message count (per data rate)
    count_recv = [0 for _ in dr_labels]

    # Lost message count (per data rate)
    count_lost = [0 for _ in dr_labels]

    # Corrupted message count (per data rate)
    count_corrupt = [0 for _ in dr_labels]

    # matplotlib plot
    fig, ax = plt.subplots()

    # Stack the bars for each data rate
    bar_width = 0.35
    bar_recv = ax.bar(dr_labels, count_recv, bar_width, label='Received')
    bar_lost = ax.bar(dr_labels, count_lost, bar_width, bottom=count_recv, label='Lost')
    bar_corrupt = ax.bar(dr_labels, count_corrupt, bar_width, bottom=count_lost, label='Corrupted')

    # Legends and labels
    ax.set_ylim([0, num_rounds])
    ax.set_ylabel('Number of Messages')
    ax.set_title(f'Channel Quality by Data Rate (EU868, frame length={frame_len})')
    ax.legend()

    # Function to update the data after each frame
    def update_chart():
        for n in range(len(dr_labels)):
            bar_recv[n].set_height(count_recv[n])
            bar_lost[n].set_height(count_lost[n])
            bar_lost[n].set_y(count_recv[n])
            bar_corrupt[n].set_height(count_corrupt[n])
            bar_corrupt[n].set_y(count_recv[n] + count_lost[n])
        fig.canvas.flush_events()
        fig.canvas.draw()

    plt.show()

    # Base channel configuration
    channel = {**default_channel, "frequency": frequency}

    # Run experiment
    for round_num in range(num_rounds):
        log_info(f"Starting round {round_num + 1}/{num_rounds}")

        for drname, dridx in zip(dr_labels, range(len(dr_labels))):
            log_debug(f"Testing {drname} (SF{datarates[drname]['spreadingfactor']})")

            # Create channel for this run and set it (this will also send devices to standby)
            channel_run = {**channel, **datarates[drname]}
            alice.set_lora_channel(**channel_run)
            bob.set_lora_channel(**channel_run)

            # Make bob the receiver
            bob.receive()

            # Create random frame data
            frm = [random.randrange(0, 256) for _ in range(frame_len)]

            # Send and capture time
            txstart = time.time()
            alice.transmit_frame(frm, blocking=True)
            txend = time.time()

            # Wait a short moment so that the receiver is done
            time.sleep(0.2)

            # Check if the receiver got the same frame
            frm_state = "lost"
            frm_rx = bob.fetch_frame()
            while frm_rx is not None and frm_state != "received":
                if frm_rx['payload'] == frm:
                    frm_state = "received"
                elif len(frm_rx['payload']) == frame_len:
                    frm_state = "corrupted"
                frm_rx = bob.fetch_frame()
            bob.standby()

            # Update the data
            if frm_state == "received":
                count_recv[dridx] += 1
                log_success(f"{drname}: Frame received correctly")
            elif frm_state == "corrupted":
                count_corrupt[dridx] += 1
                log_warn(f"{drname}: Frame corrupted")
            else:
                count_lost[dridx] += 1
                log_error(f"{drname}: Frame lost")

            # Update the chart to show real-time results
            update_chart()

            # Wait the remaining time of the duty cycle
            frm_duration = txend - txstart
            remaining_time = frm_duration / duty_cycle - frm_duration
            if remaining_time > 0:
                time.sleep(remaining_time)

    # Results summary
    log_info("=== EXPERIMENT COMPLETE ===")
    print(f"\n{'Data Rate':<10} {'Received':<10} {'Lost':<10} {'Corrupted':<10} {'Success %':<10}")
    print("-" * 60)

    results = {}
    for drname, recv, lost, corrupt in zip(dr_labels, count_recv, count_lost, count_corrupt):
        total = num_rounds
        success_rate = (recv / total) * 100 if total > 0 else 0
        results[drname] = {
            'received': recv,
            'lost': lost,
            'corrupted': corrupt,
            'success_rate': success_rate
        }

        color = Colors.GREEN if success_rate >= 80 else Colors.YELLOW if success_rate >= 50 else Colors.RED
        print(f"{color}{drname:<10} {recv:<10} {lost:<10} {corrupt:<10} {success_rate:>6.1f}%{Colors.RESET}")

    return results