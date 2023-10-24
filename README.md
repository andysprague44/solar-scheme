## Solar Scheme

An application to forecast energy consumption for a private home, to figure out if it's a worthwhile investment to install solar and/or battery technology.

## Getting started

Pre-requisite is to install Anaconda3 or miniconda (the latter is enough and saves 3 GB on your computer so preferred): 
- https://docs.conda.io/projects/miniconda/en/latest/

Then run the following:

```sh
conda env create -f environment.yml --force
conda activate solarscheme
python main.py
```

### How to use

This init code commit is specific to a house in Gloucestershire, UK. However, you can directly alter variables in `src/solar_scheme.py` to match your situation.

### Running tests

To run tests:
```sh
pytest .
```

## Contact

andy.sprague44@gmail.com
