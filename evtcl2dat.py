###############################################################################
# evtcl2dat.py
###############################################################################
#
# Process output of XRISM data pipeline into numpy files ready for analysis
#
###############################################################################


import numpy as np
import astropy.io
from astropy.io import fits
import h5py
from response_matrix import construct_response

# Parse keyword arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--filename',action='store',dest='filename',
                    default='False',type=str)
results = parser.parse_args()
filename = results.filename


# Process files
obj = fits.open(filename + '.pi')
arf = fits.open(filename + '.arf')
rmf = fits.open(filename + '.rmf')

# Extract the raw X-ray counts in each CCD channel
# Number of channels is different if mos or pn camera
# Each channel is associated with an energy, as extracted from the detector
# response files below
counts = obj['SPECTRUM'].data['COUNTS']

# Extract the exposure time for the entire observation
# Not vignetting corrected
exp = obj['SPECTRUM'].header['EXPOSURE'] # [s]

# Extract the size of the ROI from backscale
# units are (0.05'')^2, so convert to sr
roi_size = obj['SPECTRUM'].header['BACKSCAL']*(0.05*1./60./60.*np.pi/180.)**2.


cin_min, cin_max, cout_min, cout_max, det_res = construct_response((filename + '.rmf'), (filename + '.arf'), min_val = 1.e-6, nustar = False, hitomi = True, acis = False, ROSAT = False)

cout_de = cout_max - cout_min


### START OF FUNCTION ###

# cin_min = rmf['MATRIX'].data['ENERG_LO'] # [keV]
# cin_max = rmf['MATRIX'].data['ENERG_HI'] # [keV]

# cout_min = rmf['EBOUNDS'].data['E_MIN'] # [keV]
# cout_max = rmf['EBOUNDS'].data['E_MAX'] # [keV]
# cout_de = cout_max - cout_min # [keV]

# # Extract the effective area as a function of input energy
# # NB: this is vignetting corrected
# effA = arf[1].data['SPECRESP'] # [cm^2]

# # Extract the rmf matrix, which gives the probability of an input X-ray with
# # true energy in an input channel is reconstructed into a given output channel
# # At the same time we also multiply in the effective area through, combining
# # to give the full detector response
# # NB: this matrix is stored in a sparse format, so we have to reconstruct it

# # Check shape of F_CHAN, it and N_CHAN have different shape for pn than mos
# # For mos, N_GRP is always 0 or 1, for pn it can be larger
# pndat = 0
# if len(np.shape(rmf['MATRIX'].data['F_CHAN'])) == 2:
#     pndat = 1

# det_res = np.zeros((len(cout_min),len(cin_min)))

# for i in range(len(cin_min)):
    
#     # Reconstruct sparse matrix
#     det_col = np.zeros(len(cout_min))
#     jtot = 0
#     for j in range(rmf['MATRIX'].data['N_GRP'][i]): # Number of groups
#         # Account for different file strucutre in pn and mos
#         if pndat:
#             fc = rmf['MATRIX'].data['F_CHAN'][i][j] # First channel
#             sl = rmf['MATRIX'].data['N_CHAN'][i][j] # Channels in this group
#         else:
#             fc = rmf['MATRIX'].data['F_CHAN'][i] # First channel
#             sl = rmf['MATRIX'].data['N_CHAN'][i] # Channels in this group
#         det_col[fc:fc+sl] = rmf['MATRIX'].data['MATRIX'][i][jtot:jtot+sl]
#         jtot += sl

#     # To help compress matrix, set all values < 1.e-5 to 0
#     # Recall this is a pdf, so these entries have negligible impact
#     tocut = np.where(det_col < 1.e-5)
#     det_col[tocut] = 0.

#     # Save and account for effective area
#     det_res[:,i] = det_col * effA[i] # [cm^2]


### END OF FUNCTION ### 

# Calculate the differential flux in each bin
# NB: this has units of [cts/s/keV/sr], which is often how X-ray results
# are plotted. The cm^2 is wrapped up in the detector response, and stored
# seprately
flux = counts/cout_de/exp/roi_size


# Write the output as an h5 file, compressing the detector response
out_file = filename + '_processed_new.h5'
h5f = h5py.File(out_file, 'w')
h5f.create_dataset('counts',data=counts)
h5f.create_dataset('flux',data=flux)
h5f.create_dataset('det_res',data=det_res,compression='gzip',compression_opts=9)
h5f.create_dataset('exp',data=exp)
h5f.create_dataset('roi_size',data=roi_size)
h5f.create_dataset('cin_min',data=cin_min)
h5f.create_dataset('cin_max',data=cin_max)
h5f.create_dataset('cout_min',data=cout_min)
h5f.create_dataset('cout_max',data=cout_max)
h5f.close()