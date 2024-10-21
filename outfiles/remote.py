import subprocess
import re
import matplotlib.pyplot as plt
import tools as g
import shutil
import os
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
	source_log_file = "/data/jiajun/disk/LOG"  # 源 log 文件路径
	destination_folder = "/data/jiajun/logs"  # 目标文件夹路径
	copy_and_rename_log_file(source_log_file, destination_folder)
	# with open('/data/jiajun/logs/xxx.log', 'r') as file:
	with open('/data/jiajun/disk/LOG', 'r') as file:
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
  clear = 'rm /data/jiajun/disk/* -f'
  subprocess.run(clear.split())
  with open('tsvs/' + filename + '.tsv', 'w+') as f:
    subprocess.run(cmd.split(), stderr=f)
  saveLogAndOutput(cmd, filename, threads)

def runJob(threads, p, onum, multiplier, bg_threads, block_size=4, file_number=0, extra_op="", file=64, level=256, buf=64, cache=8, cr=0, wb=1, cif="false"):
	op = (int)(onum * p // threads)
	cmd = f'../db_bench -statistics -use_direct_reads -benchmarks=jsonconfigured -json_file_path=../benchy.json -use_direct_io_for_flush_and_compaction -max_background_jobs={bg_threads} -num=10000000000 -writes={op} -stats_interval_seconds=1 -stats_dump_period_sec=10 -threads={threads} -compression_type=none -db=/data/jiajun/disk -open_files=950 -max_bytes_for_level_multiplier={multiplier} -max_bytes_for_level_base={(int)(p * level * 1048576)} -target_file_size_base={(int)(p * file * 1048576)} -write_buffer_size={(int)(p * buf * 1048576)} -cache_size={(int)(p * cache * 1045876)} -block_size={(int)(block_size * 1024)} -metadata_block_size={(int)(block_size * 1024)} -compaction_readahead_size={(int)(cr * 1048576)} -writable_file_max_buffer_size={(int)(wb * 1048576)} -cache_index_and_filter_blocks={cif} {extra_op}'
	print(cmd)
	filename = f'slow{threads}threads{p}scale{onum}total{bg_threads}bg{block_size}block{multiplier}multiplier{file}file{level}level{cr}cr{buf}buf{wb}wb'
	if file_number != 0:
		filename = f'{filename}({file_number})'
	runCmd(cmd, filename, threads)

# with open('/data/jiajun/logs/2024-10-03T13:07:14.log', 'r') as file:
# 	log_content = file.read()
# g.decode_log(log_content)

onum = 10000000
# for i in [64, 4]:
# 	runJob(threads=16, p=0.5, onum=onum, bg_threads=3, block_size=i, file_number=1, multiplier=4, file=256, level=256, cr=1, buf=64, cif="true", extra_op="")
# 	runJob(threads=16, p=0.5, onum=onum, bg_threads=3, block_size=i, file_number=1, multiplier=4, file=64, level=256, cr=1, buf=64, cif="true", extra_op="")
# 	runJob(threads=16, p=0.5, onum=onum, bg_threads=3, block_size=i, file_number=1, multiplier=4, file=256, level=256, cr=0, buf=64, cif="true", extra_op="")
# 	runJob(threads=16, p=0.5, onum=onum, bg_threads=3, block_size=i, file_number=1, multiplier=4, file=64, level=256, cr=0, buf=64, cif="true",extra_op="")

# for i in [64, 4]:
	# runJob(threads=16, p=1.0, onum=onum, bg_threads=3, block_size=i, file_number=1, multiplier=4, file=256, level=256, cr=1, buf=64, cif="true", extra_op="")
	# runJob(threads=16, p=1.0, onum=onum, bg_threads=3, block_size=i, file_number=1, multiplier=4, file=64, level=256, cr=1, buf=64, cif="true", extra_op="")
	# runJob(threads=16, p=1.0, onum=onum, bg_threads=3, block_size=i, file_number=1, multiplier=4, file=256, level=256, cr=0, buf=64, cif="true", extra_op="")
	# runJob(threads=16, p=1.0, onum=onum, bg_threads=3, block_size=i, file_number=1, multiplier=4, file=64, level=256, cr=0, buf=64, cif="true",extra_op="")

# for i in [2, 4, 8, 16, 32, 64]:
# for i in [64]:
# 	runJob(threads=16, p=1.0, onum=onum, bg_threads=3, block_size=64, file_number=1, multiplier=4, file=256, level=256, cr=i, wb=i, buf=64, cif="true", extra_op="")

for i in [32]:
	runJob(threads=16, p=1.0, onum=onum, bg_threads=3, block_size=64, file_number=1, multiplier=4, file=256, level=256, cr=i, wb=i, buf=64, cif="true", extra_op="")
	runJob(threads=16, p=1.0, onum=onum, bg_threads=3, block_size=64, file_number=1, multiplier=4, file=64, level=256, cr=i, wb=i, buf=64, cif="true", extra_op="")
	runJob(threads=16, p=1.0, onum=onum, bg_threads=3, block_size=4, file_number=1, multiplier=4, file=256, level=256, cr=i, wb=i, buf=64, cif="true", extra_op="")
	runJob(threads=16, p=1.0, onum=onum, bg_threads=3, block_size=4, file_number=1, multiplier=4, file=64, level=256, cr=i, wb=i, buf=64, cif="true", extra_op="")

# onum = 2000000000
# for i in [64, 4]:
# 	runJob(threads=16, p=0.25, onum=onum, bg_threads=3, block_size=i, file_number=0, multiplier=4, file=256, level=256, cr=1, buf=64, cif="true", extra_op="")

# onum = 320000000
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=4, file_number=8, cr=1, lr=1, extra_op="")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=64, file_number=8, cr=1, lr=1, extra_op="")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=16, file_number=8, cr=1, lr=1, extra_op="")

# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=64, file_number=5, cr=1, extra_op="")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=64, file_number=6, cr=2, extra_op="")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=64, file_number=7, cr=4, extra_op="")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=4, file_number=5, extra_op="")

# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=8, file_number=0, extra_op="")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=16, file_number=0, extra_op="")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=32, file_number=0, extra_op="")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=64, file_number=0, extra_op="")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=4, file_number=0, extra_op="")


# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=4, file_number=0, extra_op="")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=64, file_number=1, extra_op="")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=64, file_number=2, extra_op="-metadata_block_size=65536")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=64, file_number=3, extra_op="-cache_index_and_filter_blocks=true")
# runJob(threads=16, p=1.0, onum=onum, multiplier=4, bg_threads=3, block_size=64, file_number=4, extra_op="-metadata_block_size=65536 -cache_index_and_filter_blocks=true")

# onum = 300000000
# runJob(threads=16, p=1, onum=onum, multiplier=4, bg_threads=3)
# runJob(threads=16, p=0.25, onum=onum, multiplier=4, bg_threads=8)
# runJob(threads=16, p=0.25, onum=onum, multiplier=4, bg_threads=4)
# runJob(threads=16, p=0.25, onum=onum, multiplier=4, bg_threads=8)

# onum = 500000000
# runJob(threads=16, p=1, onum=onum, multiplier=4, bg_threads=4)
# runJob(threads=16, p=1, onum=onum, multiplier=4, bg_threads=8)

# p = 1
# onum = 500000000
# runJob(16, p, onum, 10)
# runJob(16, p, onum, 6)
# runJob(16, p, onum, 4)

# p = 0.25
# onum = 720000000
# runJob(16, p, onum, 4)

# p = 0.5
# onum = 720000000
# runJob(16, p, onum, 4)

# p = 1
# onum = 720000000
# runJob(16, p, onum, 4)

