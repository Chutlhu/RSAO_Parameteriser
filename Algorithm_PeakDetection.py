#
# This class contains some algorithms that are useful for signal peak 
# detection.
#
# Author: Luca Remaggi 
# Email: l.remaggi@surrey.ac.uk
# 11/01/2018

from scipy import signal
import numpy as np
from audiolazy import lazy_lpc as lpc
import math


def peaks_position(RIR, fs, groupdelay_threshold, use_LPC=1, cutoff_samples=5000, nLPC=12):
    # This method estimates the position of peaks in a room impulse response by applying the DYPSA algorithm

    # Saving the RIR in output for reference
    prev_rir = RIR

    # Check that cutoff_samples is integer
    cutoff_samples = np.int_(cutoff_samples)

    # General variables internal to this method
    prev_rir = RIR  # This is defined to allow future changes at the peak positions
    l_rir = len(RIR)
    RIR[cutoff_samples:l_rir] = 0

    if use_LPC == 1:
        # LPC for reduction of amount of data in RIR
        rir_up = signal.decimate(RIR, 2)
        l_rir_lpc = len(rir_up)

        # Calculate the matching AR filter based on the RIR
        ar = lpc.lpc(rir_up, nLPC)
        a = np.array(ar.numerator)
        b = np.array(ar.denominator)

        # Convert the filter into a time-reversed impulse response
        impulse = np.zeros(l_rir_lpc)
        impulse[0] = 1
        matched_forward = signal.lfilter(b, a, impulse)
        matched = np.flipud(matched_forward)

        # Apply the matched filter to the RIR
        rir_matched = signal.convolve(rir_up, matched)
        rir_matched = rir_matched[l_rir_lpc-1:]

        # Linearly interpolating
        RIR_new = signal.upfirdn([1], rir_matched, 2)

    # Realigning the new RIR with the original one
    val_max_new = np.argmax(abs(RIR_new))
    val_max_old = np.argmax(abs(prev_rir))
    diff_max = val_max_new - val_max_old
    if diff_max > 0:
        del RIR
        RIR = np.concatenate([RIR_new[diff_max:], np.zeros(diff_max)])
    elif diff_max < 0:
        del RIR
        RIR = np.concatenate([np.zeros(abs(diff_max)), RIR_new[:l_rir-abs(diff_max)]])
    else:
        del RIR
        RIR = RIR_new

    # Running the DYPSA algorithm
    y = xewgrdel(RIR, fs)

    return RIR


def xewgrdel(RIR, fs):
    # This is the DYPSA algorithm that has been translated from Matlab to Python. The DYPSA algorithm was first
    # presented in P. A. Naylor, A. Kounoudes, J. Gudnason and M. Brookes, ''Estimation of glottal closure instants in
    # voiced speech using the DYPSA algorithm'', IEEE Trans. on Audio, Speech and Lang. Proc., Vol. 15, No. 1, Jan. 2007

    # General variables
    dy_gwlen = 0.003
    dy_fwlen = 0.00045

    # Perform group delay calculation
    gw = np.int_(2 * np.floor(dy_gwlen*fs/2) + 1)  # Force window length to be odd
    ghw = signal.hamming(gw, 1)
    ghwn = np.squeeze(ghw * [np.array(range(gw-1, -gw, -2))/2])

    RIR2 = RIR ** 2
    yn = signal.lfilter(ghwn, [1], RIR2)
    yd = signal.lfilter(ghw, [1], RIR2)
    yd[abs(yd) < 1] = 10



    return 0 #tew, sew, y, toff


def clustering_dypsa():

    return


def findpeaks():

    return