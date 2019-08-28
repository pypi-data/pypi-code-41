from hd_glio.utils import blockPrint, enablePrint
blockPrint()
from nnunet.inference.predict import predict_cases
enablePrint()
import argparse
from hd_glio.paths import folder_with_parameter_files
from hd_glio.setup_hd_glio import maybe_download_weights


def main():
    parser = argparse.ArgumentParser(description="This script will allow you to predict a single case with hd_glio. "
                                                 "If you have multiple cases, please use hd_glio_predict_folder (this one "
                                                 "will be substantially faster for multiple cases because we can "
                                                 "interleave preprocessing, GPU prediction and nifti export."
                                                 "\n"
                                                 "IMPORTANT!\n"
                                                 "The input files must be brain extracted with the non-brain region being "
                                                 "0 (you can achieve that by using hd-bet "
                                                 "(https://github.com/MIC-DKFZ/HD-BET). Furthermore, the input files "
                                                 "must be co-registered and in the same co-ordinate system (pixels "
                                                 "arrays must be aligned)\n"
                                                 "All input files must be niftis (.nii.gz)")

    parser.add_argument("-t1", type=str, required=True,
                        help="T1 input file")
    parser.add_argument("-t1c", type=str, required=True,
                        help="T1c input file")
    parser.add_argument("-t2", type=str, required=True,
                        help="T2 input file")
    parser.add_argument("-flair", type=str, required=True,
                        help="FLAIR input file")

    parser.add_argument("-o", "--output_file", type=str, required=True,
                        help="output filename. Must end with .nii.gz")

    args = parser.parse_args()
    t1 = args.t1
    t1c = args.t1c
    t2 = args.t2
    flair = args.flair
    output_file = args.output_file

    maybe_download_weights()

    predict_cases(folder_with_parameter_files, [[t1, t1c, t2, flair]], [output_file], (0, ), False, 1, 1, None, True,
                  True)

if __name__ == "__main__":
    main()
