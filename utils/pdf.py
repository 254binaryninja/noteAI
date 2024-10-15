import streamlit as st
from models.rag_model import get_pdf_files, supabase_client

def sidebar_and_pdf_display():
    # Select Unit
    st.sidebar.title("Select Unit")
    unit = st.sidebar.selectbox("Choose a Unit", [1, 2, 3, 4, 5, 6])

    # Fetch PDFs from the selected unit
    st.sidebar.title("Select PDF")
    pdf_files = get_pdf_files(unit)  # Pass the unit to get files for that specific table
    selected_pdf = st.sidebar.selectbox("Choose a PDF", pdf_files)

    if selected_pdf:
        # Fetch PDF content from the documents table
        pdf_response = supabase_client.table(f'pdf_files_unit_{unit}').select('file_content').eq('file_name', selected_pdf).limit(1).execute()
        if pdf_response.data:
            st.subheader("PDF Viewer")
            pdf_content = pdf_response.data[0]['file_content']
            st.write(f"PDF content length: {len(pdf_content)}")
            st.write(f"PDF content snippet: {pdf_content[:100]}")

    return selected_pdf, unit