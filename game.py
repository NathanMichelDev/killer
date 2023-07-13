from pydantic import BaseModel
from enum import Enum
from typing import List

from player import Player

import streamlit as st
from firestore import fb_client


def soft_load_game(game):
    game_dict = game.to_dict()
    return Game(
        state=game_dict["state"],
        name=game_dict["name"],
        description=game_dict["description"],
        player_names=game_dict["player_names"],
        pending_player_names=game_dict["pending_player_names"],
        admin=game_dict["admin"],
    )


class GameState(str, Enum):
    pending = "pending"
    active = "active"
    complete = "complete"


translated_state = {
    "pending": "En attente",
    "active": "En cours",
    "complete": "Terminée",
}


class Game(BaseModel):
    # The game id is its name
    name: str

    state: GameState
    description: str
    player_names: List[str]
    pending_player_names: List[str] = []
    admin: str

    def greetings(self):
        return f"Welcome to {self.name}! Current players are " + ", ".join(
            self.player_names
        )

    def st_describe(self):
        st.title(f"{self.name}")
        st.write(f"Description: {self.description}")
        st.write(f"Joueurs acceptés: " + ", ".join(self.player_names))
        st.write(
            f"Joueurs en attente d'acceptation: " + ", ".join(self.pending_player_names)
        )
        st.write(f"Administrateur de la partie: {self.admin}")
        st.write(f"Statut de la partie: {translated_state[self.state]}")

    def st_ask_to_join(self, player: Player):
        if player.name not in self.pending_player_names:
            if st.button(
                "Demander à rejoindre la partie", key="ask_to_join" + self.name
            ):
                self.add_pending_player(player)
                st.experimental_rerun()
        else:
            st.warning("Tu as déjà demandé à rejoindre cette partie.")

    def ask_to_leave(self):
        st.write("Are you sure you want to leave the game?")
        if st.button("Yes"):
            st.experimental_rerun()

    def add_pending_player(self, player: Player):
        remote_game_pending_player_names = (
            fb_client.collection("game")
            .document(self.name)
            .get()
            .to_dict()["pending_player_names"]
        )
        if player.name not in remote_game_pending_player_names:
            remote_game_pending_player_names.append(player.name)
            fb_client.collection("game").document(self.name).update(
                {"pending_player_names": remote_game_pending_player_names}
            )
        else:
            st.warning("You have already asked to join this game.")

    def remove_pending_player(self, player_name):
        remote_game_pending_player_names = (
            fb_client.collection("game")
            .document(self.name)
            .get()
            .to_dict()["pending_player_names"]
        )
        if player_name in remote_game_pending_player_names:
            remote_game_pending_player_names.remove(player_name)
            fb_client.collection("game").document(self.name).update(
                {"pending_player_names": remote_game_pending_player_names}
            )
            self.pending_player_names = remote_game_pending_player_names
        else:
            st.warning("Player not found in pending players.")

    def add_player(self, player_name):
        remote_game_player_names = (
            fb_client.collection("game")
            .document(self.name)
            .get()
            .to_dict()["player_names"]
        )
        if player_name not in remote_game_player_names:
            remote_game_player_names.append(player_name)
            fb_client.collection("game").document(self.name).update(
                {"player_names": remote_game_player_names}
            )
            self.player_names = remote_game_player_names
        else:
            st.warning("Player already in the game")

    def ask_to_add_pending_players(self):
        if not self.pending_player_names:
            st.success("Il n'y a pas de joueurs en attente d'acceptation.")
            return
        st.title("Pending players")
        st.header(f"There are {len(self.pending_player_names)} pending players")
        st.write("The following players have asked to join the game:")
        for player in self.pending_player_names:
            cols = st.columns(3)
            with cols[0]:
                st.write(player)
            with cols[1]:
                if st.button(
                    f"Add {player} to the game", key="add_pending_player" + player
                ):
                    self.add_player(player)
                    self.remove_pending_player(player)
                    st.experimental_rerun()
            with cols[2]:
                if st.button(
                    f"Refuse {player} to the game",
                    key="remove_pending_player" + player,
                ):
                    self.remove_pending_player(player)
                    st.experimental_rerun()

    def get_kills(self):
        return fb_client.collection("kill").where("game_name", "==", self.name).get()


def check_game_name_available(game_name: str) -> bool:
    if fb_client.collection("game").document(game_name).get().exists:
        return False
    else:
        return True


def create_game(game_name: str, game_description: str, player: Player) -> Game:
    if not check_game_name_available(game_name):
        raise Exception("Game name already taken")
    else:
        game = Game(
            name=game_name,
            state=GameState.pending,
            description=game_description,
            player_names=[player.name],
            admin=player.name,
            pending_player_names=[],
        )
        fb_client.collection("game").document(game.name).set(game.__dict__)
        return game
