import sqlite3
import pandas as pd

# Database System file
db_file = 'NBA_STATS.db'
csv_player = 'Player_Totals.csv'
df_player = pd.read_csv(csv_player, encoding='gbk')
csv_team = 'Team_Totals.csv'
df_team = pd.read_csv(csv_team, encoding='gbk')
csv_user = 'Users_Totals.csv'
df_user = pd.read_csv(csv_user, encoding='gbk')


def initialize_data():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    # Create a table Players to store the data of players.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Players (
        season INTEGER,
        player_id INTEGER PRIMARY KEY,
        player TEXT,
        position TEXT,
        age INTEGER,
        team TEXT,
        total_points INTEGER,
        field_goals_percent REAL,
        three_points_percent REAL,
        two_points_percent REAL,
        free_throw_percent REAL,
        total_rebound INTEGER,
        assist INTEGER,
        steal INTEGER,
        block INTEGER,
        turnover INTEGER,
        personal_foul INTEGER,
        FOREIGN KEY (team) REFERENCES Teams (team)
    )
    ''')

    # Create a table Teams to store the data of teams.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Teams (
        season INTEGER,
        team TEXT PRIMARY KEY,
        playoffs INTEGER,
        total_points INTEGER,
        field_goals_percent REAL,
        three_points_percent REAL,
        two_points_percent REAL,
        free_throw_percent REAL,
        total_rebound INTEGER,
        assist INTEGER,
        steal INTEGER,
        block INTEGER,
        turnover INTEGER,
        personal_foul INTEGER
    )
    ''')

    # Create a table Users to store the data of users.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT CHECK(role IN ('player', 'scout', 'admin')),
        team TEXT
    )
    ''')
    conn.commit()
    conn.close()


# import the data into the db system.
def import_data():
    conn = sqlite3.connect(db_file)
    df_player.to_sql('Players', conn, if_exists='replace', index=False)
    df_team.to_sql('Teams', conn, if_exists='replace', index=False)
    df_user.to_sql('Users', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()


# initialize the database(running this can recover the db)
initialize_data()
import_data()


# register for the new users
def register_user(player_id, username, password, team):
    role = 'player'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username FROM Users WHERE username = ?
    ''', (username,))
    if cursor.fetchone():
        print(f"User name {username} has been used. Please use another user name.")
        conn.close()
        return
    cursor.execute('''
        SELECT team FROM Teams WHERE team = ?
    ''', (team,))
    if not cursor.fetchone():
        print(f"Team {team} does not exist in the database. Please enter a valid team.")
        conn.close()
        return
    try:
        cursor.execute('''
            INSERT INTO Users (user_id, username, password, role, team)
            VALUES (?, ?, ?, ?, ?)
        ''', (player_id, username, password, role, team))
        conn.commit()
        print(f"User {username} (Player ID: {player_id}) has been registered successfully.")
        conn.close()
        return True
    except sqlite3.IntegrityError:
        print(f"User name {username} has been used. Please use another user name.")
        conn.close()
        return False


# login for the users
def login_user(username, password):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT password, role FROM Users WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()
        if result is None:
            print("The user name does not exist")
            return None
        stored_password, role = result
        if password == str(stored_password):
            print(f"The user {username} logged in successfully, role: {role}")
            return role
        else:
            print("The password is wrong!")
            return None
    finally:
        conn.close()


def view_all_teams(admin_username):
    year = input("Please input the season(remain blank will return all years): ")
    team_name = input("Please input the Team Name(remain blank will return all teams): ")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    if year and team_name:
        cursor.execute('SELECT * FROM Teams WHERE season = ? AND team = ?', (year, team_name))
    elif year:
        cursor.execute('SELECT * FROM Teams WHERE season = ?', (year,))
    elif team_name:
        cursor.execute('SELECT * FROM Teams WHERE team = ?', (team_name,))
    else:
        cursor.execute('SELECT * FROM Teams')
    teams = cursor.fetchall()
    print(f"{admin_username} can check the information of all teams:")
    print('Title for output: ', '\n', list(df_team.columns))
    for team in teams:
        print(team)
    conn.close()


def view_all_players(admin_username):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    player_name = input("Please input the Player name(Blank will return all players): ")
    season = input("Please input the season(Blank will return all seasons): ")
    if player_name and season:
        cursor.execute('''
                SELECT * FROM Players WHERE player = ? AND season = ?
            ''', (player_name, int(season)))
    elif player_name:
        cursor.execute('''
                SELECT * FROM Players WHERE player = ?
            ''', (player_name,))
    elif season:
        cursor.execute('''
                SELECT * FROM Players WHERE season = ?
            ''', (int(season),))
    else:
        cursor.execute('SELECT * FROM Players')
    players = cursor.fetchall()
    print(f"{admin_username} can check the information of all players: ")
    print('Title for output: ', '\n', list(df_player.columns))
    for player in players:
        print(player)
    conn.close()


