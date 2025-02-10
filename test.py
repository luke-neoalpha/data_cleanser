# import streamlit as st
# import pandas as pd
# from rapidfuzz import fuzz, process
# import re
# from io import BytesIO

# # Utility function to load freemail domains
# def load_freemail_domains(file_path):
#     return set(pd.read_csv(file_path, header=None)[0].str.strip().tolist())

# # Utility function to extract domains
# def extract_domain(email_list, freemail_domains):
#     if not email_list:
#         return None
    
#     # Extract domains and convert to lowercase
#     domains = [email.split("@")[-1].lower() for email in email_list.split(";") if "@" in email]
    
#     # Filter out freemail domains and invalid/empty domains
#     non_freemail = [domain for domain in domains if domain and domain not in freemail_domains]
    
#     # Return the most common non-freemail domain (if any)
#     if non_freemail:
#         return max(non_freemail, key=non_freemail.count)
    
#     return None  # No valid domain found

# def preprocess_company_name(company_name):
#     company_name = str(company_name).strip()
    
#     # Lowercase for case-insensitive comparison
#     original_name = company_name.lower()

#     # Remove parentheses and their content
#     cleaned_name = re.sub(r"\(.*?\)", "", original_name).strip()
    
#     suffixes = r"(,?\s?-?\s?)\b(Inc\.?|LLC|Corp\.?|Ltd\.?|\bCo\.?\b|\bBA\b|RCA|DMD|LTD|LLP|LP|GMBH|Private Wealth|SW|PSP|PSC|CPA|PLLC|WM|DDS|401 Plan|401\(k\)|401|L\.L\.C|L\.P|P\.C\.|Employee Stock Ownership Plan|PC|PSC|CPAs|PA|Corp)\b(\s|,|-|$)"

#     while True:
#         updated_name = re.sub(suffixes, "", cleaned_name, flags=re.IGNORECASE).strip()
#         if updated_name == cleaned_name:
#             break
#         cleaned_name = updated_name

#     cleaned_name = re.sub(r"[,\s-]+$", "", cleaned_name)
    
#     # Normalize spaces
#     cleaned_name = re.sub(r"\s{2,}", " ", cleaned_name).strip()
    
#     return original_name, cleaned_name  # Return both original and cleaned names

# # Initialize session state for tracking reviewed matches
# if "review_index" not in st.session_state:
#     st.session_state.review_index = 0  # Tracks the current match being reviewed

# if "matches_to_review" not in st.session_state:
#     st.session_state.matches_to_review = pd.DataFrame()  # Stores matches with ratio < 100

# if "current_page" not in st.session_state:
#     st.session_state.current_page = "main"

# if "matched_records" not in st.session_state:
#     st.session_state.matched_records = pd.DataFrame()

# if "unmatched_records" not in st.session_state:
#     st.session_state.unmatched_records = pd.DataFrame()

# if "hubspot_data" not in st.session_state:
#     st.session_state.hubspot_data = pd.DataFrame()

# def main_page():
#     # Streamlit app starts here
#     st.title("HubSpot Company Match")

#     st.markdown("---")

#     # Sidebar for file uploads
#     hubspot_file = st.sidebar.file_uploader("Upload HubSpot Companies Excel File", type=["xls", "xlsx"], key="hubspot")
#     ma_file = st.sidebar.file_uploader("Upload M&A Companies Excel File", type=["xls", "xlsx"], key="ma")
#     freemail_file = "freemail_domains.csv"  # Update with your repository path

#     # Load freemail domains
#     freemail_domains = load_freemail_domains(freemail_file)

#     # Load HubSpot data
#     if hubspot_file:
#         hubspot_data = pd.read_excel(hubspot_file)

#         # Convert all columns to string type
#         hubspot_data = hubspot_data.applymap(lambda x: str(x) if pd.notna(x) else x)

#         # First-time upload or detect new file
#         if st.session_state.hubspot_data.empty:
#             st.session_state.hubspot_data = hubspot_data
#             print("first upload")
#         else:
#             # Check if it's a new file by comparing with existing data
#             if not hubspot_data.equals(st.session_state.hubspot_data):
#                 st.warning("New HubSpot file detected! Resetting unmatched records.")

#                 # Update HubSpot data with the new file
#                 st.session_state.hubspot_data = hubspot_data

#     # Load M&A data
#     if ma_file:
#         ma_data = pd.read_excel(ma_file)

#         # Convert all columns to string type
#         ma_data = ma_data.applymap(lambda x: str(x) if pd.notna(x) else x)

#         if st.session_state.unmatched_records.empty:
#             st.session_state.unmatched_records = ma_data.copy()


#     if not st.session_state.unmatched_records.empty and not st.session_state.hubspot_data.empty:
#         matching_type_col ,column_selection = st.columns(2)
#         # Matching options
#         with matching_type_col:
#             match_type = st.radio("Select Matching Type", ["Column Matching", "Domain Extraction Matching", "Fuzzy Matching"])

#         st.markdown("---")

#         if match_type == "Column Matching":
                
