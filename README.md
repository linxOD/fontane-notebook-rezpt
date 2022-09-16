# Python aggregated XML download and data processing for eXist-db RESTful API

## How To CLI

* Create a Python Virtual Environment: `python venv env`
* Activate the PVE: `source env/bin/activate`
* Install dependencies: `pip install -r requirements.txt`
* Config: Adapt default parameters in `config.py` to your needs
* Download and create zip file: `python run.py`
* Process files: `python run_process.py`
* Setup for Web App: `./setup.sh`

## Output

The data output is saved in [/out](https://github.com/linxOD/fontane-notebook-rezpt/blob/main/out/) directory. It contains an archive, all xml files and processed csv tables as well as a static webapp. 

# LICENSE

[MIT](https://github.com/linxOD/fontane-notebook-rezpt/blob/main/LICENSE)
