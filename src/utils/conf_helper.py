"""Configuration helper to read variables from ini file."""
import configparser
import os


def get_path(file):
    """Return the absolute path of the app's files. They should be in the same folder as this py file."""
    folder, _ = os.path.split(__file__)
    file_path = os.path.join(folder, file)
    return file_path


def read_configuration():
    """
    Function to read variables from configuration file
    """
    config = configparser.ConfigParser()
    config.read(get_path("../variables.ini"))
    return config