#             with column_selection:
#                 hubspot_col = st.selectbox("Select HubSpot Column for Matching", hubspot_data.columns)
#                 ma_col = st.selectbox("Select M&A Column for Matching", st.session_state.unmatched_records.columns)

#             if "matching_started" not in st.session_state:
#                 st.session_state.matching_started = False
            
#             if "column_match_clicked" not in st.session_state:
#                 st.session_state.column_match_clicked = False

#             match_col, space_col, continue_col = st.columns([4,9,4])
            
#             with match_col:
#                 if st.button("Match Records", disabled=st.session_state.column_match_clicked):
#                     st.session_state.column_match_clicked = True

#                     st.session_state.unmatched_records[ma_col] = st.session_state.unmatched_records[ma_col].astype(str)
#                     hubspot_data[hubspot_col] = hubspot_data[hubspot_col].astype(str)

#                     matched = pd.merge(
#                         st.session_state.unmatched_records, hubspot_data, left_on=ma_col, right_on=hubspot_col, how="inner"
#                     )
#                     matched["Matched By"] = f"Column Matching ({ma_col} - {hubspot_col})"

#                     st.session_state.matched_records = pd.concat([st.session_state.matched_records, matched], ignore_index=True)
#                     st.session_state.unmatched_records = st.session_state.unmatched_records[
#                         ~st.session_state.unmatched_records[ma_col].isin(matched[ma_col])
#                     ]

#                     # st.success("Column matching completed!")
#                     st.session_state.matching_started = True 
#                     # st.rerun() 

#             with space_col:
#                 st.markdown(" ")

#             with continue_col:
#                 if not st.session_state.unmatched_records.empty:
#                     if st.session_state.matching_started:
#                         if st.button("Continue Matching"):
#                             st.session_state.column_match_clicked = False
#                             # hubspot_col = st.selectbox(
#                             #     "Select New HubSpot Column for Matching", hubspot_data.columns, key="new_hubspot_col"
#                             # )
#                             # ma_col = st.selectbox(
#                             #     "Select New M&A Column for Matching", st.session_state.unmatched_records.columns, key="new_ma_col"
#                             # )
#                             st.session_state.matching_started = False
#                             # st.rerun()
#                 else:
#                     st.warning("No unmatched records left.")
            
#             st.markdown("---")

#         elif match_type == "Domain Extraction Matching":
#             with column_selection:
#                 hubspot_col = st.selectbox("Select HubSpot Column (Domain)", hubspot_data.columns)
#                 ma_col = st.selectbox("Select M&A Column (Emails/Domain)", st.session_state.unmatched_records.columns)

#             if "domain_matching_started" not in st.session_state:
#                 st.session_state.domain_matching_started = False

#             if "domain_match_clicked" not in st.session_state:
#                 st.session_state.domain_match_clicked = False

#             match_col, space_col, continue_col = st.columns([7, 9, 5])

#             with match_col:
#                 if st.button("Extract Domains and Match", disabled=st.session_state.domain_match_clicked):
#                     st.session_state.domain_match_clicked = True

#                     # Extract domains from the M&A column and convert to lowercase
#                     st.session_state.unmatched_records[ma_col] = st.session_state.unmatched_records[ma_col].fillna("")
#                     st.session_state.unmatched_records["Extracted Domain"] = st.session_state.unmatched_records[ma_col].apply(
#                         lambda x: extract_domain(x, freemail_domains)
#                     )

#                     # Convert extracted domains to lowercase
#                     st.session_state.unmatched_records["Extracted Domain"] = st.session_state.unmatched_records["Extracted Domain"].str.lower()

#                     # Filter out rows with None or invalid domains
#                     valid_domains = st.session_state.unmatched_records.dropna(subset=["Extracted Domain"])
#                     invalid_domains = st.session_state.unmatched_records[st.session_state.unmatched_records["Extracted Domain"].isna()]

#                     # Convert HubSpot domain column to lowercase for case-insensitive matching
#                     hubspot_data[hubspot_col] = hubspot_data[hubspot_col].str.lower()

#                     # Perform matching only on valid domains
#                     matched = pd.merge(
#                         valid_domains, hubspot_data, left_on="Extracted Domain", right_on=hubspot_col, how="inner"
#                     )
#                     matched["Matched By"] = f"Domain Matching ({ma_col} - {hubspot_col})"

#                     # Update matched_records
#                     st.session_state.matched_records = pd.concat([st.session_state.matched_records, matched], ignore_index=True)

#                     # Remove matched records from unmatched_records using a unique identifier (e.g., email address)
#                     matched_email_addresses = matched[ma_col].tolist()  # Get list of matched email addresses
#                     st.session_state.unmatched_records = st.session_state.unmatched_records[
#                         ~st.session_state.unmatched_records[ma_col].isin(matched_email_addresses)
#                     ]

#                     # Drop the "Extracted Domain" column from unmatched_records
#                     if "Extracted Domain" in st.session_state.unmatched_records.columns:
#                         st.session_state.unmatched_records = st.session_state.unmatched_records.drop(columns=["Extracted Domain"])

