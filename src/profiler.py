import matplotlib.pyplot as plt
import csv
from collections import defaultdict, deque
import pygame

class Profiler:
    def __init__(self, max_samples=100):
        self.start_times = {}
        self.data = defaultdict(lambda: deque(maxlen=max_samples))
        self.total_times = defaultdict(float)
        self.call_counts = defaultdict(int)
        self.max_samples = max_samples
        
    def start(self, section):
        self.start_times[section] = pygame.time.get_ticks()
        
    def stop(self):
        current_section = list(self.start_times.keys())[-1]
        elapsed = pygame.time.get_ticks() - self.start_times[current_section]
        self.data[current_section].append(elapsed)
        self.total_times[current_section] += elapsed
        self.call_counts[current_section] += 1
        self.start_times.pop(current_section)

    def show_graphs(self):
        # Create figure with subplots in 2x2 layout
        fig = plt.figure(figsize=(12, 8))
        gs = fig.add_gridspec(2, 2, hspace=0.5, wspace=0.4)
        
        plt.rcParams.update({'font.size': 8})
        
        # Graph 1: Render times (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        render_sections = ['draw_clear_surface', 'draw_background', 'draw_entities', 
                        'draw_overlay', 'draw_ui', 'draw_debug', 'draw_final']
        render_times = [self.get_average_time(section) for section in render_sections]
        bars1 = ax1.bar(range(len(render_sections)), render_times)
        ax1.set_title('Renderizado', pad=20)
        ax1.set_xticks(range(len(render_sections)))
        ax1.set_xticklabels(render_sections, rotation=45, ha='right', fontsize=7)
        ax1.set_ylabel('Average time (ms)')
        self._add_value_labels(ax1, bars1)

        # Graph 2: Logic times (top right)
        ax2 = fig.add_subplot(gs[0, 1])
        logic_sections = ['update_animation_manager', 'update_player', 
                        'enemy_management', 'update_tilemap']
        logic_times = [self.get_average_time(section) for section in logic_sections]
        bars2 = ax2.bar(range(len(logic_sections)), logic_times)
        ax2.set_title('Lógica del juego', pad=20)
        ax2.set_xticks(range(len(logic_sections)))
        ax2.set_xticklabels(logic_sections, rotation=45, ha='right', fontsize=7)
        ax2.set_ylabel('Average time (ms)')
        self._add_value_labels(ax2, bars2)

        # Graph 3: Enemy details (bottom left)
        ax3 = fig.add_subplot(gs[1, 0])
        enemy_sections = ['enemy_management', 'update_enemy_manager']
        enemy_times = [self.get_average_time(section) for section in enemy_sections]
        bars3 = ax3.bar(range(len(enemy_sections)), enemy_times)
        ax3.set_title('Procesado de enemigos', pad=20)
        ax3.set_xticks(range(len(enemy_sections)))
        ax3.set_xticklabels(enemy_sections, rotation=45, ha='right', fontsize=7)
        ax3.set_ylabel('Average time (ms)')
        self._add_value_labels(ax3, bars3)

        # Graph 4: Frame history (bottom right)
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_frame_history(ax4)
        
        plt.tight_layout()
        plt.show()

    def _add_value_labels(self, ax, bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}ms',
                ha='center', va='bottom',
                fontsize=7)

    def _plot_frame_history(self, ax):
        if 'draw_entities' in self.data:
            frames = list(self.data['draw_entities'])
            ax.plot(frames, label='Frame time')
            ax.set_title('Frame Time History', pad=20)
            ax.set_xlabel('Last frames')
            ax.set_ylabel('Time (ms)')
            ax.grid(True, alpha=0.3)
            
            avg = sum(frames) / len(frames)
            ax.axhline(y=avg, color='r', linestyle='--', 
                    label=f'Average: {avg:.1f}ms')
            ax.legend(fontsize=7)

    def get_average_time(self, section):
        if section in self.data and len(self.data[section]) > 0:
            return sum(self.data[section]) / len(self.data[section])
        return 0

    def export_data(self):
        with open('profiler_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Section', 'Total Time (s)', 'Average Time (s)', 'Call Count'])
            
            for section in self.data:
                total_time = sum(self.data[section])
                avg_time = total_time / len(self.data[section]) if self.data[section] else 0
                writer.writerow([section, total_time, avg_time, self.call_counts[section]])