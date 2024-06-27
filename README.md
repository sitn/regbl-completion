# RegBL Completion
Automated building construction year detection using historical swiss maps

This project is a python translation of https://github.com/swiss-territorial-data-lab/regbl-poc by the [Swiss Territorial Data Lab](https://www.stdl.ch/).
We changed some functionalities, especially to make the code faster and more modular, and detect smaller buildings.

# Requirements / Installation
1. Install the latests version of Python
2. Install de dependencies listed in `requirements.txt`, you can use the command `pip install -r requirements.txt`

# Data requirements

## Map
- The map should be divided into tiles. Each tile must be in a .tif format and come with its attached .twf having the same same.
- The map tiles must have their name ending with the tile ID, the year and a final number separated by underscores, in following the format :`tile_name_ID_year_number.tif`. For example : `SMR25_LV95_KREL_1123_2020_1.tif` for a tile of id 1123 in year 2020.

## Input data

# Setup
1. Complete the configuration file `parameters.py` following your needs. Here are the main parameters and their meaning:
  - `INPUT_FOLDERS` : List of folders in which the map tiles are located.
  - `TILE_TO_PROCESS` : ID of the tile to process. The program will load all the tile from all the years with this ID.
  - `DATA_LOCATION` : Path to the tabular file that contains the building's identifiers (EGID) and their location. The file must have the following columns names :
    - EGID : EGID of the building 
    - GKODE : Easting coordinate of the building
    - GKODN : Northing coordinate of the building
    - GBAUJ : Building year, for reference. Can be empty
    - GAREA : Ground area of the building. Can be empty
- `GROUND_TRUTH` : Tabular file that contains the ground 

TODO
- Les lignes dans le fichier dsv doivent se finir par \t\n et pas seulement par \n
