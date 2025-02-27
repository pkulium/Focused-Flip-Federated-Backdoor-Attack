from ctypes import Union
from dataclasses import dataclass, field
from collections import defaultdict
import time
import pickle

from Params import Params


@dataclass
class Record:
    name: str
    start_time: str = field(init=False)
    rounds: dict = field(default_factory=dict)
    task = None
    model = None
    n_epochs: int = 0
    local_epoch: int = 0

    def __post_init__(self):
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def record_class_vars(self, target):
        if isinstance(target, Params):
            self.task = target.task
            self.model = target.model
            self.n_epochs = target.n_epochs
            self.local_epoch = target.local_epoch
            # pass

    def record_named_vars(self, attribute, val):
        setattr(self, attribute, val)

    def record_round_vars(self, info: dict, notation: dict = None):
        assert 'epoch' in info.keys() and 'backdoor' in info.keys()
        epoch = info.pop('epoch')
        if epoch not in self.rounds.keys():
            self.rounds[epoch] = {
                'asr': list(),
                'acc': list()
            }
        target = 'asr' if info.pop('backdoor') is True else 'acc'
        if notation is not None:
            info.update(notation)
        self.rounds[epoch][target].append(info)

    # class Report:


#     def __init__(self):
#         self.history = dict()


class FLReport:
    def __init__(self, load=None):
        if load is not None:
            self.load_history(load)
        self.current_record = None
        self.all_records = list()

    def load_history(self, load_path):
        pass

    def search_record(self, by, val):
        if by == 'name':
            for record in self.all_records:
                if record.name == val:
                    return record
        elif by == 'id':
            pass
        return 'No {}:{} found.'.format(by, val)

    def create_record(self, name, checkout=True):
        self.all_records.append(Record(name))
        if checkout:
            self.current_record = self.search_record(by='name', val=name)

    def record_class_vars(self, target):
        self.current_record.record_class_vars(target)

    def record_named_vars(self, attribute, val):
        self.current_record.record_named_vars(attribute, val)

    def record_round_vars(self, info: dict, notation:dict = None):
        self.current_record.record_round_vars(info, notation)


def save_report(report: FLReport, path):
    with open(path, 'wb') as f:
        pickle.dump(report, f)
    
    print("Saved to: {}".format(path))


def load_report(path):
    with open(path, 'rb') as f:
        report = pickle.load(f)
        return report


# import pickle
# with open("./result-fedavg/neurotoxin_fedavg_cifar_resnet18_h1.0_c20_100", 'rb') as f:
#     b = pickle.load(f)
# print(b.all_records)

import matplotlib.pyplot as plt

def plot_and_save_report(report_path, save_path):
    # Load the report
    report = load_report(report_path)

    # Extract data for plotting
    rounds = []
    accs = []
    asrs = []

    for record in report.all_records:
        for round_num, values in record.rounds.items():
            rounds.append(round_num)    
            accs.append(values['acc'][0]['Top-1'])
            asrs.append(values['asr'][0]['Top-1'])
    # accs = accs[:-1]
    # asrs = asrs[:-1]
    # rounds = rounds[:-1]

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(rounds, accs, label='Training Accuracy', marker='o')
    plt.plot(rounds, asrs, label='Attack Success Rate', marker='x')
    plt.xlabel('Rounds')
    plt.ylabel('Value')
    plt.title('Training Accuracy and ASR vs. Rounds')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path, format='png')  # Save the plot to the specified path
    plt.close()

# filename = 'naive_fedavg_imagenet_resnet18_h1_c20_100'
# filename = 'neurotoxin_fedavg_imagenet_resnet18_h1_c20_100'
# plot_and_save_report(f"./{filename}", f"./{filename}.png")
