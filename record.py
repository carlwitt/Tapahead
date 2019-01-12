"""
	Record or load tap data.
	Visualize different smoothings.

	It would be interesting to generate ground truth data by adding random noise to a known offset.
	It seems as if filtering adds a delay (which doesn't seem like a big problem when assessing whether tempo is nice and constant).

"""
from typing import Callable

from scipy.signal import savgol_filter

__author__ = 'Carl Witt'
__email__ = 'wittcarl@deneb.uberspace.de'

import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats.mstats as stats

def record():
	timestamps = []

	filename = input("Ready? Enter filename and then enter again to tap.")
	for i in range(30):
		input("tap")
		timestamps.append(time.time())

	np.savetxt(filename, np.array(timestamps), fmt='%.50e',header='tap_unix_timestamp')
	return timestamps



def sliding_difference(timestamps: [float], diff: int=1, mean: Callable=stats.tmean) -> [float]:
	"""
	:param timestamps: list of points in time when a tap happened
	:param diff: compute interval length by averaging the last diff values. 1 corresponds to simple difference.
	For example, the timestamps 1.1, 2.0, 3.2 yield two intervals, the first of length 0.9, the second of length 1.2;
	For smoothing, we can use the mean of the previous diff intervals. For diff=1 this yields the above two intervals.
	For diff = 2, we get only one interval, where the "tempo" at time 3.2 is estimated as the average of 0.9 and 1.2,
	i.e. 1.05 (for arithmetic mean) or 1.04 (for geometric mean)
	In practice, the type of mean doesn't seem to have a big influence, likely because we don't average that many numbers and they are on the same scale
	:param avg: the averaging method, arithmetic mean by default
	:return: N-diff smoothed interval lengths, where N is the number of timestamps
	"""

	raw_interval_lengths = [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))]
	smoothed_lengths = [mean(raw_interval_lengths[i-diff:i]) for i in range(diff, len(timestamps))]
	print(diff)
	print(raw_interval_lengths)
	print(smoothed_lengths)

	return smoothed_lengths

def to_bpm(interval_lengths: [float]):
	# 80 bpm = 1.3 beats per second = 0.77 seconds per beat
	# 1.55 seconds per 2 intervals = 0.775 seconds per interval = 1.29 beats per second = 77.4 bpm
	return [1. / dur * 60 for dur in interval_lengths]

if __name__ == '__main__':
	# timestamps = record()
	timestamps = np.loadtxt("shake")
	N = len(timestamps)
	print(N)
	savgol_window = 9
	savgol_order = 3

	plt.plot(range(1, N), to_bpm(sliding_difference(timestamps,1)), label="raw", color="gray", alpha=0.3)

	diffs = [(1, "raw with filter"), (3, "average 3 intervals + filter")]
	for diff, label in diffs:

		bpms = to_bpm(sliding_difference(timestamps, diff, mean=stats.hmean))
		# print(bpms)
		bpms = savgol_filter(bpms, savgol_window, savgol_order)
		# print(bpms)
		plt.plot(range(diff,N),bpms,label=label)

	plt.legend()
	plt.title("Savitzky-Golay")
	plt.ylabel("BPM")
	plt.xlabel("Tap Interval")
	plt.savefig("example.png")
	plt.show()

