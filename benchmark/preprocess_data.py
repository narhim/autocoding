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
            # if self.args.partition == "training":
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
            print(f"{out_file_dir} already exists!")

        json_file_path = out_file_dir / f"{self.args.partition}.json"
        write_to_json(self.docs_labels_list, json_file_path)
        try:
            read_from_json(self.docs_labels_list, json_file_path)
        except AssertionError:
            print(f"WARNING: json file not identical to original data!!!")
        print(f"Pre-processed {self.args.data_dir} {self.args.partition} partition saved to {json_file_path}.")


class PreprocessGuttman(Preprocess):
    def __init__(self, args):
        super(PreprocessGuttman, self).__init__(args)
        self.data_dir = self.data_root_dir
        self.ids_file_path = self.data_dir / f"output.txt"
        self.annotation_file_path = self.data_dir / f"output.txt"
        self.docs_dir = self.data_dir / f"annotation_Conny_final_npwd.xlsm"

        # Guttman specific attributes
        self.num_docs = 0
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
                    self.num_docs += 1
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


def main():
    args = cl_parser()
    print(args)
    # clef_19_preprocess = Preprocess(args)
    # clef_19_preprocess.create_dataset_json()
    args.data_dir = "guttman"
    args.partition = "all"
    print(args)
    guttmann_preprocess = PreprocessGuttman(args)
    guttmann_preprocess.create_dataset_json()


if __name__ == '__main__':
    main()
