# Remon

**Remon** is a powerful resource monitoring tool built in Python, designed to track and return resource consumption statistics of your device or server. It monitors CPU, GPU, RAM, Disk usage, Load Average, Network Load, and even provides details about the top processes consuming your system's resources.

## Features

- **Real-Time Monitoring**: Continuously monitors CPU, GPU, RAM, Disk, Load Average, and Network usage.
- **Top Processes Tracking**: Identifies the top processes by CPU, GPU, and RAM usage.
- **API Access**: Provides an API endpoint to fetch the resource statistics over a specific period.
- **Persistent Storage**: Stores collected data in a SQLite database for future reference and analysis.

  ## TODO
  - [ ] Front-end for visualizing the data
  - [ ] Integrating external databases
  - [ ] Alert mechanism that drop an email / message / slack notification / etc on certain resource threshold.

## Getting Started

### Prerequisites

- **Python 3.7+**
- **pip** (Python package installer)
- **SQLite** (bundled with Python)

### Installation

1. **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/remon.git
    cd remon
    ```

2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Create Environment File**

    You need to create a `.env` file to configure the monitoring interval.

    ```bash
    touch .env
    ```

    Add the following line to the `.env` file:

    ```bash
    INTERVAL_TIME=60  # Set the interval in seconds
    ```

4. **Run the Application**
    ```bash
    python main.py
    ```

    This will start monitoring and serve the API at `http://localhost:8000`.

### API Usage

The API provides an endpoint to retrieve resource statistics.

- **Endpoint**: `/stats`
- **Method**: `GET`
- **Parameters**: `time` (Required)
  
  The `time` parameter specifies the duration for which you want to fetch the stats. It accepts values like `1Hours`, `2Days`, `1Weeks`, etc.

  Example usage:

  ```bash
  curl http://localhost:8000/stats?time=2Days
  ```

  This will return the resource statistics for the past two days.

## Database Schema

The collected data is stored in a SQLite database named `system_stats.db` with the following structure:

- `id`: Primary key.
- `timestamp`: The time when the data was collected.
- `cpu_usage`: CPU usage percentage.
- `gpu_usage`: GPU memory usage.
- `ram_usage`: RAM usage percentage.
- `disk_usage`: Disk usage percentage.
- `load_average`: System load average.
- `network_load`: Total network load (bytes sent and received).
- `top_cpu_processes`: Top 10 processes by CPU usage.
- `top_gpu_processes`: Top 10 processes by GPU usage.
- `top_ram_processes`: Top 10 processes by RAM usage.

## Contributing

Feel free to contribute to this project by submitting a pull request. Please ensure your changes are well-documented and tested.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [psutil](https://pypi.org/project/psutil/)
- [GPUtil](https://pypi.org/project/GPUtil/)

---

Start monitoring your system resources efficiently with **Remon**! 🚀
