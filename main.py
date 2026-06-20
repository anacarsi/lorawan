"""
LoRaWAN Security Experiments - Main Entry Point

Professional structure:
- lora_simulator.py: Physics engine
- experiment1_baseline.py: Channel quality experiments
- experiment2_jammer.py: Simple reactive jammer
- experiment3_selective.py: Selective jammer (by DevAddr)
- main.py: This file - central menu
"""

import sys

# ANSI Colors
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'

def print_header():
    print("\n" + "="*70)
    print(f"{Colors.CYAN}{Colors.BOLD}LoRaWAN Security Experiments - Realistic Simulation{Colors.RESET}")
    print("="*70)
    print(f"{Colors.BLUE}Distance: Alice (0,0) <--100m--> Bob (100,0)")
    print(f"Jammer:   Mallory (100,5) - 5m from Bob{Colors.RESET}")
    print("="*70 + "\n")

def print_menu():
    print(f"\n{Colors.BOLD}Select Experiment:{Colors.RESET}")
    print(f"  {Colors.GREEN}1.{Colors.RESET} Experiment 1: Channel Baseline")
    print(f"     - 1.1: Single message test")
    print(f"     - 1.2: Channel quality (all data rates)")
    print(f"\n  {Colors.YELLOW}2.{Colors.RESET} Experiment 2: Simple Reactive Jammer")
    print(f"     - Mallory jams all detected frames")
    print(f"\n  {Colors.RED}3.{Colors.RESET} Experiment 3: Selective Jammer (Coming Soon)")
    print(f"     - Mallory jams only specific DevAddr")
    print(f"\n  {Colors.CYAN}4.{Colors.RESET} About / Help")
    print(f"  {Colors.MAGENTA}5.{Colors.RESET} Exit\n")

def show_about():
    print(f"\n{Colors.BOLD}About This Simulator{Colors.RESET}")
    print("-" * 70)
    print("This is a realistic LoRa physical layer simulator that models:")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Path loss using log-distance model")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Shadowing and fading effects")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Accurate time-on-air calculations")
    print(f"  {Colors.GREEN}✓{Colors.RESET} SNR-based reception success")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Receiver sensitivity thresholds")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Collision detection")
    print("\nNo hardware required - all physics simulated mathematically!")
    print("\nFiles:")
    print(f"  {Colors.CYAN}lora_simulator.py{Colors.RESET}     - Physics engine")
    print(f"  {Colors.CYAN}experiment1_baseline.py{Colors.RESET} - Channel experiments")
    print(f"  {Colors.CYAN}experiment2_jammer.py{Colors.RESET}   - Jamming attacks")
    print(f"  {Colors.CYAN}main.py{Colors.RESET}                - This menu")
    print("-" * 70)

def run_experiment1():
    """Run Experiment 1: Channel Baseline"""
    print(f"\n{Colors.BOLD}Experiment 1: Channel Baseline{Colors.RESET}")
    print("Choose sub-experiment:")
    print("  1. Single message (one spreading factor)")
    print("  2. Channel quality (all data rates)")
    print("  3. Test all SFs (SF7-SF12)")
    print("  0. Back to main menu")

    choice = input("\nChoice: ").strip()

    if choice == "1":
        from experiment1_baseline import single_message_test
        sf = input("Enter spreading factor (7-12) [default: 12]: ").strip()
        sf = int(sf) if sf else 12
        single_message_test(spreading_factor=sf)
    elif choice == "2":
        from experiment1_baseline import channel_quality_test
        rounds = input("Enter number of rounds [default: 3]: ").strip()
        rounds = int(rounds) if rounds else 3
        channel_quality_test(num_rounds=rounds)
    elif choice == "3":
        from experiment1_baseline import test_all_spreading_factors
        test_all_spreading_factors()
    elif choice == "0":
        return
    else:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid choice")

def run_experiment2():
    """Run Experiment 2: Simple Jammer"""
    print(f"\n{Colors.BOLD}Experiment 2: Simple Reactive Jammer{Colors.RESET}")
    print("Mallory (5m from Bob) will jam Alice's transmissions (100m away)")
    print("\nThis experiment tests different frame lengths:")
    print("  - 1 byte (minimal)")
    print("  - 3 bytes (short)")
    print("  - 12 bytes (LoRaWAN minimum)")

    input("\nPress Enter to start...")

    from experiment2_jammer import simple_jammer_experiment
    simple_jammer_experiment(num_rounds=2, frame_lengths=[1, 3, 12])

def run_experiment3():
    """Run Experiment 3: Selective Jammer"""
    print(f"\n{Colors.YELLOW}[WARN]{Colors.RESET} Experiment 3 not yet implemented")
    print("Coming soon: Selective jamming based on LoRaWAN DevAddr")

def main():
    """Main entry point"""
    print_header()

    while True:
        print_menu()
        choice = input(f"{Colors.BOLD}Choice: {Colors.RESET}").strip()

        if choice == "1":
            run_experiment1()
        elif choice == "2":
            run_experiment2()
        elif choice == "3":
            run_experiment3()
        elif choice == "4":
            show_about()
        elif choice == "5":
            print(f"\n{Colors.GREEN}[INFO]{Colors.RESET} Exiting...")
            sys.exit(0)
        else:
            print(f"{Colors.RED}[ERROR]{Colors.RESET} Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[WARN]{Colors.RESET} Interrupted by user")
        sys.exit(0)
