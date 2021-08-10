"""
This preprocessing script is adapted from https://github.com/kathrynchapman/LA_MC2C/blob/main/process_data.py
to read clef2019 (german), cantemist, codiEsp, and gutman datasets and output in <train/dev/test>.json files.
"""

import argparse
import json
from sklearn.preprocessing import MultiLabelBinarizer
from collections import Counter
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from argparse import Namespace


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
    parser.add_argument("--binarize_labels", type=bool, default=True)
    parser.add_argument("--output_dir", type=str, default="preprocessed")
    parser.add_argument("--plot", type=bool, default=True)
    parser.add_argument("--force_rerun", type=bool, default=False)

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


def write_to_file(list_of_lines, path, delimiter="\n"):
    """
    Write list of str to file path, with specified delimiter

    :param delimiter:
    :param list_of_lines: list of str
    :param path: out file path
    :return:
    """
    with open(path, mode="w", encoding="utf-8") as out_file:
        for line in list_of_lines:
            out_file.write(f"{line}{delimiter}")


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
        # arguments and paths
        self.args = args
        self.data_root_dir = Path(__file__).resolve().parent / args.data_dir
        self.data_dir = self.data_root_dir / args.partition if args.partition == "test" \
            else self.data_root_dir / "train_dev"
        self.ids_file_path = self.data_dir / f"ids_{args.partition}.txt"
        self.annotation_file_path = self.data_dir / f"anns_{args.partition}.txt" if args.partition == "test" \
            else self.data_dir / f"anns_train_dev.txt"
        self.docs_dir = self.data_dir / "docs" if args.partition == "test" else self.data_dir / "docs-training"
        self.outfile_dir = Path(__file__).resolve().parent / self.args.output_dir / self.args.data_dir

        # data components
        self.class_counter = Counter()
        self.mlb = MultiLabelBinarizer()
        self.doc_label_dict = dict()
        self.docs_labels_list = []
        self.num_docs = 0
        self.unseen_labels = []

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
            # if self.args.partition == "training":
            self.class_counter.update(labels)

    def _extract_doc(self, doc_id):
        """

        :param doc_id: id of the document in the partition to extract text
        :return: str text of a single doc corresponding to the doc_id; if doc has multiple lines, all lines are
        concatenated into part of 1 text string
        """
        doc_file_path = self.docs_dir / f"{doc_id}.txt"
        return " ".join([line for line in lines_from_file(doc_file_path)])

    def make_docs_labels_list(self):
        """
        Create list of docs : labels dicts where each dict follows this format:
        {"id": "doc_id", "doc": "doc text...", "labels_id": ["label1", "label2", "label3", ...]}

        :return: None
        """
        if not self.doc_label_dict:
            self._extract_annotation()

        for doc_id in tqdm(self._extract_ids(), desc=f"making id-doc-labels"):
            a_doc_labels_dict = dict()
            a_doc_labels_dict["id"] = doc_id
            a_doc_labels_dict["doc"] = self._extract_doc(doc_id)
            try:
                a_doc_labels_dict["labels_id"] = self.doc_label_dict[doc_id]
            except KeyError:
                a_doc_labels_dict["labels_id"] = []
            self.docs_labels_list.append(a_doc_labels_dict)
            self.num_docs += 1

    def create_dataset_json(self):
        """
        Preprocess the dataset partition to the standard json format:
        [{"id": "doc_id", "doc": "doc text...", "labels_id": ["label1", "label2", "label3", ...]},
        ...
        ]

        :return: None
        """
        if not self.docs_labels_list:
            self.make_docs_labels_list()

        try:
            self.outfile_dir.mkdir(parents=True, exist_ok=False)
            print(f"{self.outfile_dir} created to store pre-processed files.")
        except FileExistsError:
            print(f"{self.outfile_dir} already exists! File will be saved here.")

        json_file_path = self.outfile_dir / f"{self.args.partition}.json"
        write_to_json(self.docs_labels_list, json_file_path)
        try:
            read_from_json(self.docs_labels_list, json_file_path)
        except AssertionError:
            print(f"WARNING: json file not identical to original data!!!")
        print(f"Pre-processed {self.args.data_dir} {self.args.partition} partition saved to {json_file_path}.")

    def plot_label_distribution(self, save_plot=True):
        """

        Plot the frequency distribution of the labels in the dataset partition.

        :return:
        """
        if not self.class_counter:
            self._extract_annotation()

        labels, counts = zip(*self.class_counter.items())
        labels, counts = list(labels), list(counts)
        assert len(labels) == len(counts)

        # without seaborn
        # indexes = np.arange(len(labels))
        # width = 1

        # plt.bar(indexes, counts, width)
        # plt.xticks(indexes + width * 0.5, labels, rotation="vertical")
        # plt.show()

        plt.figure(num=None, figsize=(20, 18), dpi=80, facecolor='w', edgecolor='r')
        plot = sns.barplot(x=counts, y=labels, orient="h")
        plot.set_title(f"Frequency Distribution of Dataset Labels in {self.args.data_dir.title()} "
                       f"{self.args.partition.title()} Partition")
        plot.bar_label(plot.containers[0])

        if save_plot:
            plot_dir = self.outfile_dir / "plots"
            try:
                plot_dir.mkdir(parents=True, exist_ok=False)
                print(f"{plot_dir} created to store pre-processed files.")
            except FileExistsError:
                print(f"{plot_dir} already exists! Plots will be saved here.")

            outfile_path = plot_dir / f"{self.args.partition}_label_distribution.png"
            plt.savefig(outfile_path)
        plt.show()

    @classmethod
    def get_another_preprocessed_partition(cls, one_args, other_args):
        another_preprocessed_partition = cls(other_args)
        try:
            assert one_args.data_dir == other_args.data_dir
        except AssertionError:
            print(f"WARNING: Comparing partitions from different datasets!")
        another_preprocessed_partition.make_docs_labels_list()

        return another_preprocessed_partition

    def compare_labels(self, other_args):
        """

        :param other_args: parsed args for another partition; should contain the partition name of the partition to
        which labels need to be compared

        :return:
        """

        another_preprocessed_partition = self.get_another_preprocessed_partition(self.args, other_args)
        if not self.unseen_labels or other_args.force_rerun:
            self.unseen_labels = [label for label in self.class_counter.keys() if label not in
                                  another_preprocessed_partition.class_counter.keys()]
        #print(
        #    f"this partition: \n{self.class_counter.keys()} vs train:\n{another_preprocessed_partition.class_counter.keys()}")
        return self.unseen_labels

    def write_unseen_labels(self, other_args):
        """
        Write to file the list of labels in this partition not seen in the training partition

        :param other_args:
        :return:
        """
        try:
            self.outfile_dir.mkdir(parents=True, exist_ok=False)
            print(f"{self.outfile_dir} created to store pre-processed files.")
        except FileExistsError:
            print(f"{self.outfile_dir} already exists! File will be saved here.")

        outfile_path = self.outfile_dir / f"{self.args.partition}_unseen_in_{other_args.partition}.txt"
        if not self.unseen_labels:
            unseen = self.compare_labels(other_args)

        write_to_file(self.unseen_labels, outfile_path)


