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
#   source_log_file = "/data/jiajun/disk/LOG"  # 源 log 文件路径
#   destination_folder = "/data/jiajun/logs"  # 目标文件夹路径
#   copy_and_rename_log_file(source_log_file, destination_folder)
  ops_timestamps, ops_per_sec, dump_timestamps  = g.decode_tsv(filename, threads)
  with open('txts/' + filename + '.txt', 'w+') as f:
    f.write(f'ops_per_sec = {list(ops_per_sec)}\n')
    f.write(f'ops_timestamps = {ops_timestamps}\n') 
    f.write(f'\n')

def runCmd(cmd, filename, threads):
  clear = 'rm /data/jiajun/disk/* -f'
  subprocess.run(clear.split())
  with open('tsvs/' + filename + '.tsv', 'w+') as f:
    subprocess.run(cmd.split(), stderr=f)
  saveLogAndOutput(cmd, filename, threads)

def runJob(threads, p, onum, multiplier, bg_threads=4):
	op = (int)(onum * p // threads)
	cmd = f'../db_bench -statistics -use_direct_reads -benchmarks=jsonconfigured -json_file_path=../benchy.json -use_direct_io_for_flush_and_compaction -max_background_jobs={bg_threads} -num=10000000000 -writes={op} -stats_interval_seconds=1 -stats_dump_period_sec=10 -threads={threads} -compression_type=none -db=/data/jiajun/disk -open_files=950 -max_bytes_for_level_multiplier={multiplier} -max_bytes_for_level_multiplier={multiplier} -write_buffer_size={(int)(p * 67108864)} -max_bytes_for_level_base={(int)(p * 268435456)} -target_file_size_base={(int)(p * 67108864)}'
	print(cmd)
	filename = f'slow{threads}threads{p}scale{onum}total{multiplier}multiplier{bg_threads}bg'
	runCmd(cmd, filename, threads)

onum = 500000000
runJob(threads=16, p=0.25, onum=onum, multiplier=4, bg_threads=4)
runJob(threads=16, p=0.25, onum=onum, multiplier=4, bg_threads=8)

onum = 500000000
runJob(threads=16, p=1, onum=onum, multiplier=4, bg_threads=4)
runJob(threads=16, p=1, onum=onum, multiplier=4, bg_threads=8)

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

