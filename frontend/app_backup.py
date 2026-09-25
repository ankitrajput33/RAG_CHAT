import streamlit as st
import requests


BACKEND_URL = "http://127.0.0.1:8000"


# --------------------------------
# PAGE CONFIG
# --------------------------------

st.set_page_config(
    page_title="AI Knowledge Assistant",
    page_icon="🧠",
    layout="wide"
)


# --------------------------------
# TITLE
# --------------------------------

st.title("🧠 AI Knowledge Assistant")

st.write(
    "Upload documents or add a website, "
    "then ask questions from your knowledge base."
)


# --------------------------------
# SIDEBAR
# --------------------------------

with st.sidebar:

    st.header("📚 Add Knowledge")


    # ==================================
    # DOCUMENT UPLOAD
    # ==================================

    st.subheader("📄 Upload Documents")

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "docx", "txt", "csv", "md"]
    )

    if st.button(
        "⬆️ Upload Document",
        use_container_width=True
    ):

        if uploaded_file is None:

            st.warning(
                "Please choose a document first."
            )

        else:

            try:

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                with st.spinner(
                    "Processing document..."
                ):

                    response = requests.post(
                        f"{BACKEND_URL}/upload",
                        files=files,
                        timeout=120
                    )

                if response.status_code == 200:

                    result = response.json()

                    st.success(
                        f"✅ {result['file_name']} added!"
                    )

                    st.info(
                        f"Chunks added: "
                        f"{result['chunks_added']}"
                    )

                else:

                    st.error(
                        f"Upload failed: {response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ FastAPI backend is not running."
                )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )


    st.divider()


    # ==================================
    # WEBSITE
    # ==================================

    st.subheader("🌐 Add Website")

    website_url = st.text_input(
        "Paste website URL",
        placeholder="https://example.com"
    )

    if st.button(
        "🌐 Add Website",
        use_container_width=True
    ):

        if not website_url.strip():

            st.warning(
                "Please paste a website URL."
            )

        else:

            try:

                with st.spinner(
                    "Reading website..."
                ):

                    response = requests.post(
                        f"{BACKEND_URL}/add-url",
                        json={
                            "url": website_url.strip()
                        },
                        timeout=120
                    )

                if response.status_code == 200:

                    result = response.json()

                    st.success(
                        "✅ Website added!"
                    )

                    st.info(
                        f"Chunks added: "
                        f"{result['chunks_added']}"
                    )

                else:

                    st.error(
                        f"Website failed: "
                        f"{response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ FastAPI backend is not running."
                )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )


    st.divider()


    # ==================================
    # KNOWLEDGE BASE
    # ==================================

    st.subheader("📊 Knowledge Base")

    try:

        response = requests.get(
            f"{BACKEND_URL}/knowledge-base",
            timeout=10
        )

        if response.status_code == 200:

            data = response.json()

            st.metric(
                "Stored Chunks",
                data["total_chunks"]
            )

        else:

            st.warning(
                "Could not read knowledge base."
            )

    except:

        st.warning(
            "Backend not connected."
        )


# --------------------------------
# CHAT AREA
# --------------------------------

st.subheader("💬 Ask Questions")

question = st.chat_input(
    "Ask a question from your documents or websites..."
)


if question:

    # USER MESSAGE

    st.chat_message(
        "user"
    ).write(question)


    # ASSISTANT MESSAGE

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Searching your knowledge base..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "question": question
                    },
                    timeout=120
                )


                if response.status_code == 200:

                    result = response.json()


                    # ANSWER
                    st.write(
                        result["answer"]
                    )


                    # SOURCES
                    sources = result.get(
                        "sources",
                        []
                    )


                    if sources:

                        st.divider()

                        st.subheader(
                            "📚 Sources"
                        )


                        shown_sources = set()


                        for source in sources:

                            source_name = source.get(
                                "source",
                                "Unknown"
                            )


                            if source_name not in shown_sources:

                                shown_sources.add(
                                    source_name
                                )

                                source_type = source.get(
                                    "type",
                                    ""
                                )


                                if source_type == "web":

                                    st.write(
                                        f"🌐 {source_name}"
                                    )

                                else:

                                    st.write(
                                        f"📄 {source_name}"
                                    )


                else:

                    st.error(
                        f"Backend error: "
                        f"{response.text}"
                    )


            except requests.exceptions.ConnectionError:

                st.error(
                    "❌ Cannot connect to FastAPI."
                )


            except Exception as e:

                st.error(
                    f"Error: {e}"
                )