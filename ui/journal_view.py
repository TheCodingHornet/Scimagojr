# -*- coding: utf-8 -*-
#
# File Name:       journal_view.py
# Creation Date:   23/06/2023
# Version:         0.0.1
# Author:          Simon STEPHAN <simon.stephan@u-bourgogne.fr>
#
# Copyright (c) 2023,
# All rights reserved.
#

import sqlite3

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QListView, QTableWidget, \
    QTableWidgetItem, QHeaderView, QAbstractItemView

import settings


class JournalView(QDialog):
    """
    The JournalView class is responsible for creating a dialog to display the details of a specific journal.

    Example usage:
    view = JournalView(journal_id=1)
    view.show()
    """

    def __init__(self, journal_id, parent=None):
        """
        Initialize the JournalView dialog.

        Args:
            journal_id (int): The ID of the journal to display.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)

        # Set the window's configuration
        self.setWindowTitle("Journal Details")
        self.setFixedSize(1200, 800)

        # Create the layouts
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout_left = QVBoxLayout()
        self.layout_left.setContentsMargins(20, 20, 20, 20)
        self.grid_layout = QGridLayout()

        # Connect to the database and retrieve journal data
        db = sqlite3.connect(settings.database)
        cursor = db.cursor()

        # Fetch data for the specific journal
        cursor.execute("""SELECT * FROM journaux WHERE id = ?""", (journal_id,))
        journal_data = cursor.fetchone()

        # Fetch categories for the specific journal
        cursor.execute("""
                    SELECT categories.label, journaux_categories.quartile
                    FROM journaux_categories
                    JOIN categories ON categories.label = journaux_categories.label_category
                    WHERE journaux_categories.id_journal = ?
                """, (journal_id,))
        categories_data = cursor.fetchall()

        # Fetch areas for the specific journal
        cursor.execute("""
                    SELECT areas.label
                    FROM journaux_areas
                    JOIN areas ON areas.label = journaux_areas.label_area
                    WHERE journaux_areas.id_journal = ?
                """, (journal_id,))
        areas_data = cursor.fetchall()

        db.close()

        self.grid_layout.setColumnStretch(0, 1)  # Left label, 1/5 of the width
        self.grid_layout.setColumnStretch(1, 4)  # Right label, 4/5 of the width

        # Show the journal data in the grid layout
        self.display_journal_data(journal_data)

        # Add the grid layout to the left layout
        self.layout_left.addLayout(self.grid_layout)

        # Create the list of areas and add to the left layout
        self.areas_list = QListView()
        self.add_areas_to_list(areas_data)
        self.layout_left.addWidget(self.areas_list)

        # Add all the associated categories to the journal in the table
        self.categories_table = QTableWidget(1, 2)  # 1 row, 2 columns
        self.add_categories_to_table(categories_data)
        self.layout_left.addWidget(self.categories_table)

        self.layout.addLayout(self.layout_left)
        self.setLayout(self.layout)

    def display_journal_data(self, journal_data):
        """
        Display the journal data in the grid layout.

        Args:
            journal_data (tuple): The journal data.
        """
        labels = ["Source ID:", "Titre:", "Type:", "ISSN:", "SJR:", "H Index:", "Documents derniere année:",
                  "Documents 3 dernieres années:", "Références:", "Citations:", "Cités:", "Citations/documents:",
                  "Références/documents:", "Pays:", "Région:", "Editeur:"]
        for i, label in enumerate(labels):
            self.grid_layout.addWidget(QLabel(label), i, 0)
            self.grid_layout.addWidget(QLabel(str(journal_data[i + 1])), i, 1)

    def add_areas_to_list(self, areas_data):
        """
        Add all the areas of the journal to the list.

        Args:
            areas_data (list): The areas data.
        """
        areas_model = QStandardItemModel(self.areas_list)
        for area in areas_data:
            item = QStandardItem(area[0])
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            areas_model.appendRow(item)
        self.areas_list.setModel(areas_model)

    def add_categories_to_table(self, categories_data):
        """
        Add all the associated categories to the journal in the table.

        Args:
            categories_data (list): The categories data.
        """
        self.categories_table.setRowCount(len(categories_data))
        self.categories_table.setColumnCount(2)
        self.categories_table.setHorizontalHeaderLabels(["Category", "Quartile"])
        for row, category in enumerate(categories_data):
            # Add the category and the quartile to the table
            self.categories_table.setItem(row, 0, QTableWidgetItem(category[0]))
            quartile_item = QTableWidgetItem(category[1])
            # Set the cell style based on the quartile
            quartile_item.setBackground(self.get_color_based_on_quartile(category[1]))
            self.categories_table.setItem(row, 1, quartile_item)

        header = self.categories_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.categories_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.categories_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.categories_table.setSelectionMode(QAbstractItemView.SingleSelection)

    def get_color_based_on_quartile(self, quartile):
        """
        Get the color based on the quartile.

        Args:
            quartile (str): The quartile.

        Returns:
            QBrush: The brush with the corresponding color.
        """
        if quartile == "Q1":
            return QBrush(QColor('cyan'))
        elif quartile == "Q2":
            return QBrush(QColor('green'))
        elif quartile == "Q3":
            return QBrush(QColor('orange'))
        elif quartile == "Q4":
            return QBrush(QColor('red'))
        else:  # "-"
            return QBrush(QColor('gray'))
