import subprocess
import re
import json
import numpy as np
import matplotlib.pyplot as plt

def decode_log(log_content):
	# 提取所有数字
	slow_pattern = r'Slowtier IO: (\d+\.\d+) GB write, (\d+\.\d+) MB/s write, (\d+\.\d+) GB read, (\d+\.\d+) MB/s read'
	matches = re.findall(slow_pattern, log_content)
	slow_write = [float(match[1]) for match in matches]
	slow_write = slow_write[1:]
	slow_read = [float(match[3]) for match in matches]
	slow_read = slow_read[1:]
	print("slow_write = {}".format(slow_write))
	print("slow_read = {}".format(slow_read))

	fast_pattern = r'Fasttier IO: (\d+\.\d+) GB write, (\d+\.\d+) MB/s write, (\d+\.\d+) GB read, (\d+\.\d+) MB/s read'
	matches = re.findall(fast_pattern, log_content)
	fast_write = [float(match[1]) for match in matches]
	fast_write = fast_write[1:]
	fast_read = [float(match[3]) for match in matches]
	fast_read = fast_read[1:]
	print("fast_write = {}".format(fast_write))
	print("fast_read = {}".format(fast_read))

	status_p = r'FastTierStatus: (\d+\.\d+)%'
	matches = re.findall(status_p, log_content)
	status = [float(match) for match in matches]
	status = status[1:]
	print("status = {}".format(status))

	rm_p = r'Migration Status: Running (\d+), Scheduled (\d+)'
	matches = re.findall(rm_p, log_content)
	running_mig = [int(match[0]) for match in matches]
	running_mig = running_mig[1:]
	scheduled_mig = [int(match[1]) for match in matches]
	scheduled_mig = scheduled_mig[1:]
	print("running_mig = {}".format(running_mig))
	print("scheduled_mig = {}".format(scheduled_mig))

	return slow_write, slow_read, fast_write, fast_read, status, running_mig, scheduled_mig

def decode_tsv(file_name):
	# Read data from file
	file_path = file_name + '.tsv'
	with open(file_path, 'r') as file:
		data = file.read()

	# Split the TSV data into lines and extract relevant information
	lines = data.strip().split('\n')
	ops_per_second = []
	dump_timestamps = []
	
	for line in lines:
		parts = line.split("\t")
		if parts[3] == 'write':
			test_start_time = int(line.split("\t")[1])
			break
	
	for line in lines[1:]:
		parts = line.split("\t")

		if len(parts) == 1:
			break
		elif parts[3] == 'write':
			start_time = int(parts[1]) - test_start_time
			end_time = int(parts[2]) - test_start_time
			ops_per_sec = float(parts[5])

			ops_per_second.append(((end_time)/1000000, ops_per_sec))
		
		elif parts[1] == 'Dump':
			dump_timestamp = int(parts[2]) - test_start_time
			dump_timestamps.append(dump_timestamp/1000000)
	
	return ops_per_second, dump_timestamps

def array_avg(input, num):
	ret = np.array(input)
	if len(ret) % num != 0:
		ret = ret[:-(len(ret) % num)]
	ret = ret.reshape(-1, num).mean(axis=1)
	return ret

def draw_graph(slow_write, slow_read, fast_write, fast_read, status, running_mig, scheduled_mig, dump_timestamps, ops_info, num1 = 0, num2 = 0):

	ops_timestamps, ops_per_second = zip(*ops_info)
	print(len(ops_timestamps))
	print(len(dump_timestamps))

	if num1 != 0:
		slow_write = array_avg(slow_write, num1)
		slow_read = array_avg(slow_read, num1)
		fast_write = array_avg(fast_write, num1)
		fast_read = array_avg(fast_read, num1)
		status = array_avg(status, num1)
		dump_timestamps = array_avg(dump_timestamps, num1)

	if num2 != 0:
		ops_timestamps = array_avg(ops_timestamps, num2)
		ops_per_second = array_avg(ops_per_second, num2)

	# 绘制折线图
	fig, ax1 = plt.subplots()

	# 绘制第一条线，使用默认的 y 轴
	ax1.tick_params(axis='y', labelcolor='tab:blue')
	ax1.set_ylim(bottom=0, top=1000)
	ax1.set_ylabel('Tier IO Speed (MB/s)', color='tab:blue')
	ax1.plot(dump_timestamps, slow_write, label="SlowTier Write", color='tab:blue')
	ax1.plot(dump_timestamps, slow_read, label="SlowTier Read", color='tab:orange')
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
	ax4.plot(ops_timestamps, ops_per_second, color='tab:red')
	ax4.set_ylabel('Operations per Second', color='tab:red')

	plt.xlabel('Time')

	# change dims
	fig.set_size_inches(60, 15)
	fig.savefig('report' + '.png', dpi=300, bbox_inches='tight')

	plt.show()



