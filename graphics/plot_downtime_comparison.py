import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 5))

# Offset on the Y-axis so the lines don't overlap completely
y_cisco_up = 1.05
y_cisco_down = 0.02
y_p4_up = 0.95
y_p4_down = 0.0

# Cisco IP SLA Coordinates (Grey)
cisco_x = [-500, 0, 0, 4095.0, 4095.0, 5000]
cisco_y = [y_cisco_up, y_cisco_up, y_cisco_down, y_cisco_down, y_cisco_up, y_cisco_up]

# P4/ONT Coordinates (Blue)
p4_x = [-500, 0, 0, 290.6, 290.6, 5000]
p4_y = [y_p4_up, y_p4_up, y_p4_down, y_p4_down, y_p4_up, y_p4_up]

# Plotting the lines
ax.plot(cisco_x, cisco_y, color='grey', linewidth=2.5, label='Cisco IP SLA')
ax.plot(p4_x, p4_y, color='blue', linewidth=2.5, label='P4/ONT (uRLLC)')

# Texts inside the downtime "valley"
ax.text(290.6 + 100, 0.3, 'P4/ONT\n290.6 ms', color='blue', ha='left', va='center', fontweight='bold', fontsize=12)
ax.text(4095.0 / 2, 0.5, 'Cisco IP SLA\n4095.0 ms', color='grey', ha='center', va='center', fontweight='bold', fontsize=12)

# Formatting the axes to match a clean schematic look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_position(('data', -500))

# Set Y axis labels to 0 (Down) and 1 (Up)
ax.set_yticks([0, 1])
ax.set_yticklabels(['0 (Down)', '1 (Up)'], fontsize=11)

# X axis styling in English
ax.set_xlabel('Time (ms)', fontsize=12, fontweight='bold')
ax.set_xlim(-600, 5000)
ax.set_ylim(-0.1, 1.2)

# Title in English
plt.title('Downtime Comparison: P4/ONT vs Cisco IP SLA', fontsize=15, pad=15)

plt.tight_layout()
plt.savefig('graphic_downtime_comparison.png', dpi=300)
plt.show()
