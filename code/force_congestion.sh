#!/bin/bash

# Interface de saída do SW2 para o SW4
IFACE="enp0s10" 

# LIMPEZA DE SEGURANÇA: Remove qualquer regra travada de testes anteriores
sudo tc qdisc del dev $IFACE root 2>/dev/null

echo "[0s] Experimento iniciado. Tráfego normal no SW2..."
echo "Aguardando 15 segundos..."
sleep 15

echo "[15s] INJETANDO CONGESTIONAMENTO NO SW2 (Limitando $IFACE para 1Mbit)..."
sudo tc qdisc add dev $IFACE root tbf rate 100kbit burst 2kb latency 100ms
#sudo tc qdisc add dev $IFACE root tbf rate 1mbit burst 10kb latency 50ms

echo "Rede degradada. Aguardando 30 segundos..."
sleep 30

echo "[45s] REMOVENDO CONGESTIONAMENTO DO SW2 (Restaurando banda em $IFACE)..."
sudo tc qdisc del dev $IFACE root 2>/dev/null

echo "Teste concluído! Tráfego normalizado."
