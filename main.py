import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =======================
# Load Data
# =======================
@st.cache_data
def load_data():
    matches = pd.read_csv("matches_2.csv")
    deliveries = pd.read_csv("deliveries_2.csv")
    batsman_col = "batsman" if "batsman" in deliveries.columns else "batter"
    return matches, deliveries, batsman_col

matches, deliveries, batsman_col = load_data()

# =======================
# Sidebar - Category
# =======================
st.title("🏏 IPL Data Analysis Dashboard")
category = st.sidebar.radio("Select Category", ["Batting Analysis", "Bowling Analysis", "Team & Match Analysis"])
st.sidebar.subheader("Player Analysis")
player_option = st.sidebar.selectbox("Select Player Analysis", ["None", "Career Comparison", "Player Performance"])

# =======================
# Helper function for table + graph
# =======================
def display_table_graph(df, value_col=None, label_col=None):
    st.dataframe(df.reset_index().rename(columns={label_col: label_col.capitalize(), value_col: "Value"}))
    if st.checkbox("Show Bar Chart for this analysis"):
        if value_col and label_col:
            st.bar_chart(df)
        else:
            st.bar_chart(df)

# =======================
# Batting Analysis
# =======================
if category == "Batting Analysis":
    option = st.selectbox("Select Analysis", [
        "Top Batsmen","Strike Rate Leaders","Batting Average Leaders","Most Sixes",
        "Most Fours","Orange Cap","Player Comparison"
    ])
    
    if option == "Top Batsmen":
        season = st.selectbox("Select Season", sorted(matches['season'].unique()))
        season_matches = matches[matches['season']==season]
        season_deliveries = deliveries[deliveries['match_id'].isin(season_matches['id'])]
        top_batsmen = season_deliveries.groupby(batsman_col)['batsman_runs'].sum().sort_values(ascending=False).head(10)
        display_table_graph(top_batsmen, "batsman_runs", batsman_col)
        if st.checkbox("Show Pie Chart of Top 5 Batsmen"):
            fig, ax = plt.subplots()
            ax.pie(top_batsmen.head(5), labels=top_batsmen.head(5).index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
    
    elif option == "Strike Rate Leaders":
        balls_faced = deliveries.groupby(batsman_col)['ball'].count()
        runs_scored = deliveries.groupby(batsman_col)['batsman_runs'].sum()
        strike_rate = (runs_scored / balls_faced) * 100
        top_sr = strike_rate.sort_values(ascending=False).head(10)
        display_table_graph(top_sr, "strike_rate", batsman_col)
    
    elif option == "Batting Average Leaders":
        outs = deliveries.groupby(batsman_col)['player_dismissed'].count()
        runs_scored = deliveries.groupby(batsman_col)['batsman_runs'].sum()
        avg = runs_scored / outs.replace(0,1)
        top_avg = avg.sort_values(ascending=False).head(10)
        display_table_graph(top_avg, "average", batsman_col)
    
    elif option == "Most Sixes":
        sixes = deliveries[deliveries['batsman_runs']==6].groupby(batsman_col).size().sort_values(ascending=False).head(10)
        display_table_graph(sixes, "sixes", batsman_col)
    
    elif option == "Most Fours":
        fours = deliveries[deliveries['batsman_runs']==4].groupby(batsman_col).size().sort_values(ascending=False).head(10)
        display_table_graph(fours, "fours", batsman_col)
    
    elif option == "Orange Cap":
        season = st.selectbox("Select Season for Orange Cap", sorted(matches['season'].unique()))
        season_matches = matches[matches['season']==season]
        season_deliveries = deliveries[deliveries['match_id'].isin(season_matches['id'])]
        orange_cap = season_deliveries.groupby(batsman_col)['batsman_runs'].sum().sort_values(ascending=False).head(5)
        st.dataframe(orange_cap)
        if st.checkbox("Show Pie Chart of Orange Cap"):
            fig, ax = plt.subplots()
            ax.pie(orange_cap, labels=orange_cap.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
    
    elif option == "Player Comparison":
        deliveries_season = deliveries.merge(matches[['id','season']], left_on='match_id', right_on='id', how='left')
        player1 = st.selectbox("Select Player 1", deliveries[batsman_col].unique())
        player2 = st.selectbox("Select Player 2", deliveries[batsman_col].unique())
        runs1 = deliveries_season[deliveries_season[batsman_col]==player1].groupby('season')['batsman_runs'].sum()
        runs2 = deliveries_season[deliveries_season[batsman_col]==player2].groupby('season')['batsman_runs'].sum()
        comparison = pd.DataFrame({player1:runs1, player2:runs2}).fillna(0)
        st.dataframe(comparison)
        if st.checkbox("Show Comparison Line Chart"):
            st.line_chart(comparison)

# =======================
# Bowling Analysis
# =======================
elif category == "Bowling Analysis":
    option = st.selectbox("Select Analysis", ["Top Bowlers","Purple Cap","Economy Rate (Bowlers)","Best Bowling Figures"])
    
    if option == "Top Bowlers":
        top_bowlers = deliveries[deliveries['player_dismissed'].notnull()].groupby("bowler").size().sort_values(ascending=False).head(10)
        display_table_graph(top_bowlers, "wickets", "bowler")
    
    elif option == "Purple Cap":
        season = st.selectbox("Select Season for Purple Cap", sorted(matches['season'].unique()))
        season_matches = matches[matches['season']==season]
        season_deliveries = deliveries[deliveries['match_id'].isin(season_matches['id'])]
        purple_cap = season_deliveries[season_deliveries['player_dismissed'].notnull()].groupby("bowler").size().sort_values(ascending=False).head(5)
        st.dataframe(purple_cap)
    
    elif option == "Economy Rate (Bowlers)":
        runs_conceded = deliveries.groupby("bowler")['total_runs'].sum()
        balls = deliveries.groupby("bowler")['ball'].count()
        economy = runs_conceded / (balls/6)
        top_econ = economy.sort_values().head(10)
        display_table_graph(top_econ, "economy", "bowler")
    
    elif option == "Best Bowling Figures":
        wickets = deliveries[deliveries['player_dismissed'].notnull()].groupby("bowler").size()
        runs = deliveries.groupby("bowler")['total_runs'].sum()
        best_fig = (wickets*100 - runs).sort_values(ascending=False).head(10)
        display_table_graph(best_fig, "score", "bowler")

# =======================
# Team & Match Analysis
# =======================
elif category == "Team & Match Analysis":
    option = st.selectbox("Select Analysis", [
        "Team Win %","Man of the Match Leaders","Highest Team Scores",
        "Super Over Matches","Toss Impact","Venue Analysis","Season Match Counts"
    ])
    
    if option == "Team Win %":
        win_counts = matches['winner'].value_counts(normalize=True)*100
        display_table_graph(win_counts, "win_percent", "Team")
    
    elif option == "Man of the Match Leaders":
        mom = matches['player_of_match'].value_counts().head(10)
        display_table_graph(mom, "Awards", "Player")
    
    elif option == "Highest Team Scores":
        team_scores = deliveries.groupby(['match_id','batting_team'])['total_runs'].sum().reset_index()
        top_scores = team_scores.sort_values(by="total_runs", ascending=False).head(10)
        st.dataframe(top_scores)
    
    elif option == "Super Over Matches":
        if "super_over" in matches.columns:
            super_over = matches[matches['super_over']==1]
            st.dataframe(super_over[['season','team1','team2','winner']])
    
    elif option == "Toss Impact":
        if "toss_winner" in matches.columns:
            toss_win = matches[matches['toss_winner']==matches['winner']]
            st.metric("Toss Win → Match Win %", f"{len(toss_win)/len(matches)*100:.2f}%")
    
    elif option == "Venue Analysis":
        venue_table = matches['venue'].value_counts().head(10)
        st.dataframe(venue_table)
    
    elif option == "Season Match Counts":
        season_counts = matches['season'].value_counts().sort_index()
        display_table_graph(season_counts, "Matches", "Season")

# =======================
# Player Analysis Sidebar
# =======================
if player_option == "Career Comparison":
    selected_players = st.multiselect("Select Players", deliveries[batsman_col].unique())
    if selected_players:
        deliveries_season = deliveries.merge(matches[['id','season']], left_on='match_id', right_on='id', how='left')
        career_df = pd.DataFrame()
        for player in selected_players:
            runs_per_season = deliveries_season[deliveries_season[batsman_col]==player].groupby('season')['batsman_runs'].sum()
            career_df[player] = runs_per_season
        career_df = career_df.fillna(0)
        st.dataframe(career_df)
        st.line_chart(career_df)

elif player_option == "Player Performance":
    player = st.selectbox("Select Player", deliveries[batsman_col].unique())
    player_deliveries = deliveries[deliveries[batsman_col]==player]
    
    runs = player_deliveries['batsman_runs'].sum()
    balls = player_deliveries.shape[0]
    outs = player_deliveries['player_dismissed'].count()
    average = runs / outs if outs > 0 else runs
    strike_rate = (runs / balls) * 100 if balls > 0 else 0
    sixes = player_deliveries[player_deliveries['batsman_runs']==6].shape[0]
    fours = player_deliveries[player_deliveries['batsman_runs']==4].shape[0]
    
    performance_df = pd.DataFrame({
        "Metric": ["Runs","Balls","Average","Strike Rate","6s","4s"],
        "Value": [runs, balls, round(average,2), round(strike_rate,2), sixes, fours]
    })
    
    st.dataframe(performance_df)
    if st.checkbox("Show Graph for Performance"):
        fig, ax = plt.subplots()
        ax.bar(performance_df["Metric"], performance_df["Value"], color='skyblue')
        ax.set_title(f"{player} Performance Overview")
        st.pyplot(fig)
