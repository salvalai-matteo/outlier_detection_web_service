# %%
# Imports
import os
from requests import get, post
import shutil
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ml_path = os.path.join("..", "ml_microservice")
if ml_path not in sys.path:
    sys.path.append(ml_path)
from ml_microservice import configuration as c

URL = "http://localhost:5000/api/"
if 'demo' in os.listdir(c.timeseries.path):
    shutil.rmtree(os.path.join(c.timeseries.path, 'demo'))
if 'demo_test' in os.listdir(c.detectorTrainer.path):
    shutil.rmtree(os.path.join(c.detectorTrainer.path, 'demo_test'))
# %%
# ----------------------------------------------------------------------------------------
print("DEMO: XML conversion and dataset initialization")
xml_label = 'demo'
current_xml = 'demo_s11_2017_samples.xml'
with open(os.path.join(c.xml.path, current_xml), 'r') as f:
    xml_body = ''.join(f.read().replace('\n', ''))

r = get(URL+"timeseries").json()
r
# %%
print("Available datasets, labels: ", [d['label'] for d in r['available']])
print("Found label \'{}\': {}".format(
    xml_label, 
    xml_label in [d['label'] for d in r['available']]
))

r = post(URL + "conversion/xml", json=dict(
    label = xml_label,
    xml = xml_body,
    store = True,
)).json()
print("Xml conversion: {}".format(r))

r = get(URL + f"datasets/local/{xml_label}/unnamed").json()
print(f'Demo shape: {r["shape"]}')
last_value = r['shape'][0]
r = get(URL + f"datasets/local/{xml_label}/unnamed/net_amount").json()
plt.plot(r['values'])
# %%
# ----------------------------------------------------------------------------------------
print("DEMO: dataset growth")
current_xml = 'demo_s11_2018_samples.xml'
with open(os.path.join(c.xml.path, current_xml), 'r') as f:
    xml_body = ''.join(f.read().replace('\n', ''))

r = post(URL + "conversion/xml", json=dict(
    label = xml_label,
    xml = xml_body,
    store = True,
)).json()
print("Xml conversion: {}".format(r))

r = get(URL + f"datasets/local/{xml_label}/unnamed").json()
print(f'Demo shape: {r["shape"]}')
r = get(URL + f"datasets/local/{xml_label}/unnamed/net_amount").json()
serie = r['values']
plt.plot(serie)
# last_value = 53
plt.vlines(last_value, max(serie), min(serie), 'r')
# %%
# ----------------------------------------------------------------------------------------
print("DEMO: detector creation")
r = get(URL + "time_series_forecasting/models").json()
print("Possible forecasting models: {}".format([m['architecture'] for m in r['available']]))

forecaster = 'test'
mid = 'demo_test'
training_data = dict(
    label= xml_label,
    dataset= 'unnamed',
    column= 'net_amount'
)

r = post(URL + "anomaly_detectors", json = dict(
    identifier = mid,
    training = training_data,
    forecasting_model = forecaster
)).json()
print(r)

test_anomalies = np.array(r['result']['training_performance']['anomalies']).flatten()
plt.plot(serie[-len(test_anomalies):], 'y')
plt.plot(
    [i for i,a in enumerate(test_anomalies) if a == 1], 
    [e for e in np.array(serie[-len(test_anomalies):])*test_anomalies if e != 0], 
    'rx'
)

version = 'v0'
r = get(URL+f"anomaly_detectors/{mid}/{version}").json()
print("{} - {}: {}".format(mid, version, r['summary']))
# ----------------------------------------------------------------------------------------
# %%
print("DEMO: detection")
current_xml = 'demo_s11_2019_samples.xml'
with open(os.path.join(c.xml.path, current_xml), 'r') as f:
    xml_body = ''.join(f.read().replace('\n', ''))

r = post(URL + "conversion/xml", json=dict(
    label = xml_label,
    xml = xml_body,
    store = False,
)).json()
to_detect = np.array(r['extracted'][0]['data']['net_amount']).flatten()
plt.plot(to_detect)
plt.title('To detect')

version = 'v0'
r = post(URL + f"anomaly_detectors/{mid}/{version}", json = dict(
    data = to_detect.tolist(),
    pre_load = training_data,
    store = True
)).json()
print(r)
results = r['results']
data = results['data']
idx = results['start_detection_idx']
# %%
plt.plot(data, 'y')
anomalies = np.array(results['anomalies']).flatten()
for i, (v, a) in enumerate(zip(data[-len(to_detect):], anomalies)):
    if a > 0:
        plt.plot(idx + i, v, 'rx')
# %%
# ----------------------------------------------------------------------------------------
print("DEMO: Retrain")
r = post(URL + f"anomaly_detectors/{mid}/{version}", json = dict(
    data = np.random.normal(0, .1, size = (to_detect.shape[0]*5, )).tolist(),
    pre_load = training_data,
    store = True,
)).json()
print(r)
print("Detected degradation: ", r['results']['degradation'])
# %%
# CLOSING STUFF --------------------------------------------------------------------------
if 'demo' in os.listdir(c.timeseries.path):
    shutil.rmtree(os.path.join(c.timeseries.path, 'demo'))
if 'demo_test' in os.listdir(c.detectorTrainer.path):
    shutil.rmtree(os.path.join(c.detectorTrainer.path, 'demo_test'))