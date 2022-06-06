# ICRC-Twitter-hate-speech (semester project)

Ayman Mezghani, EPFL. [email](mailto:ayman.mezghani@epfl.ch)

Subervised by:
 - Karl Aberer, LSIR, EPFL. [email](mailto:karl.aberer@epfl.ch)
 - Rebekah Overdorf, LSIR, EPFL. [email](mailto:rebekah.overdorf@epfl.ch)
 - Rémi Philippe Lebret, LSIR, EPFL. [email](mailto:remi.lebret@epfl.ch)

## Interavtive Plots
Follow this [link](https://ayman-mezghani.github.io/ICRC-Twitter-hate-speech/interactive/) to access the plots.

## Setup
The file `environment.yml` contains the needed dependencies to run the code.<br>
An environment can be installed as follows:
```
conda env create -f environment.yml
```

## Files
 - `00_clean_keywords.ipynb`:
 - `01_get_tweets.ipynb`:
 - `02_clean_tweets.ipynb`:
 - `03_stats.ipynb`:
 - `04a_news_get_tweets.ipynb`:
 - `04b_news_keywords.ipynb`:
 - `04c_news_filtering.ipynb`:
 - `05a_hate_speech_dehatebert-mono-english.ipynb`:
 - `05a_hate_speech_dehatebert-mono-english.py`:
 - `05b_hate_speech_twitter-roberta-base-hate.ipynb`:
 - `05b_hate_speech_twitter-roberta-base-hate.py`:
 - `05c_hate_speech_result_analysis.ipynb`:
 - `scraper.py`:
 - `twitter_id_mapper.py`:

## Data (EPFL only)
The data is available using this [link](https://drive.google.com/drive/folders/1pP-ypxPv85wf9OOD8ajqkBntjo3PYylF?usp=sharing)<br>
The data folder is to be placed at the root of the repository and is structured as follows:
```
data
├── bad_words
├── fasttext_data
├── hate_speech
├── news
├── tweets
├── keywords_clean.csv
└── keywords.txt
```

## Data Collection
In order to use the data collection module, a `token.json` file needs to be created and placed at root.<br>
The content of the file is to be structured as follows:
```
{
  "bearer_token": <bearer_token>,
  "api_key": <api_key>,
  "api_secret": <api_secret>
}
```
