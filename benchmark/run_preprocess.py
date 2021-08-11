from preprocess_data import cl_parser, Preprocess, PreprocessGuttman
from argparse import Namespace


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
        guttmann_preprocess = PreprocessGuttman(args)
        guttmann_preprocess.create_dataset_json()
        guttmann_preprocess.plot_label_distribution()
    else:
        print(f"Invalid dataset option!")


if __name__ == '__main__':
    main()
