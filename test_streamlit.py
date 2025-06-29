import streamlit as st

st.title("🧪 Streamlit Test")
st.write("If you can see this, Streamlit is working!")
st.success("✅ Streamlit is running successfully!")

if st.button("Test Button"):
    st.balloons()
    st.write("🎉 Button clicked!")
