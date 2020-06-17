import pandas as pd
import glob
import numpy as np
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
from sklearn.model_selection import train_test_split
from sklearn.datasets import fetch_20newsgroups


def load_youtube_dataset(load_train_labels: bool = False, split_dev: bool = True, delimiter: str=None):
    filenames = sorted(glob.glob(dir_path + "/Youtube*.csv"))

    dfs = []
    for i, filename in enumerate(filenames, start=1):
        df = pd.read_csv(filename)
        # Lowercase column names
        df.columns = map(str.lower, df.columns)
        # Remove comment_id field
        df = df.drop("comment_id", axis=1)
        # Add field indicating source video
        df["video"] = [i] * len(df)
        # Rename fields
        df = df.rename(columns={"class": "label", "content": "text"})
        df = df[["label", "text"]]
        # Remove delimiter chars
        if delimiter is not None:
            df['text'].replace(regex=True, inplace=True, to_replace=delimiter, value=r'')
        df = df.reset_index(drop=True)
        dfs.append(df)
    
    # concatenate DFs, shuffle order
    df_full = pd.concat(dfs).sample(frac=1, random_state=123)
    train_size, dev_size, valid_size, test_size = 800, 200, 200, 400
    assert(test_size+valid_size+dev_size+train_size <= len(df_full))
    if not split_dev:
        dev_size = 0
        
    df_test = df_full[:test_size]
    df_valid = df_full[test_size:test_size+valid_size]
    df_dev = df_full[test_size+valid_size:test_size+valid_size+dev_size]
    df_train = df_full[test_size+valid_size+dev_size:test_size+valid_size+dev_size+train_size]
    df_test_test = df_full[test_size+valid_size+dev_size+train_size:]

    print("Held out: {}".format(len(df_test_test)))
    if not load_train_labels:
        df_train = df_train.drop("label", axis=1)

    assert(len(df_train) > 0)
    if split_dev:
        return df_train, df_dev, df_valid, df_test, df_test_test
    else:
        return df_train, df_valid, df_test


def load_amazon_dataset(load_train_labels: bool = False, split_dev: bool = True, delimiter: str=None):
    filenames = sorted(glob.glob(dir_path + "/Amazon*Dev.csv"))

    dfs = []
    for i, filename in enumerate(filenames, start=1):
        df = pd.read_csv(filename, header=None)
        # Lowercase column names
        df.columns = ["key", "text", "label"]
        # Remove delimiter chars
        if delimiter is not None:
            df['text'].replace(regex=True, inplace=True, to_replace=delimiter, value=r'')
        df = df.reset_index(drop=True)
        dfs.append(df)
    # concatenate DFs, shuffle order
    df_full = pd.concat(dfs).sample(frac=1, random_state=123)
    train_size, dev_size, valid_size, test_size = 800, 200, 200, 400
    assert(test_size+valid_size+dev_size+train_size <= len(df_full))
    
    if not split_dev:
        dev_size = 0

    df_test = df_full[:test_size]
    df_valid = df_full[test_size:test_size+valid_size]
    df_dev = df_full[test_size+valid_size:test_size+valid_size+dev_size]
    df_train = df_full[test_size+valid_size+dev_size:test_size+valid_size+dev_size+train_size]

    df_test_test = df_full[test_size+valid_size+dev_size+train_size:test_size+valid_size+dev_size+2*train_size]

    if not load_train_labels:
        df_train = df_train.drop("label", axis=1)
    
    assert(len(df_train) > 0)

    if split_dev:
        return df_train, df_dev, df_valid, df_test, df_test_test
    else:
        return df_train, df_valid, df_test

def load_news_dataset(load_train_labels: bool = False, split_dev: bool = True):
    newsgroups_train = fetch_20newsgroups(subset='train', categories=['talk.politics.guns', 'sci.electronics'], remove=('headers', 'footers', 'quotes'))
    whole_df = pd.DataFrame.from_dict({"text": newsgroups_train["data"], "label": newsgroups_train["target"]})
    df = whole_df.sample(1100, random_state=123).reset_index(drop=True)
    df = df[df["text"].apply(len) > 0]

    test_size = 100
    valid_size = 100
    if split_dev:
        dev_size = 400
    else:
        dev_size = 0
    train_size = 500

    df_test = df[:test_size]
    df_valid = df[test_size:test_size+valid_size]
    df_dev = df[test_size+valid_size:test_size+valid_size+dev_size]
    df_train = df[test_size+valid_size+dev_size:test_size+valid_size+dev_size+train_size]

    df_test_test = whole_df[~whole_df.index.isin(df.index)]

    if not load_train_labels:
        df_train = df_train.drop("label", axis=1)

    if split_dev:
        return df_train, df_dev, df_valid, df_test, df_test_test
    else:
        return df_train, df_valid, df_test


def load_film_dataset(load_train_labels: bool = False, split_dev: bool = True, delimiter: str=None):
    filename = dir_path + "/wiki_movie_plots.csv"
    df = pd.read_csv(filename)
    df = df[["text", "label", "Genre", "Title"]]
    df = df[df["text"].apply(len) <= 500]

    # Remove delimiter chars
    if delimiter is not None:
        df['text'].replace(regex=True, inplace=True, to_replace=delimiter, value=r'')
    # Shuffle order
    df = df.sample(2000, random_state=123).reset_index(drop=True)

    test_size = 0
    valid_size = 0
    if split_dev:
        dev_size = 500
    else:
        dev_size = 0
    train_size = 1500

    df_test = df[:test_size]
    df_valid = df[test_size:test_size+valid_size]
    df_dev = df[test_size+valid_size:test_size+valid_size+dev_size]
    df_train = df[test_size+valid_size+dev_size:test_size+valid_size+dev_size+train_size]

    df_test_test = df[test_size+valid_size+dev_size+train_size:2*test_size+valid_size+dev_size+train_size]
    if not load_train_labels:
        df_train = df_train.drop("label", axis=1)

    if split_dev:
        return df_train, df_dev, df_valid, df_test, df_test_test
    else:
        return df_train, df_valid, df_test

if __name__=="__main__":
    df_train, df_dev, df_valid, df_test = load_amazon_dataset()