import mne
import pandas as pd
import matplotlib.pyplot as plt

raw = mne.io.read_raw_fif("datasets/o7ai6xsn.fif", preload=True)
raw = raw.filter(l_freq=1.0, h_freq=40.0)
fig = raw.plot_psd()
fig.savefig("psd_plot.png")
