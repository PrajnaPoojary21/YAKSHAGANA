# # import streamlit as st
# # import requests

# # API_URL = "http://localhost:8000"

# # st.title("Yakshagana Padya to Story Converter")

# # uploaded_file = st.file_uploader("Upload Yakshagana Audio", type=["mp3", "wav"])

# # if uploaded_file:
# #     if st.button("Process"):
# #         files = {"file": uploaded_file}
# #         res = requests.post(f"{API_URL}/upload", files=files)

# #         if res.status_code != 200:
# #             st.error("Upload failed")
# #         else:
# #             file_path = res.json()["file_path"]

# #             response = requests.post(f"{API_URL}/process", params={"file_path": file_path})

# #             if response.status_code == 200:
# #                 data = response.json()

# #                 st.subheader("Transcription")
# #                 st.text_area("", data["transcription"], height=150)

# #                 st.subheader("Cleaned Text")
# #                 st.text_area("", data["clean_text"], height=150)

# #                 st.subheader("Generated Story")
# #                 st.text_area("", data["story"], height=300)

# #                 st.subheader("Evaluation")
# #                 st.write("Score:", data["score"])
# #                 st.write("Feedback:", data["feedback"])
# #             else:
# #                 st.error("Processing failed")
# import streamlit as st
# import requests

# API_URL = "http://localhost:8000"

# st.title("Yakshagana Padya to Story Converter")

# uploaded_file = st.file_uploader("Upload Yakshagana Audio", type=["mp3", "wav"])

# mode = st.radio(
#     "Select Mode",
#     ["Speech to Text Only", "Full Pipeline (Story Generation)"]
# )

# if uploaded_file:

#     files = {"file": uploaded_file}

#     if st.button("Process"):

#         # Step 1: Upload
#         res = requests.post(f"{API_URL}/upload", files=files)

#         if res.status_code != 200:
#             st.error("Upload failed")
#             st.stop()

#         file_path = res.json()["file_path"]

#         # Step 2: Process
#         response = requests.post(
#             f"{API_URL}/process",
#             params={"file_path": file_path}
#         )

#         if response.status_code != 200:
#             st.error(f"Processing failed: {response.text}")
#             st.stop()

#         data = response.json()

#         # =========================
#         # MODE 1: Speech → Text only
#         # =========================
#         if mode == "Speech to Text Only":

#             st.subheader("🎤 Transcribed Text")
#             st.text_area(
#                 "Kannada Speech → Text Output",
#                 data["transcription"],
#                 height=200
#             )

#         # =========================
#         # MODE 2: Full Pipeline
#         # =========================
#         else:

#             st.subheader("🎤 Transcription")
#             st.text_area("", data["transcription"], height=150)

#             st.subheader("🧹 Cleaned Text")
#             st.text_area("", data["clean_text"], height=150)

#             st.subheader("🧠 Generated Story")
#             st.text_area("", data["story"], height=300)

#             st.subheader("📊 Evaluation")
#             st.write("Score:", data["score"])
#             st.write("Feedback:", data["feedback"])
import streamlit as st
import requests

# 🔁 Use 127.0.0.1 for reliability
API_URL = "http://127.0.0.1:8000"

st.title("Yakshagana Padya to Story Converter")

# Upload audio
uploaded_file = st.file_uploader("Upload Yakshagana Audio", type=["mp3", "wav"])

# Mode selection
mode = st.radio(
    "Select Mode",
    ["Speech to Text Only", "Full Pipeline (Story Generation)"]
)

if uploaded_file:

    st.success(f"File selected: {uploaded_file.name}")

    if st.button("Process"):

        st.write("🚀 Processing started...")

        try:
            # ✅ Correct file format for requests
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            # =========================
            # STEP 1: Upload file
            # =========================
            res = requests.post(f"{API_URL}/upload", files=files)

            st.write("📤 Upload response:", res.status_code, res.text)

            if res.status_code != 200:
                st.error("❌ Upload failed")
                st.stop()

            file_path = res.json()["file_path"]

            # =========================
            # STEP 2: Process audio
            # =========================
            response = requests.post(
                f"{API_URL}/process",
                params={"file_path": file_path}
            )

            st.write("⚙️ Process response:", response.status_code)

            if response.status_code != 200:
                st.error(f"❌ Processing failed: {response.text}")
                st.stop()

            data = response.json()

            # =========================
            # MODE 1: Speech → Text only
            # =========================
            if mode == "Speech to Text Only":

                st.subheader("🎤 Transcribed Text")

                st.text_area(
                    "Kannada Speech → Text Output",
                    data.get("transcription", "No transcription found"),
                    height=250
                )

            # =========================
            # MODE 2: Full Pipeline
            # =========================
            else:

                st.subheader("🎤 Transcription")
                st.text_area("", data.get("transcription", ""), height=150)

                st.subheader("🧹 Cleaned Text")
                st.text_area("", data.get("clean_text", ""), height=150)

                st.subheader("🧠 Generated Story")
                st.text_area("", data.get("story", ""), height=300)

                st.subheader("📊 Evaluation")
                st.write("Score:", data.get("score", 0))
                st.write("Feedback:", data.get("feedback", ""))

        except Exception as e:
            st.error(f"🔥 Error: {str(e)}")