def view_all_users(admin_username):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    username = input("Please enter a username to filter (leave blank for all usernames): ")
    role = input("Please enter a role to filter (leave blank for all roles): ")
    team = input("Please enter a team to filter (leave blank for all teams): ")
    query = "SELECT user_id, username, role, team FROM Users WHERE 1=1"
    params = []
    if username:
        query += " AND username = ?"
        params.append(username)
    if role:
        query += " AND role = ?"
        params.append(role)
    if team:
        query += " AND team = ?"
        params.append(team)
    cursor.execute(query, tuple(params))
    users = cursor.fetchall()
    print(f"{admin_username} can view the following user information:")
    print("user_id | username | role | team")
    for user in users:
        print(user)
    conn.close()


def delete_user(admin_username):
    target_username = input("Please input the username to delete: ")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Users WHERE username = ?', (target_username,))
    conn.commit()
    print(f"User {target_username} has been deleted by {admin_username}")
    conn.close()


def update_player_team():
    player = input("Please input the Player's name: ")
    new_team = input("Please input the new Team's name: ")
    current_year = 2023
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT season, player_id, player, position, age 
        FROM Players 
        WHERE player = ? AND season = ?
    ''', (player, current_year))
    player_info = cursor.fetchone()
    if not player_info:
        print(f"No record found for player {player} in {current_year}.")
        conn.close()
        return
    season, player_id, player, position, age = player_info
    cursor.execute('''
        INSERT INTO Players (season, player_id, player, position, age, team, total_points, field_goals_percent,
                             three_points_percent, two_points_percent, free_throw_percent, total_rebound, assist,
                             steal, block, turnover, personal_foul)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (season, player_id, player, position, age, new_team, 0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0, 0, 0))
    conn.commit()
    print(f"Player {player} has been added to team {new_team} for the {current_year} season.")
    cursor.execute('''
        SELECT * FROM Players WHERE player = ? AND season = ?
    ''', (player, current_year))
    all_records = cursor.fetchall()
    print(f"All records for player {player} in {current_year}:")
    for record in all_records:
        print(record)
    conn.close()


def update_team_playoffs():
    team = input("Please input the Team's name: ")
    season = int(input("Please input the season year: "))
    playoffs = int(input("Enter playoffs status(1 for yes, 0 for no): "))
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('UPDATE Teams SET playoffs = ? WHERE team = ? AND season = ?', (playoffs, team, season))
    conn.commit()
    print(f"Updated record for team {team} in season {season}:")
    cursor.execute('''
            SELECT * FROM Teams WHERE team = ? AND season = ?
        ''', (team, season))
    updated_team_info = cursor.fetchone()
    print(updated_team_info)
    conn.close()


def delete_player():
    player = input("Please input the Player Name: ")
    season = int(input("Please input the season year: "))
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Players WHERE player = ? AND season = ?', (player, season))
    conn.commit()
    print(f"The player {player} from season {season} has been deleted.")
    conn.close()


def is_scout(username):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    # check whether the user is a scout.
    cursor.execute('''
        SELECT team, role FROM Users WHERE username = ?
    ''', (username,))
    result = cursor.fetchone()
    conn.close()
    if result is None:
        print("The user does not exist.")
        return None
    team, role = result
    if role != 'scout':
        print("Only scout can do this operation.")
        return None
    return team


def view_scout_team_players(username):
    team = is_scout(username)
    if team is None:
        return
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    player_name = input("Please input the Player name(Blank will return all players): ")
    season = input("Please input the season(Blank will return all seasons): ")
    if player_name and season:
        cursor.execute('''
                SELECT * FROM Players WHERE team = ? AND player = ? AND season = ?
            ''', (team, player_name, int(season)))
    elif player_name:
        cursor.execute('''
                SELECT * FROM Players WHERE team = ? AND player = ?
            ''', (team, player_name))
    elif season:
        cursor.execute('''
                SELECT * FROM Players WHERE team = ? AND season = ?
            ''', (team, int(season)))
    else:
        cursor.execute('''
                SELECT * FROM Players WHERE team = ?
            ''', (team,))
    players = cursor.fetchall()
    print(f"{username} can check the data of player from team {team}")
    print('Title for output: ', '\n', list(df_player.columns))
    for player in players:
        print(player)
    conn.close()


def view_young_players(username):
    if is_scout(username) is None:
        return
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    current_year = 2023
    position = input("Please enter a position to filter (leave blank for all positions): ")
    age_limit = input("Please enter an age limit (leave blank for age < 25): ")
    team = input("Please enter a team to filter (leave blank for all teams): ")
    age_limit = int(age_limit) if age_limit else 25
    query = '''
        SELECT * FROM Players WHERE season = ? AND age = ?
    '''
    params = [current_year, age_limit]
    if position:
        query += ' AND position = ?'
        params.append(position)
    if team:
        query += ' AND team = ?'
        params.append(team)
    cursor.execute(query, tuple(params))
    young_players = cursor.fetchall()
    print(f"{username} can check the players in all teams whose age < {age_limit}.")
    print("Title for output:\n", ["season", "player_id", "player", "position", "age", "team", "total_points",
                                  "field_goals_percent", "three_points_percent", "two_points_percent",
                                  "free_throw_percent", "total_rebound", "assist", "steal", "block",
                                  "turnover", "personal_foul"])
    print('Title for output: ', '\n', list(df_player.columns))
    for player in young_players:
        print(player)

    conn.close()


