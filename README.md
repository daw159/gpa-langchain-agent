# 🎓 AI Student Assistant — LangChain + FastMCP

An AI-powered academic assistant built using **LangChain, LangGraph, Groq, FastMCP, and Streamlit**.

The assistant helps university students calculate their GPA and CGPA, explore semester courses, plan target CGPAs, and manage academic conversations through a simple chat interface.

Unlike a basic chatbot, this project uses an **agentic AI architecture**. The language model selects and executes external tools through the Model Context Protocol (MCP) instead of performing GPA calculations by itself.

## 🚀 Features

### 1. AI-Powered GPA & CGPA Assistant
- Convert marks into grade points.
- Calculate semester GPA using course credit hours.
- Calculate updated CGPA after completing a semester.
- Determine the GPA required to achieve a target CGPA.
- Check whether a target CGPA is achievable.
- Retrieve semester courses and credit-hour information.

### 2. MCP Tool Integration
- Uses FastMCP to expose academic calculation tools.
- Connects the LangChain agent to a remote MCP server.
- Automatically selects tools based on student questions.
- Supports multiple tool calls for complex academic queries.

### 3. Persistent Conversation Memory
- Uses SQLite with LangGraph's `AsyncSqliteSaver`.
- Maintains separate conversation histories for different students.
- Restores previous conversations after restarting the application.
- Allows users to view and delete their conversation history.

### 4. Real-Time Response Streaming
- Streams AI responses as they are generated.
- Supports asynchronous tool execution.
- Provides tool execution updates in the terminal interface.

### 5. Streamlit Web Interface
- Interactive chat interface.
- Student-based conversation selection.
- Displays saved chat history.
- Clear conversation functionality.
- Streaming AI responses.

### 6. Additional Academic Tools
- Tavily-powered web search for study resources.
- Save academic reports.
- Send notifications when explicitly requested.

## 🏗️ System Architecture

```text
Student
   |
   v
Streamlit UI / Terminal
   |
   v
LangChain AI Agent
   |
   +---- Groq LLM
   |
   +---- LangGraph SQLite Memory
   |
   v
MCPAdapter
   |
   | HTTPS
   v
FastMCP Server (Render)
   |
   +---- GPA / CGPA Tools
   +---- Semester Information
   +---- Tavily Web Search
   +---- Report Saving
   +---- Notifications
```

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| LangChain | Agent creation and tool integration |
| LangGraph | Conversation state and memory |
| Groq | Large language model inference |
| FastMCP | MCP tool server |
| MCPAdapter | Connect LangChain to MCP tools |
| SQLite | Persistent chat memory |
| Streamlit | Web-based chat interface |
| Tavily | Academic web search |
| Render | Cloud hosting for MCP server |

## 🌐 Live MCP Server

The MCP server is deployed on Render.

**MCP Endpoint:**

https://gpa-agent-server.onrender.com/mcp

The server does not currently require an MCP authentication key.

Test the server using:

```bash
fastmcp list https://gpa-agent-server.onrender.com/mcp
```

> The free Render service may take some time to wake up after inactivity.

## 📁 Project Structure

```text
agent/
├── agent.py          # Terminal-based AI assistant
├── app.py            # Streamlit web interface
├── llm.py            # Groq model configuration
├── requirements.txt  # Python dependencies
├── .env              # Local API keys (not uploaded)
└── chats.db          # SQLite memory (generated locally)
```

The MCP server is maintained in a separate GitHub repository.

## ⚙️ Installation and Setup

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/gpa-ai-agent.git
cd gpa-ai-agent
```

Replace `YOUR_USERNAME` with the actual GitHub username.

### Step 2 — Create a Virtual Environment (Optional)

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

The agent requires these Python packages:

```text
langchain
langchain-groq
langchain-google-genai
langgraph
langgraph-checkpoint-sqlite
fastmcp
python-dotenv
streamlit
aiosqlite
```

The installed LangChain version must support `langchain.mcp.MCPAdapter`.

### Step 4 — Configure Environment Variables

Create a `.env` file in the agent directory:

```dotenv
GROQ_API_KEY=your_groq_api_key
GEMINI_KEY=your_gemini_api_key
MCP_URL=https://gpa-agent-server.onrender.com/mcp
```

The project is configured to use Groq by default. A Gemini API key is only needed if the model configuration is changed to Gemini.

**Never upload `.env` or real API keys to GitHub.**

## ▶️ Running the Application

### Option A — Streamlit Web Interface

Start the web application:

```bash
python -m streamlit run app.py
```

Open:

http://localhost:8501

Enter a student name and start chatting with the AI assistant.

### Option B — Terminal-Based Agent

Run:

```bash
python agent.py
```

Enter your student name when prompted.

Available terminal commands:

| Command | Description |
|---|---|
| `/switch` | Switch between students |
| `/threads` | List saved student conversations |
| `/history` | Display conversation history |
| `/forget` | Delete the current student's conversation |
| `/exit` | Exit the assistant |

**Note:** You do not need to run `server.py` locally because the MCP server is already hosted on Render.

## 💬 Example Questions

**Semester Information**

> What courses are offered in semester 5?

**Grade Point Conversion**

> I scored 85 marks. What are my grade points?

**Semester GPA**

> Calculate my semester GPA using these marks and credit hours.

**CGPA Prediction**

> My current CGPA is 3.2, and I have completed 60 credit hours. What will my CGPA be if I get a 3.8 GPA in my next 18-credit-hour semester?

**Target CGPA Planning**

> Can I achieve a 3.5 CGPA by graduation?

**Academic Web Search**

> Find useful resources for learning data structures and algorithms.

## 🧠 How the Agent Works

1. The student submits a question through Streamlit or the terminal.
2. The LangChain agent analyzes the request using the Groq LLM.
3. The agent determines whether an MCP tool is required.
4. The MCPAdapter communicates with the FastMCP server hosted on Render.
5. The server executes the requested tool and returns its result.
6. The agent generates a natural-language response.
7. LangGraph saves the conversation state in SQLite.

This separates language understanding from actual calculations and tool execution.

## 🔐 Security

- API keys are stored in environment variables.
- `.env` is excluded from version control.
- SQLite conversation data is stored locally.
- MCP tools execute on the remote server.
- The public MCP endpoint currently has no authentication; access controls are recommended before production use.

## 📌 Assignment Information

**Assignment:** Assignment 3 — MCP-Based AI Agent

**Roll Number:** BCSF24M030

**MCP Server Hosting:** Render

**MCP URL:** https://gpa-agent-server.onrender.com/mcp

**Server GitHub Repository:** Add your server repository link here.

## 👨‍💻 Author

**Muhammad Dawood**

BCSF24M030

Punjab University College of Information Technology (PUCIT)

---

*Developed as an academic project to demonstrate agentic AI, MCP tool integration, persistent memory, asynchronous programming, and cloud deployment.*
