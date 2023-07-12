import streamlit as st
from game import create_game
from player import create_player, load_player
from game import soft_load_game
from kill import create_kill, get_player_kills
import time

if "player" not in st.session_state:
    player_choice = st.radio(
        "What do you want to do?",
        ("Create a player", "Load a player"),
        key="player_choice",
        horizontal=True,
    )
    if player_choice == "Create a player":
        columns = st.columns(3)
        with columns[0]:
            player_name = st.text_input("Enter your name")
        with columns[1]:
            player_email = st.text_input("Enter your email")
        with columns[2]:
            player_password = st.text_input("Enter your password", type="password")
        if st.button("Create player"):
            if (player_name) and (player_email) and (player_password):
                try:
                    player = create_player(
                        player_name=player_name,
                        player_email=player_email,
                        player_password=player_password,
                    )
                    st.session_state.player = player
                    st.success("Player created")
                    st.session_state.player.greetings()
                    time.sleep(2)
                    st.experimental_rerun()
                except Exception as e:
                    if "Email already taken" in str(e):
                        st.error("You have already registered with this email")
                    elif "Name already taken" in str(e):
                        st.error("Name already taken")
                    else:
                        st.error(f"UNKNOWN ERROR: {e}")
            else:
                st.error("Please enter a player name and an email")
    elif player_choice == "Load a player":
        columns = st.columns(2)
        with columns[0]:
            player_email = st.text_input("Enter your email")
        with columns[1]:
            player_password = st.text_input("Enter your password", type="password")
        if st.button("Load my player"):
            if (player_email) and (player_password):
                try:
                    player = load_player(
                        player_email=player_email, player_password=player_password
                    )
                    st.session_state.player = player
                    st.success("Player loaded")
                    st.session_state.player.greetings()
                    time.sleep(2)
                    st.experimental_rerun()
                except Exception as e:
                    if "Incorrect password" in str(e):
                        st.error("Incorrect password")
                    else:
                        st.error(f"UNKNOWN ERROR: {e}")
            else:
                st.error("Please enter an email and a password")
    st.stop()

player = st.session_state.player

if "game" not in st.session_state:
    player.greetings()
    st.header("What do you want to do?")
    game_choice = st.radio(
        "",
        ("Load an existing game", "Join a game", "Create a game"),
        key="game_choice",
        horizontal=True,
        label_visibility="collapsed",
    )
    if game_choice == "Load an existing game":
        games = player.find_joined_games()
        if games:
            st.write(f"You are currently registered in {len(games)} game(s).")
            for game in games:
                # st.write(game.to_dict())
                g = soft_load_game(game)
                g.st_describe()
                g.st_ask_to_load()
        else:
            st.warning("You are not registered in any games.")
    if game_choice == "Join a game":
        game_name = st.text_input("Filter by game name")
        games = player.find_joinable_games(filter_name=game_name)
        st.write(f"There are {len(games)} game(s) that you have not yet joined.")
        for game in games:
            # st.write(game.to_dict())
            g = soft_load_game(game)
            g.st_describe()
            g.st_ask_to_join(player)
    elif game_choice == "Create a game":
        st.title("Create a game")
        cols = st.columns(3)
        with cols[0]:
            game_name = st.text_input(
                "Enter the game name",
                key="game_name",
                label_visibility="visible",
            )
        with cols[1]:
            game_description = st.text_input(
                "Enter the game description",
                key="game_description",
                label_visibility="visible",
            )
        if st.button("Create game"):
            if game_name and game_description:
                try:
                    game = create_game(game_name, game_description, player)
                    st.success("Game created")
                    st.session_state.game = game
                    time.sleep(2)
                    st.experimental_rerun()
                except Exception as e:
                    if "Game name already taken" in str(e):
                        st.error("Game name already taken")
                    else:
                        st.error("UNKNOWN ERROR:")
                        st.write(e)
            else:
                st.error("Please enter a game name and description")
    st.stop()

# if st.button("Unload game"):
#     st.session_state.pop("game")
#     st.experimental_rerun()

game = st.session_state.game
game.st_describe()

if game.state == "pending":
    if player.name == game.admin:
        game.ask_to_add_pending_players()
    st.title("Parlons peu, parlons kill!")
    st.write(
        f"En attendant que {game.admin} lance la partie, les joueurs doivent proposer des kills !"
    )
    nb_game_kills = len(game.get_kills())
    if nb_game_kills == 0:
        st.error(f"Il n'y a pas encore de kills proposés")
    elif nb_game_kills < 5:
        st.warning(f"Il y a actuellement {nb_game_kills} kills proposés")
    elif nb_game_kills < 10:
        st.info(f"Il y a actuellement {nb_game_kills} kills proposés")
    else:
        st.success(f"Il y a actuellement {nb_game_kills} kills proposés")
    st.header("Tes kills proposés")
    proposed_kills = get_player_kills(player.name)
    if proposed_kills:
        st.header("Kills que vous avez proposés")
        for proposed_kill in proposed_kills:
            proposed_kill.st_describe()
    else:
        st.error("Vous n'avez pas encore proposé de kill")
    st.header("Proposer un kill")
    cols = st.columns(2)
    with cols[0]:
        kill_content = st.text_input(
            "Enter the kill content", label_visibility="collapsed"
        )
    with cols[1]:
        if st.button("Proposer le kill"):
            if kill_content:
                try:
                    create_kill(
                        content=kill_content,
                        player_name=player.name,
                        game_name=game.name,
                    )
                except Exception as e:
                    if "Kill already exists in this game" in str(e):
                        st.error("Kill already exists in this game")
                    else:
                        st.error(f"UNKNOWN ERROR: {e}")
            else:
                st.error("Please enter a kill content")
