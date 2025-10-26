"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import logging
import streamlit as st
import constants as ct
from langchain.schema import Document
import re

############################################################
# 関数定義
############################################################

def display_app_title():
    """タイトル表示"""
    st.markdown(f"## {ct.APP_NAME}")


def display_initial_ai_message():
    """AIメッセージの初期表示"""
    with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
        st.markdown(
            "こちらは対話型の商品レコメンド生成AIアプリです。「こんな商品が欲しい」という情報・要望を画面下部のチャット欄から送信いただければ、おすすめの商品をレコメンドいたします。"
        )
        st.markdown("**入力例**")
        st.info("""
        - 「長時間使える、高音質なワイヤレスイヤホン」
        - 「机のライト」
        - 「USBで充電できる加湿器」
        """)


def display_conversation_log():
    """会話ログの一覧表示"""
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar=ct.USER_ICON_FILE_PATH):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
                display_product(message["content"])


def display_product(result):
    """商品情報の表示"""
    logger = logging.getLogger(ct.LOGGER_NAME)
    st.markdown("以下の商品をご提案いたします。")

    # 🔍 追加1: 安全チェック（空やNoneのとき）
    if not result:
        st.warning("結果が空です。")
        return

    # 🔍 追加2: result が ["Document(...)", ...] の場合に復元
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], str) and "Document(" in result[0]:
        docs = []
        for r in result:
            match = re.search(r"page_content='(.*?)'", r, re.DOTALL)
            if match:
                page_content = match.group(1).replace("\\n", "\n")
                docs.append(Document(page_content=page_content))
        result = docs

    # 🔍 追加3: 正常なDocument以外はスキップ
    if not hasattr(result[0], "page_content"):
        st.error("商品情報の形式が不正です。")
        return

    # 以下は元ファイルと同じ
    product_lines = result[0].page_content.split("\n")
    product = {item.split(": ")[0]: item.split(": ")[1] for item in product_lines if ": " in item}

    st.success(f"""
        商品名：{product.get('name','不明')}（商品ID: {product.get('id','?')}）\n
        価格：{product.get('price','不明')}
    """)

    st.code(f"""
        商品カテゴリ：{product.get('category','-')}\n
        メーカー：{product.get('maker','-')}\n
        評価：{product.get('score','-')}（{product.get('review_number','-')}件）
    """, language=None, wrap_lines=True)

    st.image(f"images/products/{product.get('file_name','default.jpg')}", width=400)
    st.code(product.get("description",""), language=None, wrap_lines=True)
    st.markdown("**こんな方におすすめ！**")
    st.info(product.get("recommended_people","情報なし"))
    st.link_button("商品ページを開く", type="primary", use_container_width=True, url="https://google.com")
