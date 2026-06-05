import streamlit as st
import ollama
import tempfile
import os
from rag_system import documentAssistant
from todo_manager import TodoManager
from email_assistant import EmailAssistant
from groq import Groq

def apply_theme():
    st.markdown("""<style>
    .stApp{background-color:#020c1b!important;color:#ccd6f6!important}
    header[data-testid="stHeader"]{background:transparent!important}
    [data-testid="stSidebar"]{background-color:#030f22!important;border-right:1px solid #00e5ff22!important}
    p,li,label,.stMarkdown,h1,h2,h3{color:#ccd6f6!important}
    .stButton>button{background:transparent!important;border:1px solid #00e5ff!important;color:#00e5ff!important;border-radius:8px!important}
    .stButton>button:hover{background:#00e5ff15!important}
    .stButton>button[kind="primary"]{background:#00e5ff!important;color:#020c1b!important}
    .stTextInput>div>div>input,.stTextArea>div>div>textarea{background:#0a1628!important;border:1px solid #00e5ff33!important;color:#ccd6f6!important;border-radius:8px!important}
    .stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:#00e5ff!important}
    [data-testid="stChatInputContainer"]{background:#0a1628!important;border:1px solid #00e5ff33!important;border-radius:12px!important}
    .stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid #00e5ff22!important}
    .stTabs [data-baseweb="tab"]{color:#00e5ff66!important}
    .stTabs [aria-selected="true"]{color:#00e5ff!important;border-bottom:2px solid #00e5ff!important}
    [data-testid="stFileUploaderDropzone"]{background:#0a1628!important;border:2px dashed #00e5ff44!important;border-radius:8px!important}
    [data-testid="stExpander"]{background:#0a1628!important;border:1px solid #00e5ff22!important;border-radius:8px!important}
    hr{border-color:#00e5ff22!important}
    [data-testid="stMetric"]{background:#0a1628!important;border:1px solid #00e5ff22!important;border-radius:8px!important;padding:12px!important}
    ::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:#020c1b}
    ::-webkit-scrollbar-thumb{background:#00e5ff44;border-radius:3px}
    </style>""", unsafe_allow_html=True)

# Page config
st.set_page_config(
    page_title='Personal AI Assistant',
    page_icon='icon.jpg',
    layout='wide'
)

apply_theme()

# Initialize Session State Variables
if 'doc_ai'        not in st.session_state:
    st.session_state.doc_ai        = documentAssistant()
if 'todos'         not in st.session_state:
    st.session_state.todos         = TodoManager()
if 'email_ai'      not in st.session_state:
    st.session_state.email_ai      = EmailAssistant()
if 'messages'      not in st.session_state:
    st.session_state.messages      = []
if 'doc_ready'     not in st.session_state:
    st.session_state.doc_ready     = False
if 'loaded_docs'   not in st.session_state:
    st.session_state.loaded_docs   = []
if 'draft_subject' not in st.session_state:
    st.session_state.draft_subject = ''
if 'draft_body'    not in st.session_state:
    st.session_state.draft_body    = ''


