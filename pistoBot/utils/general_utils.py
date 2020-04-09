import json
import logging

import yaml
from os import path
from nltk import download
import tensorflow as tf


def load_yaml(path: str):
    with open(path, 'r') as f:
        yaml_dict = yaml.load(f, Loader=yaml.FullLoader)
    return yaml_dict


def my_init(run):
    download("punkt")
    tf.random.set_seed(42)

    # Enable telegram start and stop notification
    my_info = get_my_info()
    if my_info:
        logging.info("Telegram notification enabled")
        from knockknock import telegram_sender
        telegram_decorator = telegram_sender(token=my_info['telegram_token'],
                                             chat_id=my_info['telegram_chat_id'])
        run = telegram_decorator(run)
    return run


def get_my_info(file_path: str = "../../data/inputs/personal/my-keys.txt") -> dict:
    """
    Read and return all personal
    info that will not upload on github.

    File .txt for .gitignore
    """
    my_info = None
    if path.exists(file_path):
        with open(file_path, 'r') as f:
            my_info = json.load(f)
    return my_info