# LoRaWAN Security Experiments

Security analysis and experimentation framework for LoRaWAN using ChirpOTLE.

## Experiments

### Experiment 1: Channel Baseline
- **1.1 Single Message**: Basic TX/RX test across different spreading factors
- **1.2 Multiple Channels**: Channel quality testing across all EU868 data rates (DR0-DR5)

### Experiment 2: Simple Jammer
Reactive jamming attacking all LoRa frames.

### Experiment 3: Selective Jammer  
Targeted jamming based on device address (DevAddr).

## Setup

```bash
# Install dependencies
pip install chirpotle matplotlib ipython

# Run experiments
python lorawan.py
```

## Hardware

- Alice: Transmitter (lecture hall)
- Bob: Receiver (office)
- Mallory: Jammer/Attacker (office)

## Legal Notice

These experiments are for educational purposes only. Only test on networks you own or have explicit permission to test.