#                     st.session_state.domain_matching_started = True

#             with space_col:
#                 st.markdown(" ")

#             with continue_col:
#                 if not st.session_state.unmatched_records.empty:
#                     if st.session_state.domain_matching_started:
#                         if st.button("Continue Matching"):
#                             st.session_state.domain_match_clicked = False
#                             st.session_state.domain_matching_started = False
#                 else:
#                     st.warning("No unmatched records left.")

#             st.markdown("---")

#         elif match_type == "Fuzzy Matching":
#             with column_selection:
#                 hubspot_col = st.selectbox("Select HubSpot Column for Fuzzy Matching", hubspot_data.columns, key="fuzzy_hubspot_col")
#                 ma_col = st.selectbox("Select M&A Column for Fuzzy Matching", st.session_state.unmatched_records.columns, key="fuzzy_ma_col")

#             if "fuzzy_matching_started" not in st.session_state:
#                 st.session_state.fuzzy_matching_started = False

#             if "fuzzy_match_clicked" not in st.session_state:
#                 st.session_state.fuzzy_match_clicked = False

#             match_col, space_col, continue_col = st.columns([7, 9, 5])

#             with match_col:
#                 if st.button("Fuzzy Match Records", disabled=st.session_state.fuzzy_match_clicked):
#                     st.session_state.fuzzy_match_clicked = True

#                     # Normalize text for case-insensitive matching
#                     st.session_state.unmatched_records["Company Name Normalized"] = st.session_state.unmatched_records[ma_col].str.lower()
#                     hubspot_data["Hubspot Company Name Normalized"] = hubspot_data[hubspot_col].str.lower()

#                     # Perform exact matching on normalized columns
#                     exact_matches = pd.merge(
#                         st.session_state.unmatched_records,
#                         hubspot_data,
#                         left_on="Company Name Normalized",
#                         right_on="Hubspot Company Name Normalized",
#                         how="inner"
#                     )

#                     # Drop the normalized columns if not needed
#                     exact_matches = exact_matches.drop(columns=["Company Name Normalized", "Hubspot Company Name Normalized"])

#                     # Add match metadata
#                     if not exact_matches.empty:
#                         exact_matches["Matched By"] = f"Exact Match ({ma_col} - {hubspot_col})"
#                         exact_matches["Match Ratio"] = 100  # Exact match is always 100%
#                         st.session_state.matched_records = pd.concat(
#                             [st.session_state.matched_records, exact_matches], ignore_index=True
#                         )
#                         st.session_state.unmatched_records = st.session_state.unmatched_records[
#                             ~st.session_state.unmatched_records[ma_col].str.lower().isin(exact_matches[ma_col].str.lower())
#                         ]

#                     # Step 2: Preprocess M&A Column
#                     unmatched = st.session_state.unmatched_records.copy()
#                     unmatched[["Original Name", "Cleaned Name"]] = unmatched[ma_col].apply(lambda x: pd.Series(preprocess_company_name(x)))

#                     # Step 3: Fuzzy Matching
#                     matched_rows = []
#                     matched_ma_values = set()  # Keep track of matched M&A values

#                     for _, row in unmatched.iterrows():
#                         ma_value_orig = row["Original Name"]
#                         ma_value_clean = row["Cleaned Name"]

#                         # Perform fuzzy matching on both original and cleaned names
#                         best_match_orig = process.extractOne(ma_value_orig, hubspot_data[hubspot_col].str.lower(), scorer=fuzz.ratio)
#                         best_match_clean = process.extractOne(ma_value_clean, hubspot_data[hubspot_col].str.lower(), scorer=fuzz.ratio)

#                         # Choose the better match
#                         if best_match_orig and best_match_clean:
#                             if best_match_orig[1] >= best_match_clean[1]:
#                                 best_match = best_match_orig
#                                 matched_by = f"Fuzzy Matching (Original) ({ma_col} - {hubspot_col})"
#                                 fuzzy_match_value = ma_value_orig  # Use the original name as the fuzzy match value
#                             else:
#                                 best_match = best_match_clean
#                                 matched_by = f"Fuzzy Matching (Cleaned) ({ma_col} - {hubspot_col})"
#                                 fuzzy_match_value = ma_value_clean  # Use the cleaned name as the fuzzy match value
#                         else:
#                             best_match = best_match_orig or best_match_clean  # Pick non-null match
#                             if best_match == best_match_orig:
#                                 matched_by = f"Fuzzy Matching (Original) ({ma_col} - {hubspot_col})"
#                                 fuzzy_match_value = ma_value_orig  # Use the original name as the fuzzy match value
#                             else:
#                                 matched_by = f"Fuzzy Matching (Cleaned) ({ma_col} - {hubspot_col})"
#                                 fuzzy_match_value = ma_value_clean  # Use the cleaned name as the fuzzy match value

