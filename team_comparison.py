import matplotlib as mpl
import sofascore
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

sport = 'football'
country = 'spain'
competition = 'laliga'

def camel_to_text(camel_str):
    result = re.sub(r'([A-Z])', r' \1', camel_str)
    return result.strip().capitalize()

def get_corr_matrix(df: pd.DataFrame):
    cols = [c for c in df.columns if c not in [
        'wins', 'losses', 'draws', 'points',
        'awardedMatches', 'matches', 'avgRating', 'id'
    ]]
    
    corr = df[cols].corr(method='pearson', numeric_only=True)
    
    # Clip weak correlations
    corr = corr.where(np.abs(corr) >= 0.5, 0)
    
    return corr

queries = ['Real Madrid', 'Barcelona', 'Atletico Madrid']

for query in queries:
    team_id = sofascore.search_team_by_keyword(query)[0]['entity']['id']
    
    df = sofascore.team_stats_dataframe_by_competition(
        sport, country, competition, team_id, 10
    )
    
    corr_matrix = get_corr_matrix(df)

    fig, ax = plt.subplots(figsize=(14, 12))
    
    im = ax.imshow(corr_matrix, cmap='coolwarm_r', vmin=-1, vmax=1)

    # Labels
    labels = [camel_to_text(c.replace('Against', 'ByOpposition')) for c in corr_matrix.columns]
    
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=90)
    ax.set_yticklabels(labels)

    ax.set_title(f'{query} stats correlation matrix (|corr| < 0.5 → 0)', fontsize=18)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Pearson correlation')

    plt.tight_layout()
    plt.savefig(f'{query}_corr_matrix.png')
    plt.show()