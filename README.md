# NuclideSearch
This Django application is an attempt at creating a "modern" version of [Lund/LBNL Nuclear Data Search](http://nucleardata.nuclear.lu.se/toi/). It uses the same original database as that site but presents it in a way that is easier to use and easier on the eyes. This project is by no means finished though it is quite usefull in its current state.

## Requirements
The application is basad on [Django](http://djangoproject.com/) and this version of the project has been tested with Django version 1.10.3 running under Python 3.5. It is very likely that other older and newer versions of Django will also work.

[Numpy](http://www.numpy.org) is also used for backend sorting of tables. All other dependencies should be included in the standard Python installation.

The application uses [Bootstrap](http://getbootstrap.com) for html layout and style, [bootstrap-sortable](https://github.com/drvic10k/bootstrap-sortable) for table sorting in the browser and [typeahead.js](http://twitter.github.io/typeahead.js/) for auto completion. Those libraries as well as their respective dependencies are included in the *static_content* directory.

The database required to run the application is (for various reasons) not included in this repository. If you have access to the original Microsoft Access database, its tables can be imported into the Django database using the `legacy_importer.py`-script. Note that this requires the `mdb-export` command line tool which is part of [mdbtools](https://github.com/brianb/mdbtools).

## Importing ENSDF data
To import ENSDF data into the database used by the web application, the following command has to be executed:

    python manage.py ensdf_import PATH_TO_DIRECTORY

## Running the application
For running the application under a proper webserver, take a look at the official [Django documentation](https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/modwsgi/). To test the application run:

    python manage.py runserver

## Known bugs
Many. Some of them are listed in the `ToDo.txt` file.

## License
All the files created through this project uses the GNU GPLv3 license. More information about GNU GPLv3 can be found in the `LICENSE.txt` file.

The repository also include source code from other projectes which uses their respective license.