#                         # If the best match meets the threshold, add it to the matched rows
#                         if best_match and best_match[1] >= 80:  # Match ratio threshold
#                             matched_hubspot = hubspot_data[hubspot_col].str.lower() == best_match[0]
#                             matched_row = pd.concat([row, hubspot_data[matched_hubspot].iloc[0]], axis=0).to_frame().T
#                             matched_row["Matched By"] = matched_by  # Set the "Matched By" value
#                             matched_row["Fuzzy Match Value"] = fuzzy_match_value  # Add the fuzzy match value
#                             matched_row["Match Ratio"] = best_match[1]
#                             matched_rows.append(matched_row)
#                             matched_ma_values.add(ma_value_orig)  # Track matched values

#                     # If there are matched rows, update the session state
#                     if matched_rows:
#                         fuzzy_matched = pd.concat(matched_rows, ignore_index=True)

#                         # Drop unnecessary columns
#                         columns_to_drop = ["Original Name", "Cleaned Name", "Company Name Normalized", "Hubspot Company Name Normalized"]
#                         fuzzy_matched = fuzzy_matched.drop(columns=[col for col in columns_to_drop if col in fuzzy_matched.columns])

#                         st.session_state.matched_records = pd.concat(
#                             [st.session_state.matched_records, fuzzy_matched], ignore_index=True
#                         )

#                         # Ensure unmatched records get updated properly
#                         st.session_state.unmatched_records = st.session_state.unmatched_records[
#                             ~st.session_state.unmatched_records[ma_col].str.lower().str.strip().isin(
#                                 {val.lower().strip() for val in matched_ma_values}
#                             )
#                         ]

#                         # Drop "Company Name Normalized" from unmatched records
#                         if "Company Name Normalized" in st.session_state.unmatched_records.columns:
#                             st.session_state.unmatched_records = st.session_state.unmatched_records.drop(columns=["Company Name Normalized"])

#                         st.session_state.fuzzy_matching_started = True
#                     else:
#                         st.warning("No fuzzy matches found.")
#                         st.session_state.fuzzy_matching_started = True

#             with space_col:
#                 st.markdown(" ")

#             with continue_col:
#             # Show "Continue Matching" button only after fuzzy matching is initiated
#                 if not st.session_state.unmatched_records.empty:
#                     if st.session_state.fuzzy_matching_started:
#                         if st.button("Continue Matching"):
#                             st.session_state.fuzzy_match_clicked = False
#                             st.session_state.fuzzy_matching_started = False
#                 else:
#                     st.warning("No unmatched records left.")
#             st.markdown("---")

#         # Display matched and unmatched records

#         # if st.session_state.matching_started == True and st.session_state.column_match_clicked == True:
#         #     st.success("Column matching completed!")
#         #     st.session_state.matching_started = False
#         #     st.session_state.column_match_clicked = False
        
#         # if st.session_state.domain_matching_started == True and st.session_state.domain_match_clicked == True:
#         #     st.success("Domain matching completed!")
#         #     st.session_state.domain_matching_started = False
#         #     st.session_state.domain_match_clicked = False

#         # if st.session_state.fuzzy_matching_started == True and st.session_state.fuzzy_match_clicked == True:
#         #     st.success("Fuzzy matching completed!")
#         #     st.session_state.fuzzy_matching_started = False
#         #     st.session_state.fuzzy_match_clicked = False
        
#         st.subheader("Matched Records")
#         st.dataframe(st.session_state.matched_records)
#         st.write(f"Total Matched Records: {len(st.session_state.matched_records)}")
#         st.subheader("Unmatched Records")
#         if not st.session_state.unmatched_records.empty:
#             st.dataframe(st.session_state.unmatched_records)
#             st.write(f"Total Unmatched Records: {len(st.session_state.unmatched_records)}")
#         else:
#             st.success("Matched All Records") 

#         # Ensure matched_records exists and contains data before filtering
#         if "matched_records" in st.session_state and not st.session_state.matched_records.empty:
#             if "Match Ratio" in st.session_state.matched_records.columns:
#                 fuzzy_matches_exist = not st.session_state.matched_records[
#                     st.session_state.matched_records["Match Ratio"] < 100
#                 ].empty
#             else:
#                 fuzzy_matches_exist = False  # No match ratio yet
#         else:
#             fuzzy_matches_exist = False  # No matched records yet

#         # Show "Review Fuzzy Matches" button if there are fuzzy matches
#         if fuzzy_matches_exist:
#             if st.button("Review Fuzzy Matches"):
#                 # Filter matches with ratio < 100
#                 st.session_state.matches_to_review = st.session_state.matched_records[
#                     st.session_state.matched_records["Match Ratio"] < 100
#                 ].copy()

#                 if not st.session_state.matches_to_review.empty:
#                     st.session_state.current_page = "review"  # Switch to the review page
#                     st.session_state.review_index = 0  # Start from the first match
#                 else:
#                     st.success("No fuzzy matches to review!")

#         elif not st.session_state.matched_records.empty:
#             # Show "Combine Matched and Unmatched Records" button if there are no fuzzy matches
#             if st.button("Combine Matched and Unmatched Records"):
#                 combined_records = pd.concat(
#                     [st.session_state.matched_records, st.session_state.unmatched_records],
#                     ignore_index=True
#                 )

