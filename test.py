# import streamlit as st
# import pandas as pd
# from rapidfuzz import fuzz, process
# import re


# # Utility function to load freemail domains
# def load_freemail_domains(file_path):
#     return set(pd.read_csv(file_path, header=None)[0].str.strip().tolist())


# # Utility function to extract domains
# def extract_domain(email_list, freemail_domains):
#     if not email_list:
#         return None
#     domains = [email.split("@")[-1] for email in email_list.split(";") if "@" in email]
#     non_freemail = [domain for domain in domains if domain not in freemail_domains]
#     if non_freemail:
#         return max(non_freemail, key=non_freemail.count)  # Most common non-freemail domain
#     return None


# # Preprocessing function for company names
# def preprocess_company_name(company_name):
#     company_name = str(company_name)
#     # Remove parentheses and their content
#     company_name = re.sub(r"\(.*?\)", "", company_name).strip()
#     # Remove suffixes (multiple occurrences handled)
#     while True:
#         updated_name = re.sub(
#             r"(,?\s?-?\s?)(Inc\.|\.Inc|LLC|Corp\.|Ltd\.|CO\.|RCA|DMD|LTD|LLP|LP|Inc|GMBH|Private Wealth|SW|PSP|PSC|CPA|PLLC|BA|WM|DDS|401 Plan|401\(k\)|401|L\.L\.C|L\.P|P\.C\.|Employee Stock Ownership Plan|PC|PSC|CPAs|PA|Corp)(\s|,|-|$)",
#             "",
#             company_name,
#             flags=re.IGNORECASE,
#         ).strip()
#         if updated_name == company_name:  # Stop if no more changes
#             break
#         company_name = updated_name
#     # Normalize spaces: convert multiple spaces into a single space
#     company_name = re.sub(r"\s{2,}", " ", company_name).strip()
#     return company_name


# # Streamlit app starts here
# st.title("HubSpot Company Match")

# # Sidebar for file uploads
# hubspot_file = st.sidebar.file_uploader("Upload HubSpot Companies Excel File", type=["xls", "xlsx"], key="hubspot")
# ma_file = st.sidebar.file_uploader("Upload M&A Companies Excel File", type=["xls", "xlsx"], key="ma")
# freemail_file = "freemail_domains.csv"  # Update with your repository path

# # Load freemail domains
# freemail_domains = load_freemail_domains(freemail_file)

# # Session state initialization
# if "matched_records" not in st.session_state:
#     st.session_state.matched_records = pd.DataFrame()
# if "unmatched_records" not in st.session_state:
#     st.session_state.unmatched_records = pd.DataFrame()

# # Load data
# if hubspot_file and ma_file:
#     hubspot_data = pd.read_excel(hubspot_file)
#     ma_data = pd.read_excel(ma_file)

#     # Initialize unmatched records
#     if st.session_state.unmatched_records.empty:
#         st.session_state.unmatched_records = ma_data.copy()

#     # Matching options
#     match_type = st.radio("Select Matching Type", ["Column Matching", "Domain Extraction Matching", "Fuzzy Matching"])

#     if match_type == "Column Matching":
#         hubspot_col = st.selectbox("Select HubSpot Column for Matching", hubspot_data.columns)
#         ma_col = st.selectbox("Select M&A Column for Matching", st.session_state.unmatched_records.columns)

#         if "matching_started" not in st.session_state:
#             st.session_state.matching_started = False
        
#         if "column_match_clicked" not in st.session_state:
#             st.session_state.column_match_clicked = False

#         if st.button("Match Records", disabled=st.session_state.column_match_clicked):
#             st.session_state.column_match_clicked = True
#             matched = pd.merge(
#                 st.session_state.unmatched_records, hubspot_data, left_on=ma_col, right_on=hubspot_col, how="inner"
#             )
#             matched["Matched By"] = f"Column Matching ({ma_col} - {hubspot_col})"

#             st.session_state.matched_records = pd.concat([st.session_state.matched_records, matched], ignore_index=True)
#             st.session_state.unmatched_records = st.session_state.unmatched_records[
#                 ~st.session_state.unmatched_records[ma_col].isin(matched[ma_col])
#             ]

#             st.success("Column matching completed!")
#             st.session_state.matching_started = True 
#             st.rerun() 

