import subprocess
import re
import matplotlib.pyplot as plt
import tools as g
import shutil
import os
import time
from datetime import datetime

def copy_and_rename_log_file(src_file_path, dest_folder):
	current_time_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
	new_file_name = f"{current_time_str}.log"
	if not os.path.exists(dest_folder):
		os.makedirs(dest_folder)
	dest_file_path = os.path.join(dest_folder, new_file_name)
	shutil.copy(src_file_path, dest_file_path)
	print(f"copy success!: {dest_file_path}")

def saveLogAndOutput(cmd, filename, threads):
	source_log_file = "/nvme/jiajun/disk/LOG"  # 源 log 文件路径
	destination_folder = "/nvme/jiajun/logs"  # 目标文件夹路径
	copy_and_rename_log_file(source_log_file, destination_folder)
	# with open('/nvme/jiajun/logs/xxx.log', 'r') as file:
	with open('/nvme/jiajun/disk/LOG', 'r') as file:
		log_content = file.read()
	log = g.decode_log(log_content)
	tsv  = g.decode_tsv(filename, threads)
	with open('txts/' + filename + '.txt', 'w+') as f:
		f.write(f'cmd = \'{cmd}\'\n')
		f.write(f'disk_write = {log["disk_write"]}\n')
		f.write(f'disk_read = {log["disk_read"]}\n')
		f.write(f'compaction_write = {log["compaction_write"]}\n')
		f.write(f'compaction_read = {log["compaction_read"]}\n')
		f.write(f'compaction_level_write = {log["compaction_level_write"]}\n')
		f.write(f'compaction_level_read = {log["compaction_level_read"]}\n')
		f.write(f'wal_write = {log["wal_write"]}\n')
		f.write(f'ops_per_sec = {tsv["ops_per_sec"]}\n')
		f.write(f'ops_timestamps = {tsv["ops_timestamps"]}\n') 
		f.write(f'dump_timestamps = {tsv["dump_timestamps"]}\n') 
		f.write(f'\n')

def runCmd(cmd, filename, threads):
  clear = 'rm /nvme/jiajun/disk/* -f'
  subprocess.run(clear.split())
  with open('tsvs/' + filename + '.tsv', 'w+') as f:
    subprocess.run(cmd.split(), stderr=f)
  saveLogAndOutput(cmd, filename, threads)

def runJob(threads, p, onum, multiplier, bg_threads, block_size=4, file_number=0, extra_op="", file=64, level=256, buf=64, cache=8, cr=0, wb=1, cif="false", benchy="../benchy/benchy.json"):
	op = (int)(onum * p // threads)
	cmd = f'../db_bench -statistics -use_direct_reads -benchmarks=jsonconfigured -json_file_path={benchy} -use_direct_io_for_flush_and_compaction -max_background_jobs={bg_threads} -num=10000000000 -writes={op} -stats_interval_seconds=1 -stats_dump_period_sec=10 -threads={threads} -compression_type=none -db=/nvme/jiajun/disk -open_files=950 -max_bytes_for_level_multiplier={multiplier} -max_bytes_for_level_base={(int)(p * level * 1048576)} -target_file_size_base={(int)(p * file * 1048576)} -write_buffer_size={(int)(p * buf * 1048576)} -cache_size={(int)(p * cache * 1045876)} -block_size={(int)(block_size * 1024)} -metadata_block_size={(int)(block_size * 1024)} -compaction_readahead_size={(int)(cr * 1048576)} -writable_file_max_buffer_size={(int)(wb * 1048576)} -cache_index_and_filter_blocks={cif} {extra_op}'
	print(cmd)
	filename = f'fast{threads}threads{p}scale{onum}total{bg_threads}bg{block_size}block{multiplier}multiplier{file}file{level}level{cr}cr{buf}buf{wb}wb'
	if file_number != 0:
		filename = f'{filename}({file_number})'
	runCmd(cmd, filename, threads)

# with open('/nvme/jiajun/logs/2024-10-03T13:07:14.log', 'r') as file:
# 	log_content = file.read()
# g.decode_log(log_content)

onum = 1000000000
# benchys = ["../benchy/benchy1.json", "../benchy/benchy2.json", "../benchy/benchy3.json", "../benchy/benchy4.json", "../benchy/benchy5.json", "../benchy/benchy6.json", "../benchy/benchy7.json", "../benchy/benchy8.json"]
def benchys(id):
    return f"../benchy/benchy{i}.json"



def runMixGraph():
	db_path = "/nvme/jiajun/disk"
	
	clear = f'rm {db_path}/* -f'
	subprocess.run(clear.split())
 
	num = (int)(50000000 * 1.0)
	reads = (int)(420000000 * 0.2)
	pre_cmd = f"../db_bench --benchmarks=fillrandom --perf_level=3 --compression_type=none --use_direct_reads --use_direct_io_for_flush_and_compaction --db={db_path} --num={num} --key_size=48 --value_size=43 --statistics --stats_interval_seconds=1 --stats_dump_period_sec=10 --cache_size=268435456"
	print(pre_cmd)
	subprocess.run(pre_cmd.split())
	# --cache_size=268435456 --value_k=0.2615 --value_sigma=25.45 --iter_k=2.517 --iter_sigma=14.236 --keyrange_num=1

	time.sleep(5)

	cmd = f"../db_bench --benchmarks=mixgraph --compression_type=none --histogram --use_direct_reads --use_direct_io_for_flush_and_compaction --benchmarks=mixgraph --db={db_path} --mix_get_ratio=0.83 --mix_put_ratio=0.14 --mix_seek_ratio=0.03 --sine_mix_rate --sine_mix_rate_interval_milliseconds=100 --sine_a=10000000 --sine_b=0.073 --sine_d=20000000 --perf_level=2 --reads={reads} --num={num} --key_size=48 --use_existing_db --statistics --stats_interval_seconds=1 --stats_dump_period_sec=10 --cache_size=268435456"

	print(cmd)
 
	filename = "mixgraph4"
	threads = 1
	with open('tsvs/' + filename + '.tsv', 'w+') as f:
		subprocess.run(cmd.split(), stderr=f)
	saveLogAndOutput(cmd, filename, threads)

# runMixGraph()
