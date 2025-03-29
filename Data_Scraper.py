# ===========================================
# 📦 Import Required Libraries
# ===========================================
import pandas as pd
import time
import requests as rq
from bs4 import BeautifulSoup


def handle_bs4_request(url):
    headers = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"
    }
    html = rq.get(url, headers=headers).text

    soup = BeautifulSoup(html, "lxml")

    return soup


# ===========================================
# 📂 Load Game Metadata CSV
# ===========================================
file_path = "./regular_season_game_ids.csv"
game_data = pd.read_csv(file_path)

# ===========================================
# 📊 Filter November Games from Full Dataset
# ===========================================
game_data["Date"] = pd.to_datetime(game_data["Date"])
november_games = game_data[game_data["Date"].dt.month == 11]
november_games = november_games.reset_index(drop=True)

# ===========================================
# 🗃️ Initialize Empty Lists to Store Results
# ===========================================
game_list = []  # Successfully scraped Game IDs
game_results_box_score = []  # Box Score data
game_results_team_stats = []  # Team stats data
game_results_ind_stats = []  # Individual stats (used for venue info)
game_official = []  # Referee data
no_games = []  # Games that failed scraping

# ===========================================
# 🔁 Loop in Batches of 10 Until 100 Scraped
# ===========================================
batch_size = 10
max_games = 10

for i in range(0, len(november_games), batch_size):
    if len(game_list) >= max_games:
        break

    batch = november_games.iloc[i : i + batch_size]

    for game_id in batch["Game ID"]:
        if game_id in game_list:
            continue  # Skip if already scraped

        try:
            print(f"🔄 Scraping Game ID: {game_id}")

            

            

            # -------- Team Stats --------
            url_team = f"https://stats.ncaa.org/contests/{game_id}/team_stats"
            # get the html and parse it into scrapeable objects using bs4
            soup = handle_bs4_request(url_team)
            # find the id of the particular table that you want to fetch
            table = soup.find("table", {"id": "rankings_table"})
            tbl_html = f"<table>{table.decode_contents()}</table>"
            # read_html gives the data in list and we always want the first element from the list
            df_team_stats = pd.read_html(tbl_html)[0]

            ###
            # -------- Box Score --------
            box_table = soup.find("table", {"style": "border-collapse: collapse"})
            box_tbl_html = f"<table>{box_table.decode_contents()}</table>"
            df_box_score = pd.read_html(box_tbl_html)[0]
            breakpoint()
            time.sleep(1.5)

            # -------- Individual Stats (for venue, attendance) --------
            url_ind = f"https://stats.ncaa.org/contests/{game_id}/individual_stats"
            df_ind_stats = pd.read_html(url_ind)
            time.sleep(1.5)

            # -------- Officials --------
            url_official = f"https://stats.ncaa.org/contests/{game_id}/officials"
            df_official = pd.read_html(url_official)
            time.sleep(1.5)

            # ✅ Append all results
            game_results_box_score.append(df_box_score)
            game_results_team_stats.append(df_team_stats)
            game_results_ind_stats.append(df_ind_stats)
            game_official.append(df_official)
            game_list.append(game_id)

            # 📝 Optional: Print progress every 20 games
            if len(game_list) % 20 == 0:
                print(f"✅ Scraped {len(game_list)} games so far...")

        except ValueError:
            print(f"⚠️ Failed to scrape Game ID: {game_id}")
            no_games.append(game_id)
            continue

print(f"🎉 Scraping complete! Total successful games: {len(game_list)}")
