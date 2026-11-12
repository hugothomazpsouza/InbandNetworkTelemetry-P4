#!/usr/bin/env python3
import subprocess
import time

# Target configuration
TARGET_IP = "192.168.56.201"
PORT = "80"

def cleanup():
    """SAFETY CLEANUP: Ensure no flood processes are stuck from previous tests"""
    subprocess.run(
        ["sudo", "pkill", "-f", "hping3"], 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )

def main():
    cleanup()

    print("[0s] Experiment started. Normal traffic flow...")
    print("Waiting 15 seconds...")
    time.sleep(15)

    print(f"[15s] INJECTING CONGESTION (UDP Flood from Host-3 to {TARGET_IP})...")
    
    # Start hping3 in the background
    # stdout and stderr are sent to DEVNULL to hide logs from the terminal
    hping_cmd = ["sudo", "hping3", "-2", "--flood", "-p", PORT, TARGET_IP]
    flood_process = subprocess.Popen(
        hping_cmd, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )

    print("Network under flood attack. Waiting 20 seconds...")
    time.sleep(20)

    print("[35s] REMOVING CONGESTION (Stopping UDP Flood attack)...")
    # Kill the specific hping3 process we started
    flood_process.kill()
    
    # Extra cleanup guarantee
    cleanup()

    print("Test complete! Traffic normalized.")

if __name__ == "__main__":
    main()
