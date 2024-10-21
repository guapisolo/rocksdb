import subprocess
import re
import json
import numpy as np
import matplotlib.pyplot as plt
import interpolate as itp

def decode_log(log_content):
	# 提取所有数字
	c_pattern = r'Interval compaction: (\d+\.\d+) GB write, (\d+\.\d+) MB/s write, (\d+\.\d+) GB read, (\d+\.\d+) MB/s read, (\d+\.\d+) seconds'
	matches = re.findall(c_pattern, log_content)
	c_write = [float(match[1]) for match in matches][1:]
	c_read = [float(match[3]) for match in matches][1:]
	print("c_write = {}".format(c_write))
	print("c_read = {}".format(c_read))

	wal_pattern = r'Interval WAL: (\d+[\w]*) writes, (\d+) syncs, (\d+\.\d+) writes per sync, written: (\d+\.\d+) GB, (\d+\.\d+) MB/s'
	wal_matches = re.findall(wal_pattern, log_content)
	wal_write = [float(match[4]) for match in wal_matches][1:]
	print("wal_write = {}".format(wal_write))
 
	total_write = np.add(c_write, wal_write)
	total_write = [round(x, 3) for x in total_write]
	print("total_write = {}".format(total_write))

	return {
		'disk_write': total_write,
		'disk_read': c_read,
		'compaction_write': c_write,
		'compaction_read': c_read,
		'wal_write': wal_write
	}

def decode_tsv(file_name, threads):
	# Read data from file
	file_path = 'tsvs/' + file_name + '.tsv'
	with open(file_path, 'r') as file:
		data = file.read()

	# Split the TSV data into lines and extract relevant information
	lines = data.strip().split('\n')
	tsv_result = [[] for i in range(threads)]
	dump_timestamps = []

	total = 0
	# test_start_time = int(lines[0].split("\t")[2])
	for line in lines:
		parts = line.split("\t")
		if parts[3] == 'write':
			test_start_time = int(line.split("\t")[1])
			break

	tsv_timestamp = [0 for i in range(threads)]
	tsv_sumop = [0 for i in range(threads)]

	for line in lines[1:]:
		parts = line.split("\t")

		if len(parts) == 1:
			break
		elif parts[3] == 'write':
			start_time = int(parts[1]) - test_start_time
			end_time = int(parts[2]) - test_start_time
			ops_per_sec = float(parts[5])

			flag = False
			for i in range(threads):
				if tsv_timestamp[i] == 0 or tsv_timestamp[i] == start_time:
					tsv_sumop[i] += ops_per_sec * (end_time - tsv_timestamp[i]) / 1000000
					tsv_timestamp[i] = end_time
					tsv_result[i].append((tsv_timestamp[i] / 1000000, tsv_sumop[i]))
					flag = True
					break
			assert flag, "Error: fail in decode_tsv()!"
		
		elif parts[1] == 'Dump':
			dump_timestamp = int(parts[2]) - test_start_time
			dump_timestamps.append(dump_timestamp / 1000000)
	
	print(tsv_sumop)
	default_interval = 1
	ops_timestamps, ops_sum = itp.work(tsv_result, default_interval)
	ops_per_sec = np.diff(ops_sum, prepend=0) / default_interval

	total = ops_per_sec[0] * ops_timestamps[0]
	for i in range(1, len(ops_per_sec)):
		total += ops_per_sec[i] * (ops_timestamps[i] - ops_timestamps[i - 1])
	print(total)

	return {
		'ops_per_sec': list(ops_per_sec),
		'ops_timestamps': ops_timestamps,
		'dump_timestamps': dump_timestamps
	}

def array_avg(input, num):
	ret = np.array(input)
	if len(ret) % num != 0:
		ret = ret[:-(len(ret) % num)]
	ret = ret.reshape(-1, num).mean(axis=1)
	return ret

def draw_graph(c_write, c_read, fast_write, fast_read, status, running_mig, scheduled_mig, dump_timestamps, ops_per_sec, ops_timestamps, num1 = 0, num2 = 0):

	if num1 != 0:
		c_write = array_avg(c_write, num1)
		c_read = array_avg(c_read, num1)
		fast_write = array_avg(fast_write, num1)
		fast_read = array_avg(fast_read, num1)
		status = array_avg(status, num1)
		dump_timestamps = array_avg(dump_timestamps, num1)

	if num2 != 0:
		ops_timestamps = array_avg(ops_timestamps, num2)
		ops_per_sec = array_avg(ops_per_sec, num2)

	# 绘制折线图
	fig, ax1 = plt.subplots()

	# 绘制第一条线，使用默认的 y 轴
	ax1.tick_params(axis='y', labelcolor='tab:blue')
	ax1.set_ylim(bottom=0, top=1000)
	ax1.set_ylabel('Tier IO Speed (MB/s)', color='tab:blue')
	ax1.plot(dump_timestamps, c_write, label="SlowTier Write", color='tab:blue')
	ax1.plot(dump_timestamps, c_read, label="SlowTier Read", color='tab:orange')
	ax1.plot(dump_timestamps, fast_write, label="FastTier Write", color='tab:green')
	ax1.plot(dump_timestamps, fast_read, label="FastTier Read", color='tab:pink')
	ax1.legend()

	# ax2 = ax1.twinx()
	# ax2.plot(dump_timestamps, running_mig, 'b--', label="Running Migration")
	# ax2.plot(dump_timestamps, scheduled_mig, 'y--', label="Scheduled Migration")
	# ax2.set_ylabel('Y2')
	# ax2.legend()

	ax3 = ax1.twinx()
	ax3.tick_params(axis='y', labelcolor='tab:purple')
	ax3.set_ylim(bottom=0, top=100)
	ax3.set_ylabel('Running status', color='tab:purple')
	ax3.plot(dump_timestamps, status, label="FastTier Status", color='tab:purple')
	# ax3.legend()

	ax4 = ax1.twinx()
	ax4.tick_params(axis='y', labelcolor='tab:red')
	ax4.set_ylim(bottom=0, top=10000)
	ax4.plot(ops_timestamps, ops_per_sec, color='tab:red')
	ax4.set_ylabel('Operations per Second', color='tab:red')

	plt.xlabel('Time')

	# change dims
	fig.set_size_inches(60, 15)
	fig.savefig('report' + '.png', dpi=300, bbox_inches='tight')

	plt.show()



