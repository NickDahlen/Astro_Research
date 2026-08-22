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
from pathlib import Path
from astropy.io import fits
from constructResponse import construct_response


# Parse keyword arguments
#import argparse
#parser = argparse.ArgumentParser()
#parser.add_argument('-d', '--directory',action='store',dest='dir_path',
#                    default='False',type=str)
#results = parser.parse_args()
#dir_path = results.directory


dir_path = Path('/cluster/tufts/cosmology/ndahle01/XRISMFiles/ironDirectory')

print(f"Assigning directory: {dir_path}")

# Iterate over all items in the folder
for item in dir_path.iterdir():
    
    fileNo = item.name

    print(f"Iterating over {fileNo}")
    
    filename = str(dir_path) + '/' + str(fileNo) + '/outputFile'

    # Process files
    obj = fits.open(filename + '.pi')
    arf = fits.open(filename + '.arf')
    rmf = fits.open(filename + '.rmf')

    # Extract the raw X-ray counts in each CCD channel
    # Number of channels is different if mos or pn camera
    # Each channel is associated with an energy, as extracted from the detector
    # response files below
    counts = obj['SPECTRUM'].data['COUNTS']

    print(f"Counts accessed")
    
    # Extract the exposure time for the entire observation
    # Not vignetting corrected
    exp = obj['SPECTRUM'].header['EXPOSURE'] # [s]

    print(f"Exp accesssed")
    
    # Extract the size of the ROI from backscale
    # units are (0.05'')^2, so convert to sr
    roi_size = obj['SPECTRUM'].header['BACKSCAL']*(0.05*1./60./60.*np.pi/180.)**2.

    print("ROI size accessed. Onto the hard part.")
    
    cin_min, cin_max, cout_min, cout_max, det_res = construct_response((filename + '.rmf'), (filename + '.arf'), min_val = 1.e-6, nustar = False, hitomi = True, acis = False, ROSAT = False)

    print("Response construction over!")
    
    cout_de = cout_max - cout_min


    flux = counts/cout_de/exp/roi_size

    print("Processing file!")
    
    # Write the output as an h5 file, compressing the detector response
    out_file = filename + '.h5'
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

    print("File processed. Moving to next file!")
