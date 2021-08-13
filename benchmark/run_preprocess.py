from preprocess_data import cl_parser, Preprocess, PreprocessGuttman
from argparse import Namespace
import sys


def main():
    args = cl_parser()
    print(args)

    if args.data_dir == "clef2019":
        clef_19_preprocess = Preprocess(args)
        clef_19_preprocess.create_dataset_json()
        clef_19_preprocess.plot_label_distribution()

        compared_args = Namespace(**vars(args))
        if args.partition != "training":
            compared_args.partition = "training"
        else:
            compared_args.partition = "test"
            second_compared_args = Namespace(**vars(args))
            second_compared_args.partition = "development"

        print(compared_args)
        clef_19_preprocess.write_unseen_labels(compared_args)
        if args.partition == "training":
            print(second_compared_args)
            clef_19_preprocess.write_unseen_labels(second_compared_args)

    elif args.data_dir == "guttman":
        print(args)
        if args.partition == "all":
            guttmann_preprocess = PreprocessGuttman(args)
            print(f"{len(guttmann_preprocess)} documents")
            guttmann_preprocess.create_dataset_json()
            guttmann_preprocess.plot_label_distribution()
            guttmann_preprocess.write_partition_files(partition_name="test")
            guttmann_preprocess.write_partition_files(partition_name="training")
            guttmann_preprocess.write_partition_files(partition_name="development")
        else:
            guttman_postprocess = Preprocess(args)
            guttman_postprocess.create_dataset_json()
            guttman_postprocess.plot_label_distribution()

            compared_args = Namespace(**vars(args))
            if args.partition != "training":
                compared_args.partition = "training"
            else:
                compared_args.partition = "test"
                second_compared_args = Namespace(**vars(args))
                second_compared_args.partition = "development"

            print(compared_args)
            guttman_postprocess.write_unseen_labels(compared_args)
            if args.partition == "training":
                print(second_compared_args)
                guttman_postprocess.write_unseen_labels(second_compared_args)
    else:
        print(f"Invalid dataset option!")


if __name__ == '__main__':
    main()
