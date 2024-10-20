import matplotlib.pyplot as plt
import seaborn as sns

def plot_top_tracks(df):
    top_tracks = df.sort_values(by='streams', ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x='streams', y='title', data=top_tracks)
    plt.title('Top 10 najczęściej odtwarzanych utworów')
    plt.show()