#                 # Create an Excel file in memory
#                 output = BytesIO()
#                 with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#                     combined_records.to_excel(writer, index=False, sheet_name="Combined Records")
#                 output.seek(0)

#                 # Download the Excel file
#                 st.download_button(
#                     label="Download Combined Records as Excel",
#                     data=output,
#                     file_name="combined_records.xlsx",
#                     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#                 )
#                 st.success("Matched and unmatched records have been combined!") 

#     else:
#         st.info("Please upload both HubSpot Companies and M&A Companies Excel files to proceed.")


# def review_page():
#     st.title("Review Fuzzy Matches")
#     st.markdown("---")

#     # Check if there are matches to review
#     if not st.session_state.matches_to_review.empty:
#         # Get the current match to review
#         current_match = st.session_state.matches_to_review.iloc[st.session_state.review_index]

#         # Extract M&A and HubSpot column names from the "Matched By" value
#         matched_by = current_match["Matched By"]
        
#         # Improved parsing logic
#         try:
#             # Extract the part inside the last set of parentheses
#             columns_part = matched_by.split("(")[-1].rstrip(")")
#             # Split into M&A and HubSpot columns
#             ma_col, hubspot_col = columns_part.split(" - ")
#         except (IndexError, ValueError):
#             st.error(f"Unable to parse column names from 'Matched By' value: {matched_by}")
#             return

#         # Display match details
#         st.write(f"**Match Ratio:** {current_match['Match Ratio']}")
#         st.write(f"**M&A Column ({ma_col}):** {current_match[ma_col]}")
#         st.write(f"**HubSpot Column ({hubspot_col}):** {current_match[hubspot_col]}")

#         # Buttons for manual review
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("Yes (Keep Match)"):
#                 # Keep the match in matched_records
#                 st.session_state.review_index += 1  # Move to the next match
#                 if st.session_state.review_index >= len(st.session_state.matches_to_review):
#                     st.session_state.review_index = 0  # Reset if all matches are reviewed
#                     st.session_state.matches_to_review = pd.DataFrame()  # Clear reviewed matches
#                 st.success("Match kept in matched records.")

#         with col2:
#             if st.button("No (Move to Unmatched)"):
#                 # Move the match back to unmatched_records
#                 match_to_move = st.session_state.matches_to_review.iloc[st.session_state.review_index:st.session_state.review_index + 1]
#                 st.session_state.unmatched_records = pd.concat(
#                     [st.session_state.unmatched_records, match_to_move.drop(columns=["Matched By", "Match Ratio"])],
#                     ignore_index=True
#                 )

#                 # Remove the match from matched_records and matches_to_review
#                 st.session_state.matched_records = st.session_state.matched_records[
#                     ~st.session_state.matched_records.index.isin(match_to_move.index)
#                 ]
#                 st.session_state.matches_to_review = st.session_state.matches_to_review[
#                     ~st.session_state.matches_to_review.index.isin(match_to_move.index)
#                 ]

#                 st.session_state.review_index = min(st.session_state.review_index, len(st.session_state.matches_to_review) - 1)
#                 st.warning("Match moved back to unmatched records.")

#         # Show progress
#         st.write(f"Reviewing {st.session_state.review_index + 1} of {len(st.session_state.matches_to_review)} matches.")
#     else:
#         st.success("All fuzzy matches have been reviewed!")
#         combined_records = pd.concat(
#                     [st.session_state.matched_records, st.session_state.unmatched_records],
#                     ignore_index=True
#                 )

#                 # Create an Excel file in memory
#         output = BytesIO()
#         with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#             combined_records.to_excel(writer, index=False, sheet_name="Combined Records")
#         output.seek(0)

#             # Download the Excel file
#         st.download_button(
#             label="Download Combined Records as Excel",
#             data=output,
#             file_name="combined_records.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )
#         st.success("Matching Successful") 

# # Main app logic
# if st.session_state.current_page == "main":
#     main_page()
# elif st.session_state.current_page == "review":
#     review_page()

    # if ma_file:
    #     ma_data = pd.read_excel(ma_file)

    #     # Convert all columns to string type
    #     ma_data = ma_data.applymap(lambda x: str(x) if pd.notna(x) else x)

    #     # Check if unmatched_records have already been loaded to avoid repopulating it on subsequent clicks
    #     if 'unmatched_records_loaded' not in st.session_state or not st.session_state.unmatched_records_loaded:
    #         if st.session_state.unmatched_records.empty:
    #             print("reloaded m&a")
    #             st.session_state.unmatched_records = ma_data.copy()
    #             st.session_state.unmatched_records_loaded = True  # Set flag to True to prevent reloading


import streamlit as st
import pandas as pd
from rapidfuzz import fuzz, process
import re
from io import BytesIO

# Utility function to load freemail domains
def load_freemail_domains(file_path):
    return set(pd.read_csv(file_path, header=None)[0].str.strip().tolist())

