<div align="center">

```
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   ██╗      ██████╗ ██████╗  █████╗ ██╗    ██╗ █████╗ ███╗   ██╗        ║
║   ██║     ██╔═══██╗██╔══██╗██╔══██╗██║    ██║██╔══██╗████╗  ██║        ║
║   ██║     ██║   ██║██████╔╝███████║██║ █╗ ██║███████║██╔██╗ ██║        ║
║   ██║     ██║   ██║██╔══██╗██╔══██║██║███╗██║██╔══██║██║╚██╗██║        ║
║   ███████╗╚██████╔╝██║  ██║██║  ██║╚███╔███╔╝██║  ██║██║ ╚████║        ║
║   ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═══╝        ║
║                                                                          ║
║              SECURITY EXPERIMENTS & SIMULATION FRAMEWORK                ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

<img src="https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/LoRa-868MHz-orange.svg?style=for-the-badge&logo=lorawan&logoColor=white" alt="LoRa">
<img src="https://img.shields.io/badge/Security-Research-red.svg?style=for-the-badge&logo=security&logoColor=white" alt="Security">
<img src="https://img.shields.io/badge/Status-Active-success.svg?style=for-the-badge" alt="Status">

**A comprehensive security analysis and experimentation framework for LoRaWAN networks**  
*Featuring realistic physical layer simulation and real hardware support via ChirpOTLE*

---

### Quick Navigation
[Features](#features) • [Quick Start](#quick-start) • [Experiments](#experiments) • [Architecture](#architecture) • [Hardware Setup](#using-real-hardware)

</div>

---

## Features

<div align="center">

```
     Alice                    Bob                    Mallory
   (Node 1)                (Node 2)                (Jammer)
      |                       |                       |
      |    868 MHz LoRa RF    |                       |
      +----------+------------+                       |
                 |                                    |
                 |  <------- ATTACK VECTOR -----------+
                 |
            LoRa Gateway
```

</div>

### Realistic Physical Layer Simulation

- Path Loss & Fading - Log-distance propagation model with shadowing  
- Time-on-Air Calculations - Accurate LoRa modulation timing  
- Collision Detection - Realistic packet collision scenarios  
- SNR-Based Reception - Signal-to-noise ratio evaluation  
- Capture Effect - Stronger signal dominance modeling  

### Security Experiments

- **Experiment 1.1** - Single message testing across all spreading factors
- **Experiment 1.2** - Channel quality analysis (DR0-DR5)
- **Experiment 2** - Reactive jamming attacks
- **Experiment 3** - Selective jamming by DevAddr
- **Experiment 4** - Wormhole attacks
- **Experiment 5** - Frame replay attacks

### Visualization & Logging

- Real-time matplotlib visualizations
- Color-coded logging (INFO, SUCCESS, WARN, ERROR, DEBUG)
- Success/corruption/loss rate charts
- SNR and RSSI measurements

---

## Quick Start

### Simulation Mode (No Hardware Required)

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

<div align="center">

```
┌─────────────────────────────────────────────────────────────┐
│  SELECT AN EXPERIMENT                                       │
├─────────────────────────────────────────────────────────────┤
│  [1] Single message (configurable SF)                       │
│  [2] Test all spreading factors (DR0-DR5)                   │
│  [3] Reactive jammer experiment                             │
│  [4] Exit                                                    │
└─────────────────────────────────────────────────────────────┘
```

</div>

---

## LoRa Parameters

### EU868 Data Rates

| Data Rate | Spreading Factor | Bandwidth | Range | Time-on-Air (23B) |
|:---------:|:----------------:|:---------:|:-----:|:-----------------:|
| DR0 | SF12 | 125 kHz | ~15 km | 1319 ms |
| DR1 | SF11 | 125 kHz | ~10 km | 741 ms |
| DR2 | SF10 | 125 kHz | ~7 km | 371 ms |
| DR3 | SF9 | 125 kHz | ~5 km | 205 ms |
| DR4 | SF8 | 125 kHz | ~3 km | 103 ms |
| DR5 | SF7 | 125 kHz | ~2 km | 56 ms |

**Tradeoff:** Higher SF provides longer range but slower transmission speed

---

## Experiments

### Experiment 1.1: Single Message Testing

Tests basic LoRa communication with configurable spreading factor.

**Configurable Parameters:**
- Spreading Factor (SF7-SF12)
- Transmission power
- Distance between nodes

**Measurements:**
- RSSI (Received Signal Strength Indicator)
- SNR (Signal-to-Noise Ratio)
- CRC errors
- Time-on-air

**Objective:** Observe the SF vs. range vs. speed tradeoff

---

### Experiment 1.2: Channel Quality Analysis

Tests all EU868 data rates with multiple rounds and real-time visualization.

<div align="center">

```
Success Rate by Spreading Factor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SF7  ████████░░ 80%
SF8  ██████████ 95%
SF9  ██████████ 100%
SF10 ██████████ 100%
SF11 ██████████ 100%
SF12 ██████████ 100%
```

</div>

**Objective:** Compare success/corruption/loss rates across all spreading factors

---

### Experiment 2: Reactive Jammer

Demonstrates jamming attacks on LoRaWAN communication.

<div align="center">

```
┌───────────────────────────────────────────────────────┐
│                 JAMMING SCENARIO                      │
├───────────────────────────────────────────────────────┤
│                                                       │
│    Alice (TX)  ------+                                │
│                      +---> Bob (RX)                   │
│                            ^                          │
│                            |                          │
│                         JAMMED                        │
│                            |                          │
│    Mallory (Jammer) -------+                          │
│                                                       │
└───────────────────────────────────────────────────────┘
```

</div>

**Objective:** Analyze jamming effectiveness across different spreading factors

---

## Architecture

### Simulation Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   lorawan_sim.py                        │
│         (Experiments & Visualization Layer)             │
└────────────────────┬────────────────────────────────────┘
                     |
                     v
┌─────────────────────────────────────────────────────────┐
│               lora_simulator.py                         │
│         (Physical Layer Simulation Engine)              │
│                                                         │
│  - Path loss model (log-distance + shadowing)          │
│  - Time-on-air calculation (LoRa modulation)           │
│  - Collision detection                                 │
│  - SNR evaluation & demodulation                       │
│  - Capture effect                                      │
└─────────────────────────────────────────────────────────┘
```

