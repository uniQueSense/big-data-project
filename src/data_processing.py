import pandas as pd

def load_data(path):
    return pd.read_csv(path)

def load_samples(path, rows):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 500)
    return pd.read_csv(path, nrows=rows)

def clean_data(df):
    df_cleaned = df.dropna().drop_duplicates()
    return df_cleaned