# Utility function to extract domains
def extract_domain(email_list, freemail_domains):
    if not email_list:
        return None
    
    # Extract domains and convert to lowercase
    domains = [email.split("@")[-1].lower() for email in email_list.split(";") if "@" in email]
    
    # Filter out freemail domains and invalid/empty domains
    non_freemail = [domain for domain in domains if domain and domain not in freemail_domains]
    
    # Return the most common non-freemail domain (if any)
    if non_freemail:
        return max(non_freemail, key=non_freemail.count)
    
    return None  # No valid domain found

def preprocess_company_name(company_name):
    company_name = str(company_name).strip()
    
    # Lowercase for case-insensitive comparison
    original_name = company_name.lower()

    # Remove parentheses and their content
    cleaned_name = re.sub(r"\(.*?\)", "", original_name).strip()
    
    suffixes = r"(,?\s?-?\s?)\b(Inc\.?|LLC|Corp\.?|Ltd\.?|\bCo\.?\b|\bBA\b|RCA|DMD|LTD|LLP|LP|GMBH|Private Wealth|SW|PSP|PSC|CPA|PLLC|WM|DDS|401 Plan|401\(k\)|401|L\.L\.C|L\.P|P\.C\.|Employee Stock Ownership Plan|PC|PSC|CPAs|PA|Corp)\b(\s|,|-|$)"

    while True:
        updated_name = re.sub(suffixes, "", cleaned_name, flags=re.IGNORECASE).strip()
        if updated_name == cleaned_name:
            break
        cleaned_name = updated_name

    cleaned_name = re.sub(r"[,\s-]+$", "", cleaned_name)
    
    # Normalize spaces
    cleaned_name = re.sub(r"\s{2,}", " ", cleaned_name).strip()
    
    return original_name, cleaned_name  # Return both original and cleaned names

if "current_page" not in st.session_state:
    st.session_state.current_page = "main"

if "matched_records" not in st.session_state:
    st.session_state.matched_records = pd.DataFrame()

if "unmatched_records" not in st.session_state:
    st.session_state.unmatched_records = pd.DataFrame()

if "hubspot_data" not in st.session_state:
    st.session_state.hubspot_data = pd.DataFrame()

