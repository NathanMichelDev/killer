import streamlit as st

from player import create_player, load_player
from game import create_game, soft_load_game


def successful_login(player):
    st.session_state.player = player
    st.session_state.player.greetings()
    st.session_state.sidebar_state = "collapsed"
    st.experimental_rerun()


def user_login():
    st.sidebar.title("Compte joueur")
    player_choice = st.sidebar.radio(
        "What do you want to do?",
        ("Me connecter", "Créer un compte"),
        horizontal=True,
        label_visibility="collapsed",
    )
    player_email = st.sidebar.text_input("Email")
    player_password = st.sidebar.text_input("Mot de passe", type="password")

    if player_choice == "Créer un compte":
        player_name = st.sidebar.text_input("Nom de joueur")
        if st.sidebar.button("Créer un joueur"):
            if (player_name) and (player_email) and (player_password):
                try:
                    player = create_player(
                        player_name=player_name,
                        player_email=player_email,
                        player_password=player_password,
                    )
                    st.sidebar.success("Joueur créé !")
                    successful_login(player)
                except Exception as e:
                    if "Email already taken" in str(e):
                        st.sidebar.error("L'email est déjà utilisé")
                    elif "Name already taken" in str(e):
                        st.sidebar.error("Le nom de joueur est déjà utilisé")
                    else:
                        st.sidebar.error(f"Erreur inconnue, contactez le support: {e}")
            else:
                st.sidebar.error("Entrez un nom, un email et un mot de passe.")
    elif player_choice == "Me connecter":
        if st.sidebar.button("Connexion"):
            if (player_email) and (player_password):
                try:
                    player = load_player(
                        player_email=player_email, player_password=player_password
                    )
                    st.sidebar.success("Connexion réussie !")
                    successful_login(player)
                except Exception as e:
                    if "Incorrect password" in str(e):
                        st.sidebar.error("Mot de passe incorrect")
                    else:
                        st.sidebar.error(f"Erreur inconnue, contactez le support: {e}")
            else:
                st.sidebar.error("Entrez un email et un mot de passe.")


def game_login(player):
    player.greetings()
    game_choice = st.radio(
        "",
        (
            "Charger une partie en cours",
            "Rejoindre une nouvelle partie",
            "Créer une nouvelle partie",
        ),
        horizontal=True,
        label_visibility="collapsed",
    )
    if game_choice == "Charger une partie en cours":
        games = player.find_joined_games()
        if games:
            st.write(f"Tu as actuellement {len(games)} partie(s) en cours.")
            game_names = [game.id for game in games]
            columns = st.columns(2)
            with columns[0]:
                chosen_game_id = st.selectbox(
                    "", options=game_names, label_visibility="collapsed"
                )
            for game in games:
                if game.id == chosen_game_id:
                    g = soft_load_game(game)
            with columns[1]:
                if st.button("Charger la partie"):
                    st.session_state.game = g
                    st.experimental_rerun()
            if st.checkbox("Voir les détails"):
                g.st_describe()
        else:
            st.warning("Tu n'as aucune partie en cours.")
    if game_choice == "Rejoindre une nouvelle partie":
        game_name = st.text_input("Filtrer par nom de partie")
        games = player.find_joinable_games(filter_name=game_name)
        st.write(f"Il y a {len(games)} partie(s) que tu peux demander à rejoindre.")
        for game in games:
            # st.write(game.to_dict())
            g = soft_load_game(game)
            g.st_describe()
            g.st_ask_to_join(player)
    elif game_choice == "Créer une nouvelle partie":
        st.header("Créer une nouvelle partie")
        cols = st.columns(3)
        with cols[0]:
            game_name = st.text_input(
                "Nom de la partie",
                key="game_name",
                label_visibility="visible",
            )
        with cols[1]:
            game_description = st.text_input(
                "Description",
                key="game_description",
                label_visibility="visible",
            )
        if st.button("Créer la partie"):
            if game_name and game_description:
                try:
                    game = create_game(game_name, game_description, player)
                    st.success("Partie créée !")
                    st.session_state.game = game
                    st.experimental_rerun()
                except Exception as e:
                    if "Game name already taken" in str(e):
                        st.error("Le nom de partie est déjà pris.")
                    else:
                        st.error(f"Erreur inconnue, contactez le support: {e}")
            else:
                st.error("Entrez un nom et une description de partie.")
