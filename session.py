# import streamlit as st
# import pandas as pd

# # Function to filter records where "Matched By" contains "Domain Matching"
# def filter_domain_matching(df):
#     if "Matched By" in df.columns:
#         # Use str.contains() to filter rows containing "Domain Matching"
#         return df[df["Matched By"].str.contains("Domain Matching", case=False, na=False)]
#     else:
#         st.warning("The 'Matched By' column does not exist in the DataFrame.")
#         return pd.DataFrame()  # Return an empty DataFrame if the column doesn't exist
    
# def filter_fuzzy_matching(df):
#     if "Matched By" in df.columns:
#         return df[(df["Match Ratio"] < 100) & df["Matched By"].str.contains("Fuzzy Matching", case=False, na=False)]
    
#     else:
#         st.warning("The 'Matched By' column does not exist in the DataFrame.")
#         return pd.DataFrame()  # Return an empty DataFrame if the column doesn't exist

# # Function to check for duplicates in the selected column
# def check_duplicates(df, column):
#     duplicates = df[df.duplicated(column, keep=False)]
#     return duplicates

# # Function to handle the selection of records
# def handle_duplicates(df, column):
#     duplicates = check_duplicates(df, column)
    
#     if not duplicates.empty:
#         # Get unique values of the selected column that have duplicates
#         duplicate_values = duplicates[column].unique()
        
#         # Initialize session state for tracking progress
#         if "current_duplicate_index" not in st.session_state:
#             st.session_state.current_duplicate_index = 0
        
#         # Ensure the index is within bounds
#         if st.session_state.current_duplicate_index >= len(duplicate_values):
#             st.session_state.current_duplicate_index = 0  # Reset index if out of bounds
        
#         # Get the current duplicate value to process
#         current_value = duplicate_values[st.session_state.current_duplicate_index]
#         duplicate_set = duplicates[duplicates[column] == current_value]
        
#         # Display the current set of duplicates
#         st.write(f"Processing duplicates for: {current_value}")
#         st.dataframe(duplicate_set)
        
#         # Allow user to select which record to keep
#         selected_index = st.selectbox(
#             f"Select the index of the record to keep for {current_value}:",
#             duplicate_set.index
#         )
        
#         # Drop the other duplicates
#         df = df.drop(duplicate_set.index.difference([selected_index]))
        
#         # Add a button to move to the next set of duplicates
#         if st.button("Next Set"):
#             if st.session_state.current_duplicate_index < len(duplicate_values) - 1:
#                 st.session_state.current_duplicate_index += 1
#             else:
#                 st.success("All duplicates have been processed.")
#                 st.session_state.combined_records = df  # Update the session state
#                 st.session_state.current_duplicate_index = 0  # Reset index
#                 st.experimental_rerun()  # Refresh the page to reflect changes
        
#     else:
#         st.info(f"No duplicates found in the selected column: {column}.")
    
#     return df

# def review_fuzzy_matches(df):
#     """
#     Function to review fuzzy matches with a match ratio < 100.
#     Args:
#         df (pd.DataFrame): The dataframe containing matches to review.
#     """
#     st.title("Review Fuzzy Matches")
#     st.markdown("---")

#     # Filter only fuzzy matches where Match Ratio < 100
#     df_filtered = df[(df["Match Ratio"] < 100) & (df["Matched By"].str.contains("Fuzzy Matching", na=False))]

#     # Initialize session state for tracking progress
#     if "current_match_index" not in st.session_state:
#         st.session_state.current_match_index = 0

#     # Check if there are matches to review
#     if df_filtered.empty:
#         st.success("All fuzzy matches have been reviewed!")
#         return

#     # Ensure index is within bounds
#     if st.session_state.current_match_index >= len(df_filtered):
#         st.session_state.current_match_index = 0  # Reset index

#     # Get the current match to review
#     current_match = df_filtered.iloc[st.session_state.current_match_index]

#     # Extract M&A and HubSpot column names from the "Matched By" value
#     matched_by = current_match["Matched By"]

#     try:
#         # Extract column names from parentheses
#         columns_part = matched_by.split("(")[-1].rstrip(")")
#         ma_col, hubspot_col = columns_part.split(" - ")
#     except (IndexError, ValueError):
#         st.error(f"Unable to parse column names from 'Matched By' value: {matched_by}")
#         return

#     # Display match details
#     st.write(f"**Match Ratio:** {current_match['Match Ratio']}")
#     st.write(f"**M&A Column ({ma_col}):** {current_match[ma_col]}")
#     st.write(f"**HubSpot Column ({hubspot_col}):** {current_match[hubspot_col]}")

