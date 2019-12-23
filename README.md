# TweakersBot
TweakersBot is a simple web scraper for [_Tweakers.net_](https://tweakers.net/)'s marketplace.

## Features
- Highly-configurable (see `config.json`)
- Sends e-mail if a (configurable) price drop (relative/absolute) has occurred
- Ignores listings that contain specific keywords set in the `keywords.txt`-file

## Installation
Simply use `git clone https://github.com/yzwetsloot/TweakersBot.git` to clone this repository to your local machine.

### Setup
External dependencies:
- Selenium
- Chromedriver
- Yaml

Use `pip install` to install _selenium_ and _pyyaml_. 

Download Chromedriver [here](https://chromedriver.chromium.org/) and set in path.

## Running
Use `python main.py` inside the `src` folder to run the program.

## Note
I undertook this learning project to get a better understanding of Selenium and the Python programming language.
