import streamlit as st
import rag 

# Set the title of the Streamlit app
st.title("Automate Your Business Support")

# Accept user input
prompt = st.text_input("Ask your query to our support assistant:")

if prompt:
    # Display user message
    st.write(f"**You:** {prompt}")

    # Generate response
    qa_chain = rag.setup_rag()
    response = qa_chain.invoke(prompt)
    # response = "Dummmy Response"

    # Display assistant response
    st.write(f"**Support Assistant:** {response}")