#         if not st.session_state.unmatched_records.empty:
#             if st.session_state.matching_started:
#                 if st.button("Continue Matching"):
#                     st.session_state.column_match_clicked = False
#                     # hubspot_col = st.selectbox(
#                     #     "Select New HubSpot Column for Matching", hubspot_data.columns, key="new_hubspot_col"
#                     # )
#                     # ma_col = st.selectbox(
#                     #     "Select New M&A Column for Matching", st.session_state.unmatched_records.columns, key="new_ma_col"
#                     # )
#                     st.session_state.matching_started = False
#                     st.rerun()
#         else:
#             st.warning("No unmatched records left.")

#     elif match_type == "Domain Extraction Matching":
#         hubspot_col = st.selectbox("Select HubSpot Column (Domain)", hubspot_data.columns)
#         ma_col = st.selectbox("Select M&A Column (Emails/Domain)", st.session_state.unmatched_records.columns)

#         if "domain_matching_started" not in st.session_state:
#             st.session_state.domain_matching_started = False

#         if "domain_match_clicked" not in st.session_state:
#             st.session_state.domain_match_clicked = False

#         if st.button("Extract Domains and Match", disabled=st.session_state.domain_match_clicked):
#             st.session_state.domain_match_clicked = True
#             st.session_state.unmatched_records[ma_col] = st.session_state.unmatched_records[ma_col].fillna("")
#             st.session_state.unmatched_records["Extracted Domain"] = st.session_state.unmatched_records[ma_col].apply(
#                 lambda x: extract_domain(x, freemail_domains)
#             )

#             matched = pd.merge(
#                 st.session_state.unmatched_records, hubspot_data, left_on="Extracted Domain", right_on=hubspot_col, how="inner"
#             )
#             matched["Matched By"] = f"Domain Matching ({ma_col} - {hubspot_col})"

#             st.session_state.matched_records = pd.concat([st.session_state.matched_records, matched], ignore_index=True)
#             st.session_state.unmatched_records = st.session_state.unmatched_records[
#                 ~st.session_state.unmatched_records["Extracted Domain"].isin(matched["Extracted Domain"])
#             ]

#             st.success("Domain extraction matching completed!")
#             st.session_state.domain_matching_started = True 
#             st.rerun()

#         if not st.session_state.unmatched_records.empty:
#             if st.session_state.domain_matching_started:
#                 if st.button("Continue Matching"):
#                     st.session_state.domain_match_clicked = False
#                     # hubspot_col = st.selectbox(
#                     #     "Select New HubSpot Column (Domain)", hubspot_data.columns, key="new_hubspot_col"
#                     # )
#                     # ma_col = st.selectbox(
#                     #     "Select New M&A Column (Emails/Domain)", st.session_state.unmatched_records.columns, key="new_ma_col"
#                     # )
#                     st.session_state.domain_matching_started = False 
#                     st.rerun()
#         else:
#             st.warning("No unmatched records left.")


#     elif match_type == "Fuzzy Matching":
#     # Dynamically select columns for fuzzy matching
#         hubspot_col = st.selectbox("Select HubSpot Column for Fuzzy Matching", hubspot_data.columns, key="fuzzy_hubspot_col")
#         ma_col = st.selectbox("Select M&A Column for Fuzzy Matching", st.session_state.unmatched_records.columns, key="fuzzy_ma_col")

#         # Flag to track if fuzzy matching has been initiated
#         if "fuzzy_matching_started" not in st.session_state:
#             st.session_state.fuzzy_matching_started = False

#         if st.button("Fuzzy Match Records"):
#             # Step 1: Exact Match
#             exact_matches = pd.merge(
#                 st.session_state.unmatched_records,
#                 hubspot_data,
#                 left_on=ma_col,
#                 right_on=hubspot_col,
#                 how="inner"
#             )
#             if not exact_matches.empty:
#                 exact_matches["Matched By"] = f"Exact Match ({ma_col} - {hubspot_col})"
#                 exact_matches["Match Ratio"] = 100  # Exact match is always 100%
#                 st.session_state.matched_records = pd.concat(
#                     [st.session_state.matched_records, exact_matches], ignore_index=True
#                 )
#                 # Remove exact matches from unmatched records
#                 st.session_state.unmatched_records = st.session_state.unmatched_records[
#                     ~st.session_state.unmatched_records[ma_col].isin(exact_matches[ma_col])
#                 ]

#             # Step 2: Preprocess M&A Column
#             st.session_state.unmatched_records["Cleaned Selected Column"] = st.session_state.unmatched_records[ma_col].apply(preprocess_company_name)

