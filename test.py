import mne
import pandas as pd
import matplotlib.pyplot as plt

raw = mne.io.read_raw_edf("/home/zapdos/Downloads/sample.edf", preload=True)
print(raw.info)
Marker = pd.read_csv('/home/zapdos/Downloads/sample.csv')
onset = Marker["latency"].tolist()
duration = Marker["duration"].tolist()
description = Marker["type"].tolist()
my_annot = mne.Annotations(onset,  # in seconds
                           duration,  # in seconds, too
                           description)
#print(my_annot)
raw.set_annotations(my_annot)
eeg_channels =['AF3','F7','F3','FC5','T7','P7','O1','O2','P8','T8','FC6','F4','F8','AF4']
eeg_raw=raw.pick(mne.pick_channels(raw.info['ch_names'], include=eeg_channels))
eeg_raw.set_montage('standard_1020')
fig = eeg_raw.plot()

fig.savefig("eeg.png", dpi=300, bbox_inches="tight")