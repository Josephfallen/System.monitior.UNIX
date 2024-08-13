import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SystemMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enterprise System Monitor")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f8f9fa")

        # Styling
        self.style = ttk.Style()
        self.style.configure("TNotebook", tabposition='wn', font=("Arial", 12), background="#f8f9fa")
        self.style.configure("TFrame", background="#f8f9fa")
        self.style.configure("TLabel", background="#f8f9fa", font=("Arial", 12))
        self.style.configure("TButton", relief="flat", background="#007bff", foreground="white", font=("Arial", 10))
        self.style.map("TButton", background=[('active', '#0056b3')])

        # Setting up the notebook (tab interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        # Tabs
        self.system_tab = ttk.Frame(self.notebook)
        self.process_tab = ttk.Frame(self.notebook)
        self.graphs_tab = ttk.Frame(self.notebook)
        self.network_tab = ttk.Frame(self.notebook)
        self.connections_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.system_tab, text='System Info')
        self.notebook.add(self.process_tab, text='Processes')
        self.notebook.add(self.graphs_tab, text='Graphs')
        self.notebook.add(self.network_tab, text='Network Info')
        self.notebook.add(self.connections_tab, text='Connections')

        # Setup each tab
        self.setup_system_tab()
        self.setup_process_tab()
        self.setup_graphs_tab()
        self.setup_network_tab()
        self.setup_connections_tab()

        # Data storage for graphs
        self.cpu_usage_data = []
        self.memory_usage_data = []
        self.disk_usage_data = []
        self.network_sent_data = []
        self.network_recv_data = []
        self.time_data = []

        # Stop flag for threads
        self.stop_threads = False

        # Start the update loop in separate threads
        self.update_info_thread = threading.Thread(target=self.update_info)
        self.update_processes_thread = threading.Thread(target=self.update_processes)
        self.update_network_info_thread = threading.Thread(target=self.update_network_info)
        self.update_connections_thread = threading.Thread(target=self.update_connections)

        self.update_info_thread.start()
        self.update_processes_thread.start()
        self.update_network_info_thread.start()
        self.update_connections_thread.start()

    def setup_system_tab(self):
        # Title
        title_label = tk.Label(self.system_tab, text="System Information", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # CPU Temperature
        self.cpu_temp_label = tk.Label(self.system_tab, text="CPU Temp: Missing Driver", font=("Arial", 12))
        self.cpu_temp_label.pack(pady=5, anchor='w')

        # CPU Usage
        self.cpu_usage_label = tk.Label(self.system_tab, text="CPU Usage: -- %", font=("Arial", 12))
        self.cpu_usage_label.pack(pady=5, anchor='w')

        # Memory Usage
        self.memory_usage_label = tk.Label(self.system_tab, text="Memory Usage: -- %", font=("Arial", 12))
        self.memory_usage_label.pack(pady=5, anchor='w')

        # Disk Usage
        self.disk_usage_label = tk.Label(self.system_tab, text="Disk Usage: -- %", font=("Arial", 12))
        self.disk_usage_label.pack(pady=5, anchor='w')

        # Add a refresh button
        self.refresh_button = tk.Button(self.system_tab, text="Refresh", command=self.update_info)
        self.refresh_button.pack(pady=10)

    def setup_process_tab(self):
        # Title
        title_label = tk.Label(self.process_tab, text="Running Processes", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Treeview for displaying processes
        self.process_tree = ttk.Treeview(self.process_tab, columns=('PID', 'Name', 'Status', 'Memory'), show='headings')
        self.process_tree.heading('PID', text='PID')
        self.process_tree.heading('Name', text='Name')
        self.process_tree.heading('Status', text='Status')
        self.process_tree.heading('Memory', text='Memory (%)')

        self.process_tree.column('PID', width=80, anchor='center')
        self.process_tree.column('Name', width=200, anchor='w')
        self.process_tree.column('Status', width=100, anchor='center')
        self.process_tree.column('Memory', width=100, anchor='center')

        # Scrollbar for process tree
        self.process_scroll = ttk.Scrollbar(self.process_tab, orient="vertical", command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=self.process_scroll.set)
        self.process_scroll.pack(side='right', fill='y')
        self.process_tree.pack(fill='both', expand=True)

        # Add a refresh button
        self.refresh_process_button = tk.Button(self.process_tab, text="Refresh", command=self.update_processes)
        self.refresh_process_button.pack(pady=10)

    def setup_graphs_tab(self):
        # Title
        title_label = tk.Label(self.graphs_tab, text="Usage Graphs", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # CPU Usage Graph
        self.cpu_fig, self.cpu_ax = plt.subplots(figsize=(5, 4))
        self.cpu_ax.set_title("CPU Usage (%)")
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, master=self.graphs_tab)
        self.cpu_canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Memory Usage Graph
        self.memory_fig, self.memory_ax = plt.subplots(figsize=(5, 4))
        self.memory_ax.set_title("Memory Usage (%)")
        self.memory_canvas = FigureCanvasTkAgg(self.memory_fig, master=self.graphs_tab)
        self.memory_canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Disk Usage Graph
        self.disk_fig, self.disk_ax = plt.subplots(figsize=(5, 4))
        self.disk_ax.set_title("Disk Usage (%)")
        self.disk_canvas = FigureCanvasTkAgg(self.disk_fig, master=self.graphs_tab)
        self.disk_canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def setup_network_tab(self):
        # Title
        title_label = tk.Label(self.network_tab, text="Network Information", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Network Info Labels
        self.network_sent_label = tk.Label(self.network_tab, text="Data Sent: -- KB", font=("Arial", 12))
        self.network_sent_label.pack(pady=5, anchor='w')

        self.network_recv_label = tk.Label(self.network_tab, text="Data Received: -- KB", font=("Arial", 12))
        self.network_recv_label.pack(pady=5, anchor='w')

        # Network Usage Graph
        self.network_fig, self.network_ax = plt.subplots(figsize=(7, 5))
        self.network_ax.set_title("Network Usage (KB)")
        self.network_canvas = FigureCanvasTkAgg(self.network_fig, master=self.network_tab)
        self.network_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add a refresh button
        self.refresh_network_button = tk.Button(self.network_tab, text="Refresh", command=self.update_network_info)
        self.refresh_network_button.pack(pady=10)

    def setup_connections_tab(self):
        # Title
        title_label = tk.Label(self.connections_tab, text="Active Connections", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Treeview for displaying connections
        self.connections_tree = ttk.Treeview(self.connections_tab, columns=('Local Address', 'Remote Address', 'Status'), show='headings')
        self.connections_tree.heading('Local Address', text='Local Address')
        self.connections_tree.heading('Remote Address', text='Remote Address')
        self.connections_tree.heading('Status', text='Status')

        self.connections_tree.column('Local Address', width=200, anchor='w')
        self.connections_tree.column('Remote Address', width=200, anchor='w')
        self.connections_tree.column('Status', width=100, anchor='center')

        # Scrollbar for connections tree
        self.connections_scroll = ttk.Scrollbar(self.connections_tab, orient="vertical", command=self.connections_tree.yview)
        self.connections_tree.configure(yscrollcommand=self.connections_scroll.set)
        self.connections_scroll.pack(side='right', fill='y')
        self.connections_tree.pack(fill='both', expand=True)

        # Add a refresh button
        self.refresh_connections_button = tk.Button(self.connections_tab, text="Refresh", command=self.update_connections)
        self.refresh_connections_button.pack(pady=10)

    def update_info(self):
        while not self.stop_threads:
            try:
                # Get the current time for the x-axis
                current_time = time.strftime("%H:%M:%S")
                self.time_data.append(current_time)

                # Update CPU usage
                cpu_usage = psutil.cpu_percent(interval=1)
                self.cpu_usage_data.append(cpu_usage)
                self.cpu_usage_label.config(text=f"CPU Usage: {cpu_usage:.2f} %")

                # Update Memory usage
                memory_usage = psutil.virtual_memory().percent
                self.memory_usage_data.append(memory_usage)
                self.memory_usage_label.config(text=f"Memory Usage: {memory_usage:.2f} %")

                # Update Disk usage
                disk_usage = psutil.disk_usage('/').percent
                self.disk_usage_data.append(disk_usage)
                self.disk_usage_label.config(text=f"Disk Usage: {disk_usage:.2f} %")

                # Update the graphs
                self.update_graph(self.cpu_ax, self.cpu_usage_data, "CPU Usage (%)")
                self.update_graph(self.memory_ax, self.memory_usage_data, "Memory Usage (%)")
                self.update_graph(self.disk_ax, self.disk_usage_data, "Disk Usage (%)")
            except Exception as e:
                print(f"Error updating info: {e}")

            time.sleep(1)  # Sleep to avoid excessive CPU usage

    def update_processes(self):
        while not self.stop_threads:
            try:
                # Clear previous entries
                for i in self.process_tree.get_children():
                    self.process_tree.delete(i)

                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'status', 'memory_percent']):
                    processes.append((proc.info['pid'], proc.info['name'], proc.info['status'], proc.info['memory_percent']))

                for proc in sorted(processes, key=lambda x: x[1].lower()):
                    self.process_tree.insert('', tk.END, values=proc)
            except Exception as e:
                print(f"Error updating processes: {e}")

            time.sleep(2)  # Sleep to avoid excessive CPU usage

    def update_network_info(self):
        while not self.stop_threads:
            try:
                net_io = psutil.net_io_counters()
                sent_kb = net_io.bytes_sent / 1024
                recv_kb = net_io.bytes_recv / 1024

                # Safely update the labels on the main thread
                self.network_sent_label.config(text=f"Data Sent: {sent_kb:.2f} KB")
                self.network_recv_label.config(text=f"Data Received: {recv_kb:.2f} KB")

                self.network_sent_data.append(sent_kb)
                self.network_recv_data.append(recv_kb)
                self.update_graph(self.network_ax, self.network_sent_data, "Data Sent (KB)", line_color='blue', label='Sent')
                self.update_graph(self.network_ax, self.network_recv_data, "Data Received (KB)", line_color='orange', label='Received')
            except Exception as e:
                print(f"Error updating network info: {e}")

            time.sleep(1)  # Sleep to avoid excessive CPU usage

    def update_connections(self):
        while not self.stop_threads:
            try:
                # Clear previous entries
                for i in self.connections_tree.get_children():
                    self.connections_tree.delete(i)

                connections = psutil.net_connections(kind='inet')
                for conn in connections:
                    local_address = f"{conn.laddr[0]}:{conn.laddr[1]}"
                    remote_address = f"{conn.raddr[0]}:{conn.raddr[1]}" if conn.raddr else "N/A"
                    status = conn.status
                    self.connections_tree.insert('', tk.END, values=(local_address, remote_address, status))
            except Exception as e:
                print(f"Error updating connections: {e}")

            time.sleep(2)  # Sleep to avoid excessive CPU usage

    def update_graph(self, ax, data, title, line_color='blue', label='Usage'):
        ax.clear()
        ax.plot(self.time_data[-50:], data[-50:], color=line_color, label=label)
        ax.set_title(title)
        ax.set_xlabel("Time")
        ax.set_ylabel("KB" if 'Network' in title else "Percentage")
        ax.tick_params(axis='x', rotation=45)
        ax.set_ylim(0, max(data[-50:]) * 1.1 if data else 1)
        ax.grid(True)
        ax.legend()
        ax.figure.canvas.draw()

# Create the Tkinter window
root = tk.Tk()
app = SystemMonitorApp(root)
root.mainloop()