#     # Buttons for manual review
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Yes (Keep Match)"):
#             st.success("Match kept as is.")

#     with col2:
#         if st.button("No (Remove Match)"):
#             # Update the DataFrame: Set "Match Ratio" and "Fuzzy Match Value" to empty
#             df.at[current_match.name, "Match Ratio"] = ""
#             df.at[current_match.name, "Fuzzy Match Value"] = ""
#             st.warning("Match removed.")

#     # Move to next record
#     if st.session_state.current_match_index < len(df_filtered) - 1:
#         st.session_state.current_match_index += 1
#     else:
#         st.success("All fuzzy matches have been reviewed!")
#         st.session_state.current_match_index = 0  # Reset index

#     st.write(f"Reviewing {st.session_state.current_match_index + 1} of {len(df_filtered)} matches.")

#     return df  # Return updated DataFrame


# # Main Streamlit app
# st.title("View Combined Records")

# # Check if there are combined records in session state
# if "combined_records" in st.session_state:
#     df = st.session_state.combined_records
#     st.dataframe(df)  # Display the combined records
    
#     # Filter records where "Matched By" is "Domain Matching"
#     domain_df = filter_domain_matching(df)
    
#     if not domain_df.empty:
#         # Allow the user to select a column for duplicate checking
#         column = st.selectbox(
#             "Select a column to check for duplicates:",
#             domain_df.columns
#         )
        
#         # Process duplicates one by one for the selected column
#         domain_df = handle_duplicates(domain_df, column)
        
#         # Update the original DataFrame with the changes made to the filtered DataFrame
#         df.update(domain_df)
#         st.session_state.combined_records = df  # Update the session state
#     else:
#         st.warning("No records found with 'Matched By' = 'Domain Matching'.")

#     # fuzzy_df = filter_fuzzy_matching(df)

#     # if not fuzzy_df.empty:
#     #     fuzzy_df = review_fuzzy_matches(fuzzy_df)

#     #     df.update(fuzzy_df)

#     #     st.session_state.combined_records = df 
#     # else:
#     #     st.warning("No records found with 'Matched By' = 'Fuzzy Matching'.")
# else:
#     st.warning("No combined records found. Please go back and generate them first.")

import streamlit as st
import pandas as pd

# Function to filter records where "Matched By" contains "Domain Matching"
def filter_domain_matching(df):
    if "Matched By" in df.columns:
        # Use str.contains() to filter rows containing "Domain Matching"
        return df[df["Matched By"].str.contains("Domain Matching", case=False, na=False)]
    else:
        st.warning("The 'Matched By' column does not exist in the DataFrame.")
        return pd.DataFrame()  # Return an empty DataFrame if the column doesn't exist
    
def filter_fuzzy_matching(df):
    if "Matched By" in df.columns:
        return df[(df["Match Ratio"] < 100) & df["Matched By"].str.contains("Fuzzy Matching", case=False, na=False)]
    else:
        st.warning("The 'Matched By' column does not exist in the DataFrame.")
        return pd.DataFrame()  # Return an empty DataFrame if the column doesn't exist

# Function to check for duplicates in the selected column
def check_duplicates(df, column):
    duplicates = df[df.duplicated(column, keep=False)]
    return duplicates

# Function to handle the selection of records
def handle_duplicates(df, column):
    duplicates = check_duplicates(df, column)
    
    if not duplicates.empty:
        # Get unique values of the selected column that have duplicates
        duplicate_values = duplicates[column].unique()
        
        # Initialize session state for tracking progress
        if "current_duplicate_index" not in st.session_state:
            st.session_state.current_duplicate_index = 0
        
        # Ensure the index is within bounds
        if st.session_state.current_duplicate_index >= len(duplicate_values):
            st.session_state.current_duplicate_index = 0  # Reset index if out of bounds
        
        # Get the current duplicate value to process
        current_value = duplicate_values[st.session_state.current_duplicate_index]
        duplicate_set = duplicates[duplicates[column] == current_value]
        
        # Display the current set of duplicates
        st.write(f"Processing duplicates for: {current_value}")
        st.dataframe(duplicate_set)
        
        # Allow user to select which record to keep
        selected_index = st.selectbox(
            f"Select the index of the record to keep for {current_value}:",
            duplicate_set.index
        )
        
        # Drop the other duplicates from the main DataFrame
        indices_to_drop = duplicate_set.index.difference([selected_index])
        df.drop(indices_to_drop, inplace=True)
        
        # Add a button to move to the next set of duplicates
        if st.button("Next Set"):
            if st.session_state.current_duplicate_index < len(duplicate_values) - 1:
                st.session_state.current_duplicate_index += 1
            else:
                st.success("All duplicates have been processed.")
                st.session_state.current_duplicate_index = 0  # Reset index
                st.session_state.duplicates_handled = True  # Set flag to indicate duplicates are handled
                st.experimental_rerun()  # Refresh the page to reflect changes
        
    else:
        st.info(f"No duplicates found in the selected column: {column}.")
        st.session_state.duplicates_handled = True  # Set flag to indicate duplicates are handled
    
    return df

