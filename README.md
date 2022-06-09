# ICRC Twitter Hate Speech Detection

Ayman Mezghani, EPFL. [email](mailto:ayman.mezghani@epfl.ch)

Subervised by:
 - Karl Aberer, LSIR, EPFL. [email](mailto:karl.aberer@epfl.ch)
 - Rebekah Overdorf, LSIR, EPFL. [email](mailto:rebekah.overdorf@epfl.ch)
 - Rémi Philippe Lebret, LSIR, EPFL. [email](mailto:remi.lebret@epfl.ch)

## Interactive Plots
Follow this [link](https://ayman-mezghani.github.io/ICRC-Twitter-hate-speech/interactive/) to access the plots.

## Environment Setup
The file `environment.yml` contains the needed dependencies to run the code.<br>
An environment can be installed as follows:
```
conda env create -f environment.yml
```
This will create an environment called `lsir-mezghani-hate_speech`.

## Files
 - `00_clean_keywords.ipynb`: Notebook containing keyword cleaning code
 - `01_get_tweets.ipynb`: Notebook for collecting tweets using the `scraper.py` module
 - `02_clean_tweets.ipynb`: Notebook to aggregate collected tweets and drop overlaps
 - `03_stats.ipynb`: Notebook containing statistics about the collected tweets
 - `04a_news_get_tweets.ipynb`: Notebook for collecting tweets from news outlets
 - `04b_news_keywords.ipynb`: Notebook to extract news keywords fron the news tweets
 - `04c_news_filtering.ipynb`: Noteook containing news filtering code
 - `05a_hate_speech_dehatebert-mono-english.ipynb`: Notebook containing hate speech detection code using model A
 - `05a_hate_speech_dehatebert-mono-english.py`: Module containing hate speech detection code using model A (similar code to the above notebook)
 - `05b_hate_speech_twitter-roberta-base-hate.ipynb`: Notebook containing hate speech detection code using model B
 - `05b_hate_speech_twitter-roberta-base-hate.py`: Module containing hate speech detection code using model B (similar code to the above notebook)
 - `05c_hate_speech_result_analysis.ipynb`: Notebook containing result exploration of hate speech detection
 - `scraper.py`: Module to collect tweets using the Twitter API and [`tweepy`](https://www.tweepy.org/)
 - `twitter_id_mapper.py`: Module to extract handler from Twitter user id and vice versa using [https://tweeterid.com/](https://tweeterid.com/)
 - `environment.yml`: Contains the dependencies to run the code

**Note**: The notebooks are made to be run in order in case no data is provided. The data folder structure will have to be created from scratch.

## Data Collection
In order to use the data collection module, a `token.json` file needs to be created and placed at root. The API credentials can be obtained from the [Twitter API website](https://developer.twitter.com/en/docs/twitter-api).<br>
The content of the file is to be structured as follows:
```
{
  "bearer_token": <bearer_token>,
  "api_key": <api_key>,
  "api_secret": <api_secret>
}
```

## Provided Data (EPFL only)
The data is available using this [link](https://drive.google.com/drive/folders/1pP-ypxPv85wf9OOD8ajqkBntjo3PYylF?usp=sharing).<br>
The data folder is to be placed at the root of the repository and is structured as follows:
```
data
├── bad_words/
├── fasttext_data/
├── hate_speech/
├── news/
├── tweets/
├── keywords_clean.csv
└── keywords.txt
```

## Project Report (EPFL only)
The project report can be accessed using the following [link](https://drive.google.com/file/d/15ZU7RQ-qzLJlp0KjTYTyK5Bk7bX9tlmA/view?usp=sharing).
