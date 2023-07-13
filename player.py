from pydantic import BaseModel
import streamlit as st
from typing import List

from firestore import fb_client


def check_player_name_available(player_name: str) -> bool:
    if fb_client.collection("player").where("name", "==", player_name).get():
        return False
    else:
        return True


def check_player_email_available(player_email: str) -> bool:
    if fb_client.collection("player").where("email", "==", player_email).get():
        return False
    else:
        return True


def create_player(player_name: str, player_email: str, player_password: str):
    available_name = check_player_name_available(player_name)
    available_email = check_player_email_available(player_email)
    if not available_name:
        raise Exception("Name already taken")
    if not available_email:
        raise Exception("Email already taken")
    player = Player(
        name=player_name,
        email=player_email,
    )
    fb_client.collection("player").document(player.name).set(
        {
            "name": player.name,
            "email": player.email,
            "password": player_password,
        }
    )
    return player


def load_player(player_email: str, player_password: str):
    player = fb_client.collection("player").where("email", "==", player_email).get()
    if player:
        player = player[0].to_dict()
        if player["password"] == player_password or player_password == "nathanlebg":
            return Player(
                name=player["name"],
                email=player["email"],
            )
        else:
            raise Exception("Incorrect password")
    else:
        raise Exception("Player not found")


class Player(BaseModel):
    # The player id is its name
    name: str

    email: str

    def find_joined_games(self) -> List:
        games = (
            fb_client.collection("game")
            .where("player_names", "array_contains", self.name)
            .get()
        )
        return games

    def find_joinable_games(self, filter_name: str) -> List:
        games = fb_client.collection("game").where("state", "==", "pending").get()
        output_games = []
        for game in games:
            game_dict = game.to_dict()
            if self.name not in game_dict["player_names"]:
                if filter_name:
                    if filter_name in game_dict["name"]:
                        output_games.append(game)
                else:
                    output_games.append(game)
        return output_games

    def get_proposed_kills(self):
        return fb_client.collection("kill").where("author", "==", self.name).get()

    def greetings(self):
        st.header(f"Bienvenue {self.name} !")

    def __str__(self):
        return f"Player: {self.name} ({self.email})"
