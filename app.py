import streamlit as st
import os
from supabase import create_client

# Set up page config
st.set_page_config(page_title="Shoping List", page_icon="📊")


# App title and description
st.title("Shoping List")
st.write("Let's have some food!")

# Initialize Supabase client with secrets from Streamlit's secrets management
try:
    # Access secrets from the streamlit secrets management
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(supabase_url, supabase_key)
    connection_status = "✅ Connected to Supabase"
except Exception as e:
    connection_status = f"❌ Connection error: {str(e)}"
    supabase = None

# Function to initialize Supabase connection
def init_supabase():
    if supabase_url and supabase_key:
        return create_client(supabase_url, supabase_key)
    return None
# Create dropdown list
options = ["Top Shelf", "Middle Shelf", "Fruits", "Vegetables"]
user_selection = st.selectbox("Select an option:", options)


# Create text input
user_input = st.text_input("Enter your text:")
submit_button = st.button("Save to Database")

# Main logic
if submit_button:
    if not user_input:
        st.error("Please enter some text before submitting")
    elif not (supabase_url and supabase_key):
        st.error("Please provide both Supabase URL and API key")
    else:
        try:
            supabase = init_supabase()
            
            # Insert data into a 'notes' table (create this table in your Supabase dashboard)
            response = supabase.table('notes').insert({"content": user_input, "item": user_selection}).execute()
          
            # Check for successful insertion
            if len(response.data) > 0:
                st.success("Successfully saved to database!")
                #st.json(response.data[0])  # Display the saved record
            else:
                st.error("Failed to save data")
                
        except Exception as e:
            st.error(f"Error: {e}")

# Display saved notes
if st.sidebar.checkbox("Show saved notes", value=True) and (supabase_url and supabase_key):
    try:
        supabase = init_supabase()
        response = supabase.table('notes').select("*").order('created_at', desc=True).execute()
        
        if len(response.data) > 0:
            st.subheader("Saved Notes")
            grouped_notes = {}
            for note in response.data:
                shelf = note.get("item", "Uncategorized")
                if shelf not in grouped_notes:
                    grouped_notes[shelf] = []
                grouped_notes[shelf].append(note)
            
            for shelf, notes in grouped_notes.items():
    st.markdown(f"### {shelf}")
    for note in notes:
        with st.expander(f"Product: {note['content']}"):
            st.write(note['item'])
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Bought {note['item']}", key=f"bought_{note['id']}"):
                    supabase.table('notes').update({"bought": True}).eq('id', note['id']).execute()
                    st.experimental_rerun()
            with col2:
                if st.button(f"Not Bought {note['item']}", key=f"not_bought_{note['id']}"):
                    supabase.table('notes').update({"bought": False}).eq('id', note['id']).execute()
                    st.experimental_rerun()
            with col3:
                if st.button(f"Delete {note['id']}", key=f"del_{note['id']}"):
                    supabase.table('notes').delete().eq('id', note['id']).execute()
                    st.experimental_rerun()
        else:
            st.info("No notes found in the database")
            
    except Exception as e:
        st.error(f"Error retrieving notes: {e}")


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
