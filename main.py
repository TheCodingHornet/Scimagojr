# -*- coding: utf-8 -*-
#
# File Name:       main.py
# Creation Date:   23/06/2023
# Version:         0.0.1
# Author:          Simon STEPHAN <simon.stephan@u-bourgogne.fr>
#
# Copyright (c) 2023,
# All rights reserved.
#

import sqlite3
import sys

from PyQt5.QtWidgets import QApplication

import settings
from ui.main_window import MainWindow


def initialize_database():
    """
    This function initializes the database, creating necessary tables if they don't exist.

    Example:
        >>> initialize_database()
    """

    db = sqlite3.connect(settings.database)
    cursor = db.cursor()

    # Creating the table "journals"
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journals (
            id INTEGER PRIMARY KEY,
            sourceid TEXT,
            title TEXT,
            type TEXT,
            issn TEXT,
            sjr REAL,
            h_index INTEGER,
            last_year_docs INTEGER,
            three_years_docs INTEGER,
            refs INTEGER,
            cites INTEGER,
            citables INTEGER,
            cites_on_docs REAL,
            ref_on_docs REAL,
            country TEXT,
            region TEXT,
            publisher TEXT,
            impact_factor REAL
        )
    """)
    # Creating the table "categories"
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            label TEXT PRIMARY KEY
        )
    """)
    # Creating the table "journals_categories" with the "quartile" field
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journals_categories (
            id_journal INTEGER,
            label_category TEXT,
            quartile TEXT,
            FOREIGN KEY(id_journal) REFERENCES journals(id),
            FOREIGN KEY(label_category) REFERENCES categories(label)
        )
    """)
    # Creating the table "areas"
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS areas (
            label TEXT PRIMARY KEY
        )
    """)
    # Creating the table "journals_areas"
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journals_areas (
            id_journal INTEGER,
            label_area TEXT,
            FOREIGN KEY(id_journal) REFERENCES journals(id),
            FOREIGN KEY(label_area) REFERENCES areas(label)
        )
    """)

    db.commit()
    db.close()


def main():
    """
    This is the main function, it initializes the database and starts the GUI.

    Example:
        >>> main()
    """

    initialize_database()
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
