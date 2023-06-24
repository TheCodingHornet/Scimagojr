# Scimagojr - Journal information retrieval

This project is a PyQt5 application offering a variety of features, including journal search and view, SQLite database
connection, and web interaction via Beautiful Soup.

## Description

The application offers a set of features for interacting with journal information. Users can search for journals based
on various criteria, view individual journal details, and interact with an SQLite database to store and retrieve data.
There's also a feature for data export and one for web interaction.

## Interfaces

![Main Window](tmp/main.png?raw=true "Main Window")

The Main Window serves as the launching pad for the application's features. Here, you can navigate to different
functionalities of the application such as searching for a journal or viewing a specific journal's details.

![Search Window](tmp/search.png?raw=true "Search Window")

The Search Window allows you to filter journals based on various criteria like keyword, quartile, SJR rating, impact
factor, country, region, type, categories, and areas. After entering your desired search parameters, hit the "Search"
button to display the results.

![View Window](tmp/view.png?raw=true "View Window")

The View Window presents a detailed view of a selected journal. Here, you'll find comprehensive information about the
journal, including its name, quartile, SJR rating, impact factor, country, region, type, categories, and areas.

## Getting Started

First, clone the repository to your local machine:

```bash
git clone https://github.com/TheCodingHornet/Scimagojr.git
```

Next, navigate into the cloned directory:

```bash
cd Scimagojr
```

Then, install the required Python packages:

```bash
pip install -r requirements.txt
```

After installing the required libraries, you can run the application using the following command at the root of the
repository:

```bash
python main.py
```

This will launch the application's graphical interface. You can use the various options in the interface to interact
with the application.

## Features

Here are the different features offered by this application:

- **Journal Search**: Use the search options to look for journals based on various criteria, such as keyword, date, and
  other parameters. The results are displayed in a user-friendly format.

- **Journal View**: Click on a journal from the search results to view more details about it. This includes all data
  fields associated with the journal.

- **SQLite Database Interaction**: The application allows you to interact with an SQLite database. You can store and
  retrieve data as needed.

- **Data Export**: This feature allows you to export the search results to a CSV file. This file can be saved locally
  for further analysis.

- **Web Interaction**: The application can connect to websites using the requests library and extract information using
  Beautiful Soup. This feature allows you to retrieve data from web pages.

Please note that this README is a broad overview of the application. Please refer to the individual python scripts for
more detailed information on each component of the application.

## Contributing

If you want to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## License

Distributed under the GPL 3 license : https://opensource.org/license/gpl-3-0/