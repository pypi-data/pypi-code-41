# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import matplotlib.pyplot as plt
import numpy as np

COLORMAP = plt.cm.plasma_r  # nopep8 pylint: disable=no-member


def create_trace_heatmap(output_filename,
                         rank_histories,
                         traces_to_display=30,
                         keys_to_display=40):

    # Display
    _, ax = plt.subplots(1, 1, figsize=(15, 10))

    ax.set_title('True key byte rank')
    ax.set_xlabel('Number of traces')
    ax.set_ylabel('Key')

    ranks = np.array(rank_histories)
    ranks = ranks[:traces_to_display, :keys_to_display]
    rank_logs = np.log(ranks + 1)

    ax.matshow(rank_logs, cmap=COLORMAP)

    for i, byte_ranks in enumerate(ranks):
        for j, byte_rank in enumerate(byte_ranks):
            if byte_rank != 0:
                ax.text(j, i, byte_rank, va='center', ha='center')

    plt.savefig(output_filename)


def create_confusion_matrix_plot(output_filename, confusion_matrix):

    fig, ax = plt.subplots()
    fig.set_size_inches(12, 12)

    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Guessed Byte")
    ax.set_ylabel("Real Byte")
    logged = np.log(confusion_matrix + 1)
    ax.imshow(logged, cmap=COLORMAP)
    plt.savefig(output_filename)


if __name__ == '__main__':
    create_trace_heatmap("./test.png", np.eye(15, 40))
    create_confusion_matrix_plot("./test2.png", np.eye(256, 256))
