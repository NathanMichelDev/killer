from pydantic import BaseModel
from typing import Optional
from utils import create_random_id
import streamlit as st
from firestore import fb_client


def check_kill_content_available(content, game_name):
    if (
        fb_client.collection("kill")
        .where("content", "==", content)
        .where("game_name", "==", game_name)
        .get()
    ):
        return False
    else:
        return True


def create_kill(content, player_name, game_name):
    if check_kill_content_available(content, game_name):
        kill = Kill(
            id=create_random_id(),
            author=player_name,
            content=content,
            game_name=game_name,
        )
        kill.save()
        st.experimental_rerun()
    else:
        raise Exception("Kill already exists in this game")


def get_player_kills(player_name):
    remote_kills = fb_client.collection("kill").where("author", "==", player_name).get()
    player_kills = []
    for kill in remote_kills:
        kill = kill.to_dict()
        player_kills.append(Kill(**kill))
    return player_kills


class Kill(BaseModel):
    id: str
    author: str
    content: str
    game_name: str
    target: Optional[str]

    def save(self):
        fb_client.collection("kill").document(self.id).set(self.dict())

    def st_describe(self):
        cols = st.columns(2)
        with cols[0]:
            st.write(self.content)
        with cols[1]:
            if st.button("Delete kill", key="Delete kill" + self.id):
                fb_client.collection("kill").document(self.id).delete()
                st.experimental_rerun()
