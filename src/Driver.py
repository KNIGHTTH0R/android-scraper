#!/usr/bin/env python3
from AndroidApp import AndroidApp
from Commands.InternationalizationCommand import InternationalizationCommand
from Commands.AccountManagerUseCommand import AccountManagerUseCommand
from Commands.InternetUseCommand import InternetUseCommand
from Commands.SSLUseCommand import SSLUseCommand
from Commands.SharingCenterUseCommand import SharingCenterUseCommand


__author__ = 'kocsen'

import sys
import logging
from os.path import *
from db.DBConnect import write_app_data

CONFIG_FILE = "dbconfig.json"


def main():
    """
    Setup the logging, gather the path of the UNCOMPRESSED APK
    Run static analysis tool.
    """
    arguments = sys.argv
    if len(arguments) < 2:
        logging.error("Need more arguments")
        logging.info("USAGE: ./Driver.py path/to/uncompressedAPK")
        exit()

    # Carry on with app preconditions
    path = abspath(arguments[1])
    analyze_app(path, save_to_db=False)


def analyze_app(path, save_to_db=False):
    """
    Actually analyzes the app, goes through the commands and saves results.

    :param path:
    :return:
    """
    setup_logging()

    app_name = basename(path).split(".apk.uncompressed")[0]
    logging.info("Starting Feature Scraper")
    logging.info("App name:\t%s", app_name)

    current_app = AndroidApp(app_name, abspath(path))
    internet_use = InternetUseCommand(current_app).execute()

    features = {
        'Internet': False,
        'Account Manager': False,
        'Use SSL': False,

        'Sharing-Sending': False,
        'Internationalization': False
    }

    if internet_use:
        features['Internet'] = True
        # Check for account manager
        features['Account Manager'] = AccountManagerUseCommand(current_app).execute()
        # Check for SSL
        features['Use SSL'] = SSLUseCommand(current_app).execute()

    # Check for sharing
    features['Sharing-Sending'] = SharingCenterUseCommand(current_app).execute()

    # Check for internationalization
    features['Internationalization'] = InternationalizationCommand(current_app).execute()

    logging.info("==== FINAL RESULTS ===")
    logging.info(features)

    # Now add the features to the app object.
    current_app.features = features

    if (save_to_db):
        logging.info("Saving findings to database...")
        write_app_data(current_app, CONFIG_FILE)


def setup_logging():
    """
    Logging setup
    """
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)2s ', level=logging.DEBUG)
    # logging.basicConfig(filename='android-scraper.log', level=logging.DEBUG)


if __name__ == "__main__":
    main()