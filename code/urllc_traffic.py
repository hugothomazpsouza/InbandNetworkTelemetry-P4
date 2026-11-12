import numpy as np
import subprocess
import time
from multiprocessing import Process
import os

def cleanup():
    os.system("pkill iperf")

np.random.seed(1) 

def run_urllc_traffic(
    server_ip, source_ip, bandwidth, duration, interval, lambda_param, dport
):
    try:
        iperf_command = [
            "iperf3",
            "-l", "40",         # Pacote pequeno típico de URLLC
            "-c", server_ip,
            "-b", bandwidth,
            "-t", str(duration),
            "-i", str(interval),
            "-p", str(dport),
            "-B", source_ip,
            "--pacing-timer", "1000",
        ]

        proc = subprocess.Popen(iperf_command)
        proc.wait()

    except KeyboardInterrupt:
        print(f"URLLC traffic to {server_ip}:{dport} stopped.")

if __name__ == "__main__":
    # Ajustei para 10 fluxos para facilitar o troubleshooting inicial (pode subir para 30 depois)
    NUM = 10
    
    # Endereços do seu cenário Vagrant
    TARGET_IP = "192.168.50.12"  # Host-2
    SOURCE_IP = "192.168.50.11"  # Host-1

    BANDWIDTH1 = "320k"  
    BANDWIDTH2 = "320k"  
    
    # Duração ajustada para o seu plano de teste
    DURATION = 60
    INTERVAL = 1
    LAMBDA_RANGE = (0.5, 0.8) 
    DPORT = 5001

    print("Starting URLLC-like Poisson UDP traffic generation...")

    processes = []
    lambda_param = np.random.uniform(*LAMBDA_RANGE)
    for i in range(NUM):
        processes.append(
            Process(
                target=run_urllc_traffic,
                args=(
                    TARGET_IP,
                    SOURCE_IP,
                    BANDWIDTH1 if i%2 else BANDWIDTH2,
                    DURATION,
                    INTERVAL,
                    lambda_param,
                    DPORT+i,
                ),
            )
        )

    for p in processes:
        p.start()

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()
        cleanup()
        print("URLLC traffic generation stopped.")