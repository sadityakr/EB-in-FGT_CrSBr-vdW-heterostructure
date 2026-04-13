# ---
# description: |
#   Reads AHE (Anomalous Hall Effect) hysteresis loop data from HDF5 (.h5) and
#   tab-delimited (.txt) files. Computes exchange bias field (HEB), coercivity
#   (C1, C2), AHE amplitude, and normalized/centered voltage curves.
# entry_point: from scripts.data_loader import AHE_hysteresis
# dependencies:
#   - numpy
#   - pandas
#   - h5py
#   - matplotlib
# input: |
#   Path to a .h5 (HDF5) or .txt (tab-delimited, 15-line header) file containing
#   AHE measurement data with magnetic field, Hall voltages (Ch1/Ch2), and
#   temperature channels. Optional label string and plotpath directory.
# process: |
#   Reads raw voltage and field arrays; detects current-reversal lock-in mode
#   and averages accordingly. Converts field to mT and voltages to uV.
#   Computes linear-interpolation coercivity crossings, offset, and AHE amplitude.
# output: |
#   AHE_hysteresis object with .field, .vxy, .vxy_norm, .heb, .w, .c1, .c2
#   attributes. Optionally saves a quick-look plot to plotpath/.
# last_updated: 2026-04-12
# ---

import numpy as np
import pandas as pd
import h5py
import matplotlib.pyplot as plt
import os


class AHE_hysteresis:
    def __init__(self, filepath, label=None, plotting=True, plotpath=None):

        self.filepath = filepath
        self.plotpath = plotpath
        # === Initialize all attributes ===
        self.file = None
        self.data = None

        self.field = None
        self.vxy = None

        self.vxx = None
        self.vxy_err = None
        self.vxx_err = None

        self.sample_t = None
        self.vtit = None
        self.T = None

        self.read_data()
        if label is not None:
            self.label = label
        else:
            self.label = f"{round(self.T)} K"

        self.offset = None
        self.vahe = None
        self.offset_and_ahe()
        self.vxy_norm = (self.vxy - self.offset) / self.vahe
        self.vxy_centered = self.vxy - self.offset

        self.c1 = None
        self.c2 = None
        self.coercivity()

        self.heb = (self.c1 + self.c2) / 2
        self.heb_err = np.abs(self.field[20] - self.field[21])
        self.w = (np.abs(self.c1) + np.abs(self.c2)) / 2
        self.w_err = self.heb_err

        if plotting:
            self.plot_EB()

    def read_data(self):
        if self.filepath.endswith(".h5"):
            self.read_h5()
            self.filetype = 'HDF5'
        elif self.filepath.endswith(".txt"):
            self.read_txt()
            self.filetype = 'TXT'

    def read_h5(self):
        with h5py.File(self.filepath) as f:
            field = np.array(f['Data']['Magnetic_Field'])
            vxy = np.array(f['Data']['Avg_Voltage_Hp34420A_Ch1'])
            vxx = np.array(f['Data']['Avg_Voltage_Hp34420A_Ch2'])
            vxy_err = np.array(f['Data']['Voltage_Array_Hp34420A_Ch1'])
            vxx_err = np.array(f['Data']['Voltage_Array_Hp34420A_Ch2'])
            st_arr = np.array(f['Data']['Rod_Temp'])
            vtit_arr = np.array(f['Data']['VTI_Temp'])

        self.field = []
        self.vxy = []
        self.vxx = []
        self.vxy_err = []
        self.vxx_err = []
        self.SampleT = []
        self.vtit = []

        i = 0
        while (np.abs(field[i] - field[i + 1])) < 0.01:
            i = i + 1
        P2 = i + 1

        Curr_invrtd = vxy[0] * vxy[1] < 0

        if Curr_invrtd:
            P = round(P2 / 2)
            i = 0
            while i < len(field):
                temp = field[i:i + P2]
                self.field.append(np.mean(temp))
                temp = np.mean(vxy[i:i + P] - vxy[i + P:i + P2])
                self.vxy.append(temp)
                temp = np.mean(vxx[i:i + P] - vxx[i + P:i + P2])
                self.vxx.append(temp)
                temp2 = np.abs(vxy_err[i:i + P]) + np.abs(vxy_err[i + P:i + P2])
                temp = np.std(temp2)
                self.vxy_err.append(temp)
                temp2 = np.abs(vxx_err[i:i + P]) + np.abs(vxx_err[i + P:i + P2])
                temp = np.std(temp2)
                self.vxx_err.append(temp)
                temp = np.mean(np.abs(st_arr[i:i + P2]))
                self.SampleT.append(temp)
                temp = np.mean(np.abs(vtit_arr[i:i + P2]))
                self.vtit.append(temp)
                i = i + P2
        else:
            i = 0
            while i < len(field):
                self.field.append(np.mean(field[i:i + P2]))
                self.vxy.append(np.mean(vxy[i:i + P2]))
                self.vxx.append(np.mean(vxx[i:i + P2]))
                self.vxy_err.append(np.std(vxy[i:i + P2]))
                self.vxx_err.append(np.std(vxx[i:i + P2]))
                self.SampleT.append(np.mean(st_arr[i:i + P2]))
                i = i + P2

        self.field = np.array(self.field) * 8000 / 93.17
        self.vxy = np.array(self.vxy) * 1e6
        self.vxx = np.array(self.vxx) * 1e6
        self.vxy_err = np.array(self.vxy_err) * 1e6
        self.vxx_err = np.array(self.vxx_err) * 1e6
        self.T = round(np.mean(st_arr))
        self.vtit = np.mean(vtit_arr)

    def read_txt(self):
        device = pd.read_csv(self.filepath, delimiter='\t', skiprows=15)

        self.field = device['Magnetic Field (T)'].to_numpy() * 1000
        self.vxy = device['Voltage-1(V)'].to_numpy() * 1e6
        self.vxy_err = device['Std. of V1'].to_numpy() * 1e6
        self.vxx = device['Voltage-2 (V)'].to_numpy() * 1e6
        self.vxx_err = device['Std. of V2'].to_numpy() * 1e6
        self.sample_t = device['Sample Temparture (K)'].to_numpy()
        self.vtit = device['VTI Temperature (K)'].to_numpy()
        self.T = round(self.sample_t[5])

    def offset_and_ahe(self):
        V = self.vxy
        self.offset = (np.max(V) + np.min(V)) / 2
        self.vahe = (np.max(V) - np.min(V)) / 2

    def coercivity(self):
        c = []
        for i in range(len(self.field) - 1):
            if self.vxy_norm[i] * self.vxy_norm[i + 1] < 0:
                c1 = (
                    (self.field[i] * self.vxy_norm[i + 1]) - (self.field[i + 1] * self.vxy_norm[i])
                ) / (self.vxy_norm[i + 1] - self.vxy_norm[i])
                c.append(c1)

        if len(c) > 1:
            self.c1 = c[0]
            self.c2 = c[1]
        else:
            self.c1 = 0
            self.c2 = 0

    def plot_EB(self):
        plt.figure()
        plt.xlabel('Magnetic Field (mT)')
        plt.ylabel(r'$V_{xy}$ ($\mu$V)')
        plt.title(
            f'{self.label}, T: {self.T} K, '
            f'EB: {round(self.heb)} mT, W: {round(self.w)} mT'
        )
        plt.errorbar(self.field, self.vxy, self.vxy_err, fmt='o')

        if self.plotpath:
            os.makedirs(self.plotpath, exist_ok=True)
            filepath = os.path.join(self.plotpath, f"{self.label}.png")
            plt.savefig(filepath)
        plt.close()