def review_fuzzy_matches(df):
    """
    Function to review fuzzy matches with a match ratio < 100.
    Args:
        df (pd.DataFrame): The dataframe containing matches to review.
    """
    st.title("Review Fuzzy Matches")
    st.markdown("---")

    # Convert "Match Ratio" column to numeric (if it's not already)
    df["Match Ratio"] = pd.to_numeric(df["Match Ratio"], errors="coerce")

    # Filter only fuzzy matches where Match Ratio < 100
    df_filtered = df[(df["Match Ratio"] < 100) & (df["Matched By"].str.contains("Fuzzy Matching", na=False))]

    # Initialize session state for tracking progress
    if "current_match_index" not in st.session_state:
        st.session_state.current_match_index = 0

    # Check if there are matches to review
    if df_filtered.empty:
        st.success("All fuzzy matches have been reviewed!")
        return

    # Ensure index is within bounds
    if st.session_state.current_match_index >= len(df_filtered):
        st.session_state.current_match_index = 0  # Reset index

    # Get the current match to review
    current_match = df_filtered.iloc[st.session_state.current_match_index]

    # Extract M&A and HubSpot column names from the "Matched By" value
    matched_by = current_match["Matched By"]

    try:
        # Extract column names from parentheses
        columns_part = matched_by.split("(")[-1].rstrip(")")
        ma_col, hubspot_col = columns_part.split(" - ")
    except (IndexError, ValueError):
        st.error(f"Unable to parse column names from 'Matched By' value: {matched_by}")
        return

    # Display match details
    st.write(f"**Match Ratio:** {current_match['Match Ratio']}")
    st.write(f"**M&A Column ({ma_col}):** {current_match[ma_col]}")
    st.write(f"**HubSpot Column ({hubspot_col}):** {current_match[hubspot_col]}")

    # Buttons for manual review
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes (Keep Match)"):
            st.success("Match kept as is.")

    with col2:
        if st.button("No (Remove Match)"):
            # Update the DataFrame: Set "Match Ratio" and "Fuzzy Match Value" to empty
            df.at[current_match.name, "Match Ratio"] = ""
            df.at[current_match.name, "Fuzzy Match Value"] = ""
            st.warning("Match removed.")

    # Move to next record
    if st.session_state.current_match_index < len(df_filtered) - 1:
        st.session_state.current_match_index += 1
    else:
        st.success("All fuzzy matches have been reviewed!")
        st.session_state.current_match_index = 0  # Reset index

    st.write(f"Reviewing {st.session_state.current_match_index + 1} of {len(df_filtered)} matches.")

    return df

# Main Streamlit app
st.title("View Combined Records")

# Check if there are combined records in session state
if "combined_records" in st.session_state:
    df = st.session_state.combined_records
    st.dataframe(df)  # Display the combined records
    print(df["Match Ratio"].dtype)
    
    # Initialize session state flags if not already set
    if "duplicates_handled" not in st.session_state:
        st.session_state.duplicates_handled = False
    if "fuzzy_matches_handled" not in st.session_state:
        st.session_state.fuzzy_matches_handled = False

    if not st.session_state.duplicates_handled:
        domain_df = filter_domain_matching(df)

        if not domain_df.empty:
            column = st.selectbox("Select a column to check for duplicates:", domain_df.columns)
            updated_df = handle_duplicates(df, column)
            st.session_state.combined_records = updated_df
        else:
            st.warning("No records found with 'Matched By' = 'Domain Matching'.")
            st.session_state.duplicates_handled = True  # No duplicates, move to fuzzy matching

    # Once duplicates are handled, check fuzzy matches separately
    if st.session_state.duplicates_handled and not st.session_state.fuzzy_matches_handled:
        fuzzy_df = filter_fuzzy_matching(df)
        
        if not fuzzy_df.empty:
            updated_fuzzy_df = review_fuzzy_matches(fuzzy_df)
            st.session_state.combined_records = updated_fuzzy_df
        else:
            st.warning("No records found with 'Matched By' = 'Fuzzy Matching'.")
            st.session_state.fuzzy_matches_handled = True  # Mark fuzzy matches as handled

else:
    st.warning("No combined records found. Please go back and generate them first.")