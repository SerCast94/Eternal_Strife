import time
import matplotlib.pyplot as plt
from collections import deque
import csv

class Profiler:
    def __init__(self):
        self.sections = {}
        self.current_section = None
        self.start_time = None
        self.max_frames = 300  # Máximo número de frames a mantener

    def start(self, section_name):
        self.current_section = section_name
        self.start_time = time.time()

    def stop(self):
        if self.current_section and self.start_time:
            elapsed_time = time.time() - self.start_time
            if self.current_section in self.sections:
                self.sections[self.current_section].append(elapsed_time)
                if len(self.sections[self.current_section]) > self.max_frames:
                    self.sections[self.current_section].popleft()  # Eliminar el frame más antiguo
            else:
                self.sections[self.current_section] = deque([elapsed_time], maxlen=self.max_frames)
            self.current_section = None
            self.start_time = None

    def get_stats(self):
        stats = {}
        for section, times in self.sections.items():
            stats[section] = {
                "total_time": sum(times),
                "average_time": sum(times) / len(times),
                "call_count": len(times)
            }
        return stats

    def reset(self):
        self.sections.clear()

    def show_graphs(self):
        stats = self.get_stats()
        sections = list(stats.keys())
        average_times = [stats[section]["average_time"] for section in sections]
        call_counts = [stats[section]["call_count"] for section in sections]

        fig, ax1 = plt.subplots(figsize=(12, 8))  # Ajustar el tamaño de la figura

        color = 'tab:blue'
        ax1.set_xlabel('Sections')
        ax1.set_ylabel('Average Time (s)', color=color)
        ax1.bar(sections, average_times, color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_xticklabels(sections, rotation=45, ha='right')  # Rotar las etiquetas del eje x

        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Call Count', color=color)
        ax2.plot(sections, call_counts, color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        fig.tight_layout()
        plt.subplots_adjust(bottom=0.2)  # Añadir margen inferior para las etiquetas
        plt.show()

    def export_data(self, filename="profiler_data.csv"):
        stats = self.get_stats()
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Section", "Total Time (s)", "Average Time (s)", "Call Count"])
            for section, data in stats.items():
                writer.writerow([section, data["total_time"], data["average_time"], data["call_count"]])