#             # Step 3: Fuzzy Matching
#             matched_rows = []
#             for _, row in st.session_state.unmatched_records.iterrows():
#                 ma_value = row["Cleaned Selected Column"]  # Use the cleaned version for matching
#                 best_match = process.extractOne(ma_value, hubspot_data[hubspot_col], scorer=fuzz.ratio)  # Use original HubSpot column
#                 if best_match and best_match[1] >= 87:  # Match ratio threshold
#                     matched_hubspot = hubspot_data[hubspot_data[hubspot_col] == best_match[0]].iloc[0]
#                     matched_row = pd.concat([row, matched_hubspot], axis=0).to_frame().T  # Combine rows
#                     matched_row["Matched By"] = f"Fuzzy Matching ({ma_col} - {hubspot_col})"
#                     matched_row["Match Ratio"] = best_match[1]  # Add match ratio to the record
#                     matched_rows.append(matched_row)

#             if matched_rows:
#                 fuzzy_matched = pd.concat(matched_rows, ignore_index=True)
#                 st.session_state.matched_records = pd.concat(
#                     [st.session_state.matched_records, fuzzy_matched], ignore_index=True
#                 )
#                 st.session_state.unmatched_records = st.session_state.unmatched_records[
#                     ~st.session_state.unmatched_records["Cleaned Selected Column"].isin(fuzzy_matched["Cleaned Selected Column"])
#                 ]
#                 st.success("Fuzzy matching completed!")
#                 st.session_state.fuzzy_matching_started = True
#             else:
#                 st.warning("No fuzzy matches found.")

#         # Show "Continue Matching" button only after fuzzy matching is initiated
#         if not st.session_state.unmatched_records.empty:
#             if st.session_state.fuzzy_matching_started:
#                 if st.button("Continue Matching"):
#                     # # Allow the user to select new columns and repeat the process
#                     # hubspot_col = st.selectbox("Select New HubSpot Column for Fuzzy Matching", hubspot_data.columns, key="new_fuzzy_hubspot_col")
#                     # ma_col = st.selectbox("Select New M&A Column for Fuzzy Matching", st.session_state.unmatched_records.columns, key="new_fuzzy_ma_col")
#                     st.session_state.fuzzy_matching_started = False

#         else:
#             st.warning("No unmatched records left.")

#     # Display matched and unmatched records
#     st.subheader("Matched Records")
#     st.dataframe(st.session_state.matched_records)
#     st.subheader("Unmatched Records")
#     st.dataframe(st.session_state.unmatched_records)
# else:
#     st.info("Please upload both HubSpot Companies and M&A Companies Excel files to proceed.")

import streamlit as st
import pandas as pd
from rapidfuzz import fuzz, process
import re


# Utility function to load freemail domains
def load_freemail_domains(file_path):
    return set(pd.read_csv(file_path, header=None)[0].str.strip().tolist())


# Utility function to extract domains
def extract_domain(email_list, freemail_domains):
    if not email_list:
        return None
    domains = [email.split("@")[-1] for email in email_list.split(";") if "@" in email]
    non_freemail = [domain for domain in domains if domain not in freemail_domains]
    if non_freemail:
        return max(non_freemail, key=non_freemail.count)  # Most common non-freemail domain
    return None


# Preprocessing function for company names
def preprocess_company_name(company_name):
    company_name = str(company_name)
    # Remove parentheses and their content
    company_name = re.sub(r"\(.*?\)", "", company_name).strip()
    # Remove suffixes (multiple occurrences handled)
    while True:
        updated_name = re.sub(
            r"(,?\s?-?\s?)(Inc\.|\.Inc|LLC|Corp\.|Ltd\.|CO\.|RCA|DMD|LTD|LLP|LP|Inc|GMBH|Private Wealth|SW|PSP|PSC|CPA|PLLC|BA|WM|DDS|401 Plan|401\(k\)|401|L\.L\.C|L\.P|P\.C\.|Employee Stock Ownership Plan|PC|PSC|CPAs|PA|Corp)(\s|,|-|$)",
            "",
            company_name,
            flags=re.IGNORECASE,
        ).strip()
        if updated_name == company_name:  # Stop if no more changes
            break
        company_name = updated_name
    # Normalize spaces: convert multiple spaces into a single space
    company_name = re.sub(r"\s{2,}", " ", company_name).strip()
    return company_name