def view_team_info_by_year(username):
    year = input("Please input the year (leave blank to view all years): ")
    team = is_scout(username)
    if team is None:
        return
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    if year:
        cursor.execute('''
            SELECT * FROM Teams WHERE team = ? AND season = ?
        ''', (team, year))
    else:
        cursor.execute('''
            SELECT * FROM Teams WHERE team = ?
        ''', (team,))
    team_info = cursor.fetchall()
    print(f"{username} can check the data of the team {team}")
    print('Title for output: ', '\n', list(df_team.columns))
    for info in team_info:
        print(info)
    conn.close()


def is_player(username):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT team, role FROM Users WHERE username = ?
    ''', (username,))
    result = cursor.fetchone()
    conn.close()
    if result is None:
        print("The player does not exist.")
        return None
    team, role = result
    if role != 'player':
        print("Only player can do this information!")
        return None
    return team


def view_current_team_player(username):
    team = is_player(username)
    if team is None:
        return
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    current_year = 2023
    player_name = input("Please input the Player name(Blank will return all players): ")
    if player_name:
        cursor.execute('''
                SELECT * FROM Players WHERE team = ? AND player = ? AND season = ?
            ''', (team, player_name, current_year))
    else:
        cursor.execute('''
                SELECT * FROM Players WHERE team = ? AND season = ?
            ''', (team, current_year))
    players = cursor.fetchall()
    print(f"{username} can check the data of players from team {team} in season {current_year}")
    print('Title for output: ', '\n', list(df_player.columns))
    for player in players:
        print(player)
    conn.close()


def view_current_team_info(username):
    team = is_player(username)
    if team is None:
        return
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    current_year = 2023
    cursor.execute('''
        SELECT * FROM Teams WHERE team = ? AND season = ?
    ''', (team, current_year))
    team_info = cursor.fetchall()
    print(f"{username} can check the data of team{team} in season {current_year}.")
    print('Title for output: ', '\n', list(df_team.columns))
    for info in team_info:
        print(info)
    conn.close()


def register():
    print("\n--- Register for users ---")
    username = input("Please input the user name: ")
    user_id = input("Please input the user id: ")
    password = input("Please input the password: ")
    team = input("Please input the team: ")
    register_user(user_id, username, password, team)


def admin_menu(username):
    while True:
        print(f"\n Welcome {username}, Please choose your operations: ")
        print("1. View all information of all Teams.")
        print("2. View all information of all Players.")
        print("3. View all information of all Users.")
        print("4. Update state of playoffs.")
        print("5. Delete Players.")
        print("6. Delete Users.")
        print("7. Update team of player.")
        print("8. Log Out.")
        choice = input("Please make a decision: ")
        if choice == "1":
            view_all_teams(username)
        elif choice == "2":
            view_all_players(username)
        elif choice == "3":
            view_all_users(username)
        elif choice == "4":
            update_team_playoffs()
        elif choice == "5":
            delete_player()
        elif choice == "6":
            delete_user(username)
        elif choice == "7":
            update_player_team()
        elif choice == "8":
            print("Logged out.\n")
            break
        else:
            print("Invalid choice, please try again.")


def scout_menu(username):
    while True:
        print(f"\nWelcome Scout {username}, Please choose your operation:")
        print("1. View team players information")
        print("2. View all young players information (under 25 years old) in 2023")
        print("3. View team information")
        print("4. Logout")
        choice = input("Please input the option number: ")
        if choice == "1":
            view_scout_team_players(username)
        elif choice == "2":
            view_young_players(username)
        elif choice == "3":
            view_team_info_by_year(username)
        elif choice == "4":
            print("Logged out.\n")
            break
        else:
            print("Invalid choice, please try again.")


def player_menu(username):
    while True:
        print(f"\n Welcome Player {username}, Please choose your operation:")
        print("1. View team players information in 2023")
        print("2. View team information in 2023")
        print("3. Logout")
        choice = input("Please input the option number: ")
        if choice == "1":
            view_current_team_player(username)
        elif choice == "2":
            view_current_team_info(username)
        elif choice == "3":
            print("Logged out.\n")
            break
        else:
            print("Invalid choice, please try again.")


def main_menu():
    while True:
        print("Welcome to the NBA Database System")
        print("1. Login")
        print("2. Register")
        print("3. Exit System")
        choice = input("Please choose an operation: ")
        if choice == "1":
            login()
        elif choice == "2":
            register()
        elif choice == "3":
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")


def login():
    print("\n--- User Login ---")
    username = input("Please input your username: ")
    password = input("Please input your password: ")
    # Login and get role
    role = login_user(username, password)
    if role == "admin":
        admin_menu(username)
    elif role == "scout":
        scout_menu(username)
    elif role == "player":
        player_menu(username)
    else:
        print("Login failed or invalid role, please try again.")


# Start the system
if __name__ == "__main__":
    main_menu()
