#!/usr/bin/env python

import argparse
import requests
import json

from requests.exceptions import ConnectionError

from os.path import exists, isdir, join
from os import mkdir


def download_file(url, local_filename):
    # Taken from here
    # https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py/16696317#16696317
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                #  f.flush() commented by recommendation from J.F.Sebastian
    return local_filename


def execute_from_command_line():
    parser = argparse.ArgumentParser(
        "Download files from Open Speech Corpus"
    )

    parser.add_argument(
        "--from",
        help="ID for the initial Audio Data",
        default=1
    )

    parser.add_argument(
        "--to",
        help="ID for the final Audio Data",
        default=500
    )

    parser.add_argument(
        "--url",
        help="URL for the list API endpoint",
        default="http://openspeechcorpus.contraslash.com/api/words/list/"
    )

    parser.add_argument(
        "--s3_prefix",
        default="https://s3.amazonaws.com/contraslash/openspeechcorpus/media/audio-data/v2/"
    )

    parser.add_argument(
        "--output_folder",
        help="Folder to store the recordings",
        type=str,
        required=True
    )

    parser.add_argument(
        "--output_file",
        help="File where transcriptions are stored",
        default="transcription.txt"
    )

    parser.add_argument(
        "--text_node",
        help="Inner node containing text information",
        default="level_sentence"
    )

    args = vars(parser.parse_args())
    url = args["url"]
    if args["from"] is not None or args["to"] is not None:
        url += "?"
        if args["from"] is not None:
            url += "from={}&".format(args["from"])
        if args["to"] is not None:
            url += "to={}".format(args["to"])
    print("Querying {}".format(url))
    response = requests.get(url)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode())
        print("We get {} audio datas".format(len(json_data)))
        if not exists(args["output_folder"]):
            print("Output folder does not exists")
            if args["force_create"]:
                print("force_create flag detected, creating {}".format(args["output_folder"]))
                mkdir(args["output_folder"])
            else:
                exit(1)
        if not isdir(args["output_folder"]):
            print("Output folder exists exists but is not a folder")
            exit(2)
        output_file = open(args["output_file"], "w+")
        for audio_data in json_data:
            audio_id = audio_data["audio"]["id"]
            file_name = "{}.mp4".format(join(args["output_folder"], str(audio_id)))
            output_file.write("{},{}\n".format(file_name, audio_data[args["text_node"]]["text"].strip()))
            if not exists(file_name):
                print("Download file with id: {}".format(audio_id))
                print("{}{}.mp4".format(args["s3_prefix"], audio_id))
                try:
                    download_file(
                        "{}{}.mp4".format(args["s3_prefix"], audio_id),
                        file_name
                    )
                except ConnectionError:
                    print("Error getting file {}".format(file_name))
        output_file.close()
    else:
        print("Cannot connect to server, response status was {}".format(response.status_code))