# Streamlit app starts here
st.title("HubSpot Company Match")

st.markdown("---")

# Sidebar for file uploads
hubspot_file = st.sidebar.file_uploader("Upload HubSpot Companies Excel File", type=["xls", "xlsx"], key="hubspot")
ma_file = st.sidebar.file_uploader("Upload M&A Companies Excel File", type=["xls", "xlsx"], key="ma")
freemail_file = "freemail_domains.csv"  # Update with your repository path

# Load freemail domains
freemail_domains = load_freemail_domains(freemail_file)

# Session state initialization
if "matched_records" not in st.session_state:
    st.session_state.matched_records = pd.DataFrame()
if "unmatched_records" not in st.session_state:
    st.session_state.unmatched_records = pd.DataFrame()
if "hubspot_data" not in st.session_state:
    st.session_state.hubspot_data = pd.DataFrame()
    

# Handle new HubSpot file upload
# if hubspot_file:
#     hubspot_data = pd.read_excel(hubspot_file)
    
#     # First-time upload or detect new file
#     if st.session_state.hubspot_data.empty:
#         st.session_state.hubspot_data = hubspot_data
#         print("first upload")
#     else:
#         # Check if it's a new file by comparing with existing data
#         if not hubspot_data.equals(st.session_state.hubspot_data):
#             st.warning("New HubSpot file detected! Resetting unmatched records.")
    
#             # Update HubSpot data with the new file
#             st.session_state.hubspot_data = hubspot_data
            
#             # Append unmatched records back into session state
#             # st.session_state.unmatched_records = pd.concat([unmatched_records, st.session_state.matched_records], ignore_index=True)

# # Load M&A data
# if ma_file:
#     ma_data = pd.read_excel(ma_file)
#     if st.session_state.unmatched_records.empty:
#         st.session_state.unmatched_records = ma_data.copy()

# Load HubSpot data
if hubspot_file:
    hubspot_data = pd.read_excel(hubspot_file)

    # Convert all columns to string type
    hubspot_data = hubspot_data.applymap(lambda x: str(x) if pd.notna(x) else x)

    # First-time upload or detect new file
    if st.session_state.hubspot_data.empty:
        st.session_state.hubspot_data = hubspot_data
        print("first upload")
    else:
        # Check if it's a new file by comparing with existing data
        if not hubspot_data.equals(st.session_state.hubspot_data):
            st.warning("New HubSpot file detected! Resetting unmatched records.")

            # Update HubSpot data with the new file
            st.session_state.hubspot_data = hubspot_data

# Load M&A data
if ma_file:
    ma_data = pd.read_excel(ma_file)

    # Convert all columns to string type
    ma_data = ma_data.applymap(lambda x: str(x) if pd.notna(x) else x)

    if st.session_state.unmatched_records.empty:
        st.session_state.unmatched_records = ma_data.copy()


