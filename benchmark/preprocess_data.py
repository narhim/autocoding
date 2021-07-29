"""
This preprocessing script is adapted from https://github.com/kathrynchapman/LA_MC2C/blob/main/process_data.py
to read clef2019 (german), cantemist, codiEsp, and gutman datasets and output in <train/dev/test>.json files.
"""

import argparse
import json
from sklearn.preprocessing import MultiLabelBinarizer
from collections import Counter
from pathlib import Path


def cl_parser(argv=None):
    """
    Parse command line arguments

    :param argv:
    :return:
    """
    parser = argparse.ArgumentParser(description="Preprocess Data")
    parser.add_argument("--label_threshold",
                        default=0,
                        type=int,
                        help="Exclude labels which occur <= threshold",
                        )
    parser.add_argument("--data_dir", type=str, default="clef2019")
    parser.add_argument("--partition",
                        type=str,
                        default="test",
                        help="test | development | training -- should match naming style in dataset")
    parser.add_argument("--binarize_labels", type=bool, default=False)
    parser.add_argument("--output_dir", type=str, default="preprocessed")

    return parser.parse_args(argv)


def write_to_json(data, path):
    """

    :param data: [{id:"doc id", "doc":"doc text", "labels_id": ["label1", "label2"]}, {...}]
    :param path:
    :return: None
    """
    with open(path, mode="w", encoding="utf-8") as out_file:
        json.dump(data, out_file, indent=4, ensure_ascii=False)


def read_from_json(og_data, path):
    """

    :param og_data: the original data that was written to json
    :param path:
    :return:
    """
    with open(path, mode="r", encoding="utf-8") as in_file:
        data = json.load(in_file)
    assert og_data == data


def lines_from_file(path):
    """
    :param path: path to file
    :return: each line with trailing whitespaces removed
    """
    with open(path) as f:
        for line in f:
            yield line.rstrip()


class Preprocess:

    def __init__(self, args=None):
        self.args = args
        self.data_root_dir = Path(__file__).resolve().parent / args.data_dir
        self.data_dir = self.data_root_dir / args.partition if args.partition == "test" \
            else self.data_root_dir / "train_dev"
        self.ids_file_path = self.data_dir / f"ids_{args.partition}.txt"
        self.annotation_file_path = self.data_dir / f"anns_{args.partition}.txt" if args.partition == "test" \
            else self.data_dir / f"anns_train_dev.txt"
        self.docs_dir = self.data_dir / "docs" if args.partition == "test" else self.data_dir / "docs-training"
        self.class_counter = Counter()
        self.mlb = MultiLabelBinarizer()
        self.doc_label_dict = dict()
        self.docs_labels_list = []

    def _extract_ids(self):
        yield from lines_from_file(self.ids_file_path)

    def _extract_annotation(self):
        """
        Read in the annotation file into dict of {"doc_id": ["label1", "label2", "label3", "..."]}.
        Also count frequency of each label type and store in self.class_counter
        :return:
        """
        for doc_labels in lines_from_file(self.annotation_file_path):
            doc_id, labels = doc_labels.split("\t")
            labels = labels.split("|")
            self.doc_label_dict[doc_id] = labels
            if self.args.partition == "training":
                self.class_counter.update(labels)

    def _extract_doc(self, doc_id):
        """

        :param doc_id: id of the document in the partition to extract text
        :return: str text of the doc; if doc has multiple lines, all lines are concatenated into part of 1 text string
        """
        doc_file_path = self.docs_dir / f"{doc_id}.txt"
        return " ".join([line for line in lines_from_file(doc_file_path)])

    def make_docs_labels_list(self):
        """
        Create list of docs : labels dicts where each dict follows this format:
        {"id": "doc_id", "doc": "doc text...", "labels_id": ["label1", "label2", "label3", ...]}

        :return: None
        """
        self._extract_annotation()

        for doc_id in self._extract_ids():
            a_doc_labels_dict = dict()
            a_doc_labels_dict["id"] = doc_id
            a_doc_labels_dict["doc"] = self._extract_doc(doc_id)
            try:
                a_doc_labels_dict["labels_id"] = self.doc_label_dict[doc_id]
            except KeyError:
                a_doc_labels_dict["labels_id"] = []
            self.docs_labels_list.append(a_doc_labels_dict)

    def create_dataset_json(self):
        """
        Preprocess the dataset partition to the standard json format:
        [{"id": "doc_id", "doc": "doc text...", "labels_id": ["label1", "label2", "label3", ...]},
        ...
        ]

        :return: None
        """
        self.make_docs_labels_list()

        out_file_dir = Path(__file__).resolve().parent / self.args.output_dir / self.args.data_dir
        try:
            out_file_dir.mkdir(parents=True, exist_ok=False)
            print(f"{out_file_dir} created to store pre-processed files.")
        except FileExistsError:
            print(f"{out_file_dir} alreay exists!")

        json_file_path = out_file_dir / f"{self.args.partition}.json"
        write_to_json(self.docs_labels_list, json_file_path)
        try:
            read_from_json(self.docs_labels_list, json_file_path)
        except AssertionError:
            print(f"WARNING: json file not identical to original data!!!")
        print(f"Pre-processed {self.args.data_dir} {self.args.partition} partition saved to {json_file_path}.")


def main():
    args = cl_parser()
    # print(args)
    clef_19_preprocess = Preprocess(args)
    clef_19_preprocess.create_dataset_json()


if __name__ == '__main__':
    main()
