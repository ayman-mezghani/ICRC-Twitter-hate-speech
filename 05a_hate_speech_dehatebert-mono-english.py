#!/usr/bin/env python
# coding: utf-8

# # Hate Speech Detection A

import pandas as pd
import numpy as np

from tqdm import tqdm

from pandarallel import pandarallel
pandarallel.initialize(nb_workers=4, progress_bar=False)

import torch

from scipy.special import softmax
from transformers import AutoTokenizer, AutoModelForSequenceClassification


# ## Load Model

# ### Load Tokenizer and Classifier

tokenizer = AutoTokenizer.from_pretrained("Hate-speech-CNERG/dehatebert-mono-english")

model = AutoModelForSequenceClassification.from_pretrained("Hate-speech-CNERG/dehatebert-mono-english")


# ### Load Model Label Mapping

# https://huggingface.co/Hate-speech-CNERG/dehatebert-mono-english/blob/main/config.json
id2label = {0: "NON_HATE", 1: "HATE"}


# ## Load Data

# ### Load Tweets

df_tweets = pd.read_parquet('data/tweets/en/english_tweets.parquet')


# ### Load News IDs

news_ids = pd.read_csv('data/news/news_indexes.csv', header=None).values.reshape(-1)


# ### Filter News

df_tweets['id'] = df_tweets['id'].astype(int)
df_tweets['is_news'] = df_tweets['id'].isin(news_ids)


# ## Hate Speech Detection

# ### Pre-Processing

def preprocess(text):
    new_text = []
    for t in text.split(' '):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return ' '.join(new_text)


df_tweets['pre_process_text'] = df_tweets.text.str.replace(r'\s+', ' ', regex=True).parallel_apply(preprocess)

texts = df_tweets.pre_process_text.values.tolist()


# ### Classification

device = "cuda:0" if torch.cuda.is_available() else "cpu"

model = model.to(device)

print('Allocated:', round(torch.cuda.memory_allocated(0)/1024**3,1), 'GB')
print('Cached:   ', round(torch.cuda.memory_reserved(0)/1024**3,1), 'GB')

step = 50
res = []

for i in tqdm(list(range(0, len(df_tweets), step))):
    j = min(i+step, len(df_tweets))
    print(i, j, len(df_tweets))
    
    _texts = texts[i:j]
    
    ### Tokenizing

    encoded_input = tokenizer(_texts, return_tensors='pt', padding=True).to(device)

    ### Hate Speech Classification

    output = model(**encoded_input)

    scores = softmax(output[0].detach().cpu().numpy(), axis=1)
    
    res.append(scores)
    
    del encoded_input
    del output
    torch.cuda.empty_cache()


result_scores = pd.DataFrame(np.concatenate(res, axis=0), index=sample.index).rename(columns=id2label)['HATE']

df_tweets['hate_speech_a'] = result_scores

df_tweets[['id', 'hate_speech_a']].to_parquet('data/hate_speech/hate_model_a.parquet')
