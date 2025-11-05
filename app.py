import streamlit as st
import json
import requests
import logging
import os
from vector_db import (
    create_vector_db_from_feedback,
    search_cache,
    get_vector_dataframe,
    get_embedding_model,
)
from constants import VECTOR_DB_PATH, FEEDBACK_LOG_PATH, DATA_DIR

def chat(user_query, endpoint, model_name, chat_history, system_prompt):
    """LLM sunucusuna istek gönderir ve yanıtı alır."""
    messages = [{"role": "system", "content": system_prompt}]
    for h in chat_history:
        messages.append({"role": "user", "content": h["user"]})
        if h.get("assistant"):
            messages.append({"role": "assistant", "content": h["assistant"]})
    messages.append({"role": "user", "content": user_query})
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False
    }
    try:
        response = requests.post(endpoint + "/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()
        answer = data.get("message", data.get("response", "Yanıt alınamadı."))
        if isinstance(answer, dict):
            answer = answer.get("content", str(answer))
        return answer, None
    except Exception as e:
        return None, f"API Hatası: {str(e)}"

feedback_logger = logging.getLogger('feedback')
feedback_logger.setLevel(logging.INFO)
feedback_logger.propagate = False
if not feedback_logger.handlers:
    handler = logging.FileHandler('feedback.log', mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    feedback_logger.addHandler(handler)

with open("configs.json", "r") as f:
    configs = json.load(f)

model_list = [str(item["model"]) for item in configs]
endpoint_list = [str(item["endpoint"]) for item in configs]

with open("prompt.aitk.txt", "r") as f:
    SYSTEM_PROMPT = f.read()

os.makedirs(DATA_DIR, exist_ok=True)

st.set_page_config(page_title="Basit Sohbet Arayüzü", layout="wide")
st.markdown("""
    <style>
    @media (max-width: 600px) {
        .block-container { padding-left: 0.5rem; padding-right: 0.5rem; }
        textarea, .stButton button { font-size: 1em !important; }
    }
    .sohbet-kutu { background: #f7f7fa; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; }
    .kullanici { color: #1a237e; }
    .asistan { color: #00695c; }
    </style>
    <h2 style='font-size:1.5em;'>Basit Sohbet Arayüzü (Streamlit)</h2>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])
with col1:
    model_name = st.selectbox("Model Seçiniz", model_list, index=0)
with col2:
    model_endpoint = st.selectbox("Sunucu (Endpoint) Seçiniz", endpoint_list, index=0)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

if st.session_state.clear_input:
    st.session_state.user_input = ""
    st.session_state.clear_input = False

st.markdown("---")

# --- Sidebar Toggles ---
with st.sidebar:
    st.markdown("### Vektör Veritabanı Yönetimi")
    if st.button("Vektör Veritabanını Oluştur/Güncelle", use_container_width=True):
        with st.spinner("Vektör veritabanı işleniyor..."):
            success = create_vector_db_from_feedback()
            if success:
                st.success("Vektör veritabanı başarıyla oluşturuldu/güncellendi.")
            else:
                st.warning("Yeterli beğenilen veri yok veya dosya bulunamadı.")
    if st.button("Vektör Veritabanı Durumunu Kontrol Et", use_container_width=True):
        df = get_vector_dataframe()
        if df is not None:
            st.info(f"Vektör veritabanı mevcut. Toplam {len(df)} kayıt var.")
            st.markdown("#### Vektör Özellikleri (İlk 5)")
            st.dataframe(df.head())
        else:
            st.warning("Vektör veritabanı bulunamadı.")

    st.markdown("---")

    if st.session_state.chat_history:
        chat_history_json = json.dumps(
            st.session_state.chat_history, indent=2, ensure_ascii=False
        )
        st.download_button(
            label="Sohbet Geçmişini İndir (JSON)",
            data=chat_history_json,
            file_name="sohbet_gecmisi.json",
            mime="application/json",
            use_container_width=True,
        )

    uploaded_file = st.file_uploader(
        "Sohbet Geçmişini Yükle (JSON)",
        type=["json"],
        help="Kaydedilmiş bir sohbet geçmişi dosyasını yükleyerek oturumu geri getirin.",
    )
    if uploaded_file is not None:
        try:
            new_chat_history = json.load(uploaded_file)
            # Basit doğrulama: Yüklenen verinin beklenen formatta olup olmadığını kontrol et
            if isinstance(new_chat_history, list) and all(
                "user" in item and "assistant" in item for item in new_chat_history
            ):
                st.session_state.chat_history = new_chat_history
                st.success("Sohbet geçmişi başarıyla yüklendi!")
                st.rerun()  # Arayüzü hemen güncellemek için
            else:
                st.error("Hata: JSON dosyası beklenen formatta değil.")
        except json.JSONDecodeError:
            st.error(
                "Hata: Geçersiz JSON dosyası. Lütfen dosyanın içeriğini kontrol edin."
            )

    st.markdown("---")
    st.checkbox("Show Code Canvas", key="show_code_canvas", value=False)


# --- Main Content Area ---
if st.session_state.get("show_code_canvas", False):
    main_chat_col, code_canvas_col = st.columns([2, 1])
else:
    main_chat_col = st.container() # Use a container to act as a single column

with main_chat_col:
    st.markdown("<b>Sohbet Geçmişi</b>", unsafe_allow_html=True)
    for i, h in enumerate(st.session_state.chat_history):
        with st.container():
            st.markdown(
                f"<div class='sohbet-kutu'><span class='kullanici'><b>Kullanıcı:</b> {h['user']}</span></div>",
                unsafe_allow_html=True)
            st.markdown(
                f"<div class='sohbet-kutu'><span class='asistan'><b>Asistan:</b> {h['assistant']}</span></div>",
                unsafe_allow_html=True)

            if h.get("from_cache"):
                st.info("Bu yanıt önbellekten getirildi.")
                st.write("Bu yanıt yardımcı oldu mu?")
                feedback_cols = st.columns([1, 1, 1, 10])
                with feedback_cols[0]:
                    yes_clicked = st.button("Evet", key=f"yes_{i}")
                with feedback_cols[1]:
                    no_clicked = st.button("Hayır", key=f"no_{i}")
                if yes_clicked:
                    feedback_logger.info(
                        f"CacheFeedback: helpful | Query: {h['user']} | Response: {h['assistant']}"
                    )
                    st.success("Geri bildiriminiz için teşekkürler!")
                if no_clicked:
                    feedback_logger.info(
                        f"CacheFeedback: not_helpful | Query: {h['user']} | Response: {h['assistant']}"
                    )
                    st.warning(
                        "Geri bildiriminiz için teşekkürler! Bu yanıtı iyileştirmeye çalışacağız."
                    )
            else:
                icon_cols = st.columns([1, 1, 1, 10])
                with icon_cols[0]:
                    like_clicked = st.button("👍", key=f"like_{i}", help="Beğen")
                with icon_cols[1]:
                    dislike_clicked = st.button(
                        "👎", key=f"dislike_{i}", help="Beğenme"
                    )
                with icon_cols[2]:
                    copy_clicked = st.button("📋", key=f"copy_{i}", help="Kopyala")
                if like_clicked:
                    feedback_logger.info(f"PromptForLikedResponse: {h['user']}")
                    feedback_logger.info(f"Feedback: like | Message: {h['assistant']}")
                    st.success("Beğeni kaydedildi.")
                if dislike_clicked:
                    feedback_logger.info(
                        f"Feedback: dislike | Message: {h['assistant']}"
                    )
                    st.info("Beğenmeme kaydedildi.")
                if copy_clicked:
                    st.session_state.user_input = h["assistant"]
                    st.success(
                        "Yanıt panoya kopyalandı (manuel olarak kopyalayabilirsiniz)."
                    )

    st.markdown("---")
    st.markdown("<div style='font-size:0.95em;'><b>Mesajınızı yazın:</b> <span style='color:gray;'>(Göndermek için: <b>Ctrl+Enter</b> veya <b>Cmd+Enter</b>)</span></div>", unsafe_allow_html=True)
    user_input = st.text_area(
        "Mesaj",
        height=80,
        key="user_input",
        label_visibility="collapsed",
        on_change=lambda: st.session_state.update({"send_shortcut": True})
    )
    col_send = st.columns([8,1]) # This column is relative to main_chat_col
    send = col_send[1].button("Gönder", use_container_width=True)

    send_shortcut = st.session_state.pop("send_shortcut", False) if "send_shortcut" in st.session_state else False
    if (send or send_shortcut) and st.session_state.user_input.strip():
        user_query = st.session_state.user_input
        cached_response = search_cache(user_query)
        if cached_response:
            answer = cached_response
            st.session_state.chat_history.append(
                {
                    "user": user_query,
                    "assistant": answer,
                    "from_cache": True,
                }
            )
        else:
            with st.spinner("Yanıt hazırlanıyor..."):
                answer, error = chat(
                    user_query,
                    model_endpoint,
                    model_name,
                    st.session_state.chat_history,
                    SYSTEM_PROMPT,
                )
            if error:
                st.error(error)
            else:
                st.session_state.chat_history.append(
                    {"user": user_query, "assistant": answer}
                )
        st.session_state.clear_input = True
        st.rerun()

    st.markdown(
        f"<div style='font-size:11px;color:gray;'>Model: {model_name} | Sunucu: {model_endpoint} | Toplam Karakter: {sum(len(h['user'])+len(h['assistant']) for h in st.session_state.chat_history)} | Mesaj Sayısı: {len(st.session_state.chat_history)}</div>",
        unsafe_allow_html=True)

if st.session_state.get("show_code_canvas", False):
    with code_canvas_col:
        st.markdown("### Code Canvas")
        st.text_area("Code Editor Placeholder", height=600, key="code_canvas_editor")
        # Add other elements for "other tasks" here in the future