### Real Hardware Architecture

```
┌─────────────┐                           ┌─────────────┐
│   Alice     │                           │   Bob       │
│  (LoPy4)    │─────── 868 MHz ──────────>│  (LoPy4)    │
│ Transmitter │      LoRa RF              │  Receiver   │
└──────+──────┘                           └──────+──────┘
       |                                         |
       | USB/Serial                              | USB/Serial
       |                                         |
┌──────v──────┐                           ┌──────v──────┐
│   RPi #1    │                           │   RPi #2    │
└──────+──────┘                           └──────+──────┘
       |                                         |
       | SSH + RPC                               | SSH + RPC
       |                                         |
       +─────────────────┬───────────────────────+
                         |
                  ┌──────v──────┐
                  │ Controller  │
                  │  (Your PC)  │
                  │             │
                  │ ChirpOTLE   │
                  └─────────────┘
```

---

## Using Real Hardware

For real LoRa experiments, you need:

### Hardware Requirements
- LoRa modules (e.g., Pycom LoPy4)
- Raspberry Pis
- 868 MHz antennas
- Network connectivity (SSH)

### Setup Instructions

<details>
<summary><b>Click to expand setup guide</b></summary>

1. **Clone and setup ChirpOTLE:**
```bash
git clone https://github.com/seemoo-lab/chirpotle.git
cd chirpotle
git submodule update --init --recursive submodules/tpy
```

2. **Install tpycontrol:**
```bash
cd chirpotle/submodules/tpy/controller
pip install -e .
```

3. **Install chirpotle:**
```bash
cd ../../controller/chirpotle
pip install -e .
```

4. **Configure your hardware** in `~/.chirpotle/config`

5. **Run experiments:**
```bash
python lorawan.py
```

</details>

---

## Repository Structure

```
lorawan/
├── lorawan_sim.py          # Main experiments with simulation
├── lora_simulator.py       # Physical layer simulator engine
├── experiment2_jammer.py   # Jamming attack experiments
├── lorawan.py              # Real hardware experiments (ChirpOTLE)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Legal Notice

<div align="center">

```
┌─────────────────────────────────────────────────────────────┐
│  WARNING: EDUCATIONAL PURPOSES ONLY                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  - Only test on networks you own or have permission to test│
│  - Jamming attacks may be illegal in your jurisdiction     │
│  - Respect ISM band regulations and duty cycle limits      │
│  - Be aware of other users on the frequency band           │
│  - This software is for security research and education    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

</div>

---

## Roadmap

- [x] Basic LoRa physical layer simulation
- [x] Spreading factor comparison experiments
- [x] Reactive jamming experiment
- [ ] Selective jamming by DevAddr
- [ ] Wormhole attacks
- [ ] Frame replay attacks
- [ ] ACK spoofing
- [ ] Join request manipulation
- [ ] Downlink attacks

---

## Contributing

Contributions are welcome. Feel free to:

- Report bugs and issues
- Suggest new experiments
- Improve simulation accuracy
- Enhance documentation
- Submit pull requests

---

## References

- [LoRaWAN Specification v1.1](https://lora-alliance.org/resource_hub/lorawan-specification-v1-1/)
- [ChirpOTLE Framework](https://github.com/seemoo-lab/chirpotle)
- [LoRa Modulation Basics](https://www.semtech.com/lora)
- [LoRaWAN Security Whitepaper](https://lora-alliance.org/resource_hub/lorawanr-security-whitepaper/)

---

<div align="center">

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  Made for security research and education                            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

**[Back to Top](#)**

</div>
