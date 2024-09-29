import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np

# 假设我们有n个数组，每个数组的形式是 [(timestamp1, ops_per_sec1), (timestamp2, ops_per_sec2), ...]
def work(arrays, interval):

	# 合并所有时间戳
	mx_timestamps = max([item[0] for array in arrays for item in array])
	all_timestamps = list(np.arange(interval, mx_timestamps, interval))

	print(len(arrays))
	# 构建每个时间戳对应的ops_per_sec字典
	ops_per_sec_dicts = []
	for array in arrays:
		ops_per_sec_dict = {ts: ops for ts, ops in array}
		ops_per_sec_dicts.append(ops_per_sec_dict)

	# 对于每个时间戳，计算平均ops_per_sec
	interpolated_values = []
	for ts in all_timestamps:
		ops_values = []
		for ops_per_sec_dict in ops_per_sec_dicts:
			# 插值缺失值
			timestamps = list(ops_per_sec_dict.keys())
			values = list(ops_per_sec_dict.values())
			f = interp1d(timestamps, values, fill_value="extrapolate")
			ops_values.append(f(ts))
		interpolated_values.append(np.sum(ops_values))

	return all_timestamps, interpolated_values
	# print(interpolated_values)

	# # 绘制图像
	# plt.plot(all_timestamps, interpolated_values, marker='o')
	# plt.xlabel('Timestamp')
	# plt.ylabel('Average Ops per Sec')
	# plt.title('Average Ops per Sec Over Time')
	# plt.grid(True)
	# plt.show()

# arrays = [
#     [(1, 100), (2, 150), (3, 200)],
#     [(1, 110), (2, 140), (3, 210)],
#     [(1.5, 120), (2.5, 160), (3.5, 220)],
#     [(1, 130), (2, 170), (3, 180)],
#     [(1, 140), (2, 135), (3, 195)],
#     [(1, 150), (2, 145), (3, 190)],
#     [(1, 160), (2, 155), (3, 185)],
#     [(1, 170), (2, 165), (3, 180)]
# ]
# interval = 0.5
# work(arrays, interval)