#  Page Header
st.markdown("""
<div style='background:linear-gradient(135deg,#020c1b,#041830,#062240);padding:20px;border-radius:10px;
    text-align:center;margin-bottom:20px;border:1px solid #00e5ff33;'>
  <h1 style='color:#00e5ff;margin:0 0 8px;'> Personal AI Assistant</h1>
  <p style='color:#64ffda;margin:0 0 4px;'>Chat • Documents • Tasks • Email — All in One Place</p>
  <p style='font-size:12px;color:#82b1ff;margin:0;'>Built by Stephen David | Powered by Llama3 + LangChain + RAG</p>
</div>""", unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.title("Controls")
    st.divider()

    # PDF Upload
    st.subheader(" Upload PDF for research")
    uploaded_pdf = st.file_uploader("PDF", type=['pdf'])

    if uploaded_pdf is not None:
        if st.button(" Process the document"):
            with st.spinner(f"Reading {uploaded_pdf.name}..."):
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                tmp.write(uploaded_pdf.getbuffer())
                tmp_path = tmp.name
                tmp.close()

                st.session_state.doc_ai.load_pdf(tmp_path, uploaded_pdf.name)
                os.unlink(tmp_path)

                if uploaded_pdf.name not in st.session_state.loaded_docs:
                    st.session_state.loaded_docs.append(uploaded_pdf.name)
                st.session_state.doc_ready = True
            st.success(f"{uploaded_pdf.name} document processed successfully")

    if st.session_state.loaded_docs:
        st.write("**Loaded documents:**")
        for doc in st.session_state.loaded_docs:
            st.write(f" {doc}")

    st.divider()

    # Tasks
    st.subheader(" Tasks")
    tasks = st.session_state.todos.get_all()

    if tasks:
        for task in tasks:
            c1, c2, c3 = st.columns([1.5, 1, 1])
            c1.write(f"• {task[1]}")
            if c2.button("✅", key=f"s_done_{task[0]}"):
                st.session_state.todos.complete(task[0])
                st.rerun()
            if c3.button("🗑️", key=f"s_del_{task[0]}"):
                st.session_state.todos.delete(task[0])
                st.rerun()
    else:
        st.caption("No pending tasks")

    new_task = st.text_input("New task:")
    if st.button(" Add the Task", use_container_width=True):
        if new_task:
            st.session_state.todos.add(new_task)
            st.rerun()

    st.divider()

    # Gmail Config
    with st.expander(" Gmail Setup"):
        email_input = st.text_input("Your Gmail:", placeholder="you@gmail.com")
        pass_input  = st.text_input("App Password:", type="password",
                                     placeholder="xxxx xxxx xxxx xxxx")
        if st.button(" Save Gmail Config"):
            if email_input and pass_input:
                msg = st.session_state.email_ai.save_config(email_input, pass_input)
                st.success(msg)

        if st.session_state.email_ai.is_configured():
            st.success(" Gmail configured!")
        else:
            st.warning(" Gmail not configured")


# main tab
st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] {
    justify-content: center;
}
</style>
""", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["AI Chat", "Research in Documents", "AI Email Assistant", "My Tasks", "Expense Tracker"])


# Chat tab
with tab1:
    st.subheader(" Chat with AI")

    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):
            st.write(msg['content'])

    if prompt := st.chat_input("Ask me anything..."):
        with st.chat_message("user"):
            st.write(prompt)

        st.session_state.messages.append({'role': 'user', 'content': prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                history = [
                    {
                        'role': 'system',
                        'content': 'You are a helpful personal AI assistant for Stephen David. Be friendly and professional.'
                    }
                ] + st.session_state.messages

                client   = Groq(api_key=st.secrets["GROQ_API_KEY"])
response = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=history
)
reply = response.choices[0].message.content
                
                reply    = response['message']['content']
                st.write(reply)

        st.session_state.messages.append({'role': 'assistant', 'content': reply})

    if st.button(" Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# ── TAB 2: DOCUMENTS ──
with tab2:
    st.subheader(" Ask Questions About Documents")

    if not st.session_state.doc_ready:
        st.info("👈 Upload PDFs from the sidebar first")
        st.write("*You can upload MULTIPLE documents")
        st.write("• Annual reports  • Research papers  • Course materials  • Any PDF")
    else:
        st.success(f" {len(st.session_state.loaded_docs)} document(s) loaded")
        for doc in st.session_state.loaded_docs:
            st.write(f" {doc}")

        st.divider()
        doc_q = st.text_input("Ask anything about your documents:")

        if st.button(" Search Documents", use_container_width=True):
            if doc_q:
                with st.spinner("Searching all documents..."):
                    answer = st.session_state.doc_ai.ask(doc_q)
                st.markdown("### Answer:")
                st.write(answer)


# Email tab
with tab3:
    st.subheader(" AI Email Assistant")

    if not st.session_state.email_ai.is_configured():
        st.warning(" Please configure Gmail in the sidebar first")
        st.write("**How to get App Password:**")
        st.write("1. Go to myaccount.google.com")
        st.write("2. Security → 2-Step Verification → ON")
        st.write("3. Search 'App Passwords'")
        st.write("4. Generate for Mail + Windows")
        st.write("5. Copy the 16-character password to the sidebar")

    st.divider()
    st.subheader(" Compose Email")

    col1, col2 = st.columns(2)
    with col1:
        to_email = st.text_input("To:", placeholder="recipient@email.com")
    with col2:
        cc_email = st.text_input("CC (optional):", placeholder="cc@email.com")

    purpose = st.text_area(
        "Describe what you want to say:",
        placeholder="Example: Write email to my manager requesting leave tomorrow for a medical appointment",
        height=100
    )

    # ✅ FIX: Error handling added; state only updated after successful generation
    if st.button(" Generate Draft", use_container_width=True):
        if to_email and purpose:
            with st.spinner("AI is writing your email..."):
                try:
                    subject, body = st.session_state.email_ai.generate_draft(
                        to_email, cc_email, purpose
                    )
                    # Only update state after we actually have content
                    if body.startswith('❌'):
                        st.error(body)
                        st.info("Make sure Ollama is running: open a terminal and run `ollama serve`")
                    else:
                        st.session_state.draft_subject = subject
                        st.session_state.draft_body    = body
                except Exception as e:
                    st.error(f"❌ Generation failed: {str(e)}")
                    st.info("Make sure Ollama is running: open a terminal and run `ollama serve`")
        else:
            st.error("Please fill in the To and Purpose fields")

    # Show and edit draft
    if st.session_state.draft_subject or st.session_state.draft_body:
        st.divider()
        st.subheader(" Review & Edit Draft")

        edited_subject = st.text_input("Subject:", value=st.session_state.draft_subject)
        edited_body    = st.text_area("Email Body:", value=st.session_state.draft_body, height=200)

        col1, col2 = st.columns(2)

        if col1.button(" Send Email", use_container_width=True, type="primary"):
            if to_email:
                with st.spinner("Sending..."):
                    result = st.session_state.email_ai.send_email(
                        to_email, cc_email, edited_subject, edited_body
                    )
                if "✅" in result:
                    st.success(result)
                    st.session_state.draft_subject = ''
                    st.session_state.draft_body    = ''
                else:
                    st.error(result)

        if col2.button(" Regenerate", use_container_width=True):
            st.session_state.draft_subject = ''
            st.session_state.draft_body    = ''
            st.rerun()


# Task tabs
with tab4:
    st.subheader(" Task Manager")

    tasks = st.session_state.todos.get_all()
    col1, col2 = st.columns(2)
    col1.metric("Pending Tasks", len(tasks))

    if tasks:
        st.divider()
        for task in tasks:
            c1, c2, c3, c4 = st.columns([4, 2, 1, 1])
            c1.write(f"**{task[0]}.** {task[1]}")
            c2.caption(task[2][:10])
            if c3.button("✅ Done", key=f"t4_{task[0]}"):
                st.session_state.todos.complete(task[0])
                st.rerun()
            if c4.button("🗑️", key=f"t4d_{task[0]}"):
                st.session_state.todos.delete(task[0])
                st.rerun()
    else:
        st.info("No pending tasks! Add from sidebar.")

    st.divider()
    st.subheader(" Add New Task")
    new_t = st.text_input("Task description:")
    if st.button("Add Task", use_container_width=True):
        if new_t:
            st.session_state.todos.add(new_t)
            st.success(f"Added: {new_t}")
            st.rerun()

with tab5:
    st.markdown("""
    <div style="text-align:center;">
        <h4> Coming Soon...</h4>
                
Features:     
Auto-categorization (Rapido → Transport, Swiggy → Food)

 Budget alerts

 Monthly spending dashboard

 Pie chart by category

 AI insights

 You can ask ask questions like:
                
 "How much did I spend on transport this month?"
"What is my biggest expense?"
"Show food expenses for May"
    </div>
    """, unsafe_allow_html=True)

    

# ── FOOTER ──
st.divider()
st.markdown("""
<div style='text-align:center; color:gray; font-size:12px;'>
    Personal AI Assistant | Built by Stephen David |
    LangChain + Ollama + RAG + SQLite + Streamlit
</div>
""", unsafe_allow_html=True)