if not st.session_state.unmatched_records.empty and not st.session_state.hubspot_data.empty:
    matching_type_col ,column_selection = st.columns(2)
    # Matching options
    with matching_type_col:
        match_type = st.radio("Select Matching Type", ["Column Matching", "Domain Extraction Matching", "Fuzzy Matching"])

    st.markdown("---")

    if match_type == "Column Matching":
            
        with column_selection:
            hubspot_col = st.selectbox("Select HubSpot Column for Matching", hubspot_data.columns)
            ma_col = st.selectbox("Select M&A Column for Matching", st.session_state.unmatched_records.columns)

        if "matching_started" not in st.session_state:
            st.session_state.matching_started = False
        
        if "column_match_clicked" not in st.session_state:
            st.session_state.column_match_clicked = False

        match_col, space_col, continue_col = st.columns([4,9,4])
        
        with match_col:
            if st.button("Match Records", disabled=st.session_state.column_match_clicked):
                st.session_state.column_match_clicked = True

                st.session_state.unmatched_records[ma_col] = st.session_state.unmatched_records[ma_col].astype(str)
                hubspot_data[hubspot_col] = hubspot_data[hubspot_col].astype(str)

                matched = pd.merge(
                    st.session_state.unmatched_records, hubspot_data, left_on=ma_col, right_on=hubspot_col, how="inner"
                )
                matched["Matched By"] = f"Column Matching ({ma_col} - {hubspot_col})"

                st.session_state.matched_records = pd.concat([st.session_state.matched_records, matched], ignore_index=True)
                st.session_state.unmatched_records = st.session_state.unmatched_records[
                    ~st.session_state.unmatched_records[ma_col].isin(matched[ma_col])
                ]

                # st.success("Column matching completed!")
                st.session_state.matching_started = True 
                # st.rerun() 

        with space_col:
            st.markdown(" ")

        with continue_col:
            if not st.session_state.unmatched_records.empty:
                if st.session_state.matching_started:
                    if st.button("Continue Matching"):
                        st.session_state.column_match_clicked = False
                        # hubspot_col = st.selectbox(
                        #     "Select New HubSpot Column for Matching", hubspot_data.columns, key="new_hubspot_col"
                        # )
                        # ma_col = st.selectbox(
                        #     "Select New M&A Column for Matching", st.session_state.unmatched_records.columns, key="new_ma_col"
                        # )
                        st.session_state.matching_started = False
                        # st.rerun()
            else:
                st.warning("No unmatched records left.")
        
        st.markdown("---")

    elif match_type == "Domain Extraction Matching":
        with column_selection:
            hubspot_col = st.selectbox("Select HubSpot Column (Domain)", hubspot_data.columns)
            ma_col = st.selectbox("Select M&A Column (Emails/Domain)", st.session_state.unmatched_records.columns)

        if "domain_matching_started" not in st.session_state:
            st.session_state.domain_matching_started = False

        if "domain_match_clicked" not in st.session_state:
            st.session_state.domain_match_clicked = False

        match_col, space_col, continue_col = st.columns([7,9,5])

        with match_col:
            if st.button("Extract Domains and Match", disabled=st.session_state.domain_match_clicked):
                st.session_state.domain_match_clicked = True
                st.session_state.unmatched_records[ma_col] = st.session_state.unmatched_records[ma_col].fillna("")
                st.session_state.unmatched_records["Extracted Domain"] = st.session_state.unmatched_records[ma_col].apply(
                    lambda x: extract_domain(x, freemail_domains)
                )

                matched = pd.merge(
                    st.session_state.unmatched_records, hubspot_data, left_on="Extracted Domain", right_on=hubspot_col, how="inner"
                )
                matched["Matched By"] = f"Domain Matching ({ma_col} - {hubspot_col})"

                st.session_state.matched_records = pd.concat([st.session_state.matched_records, matched], ignore_index=True)
                st.session_state.unmatched_records = st.session_state.unmatched_records[
                    ~st.session_state.unmatched_records["Extracted Domain"].isin(matched["Extracted Domain"])
                ]

                st.session_state.unmatched_records = st.session_state.unmatched_records.drop(columns=["Extracted Domain"])
                st.session_state.domain_matching_started = True 

        with space_col:
            st.markdown(" ")

        with continue_col:
            if not st.session_state.unmatched_records.empty:
                if st.session_state.domain_matching_started:
                    if st.button("Continue Matching"):
                        st.session_state.domain_match_clicked = False
                        # hubspot_col = st.selectbox(
                        #     "Select New HubSpot Column (Domain)", hubspot_data.columns, key="new_hubspot_col"
                        # )
                        # ma_col = st.selectbox(
                        #     "Select New M&A Column (Emails/Domain)", st.session_state.unmatched_records.columns, key="new_ma_col"
                        # )
                        st.session_state.domain_matching_started = False 
                        # st.rerun()
            else:
                st.warning("No unmatched records left.")

        st.markdown("---")

    elif match_type == "Fuzzy Matching":
    # Dynamically select columns for fuzzy matching
        with column_selection:
            hubspot_col = st.selectbox("Select HubSpot Column for Fuzzy Matching", hubspot_data.columns, key="fuzzy_hubspot_col")
            ma_col = st.selectbox("Select M&A Column for Fuzzy Matching", st.session_state.unmatched_records.columns, key="fuzzy_ma_col")

        # Flag to track if fuzzy matching has been initiated
        if "fuzzy_matching_started" not in st.session_state:
            st.session_state.fuzzy_matching_started = False

        if "fuzzy_match_clicked" not in st.session_state:
            st.session_state.fuzzy_match_clicked = False

        match_col, space_col, continue_col = st.columns([7,9,5])

        with match_col:
            if st.button("Fuzzy Match Records", disabled=st.session_state.fuzzy_match_clicked):
                st.session_state.fuzzy_match_clicked = True
                # Step 1: Exact Match
                exact_matches = pd.merge(
                    st.session_state.unmatched_records,
                    hubspot_data,
                    left_on=ma_col,
                    right_on=hubspot_col,
                    how="inner"
                )
                if not exact_matches.empty:
                    exact_matches["Matched By"] = f"Exact Match ({ma_col} - {hubspot_col})"
                    exact_matches["Match Ratio"] = 100  # Exact match is always 100%
                    st.session_state.matched_records = pd.concat(
                        [st.session_state.matched_records, exact_matches], ignore_index=True
                    )
                    # Remove exact matches from unmatched records
                    st.session_state.unmatched_records = st.session_state.unmatched_records[
                        ~st.session_state.unmatched_records[ma_col].isin(exact_matches[ma_col])
                    ]

                # Step 2: Preprocess M&A Column
                st.session_state.unmatched_records["Cleaned Selected Column"] = st.session_state.unmatched_records[ma_col].apply(preprocess_company_name)

                # Step 3: Fuzzy Matching
                matched_rows = []
                for _, row in st.session_state.unmatched_records.iterrows():
                    ma_value = row["Cleaned Selected Column"]  # Use the cleaned version for matching
                    best_match = process.extractOne(ma_value, hubspot_data[hubspot_col], scorer=fuzz.ratio)  # Use original HubSpot column
                    if best_match and best_match[1] >= 87:  # Match ratio threshold
                        matched_hubspot = hubspot_data[hubspot_data[hubspot_col] == best_match[0]].iloc[0]
                        matched_row = pd.concat([row, matched_hubspot], axis=0).to_frame().T  # Combine rows
                        matched_row["Matched By"] = f"Fuzzy Matching ({ma_col} - {hubspot_col})"
                        matched_row["Match Ratio"] = best_match[1]  # Add match ratio to the record
                        matched_rows.append(matched_row)

                if matched_rows:
                    fuzzy_matched = pd.concat(matched_rows, ignore_index=True)
                    st.session_state.matched_records = pd.concat(
                        [st.session_state.matched_records, fuzzy_matched], ignore_index=True
                    )
                    st.session_state.unmatched_records = st.session_state.unmatched_records[
                        ~st.session_state.unmatched_records["Cleaned Selected Column"].isin(fuzzy_matched["Cleaned Selected Column"])
                    ]
                    st.session_state.fuzzy_matching_started = True
                else:
                    st.warning("No fuzzy matches found.")
                    st.session_state.fuzzy_matching_started = True

                st.session_state.unmatched_records = st.session_state.unmatched_records.drop(columns=["Cleaned Selected Column"])

        with space_col:
            st.markdown(" ")

        with continue_col:
        # Show "Continue Matching" button only after fuzzy matching is initiated
            if not st.session_state.unmatched_records.empty:
                if st.session_state.fuzzy_matching_started:
                    if st.button("Continue Matching"):
                        st.session_state.fuzzy_match_clicked = False
                        # # Allow the user to select new columns and repeat the process
                        # hubspot_col = st.selectbox("Select New HubSpot Column for Fuzzy Matching", hubspot_data.columns, key="new_fuzzy_hubspot_col")
                        # ma_col = st.selectbox("Select New M&A Column for Fuzzy Matching", st.session_state.unmatched_records.columns, key="new_fuzzy_ma_col")
                        st.session_state.fuzzy_matching_started = False

            else:
                st.warning("No unmatched records left.")

        st.markdown("---")
    # Display matched and unmatched records

    if st.session_state.matching_started == True and st.session_state.column_match_clicked == True:
        st.success("Column matching completed!")
        st.session_state.matching_started = False
        st.session_state.column_match_clicked = False
    
    if st.session_state.domain_matching_started == True and st.session_state.domain_match_clicked == True:
        st.success("Domain matching completed!")
        st.session_state.domain_matching_started = False
        st.session_state.domain_match_clicked = False

    if st.session_state.fuzzy_matching_started == True and st.session_state.fuzzy_match_clicked == True:
        st.success("Fuzzy matching completed!")
        st.session_state.fuzzy_matching_started = False
        st.session_state.fuzzy_match_clicked = False
    
    st.subheader("Matched Records")
    st.dataframe(st.session_state.matched_records)
    st.subheader("Unmatched Records")
    if not st.session_state.unmatched_records.empty:
        st.dataframe(st.session_state.unmatched_records)
    else:
        st.success("Matched All Records")
        
else:
    st.info("Please upload both HubSpot Companies and M&A Companies Excel files to proceed.")



