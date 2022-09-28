import os
import numpy as np
import nibabel as nib
from nibabel.streamlines import load, save
import dipy
from dipy.io.streamline import load_tractogram, save_tractogram

def save_fiber_bundle(input_trk, output_trk, cluster_labels, bundle_index):
    trk_data = load_tractogram(input_trk, 'same')
    labels = np.load(cluster_labels)
    trk_list = []
    for i, idx in enumerate(labels):
        if idx == bundle_index:
            trk_list.append(trk_data.streamlines[i])
    trk_data.streamlines = trk_list
    if not os.path.exists(output_trk):
        os.mkdir(output_trk)
        print('Making {}...'.format(output_trk))
    save_tractogram(trk_data, os.path.join(output_trk, 'bundle_{}.trk'.format(bundle_index)))



if __name__ == '__main__':

    import argparse
    # parse the commandline
    parser = argparse.ArgumentParser()

    # data configuration parameters
    parser.add_argument('--input_trk', required=True, help='input filename')
    parser.add_argument('--output_trk', required=True, help='output filename')
    parser.add_argument('--label', required=True, help='label filename')
    args = parser.parse_args()

    for i in range(1, 44):
        save_fiber_bundle(args.input_trk, args.output_trk, args.label, i)
    # save_fiber_bundle(args.input_trk, args.output_trk, args.label, -1)






