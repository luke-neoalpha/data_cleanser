import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
import re

def preprocess_company_name_phase1(company_name):
    company_name = str(company_name)
    # Remove parentheses and their content
    company_name = re.sub(r"\(.*?\)", "", company_name).strip()
    # Remove suffixes (multiple occurrences handled)
    while True:
        updated_name = re.sub(
            r"(,?\s?-?\s?)(Inc\.|\.Inc|LLC|Corp\.|Ltd\.|CO\.|RCA|DMD|LTD|LLP|LP|Inc|GMBH|Private Wealth|SW|PSP|PSC|CPA|PLLC|BA|WM|DDS|401 Plan|401\(k\)|401|L\.L\.C|L\.P|P\.C\.|Employee Stock Ownership Plan|PC|PSC|CPAs|PA)(\s|,|-|$)",
            "",
            company_name,
            flags=re.IGNORECASE,
        ).strip()
        if updated_name == company_name:  # Stop if no more changes
            break
        company_name = updated_name
    # Normalize spaces: convert multiple spaces into a single space, but leave single spaces intact
    company_name = re.sub(r"\s{2,}", " ", company_name).strip()
    
    # Ensure that there is exactly one space between words
    company_name = re.sub(r"\s{2,}", " ", company_name)
    
    return company_name


# Phase 2 Preprocessing
def preprocess_company_name_phase2(company_name, clearbit_name):
    """
    Preprocess the company name by:
    - Removing parentheses and their content.
    - Removing specified suffixes.
    - Handling common words for better matching.
    - Returning the preprocessed name with the best match percentage.
    """
    # Remove parentheses and their content
    company_name = re.sub(r"\(.*?\)", "", company_name).strip()
    
    # Remove specified suffixes
    suffixes_to_remove = [", inc.", ".inc", ", llc", ", ltd.", ", lp", ".ltd", ", lp.", " inc.", "- Private Wealth"]
    for suffix in suffixes_to_remove:
        company_name = re.sub(re.escape(suffix), "", company_name, flags=re.IGNORECASE).strip()
    
    # Remove "&" and extra spaces
    company_name = company_name.replace("&", "").strip()
    
    # Split words for advanced matching logic
    words = company_name.split()
    common_words = {"a", "for", "of", "and", "to"}
    best_match = ""
    highest_score = 0
    
    for include_word in [True, False]:
        filtered_words = [
            word for word in words if include_word or word.lower() not in common_words
        ]
        acronym = "".join(word[0].upper() for word in filtered_words)
        score = fuzz.ratio(acronym.upper(), clearbit_name.upper())
        
        if score > highest_score:
            highest_score = score
            best_match = acronym
    
    return best_match, highest_score

# Initialize session state
if "matched_records" not in st.session_state:
    st.session_state["matched_records"] = pd.DataFrame()
if "unmatched_records" not in st.session_state:
    st.session_state["unmatched_records"] = pd.DataFrame()

# Streamlit app
st.title("Company Name Preprocessor and Matcher")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file:
    data = pd.read_excel(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(data)

    selected_column = st.selectbox("Select the column to preprocess:", data.columns)
    clearbit_column = st.selectbox("Select the column to match with:", data.columns)

    # Phase 1 Processing
    if st.button("Process Phase 1"):
        data['Preprocessed Company Name Phase 1'] = data[selected_column].apply(preprocess_company_name_phase1)
        data['Match Percentage'] = data.apply(
            lambda row: f"{fuzz.ratio(row['Preprocessed Company Name Phase 1'].upper(), row[clearbit_column].upper()):.2f}%", axis=1
        )
        data['Matched By'] = data['Match Percentage'].apply(
            lambda x: "1" if float(x.replace('%', '')) > 88 else ""
        )

        st.session_state["matched_records"] = data[data['Matched By'] == "1"]
        st.session_state["unmatched_records"] = data[data['Matched By'] == ""]

        st.write("**Live Processing Stats (Phase 1):**")
        st.metric("Matched Records", len(st.session_state["matched_records"]))
        st.metric("Unmatched Records", len(st.session_state["unmatched_records"]))

        st.write("Matched Records (Phase 1):")
        st.dataframe(st.session_state["matched_records"])

        st.write("Unmatched Records (Phase 1):")
        st.dataframe(st.session_state["unmatched_records"])

    # Phase 2 Processing
    if st.button("Process Phase 2"):
        if st.session_state["unmatched_records"].empty:
            st.error("Phase 1 must be processed first!")
        else:
            unmatched_records = st.session_state["unmatched_records"].copy()

            # Apply advanced Phase 2 preprocessing
            unmatched_records['Preprocessed Company Name Phase 2'], unmatched_records['Advanced Match Percentage'] = zip(*unmatched_records.apply(
                lambda row: preprocess_company_name_phase2(row[selected_column], row[clearbit_column]), axis=1
            ))

            unmatched_records['Advanced Match Percentage'] = unmatched_records['Advanced Match Percentage'].apply(lambda x: f"{x:.2f}%")
            unmatched_records['Matched By'] = unmatched_records['Advanced Match Percentage'].apply(
                lambda x: "2" if float(x.replace('%', '')) == 100 else ""
            )

            # Update matched and unmatched records
            new_matched_records = unmatched_records[unmatched_records['Matched By'] == "2"]
            st.session_state["matched_records"] = pd.concat([st.session_state["matched_records"], new_matched_records], ignore_index=True)
            st.session_state["unmatched_records"] = unmatched_records[unmatched_records['Matched By'] == ""]

            st.write("**Live Processing Stats (Phase 2):**")
            st.metric("Matched Records", len(st.session_state["matched_records"]))
            st.metric("Unmatched Records", len(st.session_state["unmatched_records"]))

            st.write("Updated Matched Records (Phase 2):")
            st.dataframe(st.session_state["matched_records"])

            st.write("Updated Unmatched Records (Phase 2):")
            st.dataframe(st.session_state["unmatched_records"])




