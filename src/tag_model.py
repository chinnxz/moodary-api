from gensim.models import Word2Vec
from src.database import db, Hashtag
import pandas as pd


def tag_model(tag, mood):
    q = db.session.query(Hashtag.tag, Hashtag.mood).distinct().filter(Hashtag.mood == mood).all()
    df = pd.DataFrame(q, columns=["text", "label"])

    text_list = df["text"].to_list()
    text_m_list = []
    for w in text_list:
        word = []
        word.append(w)
        text_m_list.append(word)

    model = Word2Vec(text_m_list, min_count=1)
    test = model.wv.most_similar(tag)
    tag_list = []

    for t in test:
        key, value = t
        tag_list.append(key)

    return tag_list[0:6]
