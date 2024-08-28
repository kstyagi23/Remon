import os
import time
import psutil
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite Database Setup
DB_NAME = "system_stats.db"

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        cpu_usage REAL,
        gpu_usage REAL,
        ram_usage REAL,
        disk_usage REAL,
        load_average REAL,
        network_load REAL,
        top_cpu_processes TEXT,
        top_gpu_processes TEXT,
        top_ram_processes TEXT
    )
    """)
    conn.commit()
    conn.close()

setup_database()

# Get total available GPU RAM (dummy value, replace with actual implementation)
def get_gpu_memory_info():
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            return gpus[0].memoryTotal / 1024  # Convert to GB
    except ImportError:
        return 0

# Watcher function
def collect_stats():
    while True:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Get system stats
        cpu_usage = psutil.cpu_percent(interval=1)
        gpu_usage = get_gpu_memory_info()  # Replace with actual GPU usage
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        load_average = os.getloadavg()[0]
        network_load = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

        # Get top 10 processes by CPU, RAM, GPU usage
        processes = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)
        top_cpu_processes = [(p.info['name'], p.info['cpu_percent']) for p in processes[:10]]
        top_ram_processes = [(p.info['name'], p.info['memory_percent']) for p in sorted(processes, key=lambda p: p.info['memory_percent'], reverse=True)[:10]]
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                top_gpu_processes = gpus[0].memoryTotal / 1024  # Convert to GB
        except ImportError:
            top_gpu_processes = "[]"  # No GPU available

        timestamp = datetime.now().isoformat()

        cursor.execute("""
        INSERT INTO stats (timestamp, cpu_usage, gpu_usage, ram_usage, disk_usage, load_average, network_load, top_cpu_processes, top_gpu_processes, top_ram_processes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, cpu_usage, gpu_usage, ram_usage, disk_usage, load_average, network_load, str(top_cpu_processes), str(top_gpu_processes), str(top_ram_processes)))

        conn.commit()
        conn.close()

        interval = int(os.environ.get("INTERVAL_TIME", 60))
        time.sleep(interval)

# Start the watcher in a separate thread
import threading
threading.Thread(target=collect_stats, daemon=True).start()

# API Endpoint to get stats
@app.get("/stats")
def get_stats(time: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Determine the time delta based on the input
    now = datetime.now()
    unit_map = {"Hours": "hours", "Days": "days", "Weeks": "weeks", "Months": "months"}
    
    try:
        x, unit = time[:-5], time[-5:]
        x = int(x)
        if unit not in unit_map:
            raise ValueError("Invalid time unit")
        delta_args = {unit_map[unit]: x}
        start_time = now - timedelta(**delta_args)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid time format: {e}")
    
    cursor.execute("""
    SELECT * FROM stats WHERE timestamp BETWEEN ? AND ?
    """, (start_time.isoformat(), now.isoformat()))

    rows = cursor.fetchall()
    conn.close()

    # Format the results
    data = {
        "usage": {
            "cpu": [row[2] for row in rows],
            "gpu": [row[3] for row in rows],
            "ram": [row[4] for row in rows],
            "load": [row[6] for row in rows],
            "network": [row[7] for row in rows],
            "time": [row[1] for row in rows],
            "processes": {
                "cpu": [eval(row[8]) for row in rows],
                "gpu": [eval(row[9]) for row in rows],
                "ram": [eval(row[10]) for row in rows]
            }
        },
        "limits": {
            "cpu": {"min": 0, "max": 100},
            "gpu": {"min": 0, "max": get_gpu_memory_info()},
            "ram": {"min": 0, "max": psutil.virtual_memory().total / (1024 ** 3)},  # Convert to GB
            "disk": {"min": 0, "max": psutil.disk_usage('/').total / (1024 ** 3)},  # Convert to GB
            "cores": psutil.cpu_count()
        }
    }

    return data
