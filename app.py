import streamlit as st
from login import user_login, game_login
from kill import create_kill, get_player_kills

if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"

st.set_page_config(initial_sidebar_state=st.session_state.sidebar_state)

if "player" not in st.session_state:
    user_login()
    st.stop()
else:
    with st.sidebar:
        if st.button("Me déconnecter"):
            st.session_state.pop("player")
            st.session_state.pop("sidebar_state")
            if "game" in st.session_state:
                st.session_state.pop("game")
            st.experimental_rerun()

player = st.session_state.player

if "game" not in st.session_state:
    game_login(player)
    st.stop()
else:
    with st.sidebar:
        if st.button("Quitter la partie"):
            st.session_state.pop("game")
            st.experimental_rerun()


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
        st.error(f"Aucun kill n'a été proposé pour le moment.")
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
