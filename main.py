import matplotlib as mpl
import sofascore
import pandas as pd
import matplotlib.pyplot as plt
import re

def camel_to_text(camel_str):
    result = re.sub(r'([A-Z])', r' \1', camel_str)
    return result.strip().capitalize()

sport = 'football'

def get_corr_to_points(country_name, competition_name):
    country_entry = sofascore.get_country_info_by_sport(country_name, sport)
    country_id = country_entry.get('id')

    comp_entry = sofascore.find_competition_info_by_country_id(competition_name, country_id)

    comp_id = comp_entry.get('id')
    seasons = sofascore.get_seasons_by_tournament_id(comp_id)
    latest_season_id = seasons[0].get('id')

    current_standings = sofascore.get_current_league_standings(comp_id, latest_season_id)

    df_cols = None
    rows = []
    index = []

    for entry in current_standings:
        team_info = entry.get('team')
        team_id = team_info.get('id')
        team_name = team_info.get('name')
        team_stats = sofascore.get_team_stats_by_competition(team_id, comp_id, latest_season_id)
        team_stats.pop('statisticsType')

        if df_cols is None:
            df_cols = ['points', 'wins', 'losses', 'draws'] + list(team_stats.keys())

        team_stats.update(entry)
        row = [team_stats[field] for field in df_cols]
        index.append(team_name)
        rows.append(row)


    df = pd.DataFrame(rows, columns=df_cols, index=index)

    cols = [c for c in df.columns if c not in ['wins', 'losses', 'draws', 'points', 'awardedMatches', 'matches', 'avgRating', 'id']]
    corr = df[cols].corrwith(df['points'], method='kendall')
    corr_df = corr.to_frame(name='points').sort_values(by='points', ascending=False)

    return corr_df

queries = [('france', 'ligue 1'), ('england', 'premier league'), ('spain', 'laliga'), ('italy', 'serie a'), ('germany', 'bundesliga')]

dfs = [get_corr_to_points(country, competition) for country, competition in queries]
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
