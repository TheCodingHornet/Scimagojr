# -*- coding: utf-8 -*-
#
# File Name:       settings.py
# Creation Date:   23/06/2023
# Version:         0.0.1
# Author:          Simon STEPHAN <simon.stephan@u-bourgogne.fr>
#
# Copyright (c) 2023,
# All rights reserved.
#

import os

# The URL to download the CSV data.
data_url = "https://www.scimagojr.com/journalrank.php?out=xls"

# The temporary folder to store the downloaded CSV data.
temporary_folder = "./tmp"

# The path of the downloaded CSV file.
csv_file_path = os.path.join(temporary_folder, "journalrank.csv")

# The SQLite database name.
database = "scimagojr.db"
