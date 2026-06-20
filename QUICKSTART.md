# Quick Start Guide

## What You Have

A **realistic LoRa physical layer simulator** - no hardware needed!

## Files You Need

- `lorawan_sim.py` - Main experiments script (RUN THIS)
- `lora_simulator.py` - Physics simulation engine (imported by lorawan_sim.py)
- `requirements.txt` - Python dependencies

## Installation

```bash
# 1. Make sure you're in the project directory
cd /Users/I756187/Documents/sec-master/semosy/lorawan

# 2. Activate virtual environment
source venv/bin/activate

# 3. Dependencies are already installed!
```

## Running Experiments

```bash
# Activate venv (if not already)
source venv/bin/activate

# Run the simulator
python lorawan_sim.py
```

## Interactive Menu

When you run the script, you'll see:

```
Select experiment:
  1. Single message (test one spreading factor)
  2. Channel quality (all data rates DR0-DR5)
  3. Exit
```

### Option 1: Single Message Test
- Tests one spreading factor
- Shows RSSI, SNR, time-on-air
- Try different SFs (7-12) to see range vs. speed tradeoff

### Option 2: Channel Quality
- Tests all 6 data rates (DR0-DR5)
- Shows bar chart visualization
- Multiple rounds per data rate
- See which spreading factors work best at 100m distance

## What It Simulates

- **3 nodes**: Alice (TX), Bob (RX), Mallory (future jammer)
- **100m distance** between Alice and Bob
- **Realistic physics**:
  - Path loss based on distance
  - Fading/shadowing
  - SNR calculations
  - Time-on-air based on LoRa parameters
  - Collision detection

## Example Session

```bash
$ python lorawan_sim.py

Select experiment:
  1. Single message (test one spreading factor)
  2. Channel quality (all data rates DR0-DR5)
  3. Exit

Choice: 1
Enter spreading factor (7-12) [default: 12]: 7

[INFO] === Experiment 1.1: Single Message (SF7) ===
[INFO] Bob is now receiving...
[INFO] Alice transmitting: 'Secure Mobile Systems'
[INFO] Frame transmitted (time-on-air: 0.056s)
[ERROR] No frame received by Bob
# SF7 is too weak for 100m!

Choice: 1
Enter spreading factor (7-12) [default: 12]: 12

[INFO] === Experiment 1.1: Single Message (SF12) ===
[INFO] Alice transmitting: 'Secure Mobile Systems'
[INFO] Frame transmitted (time-on-air: 1.487s)
[INFO] Frame received: 'Secure Mobile Systems'
[INFO]   RSSI: -72 dBm
[INFO]   SNR: 47 dB
[SUCCESS] Message received correctly!
# SF12 works great!
```

## Tips

- **Start with Option 1** to understand one spreading factor
- **Then try Option 2** to compare all data rates
- Lower SF (7-8) = fast but short range
- Higher SF (11-12) = slow but long range
- RSSI < -120 dBm typically means reception fails
- SNR must meet minimum thresholds for each SF

## Next Steps

Once comfortable, check README.md for:
- Understanding LoRa parameters
- Adding jamming experiments
- Modifying node positions/distances
- Extending the simulator