class PreprocessGuttman(Preprocess):
    def __init__(self, args):
        super(PreprocessGuttman, self).__init__(args)
        # overriding Preprocess attributes
        self.data_dir = self.data_root_dir
        self.ids_file_path = self.data_dir / f"output.txt"
        self.annotation_file_path = self.data_dir / f"output.txt"
        self.docs_dir = self.data_dir / f"annotation_Conny_final_npwd.xlsm"

        # Guttman specific attributes
        self.num_patients = 0
        self.num_missing_qualifier_docs = 0
        self.id_to_concept = dict()
        self.concept_to_id = dict()
        self.pt_to_concept_id = dict()
        self.present_concepts = Counter()
        self.mentioned_absent = Counter()
        self.mentioned_unknown_concepts = Counter()
        self.missing_qualifier_concepts = Counter()
        self.doc_id_to_doc_texts = self._extract_doc_texts()

    def _extract_doc_texts(self):
        """

        :return: dict mapping doc_id to doc text; doc_id == patientID_noteNumber e.g. "5333328_0"
        """
        excel_file = pd.ExcelFile(self.docs_dir)
        return {sheet_name: excel_file.parse(sheet_name=sheet_name, usecols="B", header=None).iloc[0][1]
                for sheet_name in excel_file.sheet_names}

    def _get_id_concept(self, id_concept_line, delimiter='|'):
        """

        :param id_concept_line:
        :param delimiter:
        :return:
        """
        id, concept, *qualifier = id_concept_line.split(delimiter)
        id = id.strip()
        concept = concept.strip()
        self.id_to_concept[id] = concept
        self.concept_to_id[concept] = id
        return id, concept

    def _update_id_concept(self, id_concept_line, p_id, n_num, delimiter='|'):
        """

        :param id_concept_line:
        :param p_id:
        :param n_num:
        :param delimiter:
        :return:
        """
        id, concept = self._get_id_concept(id_concept_line, delimiter)
        self.pt_to_concept_id[p_id][n_num].add(id)
        self.doc_label_dict[f"{p_id}_{n_num}"].add(id)
        return id, concept

    def _extract_ids(self):
        for line in lines_from_file(self.ids_file_path):
            if line:
                # pt id line, in format: #######_#
                if '_' in line and '|' not in line:
                    yield line

    def _extract_annotation(self):
        pt_id, note_num = 0, 0
        for line in lines_from_file(self.annotation_file_path):
            if line:
                # pt id line, in format: #######_#
                if '_' in line and '|' not in line:
                    # print(f'pt id: {line}')
                    pt_id, note_num = line.split('_')
                    if not self.pt_to_concept_id.get(pt_id):
                        self.num_patients += 1
                        self.pt_to_concept_id[pt_id] = dict()
                        self.pt_to_concept_id[pt_id][note_num] = set()
                    else:
                        self.pt_to_concept_id[pt_id][note_num] = set()
                    self.doc_label_dict[f"{pt_id}_{note_num}"] = set()
                    continue

                # only 1 concept in line
                if ';' not in line:
                    if 'present' in line or '410515003' in line:
                        id, _ = self._update_id_concept(line, pt_id, note_num)
                        self.class_counter.update([id])
                        continue
                    elif 'Unknown' in line or '261665006' in line:
                        id, _ = self._get_id_concept(line)
                        self.mentioned_unknown_concepts.update([id])
                        continue
                    elif 'absent' in line or '410516002' in line:
                        id, _ = self._get_id_concept(line)
                        self.mentioned_absent.update([id])
                        continue
                    else:
                        print(f'Some other type of qualifier??? in line:\n'
                              f'{line}, pt ID: {pt_id}_{note_num}')
                        id, _ = self._get_id_concept(line)
                        self.missing_qualifier_concepts.update([id])
                        self.num_missing_qualifier_docs += 1

                elif ';' in line:
                    # more than 1 concept in line, ';' delimited
                    for concept_line in line.split(';'):
                        if 'present' in concept_line or '410515003' in concept_line:
                            id, _ = self._update_id_concept(concept_line, pt_id, note_num)
                            self.class_counter.update([id])
                        elif 'Unknown' in concept_line or '261665006' in concept_line:
                            id, _ = self._get_id_concept(concept_line)
                            self.mentioned_unknown_concepts.update([id])
                        elif 'absent' in concept_line or '410516002' in concept_line:
                            id, _ = self._get_id_concept(concept_line)
                            self.mentioned_absent.update([id])
                        else:
                            print(f'Some other type of qualifier??? in line:\n'
                                  f'{concept_line}')
                            id, _ = self._get_id_concept(concept_line)
                            self.missing_qualifier_concepts.update([id])
                            self.num_missing_qualifier_docs += 1
                else:
                    print(f'What is different about this line? Should not land here!!:\n'
                          f'{line}')
                    continue

        # set to list in self.doc_label_dict
        self.doc_label_dict = {doc_id: list(label_set) for doc_id, label_set in self.doc_label_dict.items()}

    def _extract_doc(self, doc_id):
        return self.doc_id_to_doc_texts[doc_id]

    def get_ids_and_binary_labels(self):
        if not self.docs_labels_list:
            self.make_docs_labels_list()

        labels = [d['labels_id'] for d in self.docs_labels_list]
        doc_ids = [d['ids'] for d in self.docs_labels_list]

        binarized_labels = self.mlb.fit_transform(labels)

        return doc_ids, binarized_labels

    # TODO: guttman stratified partitions


def main():
    args = cl_parser()
    print(args)
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

    # args.data_dir = "guttman"
    # args.partition = "all"
    # print(args)
    # guttmann_preprocess = PreprocessGuttman(args)
    # guttmann_preprocess.create_dataset_json()
    # guttmann_preprocess.plot_label_distribution()


if __name__ == '__main__':
    main()
