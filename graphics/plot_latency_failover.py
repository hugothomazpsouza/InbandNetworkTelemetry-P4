import pandas as pd
import matplotlib.pyplot as plt

# 1. Carregar os dados
df = pd.read_csv('./experiment03/experimento_p4_int_20261112_231846.csv')

# --- CONVERSÃO DA ESCALA DE TEMPO PARA MILISSEGUNDOS ---
tempo_inicial = df['timestamp'].min()
# Subtrai o tempo inicial e multiplica por 1000 para converter de segundos para milissegundos
df['tempo_ms'] = (df['timestamp'] - tempo_inicial) * 1000.0

abaixo_limite = df[df['latencia_ms'] <= 5.0]
acima_limite = df[df['latencia_ms'] > 5.0]

plt.figure(figsize=(14, 7))

# Gráfico de dispersão e linha EWMA (usando o tempo em ms)
plt.scatter(abaixo_limite['tempo_ms'], abaixo_limite['latencia_ms'], color='blue', alpha=0.6, s=20, label='Normal Packets (<= 5ms)')
plt.scatter(acima_limite['tempo_ms'], acima_limite['latencia_ms'], color='orange', alpha=0.8, s=30, label='Degraded Packets (> 5ms)')
plt.plot(df['tempo_ms'], df['ewma_ms'], color='purple', linestyle='-', linewidth=2.5, label='Smoothed EWMA')

# Linha do Limiar (Threshold)
plt.axhline(y=5.0, color='red', linestyle='--', linewidth=2, label='Threshold (5 ms)')

# --- EVENTOS EM MILISSEGUNDOS ---
try:
    # Procura o momento em que a EWMA excedeu 5ms (agora já em milissegundos)
    t_deteccao = df[df['ewma_ms'] > 5.0]['tempo_ms'].min()
    
    # Define os tempos exatos dos eventos
    t_start = t_deteccao - 50
    t_fail = t_deteccao + 290.6
    
    # Marcadores Verticais
    plt.axvline(x=t_start, color='gray', linestyle=':', linewidth=2, label='Congestion Start (Approx)')
    plt.axvline(x=t_deteccao, color='orange', linestyle='--', linewidth=2, label='Threshold Detection')
    plt.axvline(x=t_fail, color='green', linestyle='-', linewidth=2.5, label='Failover / Convergence (+290ms)')
    
    # --- ADICIONANDO OS VALORES EM TEXTO SEM SOBREPOSIÇÃO ---
    # Descobre a altura máxima do gráfico para calcular proporções (ex: 90% da altura, 80%, 70%)
    y_max = max(df['latencia_ms'].max() * 1.1, 10)
    
    # Estilo da caixinha de texto (fundo branco, borda suave)
    box_style = dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="lightgray", alpha=0.9)
    
    # Coloca o texto do Início do Congestionamento mais alto e alinhado à esquerda da linha (ha='right')
    plt.text(t_start - 30, y_max * 0.90, f'{t_start:.1f} ms', 
             color='dimgray', fontsize=11, fontweight='bold', ha='right', bbox=box_style)
             
    # Coloca o texto da Detecção um pouco mais baixo e alinhado à direita da linha (ha='left')
    plt.text(t_deteccao + 30, y_max * 0.80, f'{t_deteccao:.1f} ms', 
             color='darkorange', fontsize=11, fontweight='bold', ha='left', bbox=box_style)
             
    # Coloca o texto do Failover mais abaixo e também alinhado à direita
    plt.text(t_fail + 30, y_max * 0.70, f'{t_fail:.1f} ms', 
             color='darkgreen', fontsize=11, fontweight='bold', ha='left', bbox=box_style)
    
    # --- ZOOM EM MILISSEGUNDOS ---
    # Zoom de 2000 ms (2s) antes e 4000 ms (4s) depois da detecção
    window_start = max(0, t_deteccao - 2000)
    window_end = t_deteccao + 4000
    plt.xlim(window_start, window_end)

except Exception as e:
    print("Aviso: Falha ao detetar o evento. Erro:", e)
    
# Importante: Atualize também a formatação para usar o y_max que calculamos
plt.ylim(-1, y_max)

# 4. Formatação
plt.title('Graph 1: Packet Latency and Failover Trigger (P4/ONT)', fontsize=16)
plt.xlabel('Relative Time (milliseconds)', fontsize=14)
plt.ylabel('Latency / EWMA (ms)', fontsize=14)
plt.legend(loc='upper right', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.5)
plt.ylim(-1, max(df['latencia_ms'].max() * 1.1, 10))

plt.tight_layout()
plt.savefig('graphic_plot_latency_failover.png', dpi=300)
plt.show()
