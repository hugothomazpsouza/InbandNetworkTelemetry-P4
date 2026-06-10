#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import os

path_changed = False

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
    """any thing after this packet is extracted is padding"""
    def extract_padding(self, p):
                return "", p

class nodeCount(Packet):
  name = "nodeCount"
  fields_desc = [ ShortField("count", 0),
                  PacketListField("INT", [], InBandNetworkTelemetry, count_from=lambda pkt:(pkt.count*1))]

def handle_pkt(pkt):
  global path_changed
  pkt.show2()
  
  if nodeCount in pkt:
      total_delay = 0
      for int_hdr in pkt[nodeCount].INT:
          total_delay += (int_hdr.egress_global_timestamp - int_hdr.ingress_global_timestamp)
          
      # Temporário: Exibir o delay atual em milissegundos
      print(f"--- Current Delay: {total_delay / 1000.0:.3f} ms ---")
          
      if total_delay > 400 and not path_changed:
          print(f"Total delay {total_delay} us exceeded 400 us! Changing path to secondary (SW3)...")
          os.system("sshpass -p vagrant ssh -o StrictHostKeyChecking=no vagrant@192.168.56.200 'echo \"table_modify MyIngress.ipv4_lpm MyIngress.ipv4_forward 1 08:00:27:1d:e0:27 2\" | simple_switch_CLI'")
          path_changed = True
  
def main():

  iface = 'enp0s8'
  bind_layers(IP, nodeCount, proto = 253)
  sniff(filter = "ip proto 253", iface = iface, prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()

