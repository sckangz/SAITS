import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


type_series='X-MRNN-Jupiter'
size = 32

df = pd.read_csv('error_cal.csv')
show_output = df['output'].values
ground_truth = df['truth'].values
show_output_n=np.array(show_output)
ground_truth_n=np.array(ground_truth)

fig2 = plt.figure(figsize=(19.2,10.8))
plt.plot(show_output, color='red', label='predict', linewidth=size/10)
plt.plot(ground_truth, color='blue', label='ground truth', linewidth=size/10)
plt.plot(ground_truth, color='blue', linewidth=size/10)

plt.xticks(rotation=0,size=size)
plt.yticks(rotation=0,size=size)
plt.xlabel('timestep', fontsize=size)
plt.ylabel("X/nT", fontsize=size)
plt.rcParams.update({'font.size':size})
plt.legend()
plt.savefig(type_series+'.png')
plt.show()