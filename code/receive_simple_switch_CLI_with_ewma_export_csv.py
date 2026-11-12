#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import os
import time
import csv
from datetime import datetime

current_path_port = 1  # 1 = Rota Primária (SW2), 2 = Rota Secundária (SW3)
last_switch_time = 0
COOLDOWN_SECONDS = 5

# --- Variáveis para a Média Móvel (EWMA) ---
ewma_delay = None
ALPHA = 0.7  # Peso do novo pacote (70%). O histórico pesa 30%.

# --- Configuração do arquivo CSV ---
CSV_FILENAME = f"experimento_p4_int_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Inicializa o CSV criando o cabeçalho
with open(CSV_FILENAME, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        "timestamp", 
        "latencia_ms", 
        "ewma_ms", 
        "porta_ativa", 
        "sequencia_switches"
    ])

from time import sleep
from scapy.all import Packet, bind_layers, XByteField, FieldLenField, BitField, ShortField, IntField, PacketListField, Ether, IP, UDP, sendp, get_if_hwaddr, sniff


class InBandNetworkTelemetry(Packet):
    fields_desc = [ BitField("switchID_t", 0, 31),
                    BitField("ingress_port",0, 9),
                    BitField("egress_port",0, 9),
                    BitField("egress_spec", 0, 9),
                    BitField("ingress_global_timestamp", 0, 48),
                    BitField("egress_global_timestamp", 0, 48),
                    BitField("enq_timestamp",0, 32),
                    BitField("enq_qdepth",0, 19),
                    BitField("deq_timedelta", 0, 32),
                    BitField("deq_qdepth", 0, 19)
                  ]
    def extract_padding(self, p):
                return "", p

class nodeCount(Packet):
  name = "nodeCount"
  fields_desc = [ ShortField("count", 0),
                  PacketListField("INT", [], InBandNetworkTelemetry, count_from=lambda pkt:(pkt.count*1))]

def handle_pkt(pkt):
  global current_path_port, last_switch_time, ewma_delay
  pkt.show2()
  
  if nodeCount in pkt:
      total_delay = 0
      switch_sequence = []
      for int_hdr in pkt[nodeCount].INT:
          total_delay += (int_hdr.egress_global_timestamp - int_hdr.ingress_global_timestamp)
          switch_sequence.append(int_hdr.switchID_t)
          
      current_delay_ms = total_delay / 1000.0
      
      # --- Cálculo da Média Móvel (EWMA) ---
      if ewma_delay is None:
          ewma_delay = current_delay_ms  
      else:
          ewma_delay = (ALPHA * current_delay_ms) + ((1 - ALPHA) * ewma_delay)
          
      print(f"--- Pacote: {current_delay_ms:.3f} ms | EWMA Suavizada: {ewma_delay:.3f} ms ---")
      
      # --- Salva os dados no arquivo CSV a cada pacote recebido ---
      with open(CSV_FILENAME, mode='a', newline='') as f:
          writer = csv.writer(f)
          writer.writerow([
              time.time(),
              f"{current_delay_ms:.3f}",
              f"{ewma_delay:.3f}",
              current_path_port,
              "-".join(map(str, switch_sequence))
          ])
      
      current_time = time.time()
      
      # LÓGICA DE FAILOVER: Só atua se estivermos na Rota Primária (Porta 1) e a EWMA estourar
      if current_path_port == 1 and ewma_delay > 5.0:
          if (current_time - last_switch_time) > COOLDOWN_SECONDS:
              new_port = 2
              print(f"[FAILOVER] EWMA {ewma_delay:.3f} ms exceeded 5.0 ms! Primary degraded. Changing to SW3 (Port {new_port})...")
              
              # Envia o comando Thrift corrigido para o IP correto do SW1 (192.168.56.200)
              os.system(f"echo \"table_modify MyIngress.ipv4_lpm MyIngress.ipv4_forward 1 08:00:27:1d:e0:27 {new_port}\" | simple_switch_CLI --thrift-ip 192.168.56.200 --thrift-port 9090")
              
              current_path_port = new_port
              last_switch_time = current_time
              ewma_delay = None  # Reseta a EWMA para evitar falsos positivos imediatos na nova rota
              
      # LÓGICA DE FALLBACK: Se estivermos na Rota Secundária (Porta 2), aguarda o timeout para testar o retorno
      elif current_path_port == 2:
          if (current_time - last_switch_time) > 20:  # Após 20 segundos no backup
              print("Timeout on Secondary path (20s). Optimistically failing back to Primary (SW2) to check health...")
              new_port = 1
              
              # Envia o comando Thrift de retorno para o IP correto do SW1
              os.system(f"echo \"table_modify MyIngress.ipv4_lpm MyIngress.ipv4_forward 1 08:00:27:1d:e0:27 {new_port}\" | simple_switch_CLI --thrift-ip 192.168.56.200 --thrift-port 9090")
              
              current_path_port = new_port
              last_switch_time = current_time
              ewma_delay = None  # Reseta a EWMA para estabilizar a medição no retorno

def main():
  iface = 'enp0s8'
  bind_layers(IP, nodeCount, proto = 253)
  sniff(filter = "ip proto 253", iface = iface, prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
