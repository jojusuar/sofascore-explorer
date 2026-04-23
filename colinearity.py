import sofascore
import pandas as pd
import matplotlib.pyplot as plt

sport = 'football'

def get_colinearity_matrix(df: pd.DataFrame):
    cols = [c for c in df.columns if c not in ['wins', 'losses', 'draws', 'points', 'awardedMatches', 'matches', 'avgRating', 'id']]
    df = df[cols]

    corr = df.corr(method='pearson')
    return corr


queries = [('france', 'ligue 1'), ('england', 'premier league'), ('spain', 'laliga'), ('italy', 'serie a'), ('germany', 'bundesliga')]

dfs = [get_colinearity_matrix(sofascore.stats_dataframe_by_competition(sport=sport,
                                                                   country_name=country,
                                                                   competition_name=competition)) for country, competition in queries]

avg_corr = sum(dfs) / len(dfs)


fig, ax = plt.subplots(figsize=(12, 12))
cax = ax.imshow(avg_corr, interpolation='nearest', cmap='coolwarm_r')


ax.set_xticks(range(len(avg_corr.columns)))
ax.set_yticks(range(len(avg_corr.columns)))
ax.set_xticklabels(avg_corr.columns, rotation=90)
ax.set_yticklabels(avg_corr.columns)

fig.colorbar(cax)

plt.title("Average Correlation Matrix Across Leagues")
plt.tight_layout()
plt.show()