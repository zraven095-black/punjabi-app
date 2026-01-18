import streamlit as st
import pandas as pd
import emoji
import re
from collections import Counter

# --- Configuration & Styles ---
st.set_page_config(
    page_title="Lafz-Vigyan",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Dark Mode aesthetics
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }
    .stTextArea textarea {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #4B5563;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Standard Dictionary (Sample of 100+ common Punjabi words) ---
# This serves as the baseline for "Known Words". In a real app, this would be a database.
STANDARD_PUNJABI_DICT = set([
    "ਮੈਂ", "ਤੂੰ", "ਅਸੀਂ", "ਤੁਸੀਂ", "ਉਹ", "ਹਾਂ", "ਸੀ", "ਨੇ", "ਨੂੰ", "ਦਾ", "ਦੇ", "ਦੀ", "ਵਿੱਚ", "ਤੇ", "ਅਤੇ",
    "ਪਰ", "ਜਾਂ", "ਕਿਉਂਕਿ", "ਜਦੋਂ", "ਤਦ", "ਹੁਣ", "ਕੱਲ੍ਹ", "ਅੱਜ", "ਸਾਡਾ", "ਤੁਹਾਡਾ", "ਮੇਰਾ", "ਕੀ", "ਕਿਵੇਂ",
    "ਕਿੱਥੇ", "ਕੌਣ", "ਜਾ", "ਆ", "ਖਾ", "ਪੀ", "ਸੌਂ", "ਰਹਿ", "ਕਰ", "ਦੇਖ", "ਸੁਣ", "ਬੋਲ", "ਲਿਖ", "ਪੜ੍ਹ",
    "ਘਰ", "ਸਕੂਲ", "ਕੰਮ", "ਪਾਣੀ", "ਰੋਟੀ", "ਚਾਹ", "ਦੁੱਧ", "ਮਾਂ", "ਪਿਓ", "ਭਰਾ", "ਭੈਣ", "ਦੋਸਤ", "ਮਿੱਤਰ",
    "ਖੁਸ਼ੀ", "ਗ਼ਮ", "ਪਿਆਰ", "ਨਫ਼ਰਤ", "ਜ਼ਿੰਦਗੀ", "ਮੌਤ", "ਸੱਚ", "ਝੂਠ", "ਦਿਨ", "ਰਾਤ", "ਸਵੇਰ", "ਸ਼ਾਮ",
    "ਵਧੀਆ", "ਮਾੜਾ", "ਚੰਗਾ", "ਸੋਹਣਾ", "ਵੱਡਾ", "ਛੋਟਾ", "ਨਵਾਂ", "ਪੁਰਾਣਾ", "ਲਾਲ", "ਕਾਲਾ", "ਚਿੱਟਾ", "ਨੀਲਾ",
    "ਇੱਕ", "ਦੋ", "ਤਿੰਨ", "ਚਾਰ", "ਪੰਜ", "ਦਸ", "ਸੌ", "ਹਜ਼ਾਰ", "ਲੱਖ", "ਕਰੋੜ",
    "ਭਾਰਤ", "ਪੰਜਾਬ", "ਦੁਨੀਆ", "ਧਰਤੀ", "ਅਸਮਾਨ", "ਸੂਰਜ", "ਚੰਦ", "ਤਾਰੇ", "ਹਵਾ", "ਅੱਗ",
    "ਕਿਤਾਬ", "ਕਾਪੀ", "ਕਲਮ", "ਫੋਨ", "ਗੱਡੀ", "ਬੱਸ", "ਰੇਲ", "ਜਹਾਜ਼", "ਰਸਤਾ", "ਸ਼ਹਿਰ", "ਪਿੰਡ"
])

# --- Helper Functions ---

def clean_text_gurmukhi(text):
    """
    Tokenizes text by removing punctuation and numbers, keeping Gurmukhi chars.
    """
    # Remove emojis and generic punctuation for word analysis
    text_no_emoji = emoji.replace_emoji(text, replace='')
    # Keep Gurmukhi characters and basic punctuation marks potentially part of words if needed,
    # but strictly speaking we want to isolate words.
    # Pattern: Blocks not suitable for Gurmukhi words (keep \w which includes Unicode letters)
    # Simple regex to extract sequences of alphanumeric chars (Unicode aware)
    words = re.findall(r'\w+', text_no_emoji)
    return [w for w in words if not w.isnumeric()] 

def extract_emojis(text):
    """
    Returns a list of all emojis found in the text.
    """
    return [char['emoji'] for char in emoji.emoji_list(text)]

def calculate_evolution_score(neologism_count, total_words):
    if total_words == 0:
        return 0
    return (neologism_count / total_words) * 100

# --- Main Application ---

def main():
    st.title("Lafz-Vigyan: Punjabi Digital Evolution Tracker")
    st.markdown("### Detect new Punjabi words and track digital language trends.")

    # Sidebar for Context & Disclaimer
    with st.sidebar:
        st.header("About")
        st.info(
            "**Academic Disclaimer**:\n\n"
            "This tool uses simulated data for conceptual research demonstration. "
            "It compares input text against a limited prototype lexicon."
        )
        st.markdown("---")
        st.markdown("**Version**: 1.0.0 (Research Prototype)")

    # Input Section
    with st.container():
        user_input = st.text_area("Paste Punjabi Text Here:", height=200, placeholder="ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ! ਅੱਜ ਕੱਲ੍ਹ ਸੋਸ਼ਲ ਮੀਡੀਆ 'ਤੇ ਬਹੁਤ hashtag ਚੱਲ ਰਹੇ ਹਨ...")

    if st.button("Analyze Text", type="primary"):
        if not user_input.strip():
            st.warning("Please enter some text to analyze.")
            return

        with st.spinner("Analyzing linguistic patterns..."):
            # 1. Extraction & Cleaning
            all_words_raw = clean_text_gurmukhi(user_input)
            all_emojis = extract_emojis(user_input)
            
            # Filter empty strings if any
            all_words = [w for w in all_words_raw if w.strip()]
            total_word_count = len(all_words)
            
            # 2. Neologism Detection
            # Normalize dictionary for comparison? (Assuming dict provided is standard)
            known_words_set = STANDARD_PUNJABI_DICT
            
            neologisms = []
            known_count = 0
            
            for word in all_words:
                if word in known_words_set:
                    known_count += 1
                else:
                    neologisms.append(word)
            
            neologism_counts = Counter(neologisms)
            emoji_counts = Counter(all_emojis)
            
            neologism_total_count = len(neologisms)
            evolution_score = calculate_evolution_score(neologism_total_count, total_word_count)

            # 3. Display Metrics
            st.markdown("### Analysis Results")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Words", total_word_count)
            with col2:
                st.metric("Neologisms Found", neologism_total_count, delta=f"{evolution_score:.1f}% Ratio", delta_color="inverse")
            with col3:
                st.metric("Emojis Used", len(all_emojis))
            with col4:
                st.metric("Known Words", known_count)

            st.divider()

            # 4. Detailed Breakdown
            row1_col1, row1_col2 = st.columns([1, 1])

            with row1_col1:
                st.subheader("Potential New Words")
                if neologism_counts:
                    neo_df = pd.DataFrame(neologism_counts.items(), columns=["Word", "Frequency"]).sort_values(by="Frequency", ascending=False)
                    st.dataframe(neo_df, use_container_width=True, hide_index=True)
                    
                    # Download CSV
                    csv = neo_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📄 Download Neologism Report",
                        data=csv,
                        file_name="punjabi_neologisms.csv",
                        mime="text/csv",
                    )
                else:
                    st.info("No new words detected based on the current standard dictionary.")

            with row1_col2:
                st.subheader("Top Used Emojis")
                if emoji_counts:
                    emoji_df = pd.DataFrame(emoji_counts.most_common(5), columns=["Emoji", "Count"])
                    # Use st.bar_chart
                    st.bar_chart(emoji_df.set_index("Emoji"))
                else:
                    st.caption("No emojis found in the text.")

            # 5. Language Evolution Score Visual
            st.subheader("Language Evolution Score")
            st.progress(min(evolution_score / 100, 1.0))
            if evolution_score > 50:
                 st.caption(f"⚠️ High divergence ({evolution_score:.1f}%) from standard lexicon.")
            else:
                 st.caption(f"This text diverges {evolution_score:.1f}% from the standard lexicon.")

if __name__ == "__main__":
    main()
