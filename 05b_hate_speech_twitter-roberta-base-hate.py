#!/usr/bin/env python
# coding: utf-8

# # Hate Speech Detection B

import requests
import pandas as pd
import numpy as np

from tqdm import tqdm

from pandarallel import pandarallel
pandarallel.initialize(nb_workers=4, progress_bar=False)

import torch

from scipy.special import softmax
from transformers import AutoTokenizer, AutoModelForSequenceClassification


# ## Load Model

tokenizer = AutoTokenizer.from_pretrained('cardiffnlp/twitter-roberta-base-hate')

model = AutoModelForSequenceClassification.from_pretrained('cardiffnlp/twitter-roberta-base-hate')


# ### Load Model Label Mapping

mapping_link = f'https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/hate/mapping.txt'

response = requests.get(mapping_link)

labels = {i: s.split('\t')[1] for i, s in enumerate(response.content.decode('utf-8').split('\n'))}


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

step = 1
res = []

for i in tqdm(list(range(0, len(df_tweets), step))[]):
    j = min(i+step, len(df_tweets))
    
    _texts = texts[i:j]
    
    ### Tokenizing

    encoded_input = tokenizer(_texts, return_tensors='pt', padding=True).to(device)
    # encoded_input = tokenizer(_texts, return_tensors='pt', padding=True)

    ### Hate Speech Classification
    try:
        output = model(**encoded_input)
        scores = output[0].detach().cpu().numpy()
        # scores = output[0].detach().numpy()
    except:
        output = None
        scores = np.array([[0, 0]])
    
    res.append(scores)
    
    del encoded_input
    del output
    torch.cuda.empty_cache()

res = np.concatenate(res, axis=0)

result_scores = pd.DataFrame(res, index=df_tweets.index).rename(columns=labels)
result_softmax = pd.DataFrame(softmax(res, axis=1), index=df_tweets.index).rename(columns=labels)

df_tweets = df_tweets.join(result_scores).join(result_softmax, rsuffix='_softmax')

df_tweets[['id', 'not-hate', 'hate', 'not-hate_softmax', 'hate_softmax']].to_parquet('data/hate_speech/hate_model_b.parquet')
