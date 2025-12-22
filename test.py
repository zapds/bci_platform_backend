import mne
import pandas as pd

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

print(raw.__repr__())