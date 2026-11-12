import matplotlib.pyplot as plt

# Data collected from benchmarks
tecnologias = ['Cisco IP SLA', 'P4/ONT (uRLLC)']
tempos_convergencia_ms = [4095.0, 290.6]

plt.figure(figsize=(8, 6))
# Using a nice grey for legacy and a strong blue for the new approach
barras = plt.bar(tecnologias, tempos_convergencia_ms, color=['#7f8c8d', '#2b5c8f'], width=0.45, edgecolor='black', linewidth=0.8)

# Style for the text boxes (similar to Graph 1)
box_style = dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="lightgray", alpha=0.9)

# Add exact values on top of each bar
for i, barra in enumerate(barras):
    altura = barra.get_height()
    # Different text colors to match the bars
    color_text = '#555555' if i == 0 else '#1f4068'
    
    plt.text(barra.get_x() + barra.get_width()/2., altura + 150,
             f'{altura:.1f} ms',
             ha='center', va='bottom', fontsize=12, fontweight='bold', 
             color=color_text, bbox=box_style)

# English Formatting and P4/ONT Title
plt.title('Graph 2: Convergence Time Comparison (Failover)', fontsize=15, pad=15)
plt.ylabel('Recovery Time (milliseconds)', fontsize=13)
plt.ylim(0, max(tempos_convergencia_ms) * 1.25) # Dynamically scales Y axis to leave room for text
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.gca().set_axisbelow(True) # Puts the grid behind the bars

plt.tight_layout()
plt.savefig('graphic_plot_convergence_bars.png', dpi=300)
plt.show()
