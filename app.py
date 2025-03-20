import streamlit as st
import os
from supabase import create_client
from collections import defaultdict

# Set up page config
st.set_page_config(page_title="Shopping List", page_icon="📊")

# App title and description
st.title("Shopping List")
st.write("Let's have some food!")

# Initialize Supabase client with secrets from Streamlit's secrets management
def init_supabase():
    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")
        return None

supabase = init_supabase()
connection_status = "✅ Connected to Supabase" if supabase else "❌ Connection error"

# Create dropdown list
options = ["Top Shelf", "Middle Shelf", "Fruits", "Vegetables"]
user_selection = st.selectbox("Select an option:", options)

# Create text input
user_input = st.text_input("Enter your text:")
submit_button = st.button("Save to Database")

def save_note_to_db(supabase, content, item):
    try:
        response = supabase.table('notes').insert({"content": content, "item": item}).execute()
        if response.data:
            st.success("Successfully saved to database!")
        else:
            st.error("Failed to save data")
    except Exception as e:
        st.error(f"Error saving data: {e}")

# Main logic
if submit_button:
    if not user_input:
        st.error("Please enter some text before submitting")
    elif not supabase:
        st.error("Please provide both Supabase URL and API key")
    else:
        save_note_to_db(supabase, user_input, user_selection)

def display_saved_notes(supabase):
    try:
        response = supabase.table('notes').select("*").order('created_at', desc=True).execute()
        if response.data:
            st.subheader("Saved Notes")
            grouped_notes = defaultdict(list)
            for note in response.data:
                grouped_notes[note.get("item", "Uncategorized")].append(note)

            for shelf, notes in grouped_notes.items():
                st.markdown(f"### {shelf}")
                for note in notes:
                    with st.expander(f"Product: {note['content']}"):
                        st.write(note['item'])
                        col1, col2 = st.columns(3)
                        with col1:
                            if st.button(f"Bought", key=f"itemb_{note['id']}"):
                                supabase.table('notes').update({"item": "Bought"}).eq('id', note['id']).execute()
                                st.experimental_rerun()
                        with col2:
                            if st.button(f"Not Bought {note['item']}", key=f"itemnb_{note['id']}"):
                                supabase.table('notes').update({"item": "Not bought"}).eq('id', note['id']).execute()
                                st.experimental_rerun()
                       
        else:
            st.info("No notes found in the database")
    except Exception as e:
        st.error(f"Error retrieving notes: {e}")

# Display saved notes
if st.sidebar.checkbox("Show saved notes", value=True) and supabase:
    display_saved_notes(supabase)

# Instructions in the sidebar
with st.sidebar:
    st.subheader("How to use this app")
    st.write("""
    1. Enter your Supabase URL and API key in the fields above
    2. Create a table named 'notes' in your Supabase dashboard with columns:
        - id (int, primary key)
        - content (text)
        - created_at (timestamp with timezone, default: now())
    3. Enter text in the main panel and click 'Save to Database'
    4. Check 'Show saved notes' to view and manage your saved entries
    """)