def main_page():
    # Streamlit app starts here
    st.title("HubSpot Company Match")

    st.markdown("---")

    # Sidebar for file uploads
    hubspot_file = st.sidebar.file_uploader("Upload HubSpot Companies Excel File", type=["xls", "xlsx"], key="hubspot")
    ma_file = st.sidebar.file_uploader("Upload M&A Companies Excel File", type=["xls", "xlsx"], key="ma")
    freemail_file = "freemail_domains.csv"  # Update with your repository path

    # Load freemail domains
    freemail_domains = load_freemail_domains(freemail_file)

    # Load HubSpot data
    if hubspot_file:
        hubspot_data = pd.read_excel(hubspot_file)

        # Convert all columns to string type
        hubspot_data = hubspot_data.map(lambda x: str(x) if pd.notna(x) else x)

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
        ma_data = ma_data.map(lambda x: str(x) if pd.notna(x) else x)

        # Only populate unmatched_records if it's empty
        # if st.session_state.unmatched_records.empty:
        #     st.session_state.unmatched_records = ma_data.copy()

        if st.session_state.unmatched_records.empty and "ma_file_uploaded" not in st.session_state:
            st.session_state.unmatched_records = ma_data.copy()
            st.session_state.ma_file_uploaded = True

    if not st.session_state.unmatched_records.empty and not st.session_state.hubspot_data.empty:
        matching_type_col, column_selection = st.columns(2)
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

            match_col, space_col, continue_col = st.columns([4, 9, 4])
            
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

                    st.session_state.matching_started = True 

            with space_col:
                st.markdown(" ")

            with continue_col:
                if not st.session_state.unmatched_records.empty:
                    if st.session_state.matching_started:
                        if st.button("Continue Matching"):
                            st.session_state.column_match_clicked = False
                            st.session_state.matching_started = False
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

            match_col, space_col, continue_col = st.columns([7, 9, 5])

            with match_col:
                if st.button("Extract Domains and Match", disabled=st.session_state.domain_match_clicked):
                    st.session_state.domain_match_clicked = True

                    # Extract domains from the M&A column and convert to lowercase
                    st.session_state.unmatched_records[ma_col] = st.session_state.unmatched_records[ma_col].fillna("")
                    st.session_state.unmatched_records["Extracted Domain"] = st.session_state.unmatched_records[ma_col].apply(
                        lambda x: extract_domain(x, freemail_domains)
                    )

                    # Convert extracted domains to lowercase
                    st.session_state.unmatched_records["Extracted Domain"] = st.session_state.unmatched_records["Extracted Domain"].str.lower()

                    # Filter out rows with None or invalid domains
                    valid_domains = st.session_state.unmatched_records.dropna(subset=["Extracted Domain"])
                    invalid_domains = st.session_state.unmatched_records[st.session_state.unmatched_records["Extracted Domain"].isna()]

                    # Convert HubSpot domain column to lowercase for case-insensitive matching
                    hubspot_data[hubspot_col] = hubspot_data[hubspot_col].str.lower()

                    # Perform matching only on valid domains
                    matched = pd.merge(
                        valid_domains, hubspot_data, left_on="Extracted Domain", right_on=hubspot_col, how="inner"
                    )
                    matched["Matched By"] = f"Domain Matching ({ma_col} - {hubspot_col})"

                    # Update matched_records
                    st.session_state.matched_records = pd.concat([st.session_state.matched_records, matched], ignore_index=True)

                    # Remove matched records from unmatched_records using a unique identifier (e.g., email address)
                    matched_email_addresses = matched[ma_col].tolist()  # Get list of matched email addresses
                    st.session_state.unmatched_records = st.session_state.unmatched_records[
                        ~st.session_state.unmatched_records[ma_col].isin(matched_email_addresses)
                    ]

                    # Drop the "Extracted Domain" column from unmatched_records
                    if "Extracted Domain" in st.session_state.unmatched_records.columns:
                        st.session_state.unmatched_records = st.session_state.unmatched_records.drop(columns=["Extracted Domain"])

                    st.session_state.domain_matching_started = True

            with space_col:
                st.markdown(" ")

            with continue_col:
                if not st.session_state.unmatched_records.empty:
                    if st.session_state.domain_matching_started:
                        if st.button("Continue Matching"):
                            st.session_state.domain_match_clicked = False
                            st.session_state.domain_matching_started = False
                else:
                    st.warning("No unmatched records left.")

            st.markdown("---")

        elif match_type == "Fuzzy Matching":
            with column_selection:
                hubspot_col = st.selectbox("Select HubSpot Column for Fuzzy Matching", hubspot_data.columns, key="fuzzy_hubspot_col")
                ma_col = st.selectbox("Select M&A Column for Fuzzy Matching", st.session_state.unmatched_records.columns, key="fuzzy_ma_col")

            if "fuzzy_matching_started" not in st.session_state:
                st.session_state.fuzzy_matching_started = False

            if "fuzzy_match_clicked" not in st.session_state:
                st.session_state.fuzzy_match_clicked = False

            match_col, space_col, continue_col = st.columns([7, 9, 5])

            with match_col:
                if st.button("Fuzzy Match Records", disabled=st.session_state.fuzzy_match_clicked):
                    st.session_state.fuzzy_match_clicked = True

                    # Normalize text for case-insensitive matching
                    st.session_state.unmatched_records["Company Name Normalized"] = st.session_state.unmatched_records[ma_col].str.lower()
                    hubspot_data["Hubspot Company Name Normalized"] = hubspot_data[hubspot_col].str.lower()

                    # Perform exact matching on normalized columns
                    exact_matches = pd.merge(
                        st.session_state.unmatched_records,
                        hubspot_data,
                        left_on="Company Name Normalized",
                        right_on="Hubspot Company Name Normalized",
                        how="inner"
                    )

                    # Drop the normalized columns if not needed
                    exact_matches = exact_matches.drop(columns=["Company Name Normalized", "Hubspot Company Name Normalized"])

                    # Add match metadata
                    if not exact_matches.empty:
                        exact_matches["Matched By"] = f"Exact Match ({ma_col} - {hubspot_col})"
                        exact_matches["Match Ratio"] = 100  # Exact match is always 100%
                        st.session_state.matched_records = pd.concat(
                            [st.session_state.matched_records, exact_matches], ignore_index=True
                        )
                        st.session_state.unmatched_records = st.session_state.unmatched_records[
                            ~st.session_state.unmatched_records[ma_col].str.lower().isin(exact_matches[ma_col].str.lower())
                        ]

                    # Step 2: Preprocess M&A Column
                    unmatched = st.session_state.unmatched_records.copy()
                    unmatched[["Original Name", "Cleaned Name"]] = unmatched[ma_col].apply(lambda x: pd.Series(preprocess_company_name(x)))

                    # Step 3: Fuzzy Matching
                    matched_rows = []
                    matched_ma_values = set()  # Keep track of matched M&A values

                    for _, row in unmatched.iterrows():
                        ma_value_orig = row["Original Name"]
                        ma_value_clean = row["Cleaned Name"]

                        # Perform fuzzy matching on both original and cleaned names
                        best_match_orig = process.extractOne(ma_value_orig, hubspot_data[hubspot_col].str.lower(), scorer=fuzz.ratio)
                        best_match_clean = process.extractOne(ma_value_clean, hubspot_data[hubspot_col].str.lower(), scorer=fuzz.ratio)

                        # Choose the better match
                        if best_match_orig and best_match_clean:
                            if best_match_orig[1] >= best_match_clean[1]:
                                best_match = best_match_orig
                                matched_by = f"Fuzzy Matching (Original) ({ma_col} - {hubspot_col})"
                                fuzzy_match_value = ma_value_orig  # Use the original name as the fuzzy match value
                            else:
                                best_match = best_match_clean
                                matched_by = f"Fuzzy Matching (Cleaned) ({ma_col} - {hubspot_col})"
                                fuzzy_match_value = ma_value_clean  # Use the cleaned name as the fuzzy match value
                        else:
                            best_match = best_match_orig or best_match_clean  # Pick non-null match
                            if best_match == best_match_orig:
                                matched_by = f"Fuzzy Matching (Original) ({ma_col} - {hubspot_col})"
                                fuzzy_match_value = ma_value_orig  # Use the original name as the fuzzy match value
                            else:
                                matched_by = f"Fuzzy Matching (Cleaned) ({ma_col} - {hubspot_col})"
                                fuzzy_match_value = ma_value_clean  # Use the cleaned name as the fuzzy match value

                        # If the best match meets the threshold, add it to the matched rows
                        if best_match and best_match[1] >= 80:  # Match ratio threshold
                            matched_hubspot = hubspot_data[hubspot_col].str.lower() == best_match[0]
                            matched_row = pd.concat([row, hubspot_data[matched_hubspot].iloc[0]], axis=0).to_frame().T
                            matched_row["Matched By"] = matched_by  # Set the "Matched By" value
                            matched_row["Fuzzy Match Value"] = fuzzy_match_value  # Add the fuzzy match value
                            matched_row["Match Ratio"] = best_match[1]
                            matched_rows.append(matched_row)
                            matched_ma_values.add(ma_value_orig)  # Track matched values

                    # If there are matched rows, update the session state
                    if matched_rows:
                        fuzzy_matched = pd.concat(matched_rows, ignore_index=True)

                        # Drop unnecessary columns
                        columns_to_drop = ["Original Name", "Cleaned Name", "Company Name Normalized", "Hubspot Company Name Normalized"]
                        fuzzy_matched = fuzzy_matched.drop(columns=[col for col in columns_to_drop if col in fuzzy_matched.columns])

                        st.session_state.matched_records = pd.concat(
                            [st.session_state.matched_records, fuzzy_matched], ignore_index=True
                        )

                        # Ensure unmatched records get updated properly
                        st.session_state.unmatched_records = st.session_state.unmatched_records[
                            ~st.session_state.unmatched_records[ma_col].str.lower().str.strip().isin(
                                {val.lower().strip() for val in matched_ma_values}
                            )
                        ]

                        # Drop "Company Name Normalized" from unmatched records
                        if "Company Name Normalized" in st.session_state.unmatched_records.columns:
                            st.session_state.unmatched_records = st.session_state.unmatched_records.drop(columns=["Company Name Normalized"])

                        st.session_state.fuzzy_matching_started = True
                    else:
                        st.warning("No fuzzy matches found.")
                        st.session_state.fuzzy_matching_started = True

            with space_col:
                st.markdown(" ")

            with continue_col:
                # Show "Continue Matching" button only after fuzzy matching is initiated
                if not st.session_state.unmatched_records.empty:
                    if st.session_state.fuzzy_matching_started:
                        if st.button("Continue Matching"):
                            st.session_state.fuzzy_match_clicked = False
                            st.session_state.fuzzy_matching_started = False
                else:
                    st.warning("No unmatched records left.")
            st.markdown("---")

        # Display matched and unmatched records
        st.subheader("Matched Records")
        st.dataframe(st.session_state.matched_records)
        st.write(f"Total Matched Records: {len(st.session_state.matched_records)}")
        st.subheader("Unmatched Records")
        if not st.session_state.unmatched_records.empty:
            st.dataframe(st.session_state.unmatched_records)
            st.write(f"Total Unmatched Records: {len(st.session_state.unmatched_records)}")
        else:
            st.success("Matched All Records") 

        # if not st.session_state.matched_records.empty:
        #     # Show "Combine Matched and Unmatched Records" button if there are no fuzzy matches
        #     if st.button("Combine Matched and Unmatched Records"):

        #         if st.session_state.unmatched_records.empty:
        #             combined_records = st.session_state.matched_records
        #         else:
        #             combined_records = pd.concat(
        #                 [st.session_state.matched_records, st.session_state.unmatched_records],
        #                 ignore_index=True
        #             )

        #         st.session_state.combined_records = combined_records  

        #         # Create an Excel file in memory
        #         output = BytesIO()
        #         with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        #             combined_records.to_excel(writer, index=False, sheet_name="Combined Records")
        #         output.seek(0)

        #         # Download the Excel file
        #         st.download_button(
        #             label="Download Combined Records as Excel",
        #             data=output,
        #             file_name="combined_records.xlsx",
        #             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        #         )
        #         st.success("Matched and unmatched records have been combined!") 

        if not st.session_state.matched_records.empty:
            # Show "Combine Matched and Unmatched Records" button if there are no fuzzy matches
                if st.session_state.unmatched_records.empty:
                    combined_records = st.session_state.matched_records
                else:
                    combined_records = pd.concat(
                    [st.session_state.matched_records, st.session_state.unmatched_records],
                        ignore_index=True
                    )

                st.session_state.combined_records = combined_records

    else:
        st.info("Please upload both HubSpot Companies and M&A Companies Excel files to proceed.")


# Main app logic
if st.session_state.current_page == "main":
    main_page()