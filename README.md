# NMAstudio web-application

## About this app

This is an interactive app to produce and perform network meta-analysis. 

The app is currently deployed here: www.nmastudioapp.com

## How to run this app locally

(The following instructions apply to Posix/bash. Windows users should check
[here](https://docs.python.org/3/library/venv.html).)

First, clone this repository and open a terminal inside the root folder.

Make sure you have installed (mini)conda on your machine.

Create and activate a new conda environment by running
the following:

Create nmastudio environment and install requirements:
```bash
conda env create -f requirements.yml
```

Activate environment
```bash
conda activate nmastudio
```
Run the app:

```bash
python app.py
```
Open a browser at http://127.0.0.1:8080


 ![demo.gif](assets/favicon.ico) 

