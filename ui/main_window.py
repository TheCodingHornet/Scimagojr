# -*- coding: utf-8 -*-
#
# File Name:       main_window.py
# Creation Date:   23/06/2023
# Version:         0.0.1
# Author:          Simon STEPHAN <simon.stephan@u-bourgogne.fr>
#
# Copyright (c) 2023,
# All rights reserved.
#

import csv
import os
import re
import sqlite3

import requests
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QLabel, QTableWidget, QWidget, QHBoxLayout, \
    QTableWidgetItem, QAbstractItemView, QHeaderView, QMessageBox

import settings
from ui.journal_view import JournalView
from ui.search_view import SearchView


class MainWindow(QMainWindow):
    """
    The MainWindow class is responsible for creating the main window of the application.

    Example usage:
    window = MainWindow()
    window.show()
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the MainWindow dialog.
        """

        super(MainWindow, self).__init__(*args, **kwargs)

        # Window configuration
        self.setWindowTitle("SciMago Ranking")
        self.setFixedSize(1200, 800)

        # Widget creation
        self.label = QLabel("Label Text")
        self.table = QTableWidget(0, 4)

        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Categories", "Domains"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.cellDoubleClicked.connect(self.open_journal_view)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.updateListButton = QPushButton("Update List")
        self.updateListButton.clicked.connect(self.update_list)

        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.open_search)

        self.viewButton = QPushButton("View")
        self.viewButton.clicked.connect(self.open_selected)

        self.closeAppButton = QPushButton("Close")
        self.closeAppButton.clicked.connect(self.close_app)

        # Connecting the "clicked" signal of the "Update List" button to the "update_list" method

        # Layout configuration
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.label)
        mainLayout.addWidget(self.table)

        # Button alignment
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.updateListButton)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.searchButton)
        buttonLayout.addWidget(self.viewButton)
        buttonLayout.addWidget(self.closeAppButton)
        mainLayout.addLayout(buttonLayout)

        # Central widget configuration
        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        self.load_data()

    def open_journal_view(self, row):
        """
        Opens the view for a selected journal, assuming its ID is stored in the first column
        """
        journal_id = self.table.item(row, 0).text()
        self.journal_view = JournalView(journal_id)
        self.journal_view.show()

    def update_list(self):
        """
        Updates the list of journals
        """

        db = sqlite3.connect(settings.database)
        cursor = db.cursor()

        # Create the directory if it does not exist
        if not os.path.isdir(settings.temporary_folder):
            os.makedirs(settings.temporary_folder)

        # Download the file
        response = requests.get(settings.data_url)
        response.raise_for_status()

        # Save the file
        with open(settings.csv_file_path, "wb") as f:
            f.write(response.content)

        # Delete all records from the journaux_categories and journaux_areas tables
        cursor.execute("DELETE FROM journaux_categories")
        cursor.execute("DELETE FROM journaux_areas")

        # Register the file in the database
        with open(settings.csv_file_path, 'r') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                # Check if the journal already exists
                cursor.execute("""
                    SELECT id FROM journaux WHERE issn = ?
                """, (row['Issn'],))
                result = cursor.fetchone()

                sjr_value = row['SJR']
                sjr_value = sjr_value.replace(",", ".")  # Replace comma with a dot

                if sjr_value != '':
                    sjr_value = float(sjr_value)  # Convert to float
                else:
                    sjr_value = 0.0

                if result is not None:
                    journal_id = result[0]
                    # Update existing journal
                    cursor.execute("""
                        UPDATE journaux SET 
                        sourceid = ?, title = ?, type = ?, sjr = ?, h_index = ?, last_year_docs = ?, 
                        three_years_docs = ?, refs = ?, cites = ?, citables = ?, cites_on_docs = ?, 
                        ref_on_docs = ?, country = ?, region = ?, publisher = ?
                        WHERE issn = ?
                    """, (
                        row['Sourceid'], row['Title'], row['Type'], sjr_value, row['H index'],
                        row['Total Docs. (2022)'],
                        row['Total Docs. (3years)'], row['Total Refs.'], row['Total Cites (3years)'],
                        row['Citable Docs. (3years)'], row['Cites / Doc. (2years)'], row['Ref. / Doc.'], row['Country'],
                        row['Region'], row['Publisher'], row['Issn']
                    ))
                else:
                    # Create a new journal
                    cursor.execute("""
                        INSERT INTO journaux (
                        sourceid, title, type, issn, sjr, h_index, last_year_docs, 
                        three_years_docs, refs, cites, citables, cites_on_docs, 
                        ref_on_docs, country, region, publisher
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['Sourceid'], row['Title'], row['Type'], row['Issn'], row['SJR'], row['H index'],
                        row['Total Docs. (2022)'], row['Total Docs. (3years)'], row['Total Refs.'],
                        row['Total Cites (3years)'],
                        row['Citable Docs. (3years)'], row['Cites / Doc. (2years)'], row['Ref. / Doc.'], row['Country'],
                        row['Region'], row['Publisher']
                    ))
                    journal_id = cursor.lastrowid

                # Process categories
                for category in row['Categories'].split(';'):
                    # We use a regular expression to separate the name of the category and the quartile
                    match = re.match(r'(.*)(\(Q[1-4]\))$', category.strip())

                    if match is not None:
                        category, quartile = match.groups()
                        category = category.strip()
                        quartile = quartile.strip('()')
                    else:
                        category = category.strip()
                        quartile = '-'

                    cursor.execute("""
                        INSERT OR IGNORE INTO categories (label)
                        VALUES (?)
                    """, (category,))

                    cursor.execute("""
                        INSERT OR REPLACE INTO journaux_categories (id_journal, label_category, quartile)
                        VALUES (?, ?, ?)
                    """, (journal_id, category, quartile))

                # Process areas
                for area in row['Areas'].split(';'):
                    area = area.strip()

                    cursor.execute("""
                        INSERT OR IGNORE INTO areas (label)
                        VALUES (?)
                    """, (area,))

                    cursor.execute("""
                        INSERT OR REPLACE INTO journaux_areas (id_journal, label_area)
                        VALUES (?, ?)
                    """, (journal_id, area))

        db.commit()
        db.close()

        # Load data into the table
        self.load_data()

    def load_data(self):
        """
        Load data into the table
        """

        db = sqlite3.connect(settings.database)
        cursor = db.cursor()

        # Clear table data
        self.table.setRowCount(0)

        # Get all journal data from the database
        cursor.execute("""
            SELECT journaux.id, journaux.title, GROUP_CONCAT(categories.label), GROUP_CONCAT(areas.label) 
            FROM journaux
            LEFT JOIN journaux_categories ON journaux.id = journaux_categories.id_journal
            LEFT JOIN categories ON categories.label = journaux_categories.label_category
            LEFT JOIN journaux_areas ON journaux.id = journaux_areas.id_journal
            LEFT JOIN areas ON areas.label = journaux_areas.label_area
            GROUP BY journaux.id
        """)
        rows = cursor.fetchall()

        # Show the number of journals found
        self.label.setText(str(len(rows)) + " journals found")

        for row in rows:
            id, title, categories, areas = row
            categories_list = categories.split(',')
            areas_list = areas.split(',')

            if len(categories_list) > 2:
                categories_str = ', '.join(categories_list[:2]) + f' (+{len(categories_list) - 2} categories)'
            else:
                categories_str = ', '.join(categories_list)

            if len(areas_list) > 2:
                areas_str = ', '.join(areas_list[:2]) + f' (+{len(areas_list) - 2} domains)'
            else:
                areas_str = ', '.join(areas_list)

            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(id)))
            self.table.setItem(row_position, 1, QTableWidgetItem(title))
            self.table.setItem(row_position, 2, QTableWidgetItem(categories_str))
            self.table.setItem(row_position, 3, QTableWidgetItem(areas_str))

        db.close()

    def open_selected(self):
        """
        Open selected journal
        """
        # Get the index of the selected row
        selected_indexes = self.table.selectionModel().selectedRows()
        if selected_indexes:
            # If a row is selected, retrieve the journal ID
            selected_index = selected_indexes[0]
            # Open the journal view
            self.open_journal_view(selected_index.row())
        else:
            # If no row is selected, display an error message
            QMessageBox.critical(self, "Error", "No journal selected")

    def open_search(self):
        """
        Open the search view
        """
        self.search_view = SearchView(self)
        self.search_view.show()

    def close_app(self):
        """
        Close the application
        """
        self.close()
