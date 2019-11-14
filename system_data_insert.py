import psutil
from influxdb import InfluxDBClient
import time

client = InfluxDBClient(host='localhost', port=8086)
client.create_database('system')

measurement_name = 'system_data'
data_end_time = int(time.time() * 1000)
data = []
cpu_p, mem_p, disk_read, disk_write, net_sent, net_recv, temp, boot_time = \
    0, 0, 0, 0, 0, 0, 0, 0


def get_system_data():
    global cpu_p, mem_p, disk_write, disk_read, net_recv, net_sent, temp, \
        boot_time, data_end_time
    data_end_time = int(time.time() * 1000)
    cpu_p = psutil.cpu_percent()
    mem_p = psutil.virtual_memory().percent
    disk_read = psutil.disk_io_counters().read_count
    disk_write = psutil.disk_io_counters().write_count
    net_sent = psutil.net_io_counters().bytes_sent
    net_recv = psutil.net_io_counters().bytes_recv
    temp = psutil.sensors_temperatures()['acpitz'][0].current
    boot_time = psutil.boot_time()

    data.append(
        {
            "measurement": "system_data",
            "tags": {
                "boot_time": boot_time
            },
            "fields": {
                "cpu_percent": cpu_p,
                "memory_percent": mem_p,
                "disk_read": disk_read,
                "disk_write": disk_write,
                "net_sent": net_sent,
                "net_received": net_recv,
                "temperature": temp,
            },
            "time": data_end_time
        }
    )

    client.write_points(data, database='system', time_precision='ms',
                        protocol='json')


def run(interval=15):  # interval in seconds
    while 1:
        try:
            get_system_data()
            time.sleep(interval)
        except KeyboardInterrupt:
            quit()
        except:
            pass


run()

