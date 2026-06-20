# LoRaWAN Security Experiments

Security analysis and experimentation framework for LoRaWAN. Includes both **realistic simulation** and support for **real hardware** via ChirpOTLE.

## Features

- **Realistic LoRa Physical Layer Simulation**
  - Path loss and fading models
  - Accurate time-on-air calculations
  - Collision detection
  - SNR-based reception success
  - Capture effect simulation

- **Experiments Implemented**
  - Experiment 1.1: Single message testing
  - Experiment 1.2: Channel quality across all EU868 data rates
  - (More experiments coming: jamming, selective attacks)

- **Colored logging** (INFO, SUCCESS, WARN, ERROR, DEBUG)
- **Real-time matplotlib visualization**

## Quick Start (Simulation Mode)

```bash
# Clone the repository
git clone https://github.com/anacarsi/lorawan.git
cd lorawan

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the simulator
python lorawan_sim.py
```

## Files

- `lorawan_sim.py` - Main experiments with realistic simulation
- `lora_simulator.py` - Physical layer simulator engine
- `lorawan.py` - Original script for real hardware (requires ChirpOTLE)
- `lorawan_demo.py` - Simple demo version

## Simulation vs Real Hardware

### Using the Simulator (No Hardware Needed)

```bash
python lorawan_sim.py
```

**What it simulates:**
- 3 nodes: Alice (transmitter), Bob (receiver), Mallory (jammer)
- 100m distance between Alice and Bob
- Realistic path loss (log-distance model)
- Shadowing/fading effects
- Time-on-air based on LoRa modulation parameters
- SNR requirements for successful demodulation
- Collision detection

**Perfect for:**
- Learning LoRaWAN concepts
- Testing attack strategies
- Understanding spreading factor tradeoffs
- Prototyping experiments before hardware deployment

### Using Real Hardware

For real LoRa experiments, you need:
1. **Hardware**: LoRa modules (e.g., Pycom LoPy4) connected to Raspberry Pis
2. **ChirpOTLE**: Framework to control the hardware
3. **Network**: SSH access to the nodes

**Setup instructions:**

1. Clone and setup ChirpOTLE:
```bash
git clone https://github.com/seemoo-lab/chirpotle.git
cd chirpotle
git submodule update --init --recursive submodules/tpy
```

2. Install tpycontrol:
```bash
cd chirpotle/submodules/tpy/controller
pip install -e .
```

3. Install chirpotle:
```bash
cd ../../controller/chirpotle
pip install -e .
```

4. Configure your hardware in `~/.chirpotle/config`

5. Run experiments:
```bash
python lorawan.py
```

## Experiments

### Experiment 1.1: Single Message

Tests basic LoRa communication with one spreading factor.

- Configurable SF (7-12)
- Shows RSSI, SNR, CRC errors
- Measures time-on-air

**Key Learning:** Higher SF = longer range but slower transmission

### Experiment 1.2: Channel Quality

Tests all EU868 data rates (DR0-DR5) with multiple rounds.

- Visualizes success/corruption/loss rates
- Compares all spreading factors
- Real-time updating bar chart

**Key Learning:** SF vs. distance tradeoff

## LoRa Parameters

### EU868 Data Rates

| Data Rate | Spreading Factor | Bandwidth |
|-----------|------------------|-----------|
| DR0       | 12               | 125 kHz   |
| DR1       | 11               | 125 kHz   |
| DR2       | 10               | 125 kHz   |
| DR3       | 9                | 125 kHz   |
| DR4       | 8                | 125 kHz   |
| DR5       | 7                | 125 kHz   |

### Spreading Factor Tradeoffs

| SF  | Range        | Speed        | Time-on-Air (23B) |
|-----|--------------|--------------|-------------------|
| 7   | ~2 km        | Fastest      | ~56 ms            |
| 8   | ~3 km        | Fast         | ~103 ms           |
| 9   | ~5 km        | Medium       | ~205 ms           |
| 10  | ~7 km        | Slow         | ~371 ms           |
| 11  | ~10 km       | Slower       | ~741 ms           |
| 12  | ~15 km       | Slowest      | ~1319 ms          |

## Architecture

### Simulation Architecture

```
┌─────────────────────┐
│   lorawan_sim.py    │  Experiments & visualization
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ lora_simulator.py   │  Physical layer simulation
│                     │
│ - Path loss model   │
│ - Time-on-air calc  │
│ - Collision detect  │
│ - SNR evaluation    │
└─────────────────────┘
```

### Real Hardware Architecture

```
┌─────────────┐                  ┌─────────────┐
│   Alice     │                  │   Bob       │
│  (LoPy4)    │───── RF ────────>│  (LoPy4)    │
│ Transmitter │   868 MHz        │  Receiver   │
└──────┬──────┘                  └──────┬──────┘
       │                                │
       │ USB/Serial                     │ USB/Serial
       │                                │
┌──────▼──────┐                  ┌──────▼──────┐
│   RPi #1    │                  │   RPi #2    │
└──────┬──────┘                  └──────┬──────┘
       │                                │
       │ SSH + RPC                      │ SSH + RPC
       │                                │
       └────────────┬───────────────────┘
                    │
             ┌──────▼──────┐
             │ Controller  │
             │  (Your Mac) │
             │             │
             │ ChirpOTLE   │
             └─────────────┘
```

## Legal Notice

These experiments are for **educational purposes only**. 

- Only test on networks you own or have explicit permission to test
- Jamming attacks may be illegal in your jurisdiction
- Respect ISM band regulations and duty cycle limits
- Be aware of others using the frequency band

## Future Experiments

Coming soon:
- Experiment 2: Simple reactive jammer
- Experiment 3: Selective jammer (by DevAddr)
- Experiment 4: Wormhole attacks
- Experiment 5: Frame replay attacks
- Experiment 6: ACK spoofing

## Contributing

Feel free to:
- Add new experiments
- Improve the simulation accuracy
- Report issues
- Submit pull requests

## References

- [LoRaWAN Specification](https://lora-alliance.org/resource_hub/lorawan-specification-v1-1/)
- [ChirpOTLE Framework](https://github.com/seemoo-lab/chirpotle)
- [LoRa Modulation Basics](https://www.semtech.com/lora)
