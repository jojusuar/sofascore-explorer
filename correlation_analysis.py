import matplotlib as mpl
import sofascore
import pandas as pd
import matplotlib.pyplot as plt
import re

sport = 'football'


def camel_to_text(camel_str):
    result = re.sub(r'([A-Z])', r' \1', camel_str)
    return result.strip().capitalize()


def get_corr_to_points(df: pd.DataFrame):
    cols = [c for c in df.columns if c not in ['wins', 'losses', 'draws', 'points', 'awardedMatches', 'matches', 'avgRating', 'id']]
    corr = df[cols].corrwith(df['points'], method='kendall')
    corr_df = corr.to_frame(name='corr').sort_values(by='corr', ascending=False)

    return corr_df


queries = [('france', 'ligue 1'), ('england', 'premier league'), ('spain', 'laliga'), ('italy', 'serie a'), ('germany', 'bundesliga')]

dfs = [get_corr_to_points(sofascore.stats_dataframe_by_competition(sport=sport,
                                                                   country_name=country,
                                                                   competition_name=competition)) for country, competition in queries]

stacked = pd.concat(dfs, keys=range(len(dfs)))

var_df = stacked.groupby(level=1).var()
mean_df = stacked.groupby(level=1).mean()

summary = pd.concat([mean_df, var_df], axis=1, keys=['mean', 'var'])
summary.columns = ['mean', 'var']
summary = summary.sort_values(by='mean', ascending=False)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

print(summary)


# y = corr_df.index
# x = corr_df['points']

# y = corr_df.index
# x = corr_df['points'].values

# fig, ax = plt.subplots(figsize=(16, 20))

# norm = mpl.colors.Normalize(vmin=-1, vmax=1)
# cmap = plt.cm.coolwarm_r

# for i, val in enumerate(x):
#     color = cmap(norm(val))
#     ax.plot([0, val], [i, i], color=color)
#     ax.plot(val, i, 'o', color=color)

# ax.axvline(0, color='black')
# ax.set_xlim(-1, 1)

# y_labels = [camel_to_text(label.replace('Against', 'ByOpposition')) for label in y]
# ax.set_yticks(range(len(y)))
# ax.set_yticklabels(y_labels)

# ax.set_xlabel("Kendall correlation with standings as of April 21th, 2026")
# ax.set_title(f'Correlation between team stats and {competition_name.title()} standings', fontsize=30)
# ax.grid(axis='x', linestyle='--', alpha=0.5)
# plt.tight_layout()

# plt.savefig(f'{competition_name}.png')
# plt.show()
