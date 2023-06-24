# -*- coding: utf-8 -*-
#
# Nom du fichier:       search_view.py
# Date de création:     23/06/2023
# Version:              0.0.1
# Auteur:               Simon STEPHAN <simon.stephan@u-bourgogne.fr>
#
# Copyright (c) 2023,
# Tous droits réservés. 
#
import csv
import sqlite3

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, \
    QListWidget, QTableWidgetItem, QAbstractItemView, QTableWidget, QWidget, QListWidgetItem, QHeaderView, QFileDialog
from PyQt5.QtWidgets import QSplitter, QPushButton, QVBoxLayout, QHBoxLayout

import settings
from ui import JournalView


class SearchView(QDialog):
    def __init__(self, *args, **kwargs):

        super(SearchView, self).__init__(*args, **kwargs)

        self.resize(1600, 1000)

        # Get unique and sorted countries and regions
        categories, areas, countries, regions, types = self.load_data()

        # Définir le titre de la fenêtre
        self.setWindowTitle("Search View")

        # Initialiser le layout principal
        self.layout = QHBoxLayout(self)

        # Initialiser le label de resultats
        self.labelCount = QtWidgets.QLabel('- results')

        # Définir le splitter
        splitter = QSplitter()

        # Partie gauche : formulaire
        self.formLayout = QVBoxLayout()
        leftWidget = QWidget()

        # Champs du formulaire
        self.keywordLabel = QLabel("Keyword:")
        self.keywordEdit = QLineEdit()
        self.formLayout.addWidget(self.keywordLabel)
        self.formLayout.addWidget(self.keywordEdit)

        # Quartile selection
        self.quartileLabel = QLabel("Quartile:")
        self.quartileCombo = QComboBox()
        self.quartileCombo.addItems(['-', 'Q1', 'Q2', 'Q3', 'Q4'])
        self.formLayout.addWidget(self.quartileLabel)
        self.formLayout.addWidget(self.quartileCombo)

        # SJR rating selection
        self.sjrLabel = QLabel("SJR:")
        self.sjrEdit = QLineEdit()
        self.formLayout.addWidget(self.sjrLabel)
        self.formLayout.addWidget(self.sjrEdit)

        # Impact Factor
        self.impactFactorLabel = QLabel("Impact Factor:")
        self.impactFactorEdit = QLineEdit()
        self.formLayout.addWidget(self.impactFactorLabel)
        self.formLayout.addWidget(self.impactFactorEdit)

        # Country selection
        self.countryLabel = QLabel("Country:")
        self.countryCombo = QComboBox()
        self.countryCombo.addItem("-")  # For allowing an empty option
        self.countryCombo.addItems(countries)
        self.formLayout.addWidget(self.countryLabel)
        self.formLayout.addWidget(self.countryCombo)

        # Region selection
        self.regionLabel = QLabel("Region:")
        self.regionCombo = QComboBox()
        self.regionCombo.addItem("-")  # For allowing an empty option
        self.regionCombo.addItems(regions)
        self.formLayout.addWidget(self.regionLabel)
        self.formLayout.addWidget(self.regionCombo)

        # Type selection
        self.typeLabel = QLabel("Type:")
        self.typeCombo = QComboBox()
        self.typeCombo.addItem("-")  # For allowing an empty option
        self.typeCombo.addItems(types)
        self.formLayout.addWidget(self.typeLabel)
        self.formLayout.addWidget(self.typeCombo)

        # Categories List
        self.categoriesLabel = QLabel("Categories:")
        self.categoriesList = QListWidget()
        self.categoriesList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for category in categories:
            item = QListWidgetItem(category[0])  # assuming category is a tuple
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Unchecked)
            self.categoriesList.addItem(item)
        self.formLayout.addWidget(self.categoriesLabel)
        self.formLayout.addWidget(self.categoriesList)

        # Categories Filter
        self.categoriesFilterLabel = QLabel("Filter Categories:")
        self.categoriesFilter = QLineEdit()
        self.categoriesFilter.textChanged.connect(self.update_categories)
        self.formLayout.addWidget(self.categoriesFilterLabel)
        self.formLayout.addWidget(self.categoriesFilter)

        # Areas List
        self.areasLabel = QLabel("Areas:")
        self.areasList = QListWidget()
        self.areasList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for area in areas:
            item = QListWidgetItem(area[0])  # assuming area is a tuple
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Unchecked)
            self.areasList.addItem(item)
        self.formLayout.addWidget(self.areasLabel)
        self.formLayout.addWidget(self.areasList)

        # Areas Filter
        self.areasFilterLabel = QLabel("Filter Areas:")
        self.areasFilter = QLineEdit()
        self.areasFilter.textChanged.connect(self.update_areas)
        self.formLayout.addWidget(self.areasFilterLabel)
        self.formLayout.addWidget(self.areasFilter)

        # Annuler

        # Bouton de recherche
        searchButtonLayout = QHBoxLayout()
        self.searchButton = QPushButton("Search")
        self.searchButton.setDefault(True)  # Make it the default button
        self.searchButton.clicked.connect(self.search_journals)
        searchButtonLayout.addStretch(1)
        searchButtonLayout.addWidget(self.searchButton)
        self.formLayout.addLayout(searchButtonLayout)

        leftWidget.setLayout(self.formLayout)

        # Right part: Journals table
        self.journalsTable = QTableWidget(0, 8)
        self.journalsTable.setHorizontalHeaderLabels(
            ["ID", "Title", "Type", "SJR", "ImpactFactor", "H Index", "Country",
             "Region", "Publisher", "Categories", "Areas"])

        self.journalsTable.verticalHeader().setVisible(False)
        self.journalsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.journalsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.journalsTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.journalsTable.cellDoubleClicked.connect(self.open_journal_view)

        self.resize_table()

        rightWidget = QWidget()
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.journalsTable)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.clear_form)

        exportButtonLayout = QHBoxLayout()
        self.exportButton = QPushButton("Export")
        self.exportButton.clicked.connect(self.export_data)

        exportButtonLayout.addStretch(1)
        exportButtonLayout.addWidget(self.labelCount)
        exportButtonLayout.addWidget(self.cancelButton)
        exportButtonLayout.addWidget(self.exportButton)
        rightLayout.addLayout(exportButtonLayout)

        rightWidget.setLayout(rightLayout)

        # Add widgets to splitter
        splitter.addWidget(leftWidget)
        splitter.addWidget(rightWidget)

        # Set initial proportions
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self.areasList.sortItems()
        self.categoriesList.sortItems()

        # Add splitter to layout
        self.layout.addWidget(splitter)

        # Configure the central widget
        self.setLayout(self.layout)

    def update_categories(self, text):
        """This method updates the categories list based on the entered text."""

        for i in range(self.categoriesList.count()):
            item = self.categoriesList.item(i)
            item.setHidden(text != "" and text.lower() not in item.text().lower())
        self.categoriesList.sortItems()

    def update_areas(self, text):
        """This method updates the areas list based on the entered text."""

        for i in range(self.areasList.count()):
            item = self.areasList.item(i)
            item.setHidden(text != "" and text.lower() not in item.text().lower())
        self.areasList.sortItems()

    def search_journals(self):
        """This method performs the search in the database based on the form field values."""

        self.journalsTable.setRowCount(0)

        # Retrieve form field values
        keyword = self.keywordEdit.text()
        quartile = self.quartileCombo.currentText()
        sjr = self.sjrEdit.text()
        impactfactor = self.impactFactorEdit.text()

        type_ = self.typeCombo.currentText()
        country = self.countryCombo.currentText()
        region = self.regionCombo.currentText()

        areas = [self.areasList.item(i).text() for i in range(self.areasList.count()) if
                 self.areasList.item(i).checkState() == Qt.Checked]
        categories = [self.categoriesList.item(i).text() for i in range(self.categoriesList.count()) if
                      self.categoriesList.item(i).checkState() == Qt.Checked]

        # Prepare the SQL query
        query = """SELECT journaux.* FROM journaux
                LEFT JOIN journaux_categories ON journaux.id = journaux_categories.id_journal
                LEFT JOIN journaux_areas ON journaux.id = journaux_areas.id_journal
                """
        params = []

        # Start WHERE clause
        where_clauses = []

        # Add search criteria as needed
        if keyword:
            keyword = keyword.replace(' ', '%')
            where_clauses.append("journaux.title LIKE ?")
            params.append(f"%{keyword}%")

        if sjr:
            where_clauses.append("CAST(journaux.sjr AS REAL) >= ?")
            params.append(sjr)

        if impactfactor:
            where_clauses.append("CAST(journaux.impact_factor AS REAL) >= ?")
            params.append(impactfactor)

        if type_ != "-":
            where_clauses.append("journaux.type = ?")
            params.append(type_)

        if country != '-':
            where_clauses.append("journaux.country = ?")
            params.append(country)

        if region != '-':
            where_clauses.append("journaux.region = ?")
            params.append(region)

        if categories:
            where_clauses.append(
                "journaux_categories.label_category IN ({})".format(', '.join(['?'] * len(categories))))
            params.extend(categories)

        if quartile != '-':
            quartile_value = int(quartile[1])  # Convert "q1", "q2", etc. to 1, 2, etc.
            where_clauses.append("CAST(SUBSTR(journaux_categories.quartile, 2) AS INTEGER) <= ?")
            params.append(quartile_value)

        if areas:
            where_clauses.append("journaux_areas.label_area IN ({})".format(', '.join(['?'] * len(areas))))
            params.extend(areas)

        # Construct WHERE clause
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        # Finalize query
        query += " GROUP BY journaux.id"

        # Execute the query
        db = sqlite3.connect(settings.database)
        cursor = db.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Check number of results
        if len(rows) > 1000:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("Too many results. Please narrow down your search.")
            error_dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
            error_dialog.exec_()
            return

        # Update labelCount with number of results
        self.labelCount.setText(f"{len(rows)} results")

        # Affiche les journaux dans le tableau
        for row in rows:
            current_row_index = self.journalsTable.rowCount()
            self.journalsTable.insertRow(current_row_index)

            # Insert basic data
            self.journalsTable.setItem(current_row_index, 0, QTableWidgetItem(str(row[0])))  # id
            self.journalsTable.setItem(current_row_index, 1, QTableWidgetItem(row[2]))  # title
            self.journalsTable.setItem(current_row_index, 2, QTableWidgetItem(row[3]))  # type
            self.journalsTable.setItem(current_row_index, 3, QTableWidgetItem(row[5]))  # sjr
            self.journalsTable.setItem(current_row_index, 4, QTableWidgetItem(str(row[17])))  # impact_factor
            self.journalsTable.setItem(current_row_index, 5, QTableWidgetItem(str(row[6])))  # h_index
            self.journalsTable.setItem(current_row_index, 6, QTableWidgetItem(row[14]))  # country
            self.journalsTable.setItem(current_row_index, 7, QTableWidgetItem(row[15]))  # region
            self.journalsTable.setItem(current_row_index, 8, QTableWidgetItem(row[16]))  # publisher

            # Get and insert categories
            cursor.execute("""SELECT label_category FROM journaux_categories WHERE id_journal = ?""", (row[0],))
            categories = [c[0] for c in cursor.fetchall()]
            categories_text = ', '.join(categories[:3])
            if len(categories) > 3:
                categories_text += f" and {len(categories) - 3} more categories"
            self.journalsTable.setItem(current_row_index, 8, QTableWidgetItem(categories_text))

            # Get and insert areas
            cursor.execute("""SELECT label_area FROM journaux_areas WHERE id_journal = ?""", (row[0],))
            areas = [a[0] for a in cursor.fetchall()]
            areas_text = ', '.join(areas[:3])
            if len(areas) > 3:
                areas_text += f" and {len(areas) - 3} more areas"
            self.journalsTable.setItem(current_row_index, 9, QTableWidgetItem(areas_text))

        db.close()

    def load_data(self):

        # Connect to the database
        db = sqlite3.connect(settings.database)
        cursor = db.cursor()

        cursor.execute("""SELECT * FROM categories""")
        categories = cursor.fetchall()

        cursor.execute("""SELECT * FROM areas""")
        areas = cursor.fetchall()

        cursor.execute("SELECT DISTINCT type FROM journaux ORDER BY type")
        types = [row[0] for row in cursor.fetchall()]

        # Execute SQL queries to get unique and sorted list of countries and regions
        cursor.execute("SELECT DISTINCT country FROM journaux ORDER BY country")
        countries = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT region FROM journaux ORDER BY region")
        regions = [row[0] for row in cursor.fetchall()]

        # Close the connection
        db.close()

        return categories, areas, countries, regions, types

    def clear_form(self):
        # Clear the table
        self.journalsTable.setRowCount(0)

        # Clear form fields
        self.keywordEdit.clear()
        self.quartileCombo.setCurrentIndex(0)
        self.sjrEdit.clear()
        self.typeCombo.setCurrentIndex(0)
        self.countryCombo.setCurrentIndex(0)
        self.regionCombo.setCurrentIndex(0)

        self.labelCount.setText(f"- results")

        # Clear the checked items in areasList and categoriesList
        for i in range(self.areasList.count()):
            self.areasList.item(i).setCheckState(Qt.Unchecked)
        for i in range(self.categoriesList.count()):
            self.categoriesList.item(i).setCheckState(Qt.Unchecked)

    def resize_table(self):
        header = self.journalsTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def open_journal_view(self, row):
        # Récupère l'ID du journal en supposant qu'il est stocké dans la première colonne
        journal_id = self.journalsTable.item(row, 0).text()
        self.journal_view = JournalView(journal_id)
        self.journal_view.show()

    def export_data(self):

        if self.journalsTable.rowCount() == 0:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
            error_dialog.setWindowTitle("Error")
            error_dialog.setText("No data to export.")
            error_dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
            error_dialog.exec_()
            return

        # Demandez à l'utilisateur où enregistrer le fichier CSV
        save_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV(*.csv)')

        if save_path:
            # Ouvrir le fichier CSV en mode écriture
            with open(save_path, 'w', newline='') as file:
                writer = csv.writer(file)

                # Écrire les en-têtes de colonne
                headers = ['ID', 'SourceID', 'Title', 'Type', 'ISSN', 'SJR', 'H Index', 'Last Year Docs',
                           'Three Years Docs',
                           'Refs', 'Cites', 'Citable Docs', 'Cites per Docs', 'Ref per Docs', 'Country', 'Region',
                           'Publisher', 'IF', 'Categories (Quartile)', 'Areas']
                writer.writerow(headers)

                # Ouvrir la connexion à la base de données
                db = sqlite3.connect(settings.database)
                cursor = db.cursor()

                # Parcourir chaque ligne du tableau
                for row_number in range(self.journalsTable.rowCount()):
                    # Récupérer l'ID du journal
                    journal_id = self.journalsTable.item(row_number, 0).text()

                    # Exécuter la requête pour récupérer les informations complètes du journal
                    cursor.execute("SELECT * FROM journaux WHERE id = ?", (journal_id,))
                    journal_data = cursor.fetchone()

                    # Récupérer les catégories et les zones
                    cursor.execute("SELECT label_category, quartile FROM journaux_categories WHERE id_journal = ?",
                                   (journal_id,))
                    categories = cursor.fetchall()
                    categories_text = '; '.join([f"{c[0]}({c[1]})" for c in categories])

                    cursor.execute("SELECT label_area FROM journaux_areas WHERE id_journal = ?", (journal_id,))
                    areas = cursor.fetchall()
                    areas_text = '; '.join(a[0] for a in areas)

                    # Ajouter les données de journal au CSV
                    row = list(journal_data) + [categories_text, areas_text]
                    writer.writerow(row)

                db.close()
