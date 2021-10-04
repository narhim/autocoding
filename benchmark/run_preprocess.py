from preprocess_data import cl_parser, Preprocess, PreprocessGuttman
from preprocess_data import CodiespToClef2019, PreprocessCodiesp, CantemistToClef2019
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
            guttmann_preprocess.write_partition_files(partition_name="test", random_state=args.random_state)
            guttmann_preprocess.write_partition_files(partition_name="training", random_state=args.random_state)
            guttmann_preprocess.write_partition_files(partition_name="development", random_state=args.random_state)
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

    elif args.data_dir == "codiesp":
        if args.partition == "all":
            print(f"Re-writing dataset to clef2019 format...")
            partitions = ["test", "dev", "train"]
            tracks = ["D", "P", "X"]

            # making id and annotation files for all partitions and all track
            # copying Spanish doc files for all partitions
            for partition in partitions:
                for track in tracks:
                    args.partition = partition
                    args.track = track
                    print(args)
                    codi_clef = CodiespToClef2019(args)
                    if track == "D":
                        codi_clef.write_doc_ids_to_file()
                        codi_clef.copy_doc_files()
                    codi_clef.write_annotation_file()

            # copying English version doc files for all partitions
            args.lang = "en"
            for partition in partitions:
                args.partition = partition
                codi_clef = CodiespToClef2019(args)
                codi_clef.copy_doc_files()
        else:
            args.data_dir = "codiesp_clef"
            codiesp_preprocess = PreprocessCodiesp(args)
            codiesp_preprocess.create_dataset_json()

            # plotting label distribution and comparing labels between partitions
            # since labels are identical in "esp" and "en" only do this for "esp"
            if args.lang == "esp":
                codiesp_preprocess.plot_label_distribution()

                compared_args = Namespace(**vars(args))
                if args.partition != "training":
                    compared_args.partition = "training"
                else:
                    compared_args.partition = "test"
                    second_compared_args = Namespace(**vars(args))
                    second_compared_args.partition = "development"

                print(compared_args)
                codiesp_preprocess.write_unseen_labels(compared_args)
                if args.partition == "training":
                    print(second_compared_args)
                    codiesp_preprocess.write_unseen_labels(second_compared_args)

    elif args.data_dir == "cantemist":
        if args.partition == "all":
            print(f"Re-writing dataset to clef2019 format...")
            partitions = ["test", "train", "dev"]
            tracks = ["coding", "ner", "norm"]

            for partition in partitions:
                if partition == "dev":
                    args.version = "1"
                for track in tracks:
                    args.partition = partition
                    args.track = track
                    print(args)
                    cantemist_clef = CantemistToClef2019(args)
                    if track == "norm":
                        if partition == "dev":
                            cantemist_clef.write_doc_ids_to_file(append=True)
                        else:
                            cantemist_clef.write_doc_ids_to_file()
                        cantemist_clef.copy_doc_files()
                    cantemist_clef.write_annotation_file()

            # there are 2 dev sets, processing dev-set2 after dev-set1
            args.version = "2"
            assert args.partition == "dev", f"{args.partition} does not have version 1 or 2!!"
            for track in tracks:
                args.track = track
                print(args)
                cantemist_clef = CantemistToClef2019(args)
                if track == "norm":
                    cantemist_clef.write_doc_ids_to_file(append=True)
                    cantemist_clef.copy_doc_files()
                cantemist_clef.write_annotation_file()
        else:
            # same approach as preprocessing from codiesp_clef
            # use cl arguments to specify partition and track
            # only esp for language option
            args.data_dir = "cantemist_clef"
            cantemist_preprocess = PreprocessCodiesp(args)
            cantemist_preprocess.create_dataset_json()

            # plotting label distribution and comparing labels between partitions
            cantemist_preprocess.plot_label_distribution()
            compared_args = Namespace(**vars(args))
            if args.partition != "training":
                compared_args.partition = "training"
            else:
                compared_args.partition = "test"
                second_compared_args = Namespace(**vars(args))
                second_compared_args.partition = "development"

            print(compared_args)
            cantemist_preprocess.write_unseen_labels(compared_args)
            if args.partition == "training":
                print(second_compared_args)
                cantemist_preprocess.write_unseen_labels(second_compared_args)
    else:
        print(f"Invalid dataset option!")


if __name__ == '__main__':
    main()
