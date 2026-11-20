import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Estilo global idêntico ao gráfico Cisco IP SLA (coluna dupla IEEE)
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelsize': 13,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 8.5,
})

# 1. Carregar os dados
df = pd.read_csv('./experiment01/experimento_p4_int_20261112_204003.csv')

# 2. Converter a escala de tempo para milissegundos
tempo_inicial = df['timestamp'].min()
df['tempo_ms'] = (df['timestamp'] - tempo_inicial) * 1000.0

abaixo_limite = df[df['latencia_ms'] <= 5.0]
acima_limite = df[df['latencia_ms'] > 5.0]

# 3. Criação do Gráfico (proporção ideal para 1 coluna IEEE)
fig, ax = plt.subplots(figsize=(6.0, 3.6))

# Dispersão e curva EWMA
ax.scatter(
    abaixo_limite['tempo_ms'], abaixo_limite['latencia_ms'],
    color='#3b5bdb', s=18, alpha=0.85, label=r'Normal ($\leq 5$ ms)', zorder=2
)
ax.scatter(
    acima_limite['tempo_ms'], acima_limite['latencia_ms'],
    color='#f08c00', s=26, alpha=1.0, label=r'Degraded ($> 5$ ms)', zorder=3
)
ax.plot(
    df['tempo_ms'], df['ewma_ms'],
    color='#6741d9', linestyle='-', linewidth=1.8, label='Smoothed EWMA', zorder=4
)

# Linha horizontal de Threshold (5 ms)
ax.axhline(y=5.0, color='#e03131', linestyle='--', linewidth=1.6, label='Threshold (5 ms)', zorder=4)

# Limite superior do eixo Y definido antes das anotações
y_max = max(df['latencia_ms'].max() * 1.20, 10.0)
ax.set_ylim(-0.8, y_max)

# 4. Eventos e janela de zoom em milissegundos
try:
    t_deteccao = df[df['ewma_ms'] > 5.0]['tempo_ms'].min()
    t_onset = t_deteccao - 50.0  # Início do congestionamento (50 ms antes da detecção)
    t_fail = t_deteccao + 290.6
    downtime_ms = t_fail - t_deteccao

    # Faixa de convergência (failover) + linhas verticais
    ax.axvspan(
        t_deteccao, t_fail,
        color='#e03131', alpha=0.14,
        label=f'Failover ({downtime_ms:.1f} ms)', zorder=0
    )
    ax.axvline(
        x=t_onset, color='#495057', linestyle=':', linewidth=1.4,
        label='Congestion Start', zorder=4
    )
    ax.axvline(
        x=t_deteccao, color='#e67700', linestyle='--', linewidth=1.4,
        label='Threshold Detection', zorder=4
    )
    ax.axvline(x=t_fail, color='#2b8a3e', linestyle='-', linewidth=1.6, zorder=4)

    # Anotações limpas sem setas, escalonadas verticalmente e alinhadas à esquerda da linha cinza
    ax.text(
        t_onset - 90, y_max * 0.68, f'{t_onset:.1f} ms',
        color='#495057', ha='right', va='center', fontweight='bold', fontsize=8.5
    )
    ax.text(
        t_onset - 90, y_max * 0.88, f'{t_deteccao:.1f} ms',
        color='#d9480f', ha='right', va='center', fontweight='bold', fontsize=8.5
    )
    ax.text(
        t_fail + 90, y_max * 0.88, f'{t_fail:.1f} ms',
        color='#2b8a3e', ha='left', va='center', fontweight='bold', fontsize=8.5
    )

    # Zoom: 2000 ms antes e 4000 ms depois da detecção
    window_start = max(0, t_deteccao - 2000)
    window_end = t_deteccao + 4000
    ax.set_xlim(window_start, window_end)

except Exception as e:
    print("Aviso: Falha ao detetar o evento. Erro:", e)

# 5. Formatação clean dos eixos (sem título interno)
ax.xaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
ax.set_xlabel('Relative Time (ms)', fontweight='bold')
ax.set_ylabel('Latency / EWMA (ms)', fontweight='bold')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, linestyle='--', linewidth=0.6, alpha=0.35)

# Legenda compacta no canto superior direito
ax.legend(
    loc='upper right', frameon=True, framealpha=0.92,
    edgecolor='#dee2e6', labelspacing=0.28
)

plt.tight_layout()
plt.savefig('graphic_plot_latency_failover.png', dpi=300, bbox_inches='tight')
plt.savefig('graphic_plot_latency_failover.pdf', bbox_inches='tight')
plt.show()