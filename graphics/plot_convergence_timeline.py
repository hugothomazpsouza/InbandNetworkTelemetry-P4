import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Aumentamos um pouco a largura do gráfico (figsize de 10 para 11) 
# para garantir que o texto longo da Cisco caiba perfeitamente à direita
fig, ax = plt.subplots(figsize=(11, 4))

start_time = 0
cisco_time = 4095.0
p4_time = 290.6

# Desenha a linha principal do eixo
ax.plot([0, 5000], [0, 0], color='black', linewidth=1.5)

# P4/ONT timeline (Azul) - Texto ao lado
ax.add_patch(patches.Rectangle((start_time, 0.2), p4_time, 0.4, facecolor='#2b5c8f', edgecolor='black', zorder=3))
ax.text(p4_time + 80, 0.4, 'P4/ONT: 290.6 ms', color='#2b5c8f', ha='left', va='center', fontweight='bold', fontsize=11, zorder=4)

# Cisco IP SLA timeline (Cinza) - Texto ao lado usando a mesma lógica
ax.add_patch(patches.Rectangle((start_time, -0.6), cisco_time, 0.4, facecolor='#7f8c8d', edgecolor='black', zorder=3))
ax.text(cisco_time + 80, -0.4, 'Cisco IP SLA: 4095.0 ms', color='#7f8c8d', ha='left', va='center', fontweight='bold', fontsize=11, zorder=4)

# Marcadores Vermelhos da Falha
ax.axvline(x=0, color='red', linestyle='--', ymin=0.1, ymax=0.9, zorder=1)
ax.text(0, 0.8, 'Failure\nDetected', color='red', ha='center', va='bottom', fontweight='bold')

# Marcadores de Recuperação
ax.axvline(x=p4_time, color='#2b5c8f', linestyle=':', ymin=0.4, ymax=0.8, zorder=1)
ax.axvline(x=cisco_time, color='#7f8c8d', linestyle=':', ymin=0.1, ymax=0.4, zorder=1)
ax.text(cisco_time, -0.7, 'Cisco Recovery', color='#7f8c8d', ha='center', va='top', fontweight='bold')

# Aumentamos o limite do x_lim para 6000 para acomodar o texto da Cisco
ax.set_xlim(-500, 6000)
ax.set_ylim(-1, 1)
ax.axis('off')

plt.title('Convergence Time Comparison: P4/ONT vs Cisco IP SLA', fontsize=15, pad=20)

plt.tight_layout()
plt.savefig('graphic_plot_convergence_timeline.png', dpi=300)
plt.show()
