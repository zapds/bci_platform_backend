import mne
import pandas as pd
import matplotlib.pyplot as plt

raw = mne.io.read_raw_fif("datasets/kicd32sf.fif", preload=True)

(events, event_id) = mne.events_from_annotations(raw)

print(events, event_id)