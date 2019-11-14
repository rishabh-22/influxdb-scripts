import psutil
from influxdb import InfluxDBClient
import time

client = InfluxDBClient(host='localhost', port=8086)
client.create_database('system')

measurement_name = 'system_data'
data_end_time = int(time.time() * 1000)
data = []
cpu_p, mem_p, disk_read, disk_write, net_sent_now, net_recv_now, temp, \
    boot_time, net_sent_prev, net_recv_prev = \
    0, 0, 0, 0, 0, 0, 0, 0, \
    psutil.net_io_counters().bytes_sent, psutil.net_io_counters().bytes_recv


def get_system_data():
    global cpu_p, mem_p, disk_write, disk_read, net_recv_now, net_sent_now,\
        temp, boot_time, data_end_time
    data_end_time = int(time.time() * 1000)
    cpu_p = psutil.cpu_percent()
    mem_p = psutil.virtual_memory().percent
    disk_read = psutil.disk_io_counters().read_count
    disk_write = psutil.disk_io_counters().write_count
    net_sent_now = psutil.net_io_counters().bytes_sent
    net_recv_now = psutil.net_io_counters().bytes_recv
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
                "net_sent": net_sent_now-net_sent_prev,
                "net_received": net_recv_now-net_recv_prev,
                "temperature": temp,
            },
            "time": data_end_time
        }
    )

    client.write_points(data, database='system', time_precision='ms',
                        protocol='json')


def run(interval=5):  # interval in seconds
    global net_recv_prev, net_sent_prev
    while 1:
        try:
            get_system_data()
            net_sent_prev = psutil.net_io_counters().bytes_sent
            net_recv_prev = psutil.net_io_counters().bytes_recv
            time.sleep(interval)
        except KeyboardInterrupt:
            quit()
        except:
            pass


run()

