#
# This class is used to perform the segmentation of early reflections given RIRs.
#
# Author: Luca Remaggi
# Email: l.remaggi@surrey.ac.uk
# 05/02/2018

import numpy as np
from Algorithm_PeakDetection import Peakpicking


class Segmentation:

    def __init__(self, RIRs, fs, groupdelay_threshold, use_LPC, discrete_mode, nPeaks, hamm_lengths):
        self.RIRs = RIRs
        self.fs = fs
        self.groupdelay_threshold = groupdelay_threshold
        self.use_LPC = use_LPC
        self.discrete_mode = discrete_mode
        self.nPeaks = nPeaks
        self.segments = None
        self.TOAs_sample_single_mic = None
        self.hamm_lengths = hamm_lengths

    def segmentation(self):
        # Run DYPSA with the B-format omni component only (W channel)
        peakpicking = Peakpicking(RIR=self.RIRs[:, 0], fs=self.fs,
                                  groupdelay_threshold=self.groupdelay_threshold,
                                  use_LPC=self.use_LPC)
        peakpicking.DYPSA()
        p_pos = peakpicking.p_pos

        # Choosing which peaks to prioritize
        if self.discrete_mode is 'first':
            # Find peaks in the DYPSA output
            locs_all = np.transpose(np.array(np.where(p_pos[:, 0] != 0)))
            locs = locs_all[:(self.nPeaks + 5)]
            peaks = np.squeeze(p_pos[locs])
            firstearlypeaks = []
            firstearlylocs = []
        elif self.discrete_mode is 'strongest':
            # Find the first two in time
            locs_all = np.transpose(np.array(np.where(p_pos[:, 0] != 0)))
            firstearlylocs = locs_all[:2]
            firstearlypeaks = np.squeeze(p_pos[firstearlylocs])

            # Then finds the first peaks in energy-descending order
            peaks = np.squeeze(p_pos[locs_all])
            peaks = list(peaks)
            peaks = np.array(sorted(peaks, reverse=True))
            locs_mixed, idx_locs = np.where(p_pos == peaks)
            locs = locs_mixed[idx_locs]

        # Select the reflections TOAs
        first_and_strong = list(locs) + list(firstearlylocs)
        uniquelocs = np.unique(first_and_strong)
        self.TOAs_sample_single_mic = uniquelocs[0:self.nPeaks]

        # Create a dictionary and store inside the reflection segments
        self.segments = {'Direct_sound': self.RIRs[self.TOAs_sample_single_mic[0]-self.hamm_lengths[0]:
                                                   self.TOAs_sample_single_mic[0] + self.hamm_lengths[0], :]}
        for idx_refl in range(1, self.nPeaks):
            self.segments['Reflection' + str(idx_refl)] = self.RIRs[self.TOAs_sample_single_mic[idx_refl] -
                                                                    self.hamm_lengths[idx_refl]:self.TOAs_sample_single_mic[idx_refl] +
                                                                                               self.hamm_lengths[idx_refl], :]

        return self
