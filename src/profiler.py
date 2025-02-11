import time
import matplotlib.pyplot as plt
from collections import deque
import csv

class Profiler:
    def __init__(self):
        self.sections = {}
        self.metrics = {}  # Nuevo diccionario para métricas adicionales
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

    def add_metric(self, name, value):
        """Añade una métrica al profiler"""
        if name not in self.metrics:
            self.metrics[name] = deque(maxlen=self.max_frames)
        self.metrics[name].append(value)

    def get_metrics(self):
        """Obtiene las estadísticas de las métricas"""
        stats = {}
        for metric, values in self.metrics.items():
            stats[metric] = {
                "current": values[-1] if values else 0,
                "average": sum(values) / len(values) if values else 0,
                "max": max(values) if values else 0,
                "min": min(values) if values else 0
            }
        return stats

    def show_graphs(self):
        # Código existente para las secciones
        stats = self.get_stats()
        sections = list(stats.keys())
        average_times = [stats[section]["average_time"] for section in sections]
        call_counts = [stats[section]["call_count"] for section in sections]

        # Crear una figura con múltiples subplots
        fig = plt.figure(figsize=(15, 10))
        
        # Subplot para tiempos de sección
        ax1 = fig.add_subplot(221)
        ax1.set_title('Section Times')
        ax1.bar(sections, average_times)
        ax1.set_xticklabels(sections, rotation=45)
        ax1.set_ylabel('Average Time (s)')

        # Subplot para cantidad de enemigos
        ax2 = fig.add_subplot(222)
        metrics = self.get_metrics()
        if 'enemy_count' in metrics:
            enemy_counts = list(self.metrics['enemy_count'])
            ax2.set_title('Enemy Count Over Time')
            ax2.plot(enemy_counts)
            ax2.set_ylabel('Number of Enemies')
            ax2.set_xlabel('Frame')

        # Subplot para tiempo por enemigo
        ax3 = fig.add_subplot(223)
        if 'time_per_enemy' in metrics:
            time_per_enemy = list(self.metrics['time_per_enemy'])
            ax3.set_title('Processing Time per Enemy')
            ax3.plot(time_per_enemy)
            ax3.set_ylabel('Time (ms)')
            ax3.set_xlabel('Frame')

        plt.tight_layout()
        plt.show()

    def export_data(self, filename="profiler_data.csv"):
        stats = self.get_stats()
        metrics = self.get_metrics()
        
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Type", "Name", "Value", "Average", "Min", "Max"])
            
            # Escribir stats de secciones
            for section, data in stats.items():
                writer.writerow(["Section", section, data["total_time"], 
                               data["average_time"], "-", "-"])
            
            # Escribir métricas
            for metric, data in metrics.items():
                writer.writerow(["Metric", metric, data["current"], 
                               data["average"], data["min"], data["max"]])
    def get_last_value(self, metric_name):
        """Get the last recorded value for a metric"""
        try:
            if metric_name in self.metrics:
                return self.metrics[metric_name][-1] if self.metrics[metric_name] else 0
            return 0
        except Exception as e:
            print(f"Error getting metric {metric_name}: {e}")
            return 0

    def add_metric(self, name, value):
        """Add a new value to a metric"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)
        # Keep only last 100 values to avoid memory issues
        if len(self.metrics[name]) > 100:
            self.metrics[name].pop(0)

    def add_detailed_metrics(self):
        self.add_metric("spatial_grid_updates", self.spatial_grid_update_time)
        self.add_metric("collision_checks", self.collision_checks_count)
        self.add_metric("active_threads", len([t for t in self.threads if t.is_alive()]))