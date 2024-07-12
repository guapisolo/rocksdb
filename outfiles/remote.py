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

def saveLogAndOutput(cmd, filename):
  ops_per_second, dump_timestamps = g.decode_tsv(filename)
  # 打开一个文件进行写入
  with open(filename + '.txt', 'w+') as f:
    f.write(f'ops_per_second = {ops_per_second}\n')
    f.write(f'\n')

def runCmd(cmd, filename):
  with open(filename + '.tsv', 'w+') as f:
    subprocess.run(cmd.split(), stderr=f)
  saveLogAndOutput(cmd, filename)

cmd = 'sudo ../db_bench -statistics -use_direct_reads -benchmarks=jsonconfigured -use_direct_io_for_flush_and_compaction -max_background_jobs=16 -level0_slowdown_writes_trigger=6 -level0_file_num_compaction_trigger=4 -level0_stop_writes_trigger=10 -target_file_size_base=10485760 -max_bytes_for_level_base=41943040 -max_bytes_for_level_multiplier=10 -num=100000 -key_size=100 -value_size=1000 -stats_interval_seconds=10 -json_file_path=../benchy.json -threads=8 -compression_type=none -compression_ratio=1.0'
runCmd(cmd, '1e7nfast8threads')
