import numpy as np
from astropy.io import fits

def construct_response(fits_file_dir, fits_arf_dir, min_val = 1.e-6, nustar = False, hitomi = False, acis = False, ROSAT = False):
    
    with fits.open(fits_file_dir) as rmf:

        # Calculate the detector response, using the arf and rmf
        # This maps from a series of input channels (energies) to output ones,
        # accounting for the effective area. This is a square matrix for the mos
        # camera, but not for the pn

        # Get the input and output energy arrays - for pn not uniformly spaced            
        cin_min = rmf['MATRIX'].data['ENERG_LO'] # [keV]
        cin_max = rmf['MATRIX'].data['ENERG_HI'] # [keV]

        cout_min = rmf['EBOUNDS'].data['E_MIN'] # [keV]
        cout_max = rmf['EBOUNDS'].data['E_MAX'] # [keV]
        
        cout_de = cout_max - cout_min # [keV]

    if not ROSAT:
        with fits.open(fits_arf_dir) as arf:
            # Extract the effective area as a function of input energy
            # NB: this is vignetting corrected
            effA = arf[1].data['SPECRESP'] # [cm^2]
    else:
        effA = np.ones(len(cin_min))

    # Extract the rmf matrix, which gives the probability of an input X-ray with
    # true energy in an input channel is reconstructed into a given output channel
    # At the same time we also multiply in the effective area through, combining
    # to give the full detector response
    # NB: this matrix is stored in a sparse format, so we have to reconstruct it
    
    with fits.open(fits_file_dir) as rmf:

        # Check shape of F_CHAN, it and N_CHAN have different shape for pn than mos
        # For mos, N_GRP is always 0 or 1, for pn it can be larger
        # NuSTAR chooses one of these, because most generally it is just if there
        # are multiple groups.
        pndat = 0
        if len(np.shape(rmf['MATRIX'].data['F_CHAN'])) == 2:
            pndat = 1
            
        det_res = np.zeros((len(cout_min),len(cin_min)))

        for i in range(len(cin_min)):

            # Reconstruct sparse matrix
            det_col = np.zeros(len(cout_min))
            jtot = 0
            for j in range(rmf['MATRIX'].data['N_GRP'][i]): # Number of groups
                # Account for different file structure in pn and mos
                if pndat or nustar or hitomi:
                    fc = rmf['MATRIX'].data['F_CHAN'][i][j] # First channel
                    sl = rmf['MATRIX'].data['N_CHAN'][i][j] # Channels in this group
                elif acis:
                    fc = rmf['MATRIX'].data['F_CHAN'][i][j]-1 # First channel but it's 1-indexed
                    sl = rmf['MATRIX'].data['N_CHAN'][i][j] # Channels in this group
                else:
                    fc = rmf['MATRIX'].data['F_CHAN'][i] # First channel
                    sl = rmf['MATRIX'].data['N_CHAN'][i] # Channels in this group
                det_col[fc:fc+sl] = rmf['MATRIX'].data['MATRIX'][i][jtot:jtot+sl]
                jtot += sl

            # To help compress matrix, set all values < min_val to 0
            # Recall this is a pdf, so these entries have negligible impact
            # NB: rmfgen already has cut values < 1.e-6
            tocut = np.where(det_col < min_val)
            det_col[tocut] = 0.

            # Save and account for effective area
            det_res[:,i] = det_col * effA[i] # [cm^2]

    return cin_min, cin_max, cout_min, cout_max, det_res
