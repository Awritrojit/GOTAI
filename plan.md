# Project Plan: GOT-AI (Globally Operating & Theorizing AI)

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Directory & File Structure](#3-directory--file-structure)
4. [Component Breakdown & Pseudocode](#4-component-breakdown--pseudocode)
   - [`backend/app/config.py`](#backendappconfigpy)
   - [`backend/app/db/data_models.py`](#backendappdbdata_modelspy)
   - [`backend/app/llm/llm_interface.py`](#backendappllmllm_interfacepy)
   - [`backend/app/db/vector_store.py`](#backendappdbvector_storepy)
   - [`backend/app/core/scoring.py`](#backendappcorescoringpy)
   - [`backend/app/core/agent.py`](#backendappcoreagentpy)
   - [`backend/app/core/orchestrator.py`](#backendappcoreorchestratorpy)
   - [`backend/api.py`](#backendapipy)
   - [`frontend/js/graph.js`](#frontendjsgraphjs)
5. [Development Roadmap](#5-development-roadmap)

---

## 1. Project Overview

**Goal:** To create a web application that implements the GOT-AI reasoning framework. A user provides an initial hypothesis, and the system autonomously explores branching trajectories of thought, scoring and pruning them in real-time. The process is visualized as a dynamic, interactive graph.

**Core Components:**
*   **Backend:** A Python server (using FastAPI) to orchestrate the AI agents, manage data, and serve the API.
*   **LLM Interface:** A pluggable module to interact with a local LLM (e.g., Qwen 1.5B via Ollama or a similar library).
*   **Knowledge Base:** A local vector database (ChromaDB) to store and retrieve all generated thoughts ("nodes") efficiently.
*   **Frontend:** A browser-based UI (using HTML, CSS, and JavaScript with a visualization library like D3.js) to display the reasoning graph in real-time.

---

## 2. System Architecture

```
+----------------+      (HTTP API Calls)      +---------------------+
|                | <------------------------> |                     |
|  Frontend      |      (GET /graph_data)     |   Python Backend    |
| (Browser, D3.js)|      (GET /node/{id})      |    (FastAPI)        |
|                |                            |                     |
+----------------+      (POST /start)         +---------+-----------+
                                                        |
                                                        | (Manages)
                                          +-------------+-------------+
                                          |                           |
+--------------------+            +-------v-------+            +------v------+
|                    |            |               |            |             |
| Local LLM Runner   | <--+       |  Orchestrator | ---------> | Vector DB   |
| (e.g., Ollama)     |    |       |  (GOT-AI Logic) |            | (ChromaDB)  |
|                    |    +-----> |               | <--------> |             |
+--------------------+  (Prompts) +---------------+  (Store/Query) +-------------+

```

---

## 3. Directory & File Structure

```
got-ai-project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api.py              # FastAPI endpoints (/start, /graph_data, etc.)
│   │   ├── config.py           # Configuration (model names, prompts, paths)
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py        # The Agent class that generates new thoughts
│   │   │   ├── orchestrator.py # The main "First Agent" that runs the simulation
│   │   │   └── scoring.py      # The score() function logic
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── data_models.py  # Pydantic models for Node, Trajectory
│   │   │   └── vector_store.py # Wrapper for ChromaDB interactions
│   │   └── llm/
│   │       ├── __init__.py
│   │       └── llm_interface.py # Interface for communicating with the local LLM
│   └── main.py                 # Main script to launch the FastAPI server
│
├── frontend/
│   ├── index.html              # The main page structure
│   ├── css/
│   │   └── style.css           # Styling for the graph and UI elements
│   └── js/
│       ├── app.js              # Main JS logic for fetching data and UI updates
│       └── graph.js            # D3.js code for rendering the graph
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 4. Component Breakdown & Pseudocode

### **`backend/app/config.py`**

```python
# Configuration settings
LOCAL_LLM_MODEL = "qwen:1.5b" # Model name for Ollama or other runners
VECTOR_DB_PATH = "./db_data"
COLLECTION_NAME = "got_ai_knowledge"

# The Interrogative Battery
INTERROGATIVE_BATTERY = ["Why is this the case?", "What are the underlying assumptions?", "How can this be explained differently?", "What is the primary consequence of this?", "Where would this have the biggest impact?"]

# Prompts
AGENT_PROMPT_TEMPLATE = """
You are a creative and logical thinker. Given the following statement, generate a concise, one-sentence outcome for the question: "{question}"

Statement: "{statement_text}"

Your one-sentence outcome:
"""

LOGIC_SCORING_PROMPT_TEMPLATE = """
On a scale from 0.0 to 1.0, how logically sound and internally consistent is the following statement? Output ONLY the number.

Statement: "{text}"

Score:
"""
```

### **`backend/app/db/data_models.py`**

```python
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid

class Node(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    trajectory_id: str
    text: str
    score: float = 0.0
    cumulative_score: float = 0.0
    is_pruned: bool = False
    is_fully_explored: bool = False
    # To store the vector representation
    embedding: Optional[List[float]] = None
```

### **`backend/app/llm/llm_interface.py`**

```python
# This file will use a library like 'requests' or 'ollama'
# to talk to the running LLM.

import requests
from .. import config

class LLMInterface:
    def generate(self, prompt: str) -> str:
        # Placeholder for calling a local LLM API (e.g., Ollama)
        # In a real implementation, this would involve an HTTP POST request.
        try:
            response = requests.post("http://localhost:11434/api/generate",
                                     json={"model": config.LOCAL_LLM_MODEL, "prompt": prompt, "stream": False})
            response.raise_for_status()
            return response.json()["response"].strip()
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "Error: Could not generate response."

llm_client = LLMInterface()
```

### **`backend/app/db/vector_store.py`**

```python
import chromadb
from sentence_transformers import SentenceTransformer
from .data_models import Node
from .. import config

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=config.VECTOR_DB_PATH)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2') # Small, fast, local
        self.collection = self.client.get_or_create_collection(name=config.COLLECTION_NAME)

    def add_node(self, node: Node):
        embedding = self.embedding_model.encode(node.text).tolist()
        node.embedding = embedding
        self.collection.add(
            ids=[node.id],
            embeddings=[embedding],
            metadatas=[node.dict(exclude={'embedding'})] # Store all other data as metadata
        )

    def get_all_nodes_for_graph(self) -> list[Node]:
        # Retrieve all nodes for visualization
        nodes_data = self.collection.get(include=["metadatas"])
        return [Node(**meta) for meta in nodes_data['metadatas']]

    def get_node_by_id(self, node_id: str) -> Optional[Node]:
        data = self.collection.get(ids=[node_id], include=["metadatas"])
        if data['metadatas']:
            return Node(**data['metadatas'][0])
        return None

    def find_relevant_knowledge(self, query_text: str, n_results: int = 3) -> str:
        # For providing context to agents
        query_embedding = self.embedding_model.encode(query_text).tolist()
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        return "\n".join([meta['text'] for meta in results['metadatas'][0]])

vector_store_client = VectorStore()
```

### **`backend/app/core/scoring.py` with Robust Parsing**

```python
import re
from ..llm.llm_interface import llm_client
from .. import config
# from tools import concise_search

class Scorer:
    def _parse_llm_score_response(self, response: str) -> float:
        """
        Aggressively parses an LLM's response to find a float score.
        Returns a score from 0.0 to 1.0, or a penalty score if un-parsable.
        """
        response = response.strip()
        
        # 1. Ideal case: the response is just a number.
        try:
            return float(response)
        except ValueError:
            pass # Continue to the next method

        # 2. Common case: the response contains a number.
        # Regex to find the first instance of a number like 0.8, .8, 1.0, etc.
        match = re.search(r'(\d\.\d+|\.\d+)', response)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass # This should not happen with this regex, but for safety.

        # 3. Last resort: if no number is found, assign a penalty.
        # This indicates the model failed to follow instructions.
        print(f"Warning: Could not parse score from LLM response: '{response}'")
        return 0.1 # Penalty score

    def score_logic(self, text: str) -> float:
        """Calculates the logical soundness score for a piece of text."""
        prompt = config.LOGIC_SCORING_PROMPT_TEMPLATE.format(text=text)
        
        # In a real implementation, you'd also set temperature=0 here
        raw_response = llm_client.generate(prompt) 
        
        return self._parse_llm_score_response(raw_response)

    def score_plausibility(self, text: str) -> float:
        # This function would also benefit from the same robust parsing
        # if it uses an LLM to compare against search results.
        # For now, let's keep it simple.
        # In a real implementation, this would involve a search call.
        # e.g., search_results = concise_search(text)
        # prompt = f"Text: {text}\nSearch Results: {search_results}\nScore plausibility:"
        # raw_response = llm_client.generate(prompt)
        # return self._parse_llm_score_response(raw_response)
        return 0.8 # Placeholder

    def calculate_final_score(self, text: str) -> float:
        """Calculates the weighted average final score for a node."""
        # Check for empty/invalid text to avoid unnecessary LLM calls
        if not text or not isinstance(text, str) or len(text.split()) < 2:
            return 0.0

        logic = self.score_logic(text)
        plausibility = self.score_plausibility(text) # Placeholder for now
        
        # Weighted average
        final_score = (0.6 * logic) + (0.4 * plausibility)
        return round(final_score, 3)

# Make it a singleton instance for the app to use
scorer = Scorer()
```

### **`backend/app/core/agent.py`**

```python
from ..llm.llm_interface import llm_client
from .. import config
from .scoring import scorer
from ..db.data_models import Node

class Agent:
    def investigate(self, source_node: Node) -> list[Node]:
        new_nodes = []
        for question in config.INTERROGATIVE_BATTERY:
            prompt = config.AGENT_PROMPT_TEMPLATE.format(question=question, statement_text=source_node.text)
            new_text = llm_client.generate(prompt)

            if "Error:" not in new_text:
                new_node = Node(
                    parent_id=source_node.id,
                    trajectory_id=source_node.trajectory_id,
                    text=new_text
                )
                new_node.score = scorer.calculate_final_score(new_text)
                new_node.cumulative_score = source_node.cumulative_score + new_node.score
                new_nodes.append(new_node)
        return new_nodes
```

### **`backend/app/core/orchestrator.py`**

```python
# This is the most complex part. It runs the main loop in a background thread.
import time
from .agent import Agent
from ..db.vector_store import vector_store_client
from ..db.data_models import Node

class Orchestrator:
    def __init__(self):
        self.is_running = False
        self.agent = Agent()

    def start_analysis(self, hypothesis: str):
        # 1. Clear previous data from ChromaDB
        # 2. Create the root node
        root_node = Node(text=hypothesis, trajectory_id="root", cumulative_score=0.5)
        root_node.score = 0.5 # Initial score
        vector_store_client.add_node(root_node)
        self.is_running = True
        # 3. Run the main loop
        while self.is_running:
            self.run_cycle()
            time.sleep(5) # Pause between cycles

    def run_cycle(self):
        # 1. Get all nodes from DB to find the best one to expand
        all_nodes = vector_store_client.get_all_nodes_for_graph()
        open_nodes = [n for n in all_nodes if not n.is_fully_explored and not n.is_pruned]

        if not open_nodes:
            self.is_running = False
            print("Exploration complete.")
            return

        # 2. Select node with the highest score to explore next (greedy search)
        node_to_explore = max(open_nodes, key=lambda n: n.score)

        # 3. Use an agent to generate new child nodes
        new_nodes = self.agent.investigate(node_to_explore)

        # 4. Save new nodes to the database
        for node in new_nodes:
            vector_store_client.add_node(node)

        # 5. Mark the parent node as explored
        node_to_explore.is_fully_explored = True
        vector_store_client.add_node(node_to_explore) # This will update the node in ChromaDB

        # 6. TODO: Implement pruning logic
        # (e.g., find trajectories where average score is low and set node.is_pruned=True)

orchestrator = Orchestrator()
```

### **`backend/api.py`**

```python
from fastapi import FastAPI, BackgroundTasks
from .core.orchestrator import orchestrator
from .db.vector_store import vector_store_client
from .db.data_models import Node

app = FastAPI()

@app.post("/api/start")
def start_process(hypothesis: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(orchestrator.start_analysis, hypothesis)
    return {"message": "GOT-AI analysis started."}

@app.get("/api/graph_data")
def get_graph_data():
    nodes = vector_store_client.get_all_nodes_for_graph()
    # Format for D3.js (nodes and links)
    links = [{"source": n.id, "target": n.parent_id} for n in nodes if n.parent_id]
    return {"nodes": [n.dict() for n in nodes], "links": links}

@app.get("/api/node/{node_id}")
def get_node_details(node_id: str):
    node = vector_store_client.get_node_by_id(node_id)
    return node or {"error": "Node not found"}
```

### **`frontend/js/graph.js`**

```javascript
// This file will contain D3.js logic.
// Pseudocode for its functionality:

function renderGraph(graphData) {
    const nodes = graphData.nodes;
    const links = graphData.links;

    // Use D3's force simulation
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(50))
        .force("charge", d3.forceManyBody().strength(-150))
        .force("center", d3.forceCenter(width / 2, height / 2));

    // Create SVG elements for links (lines)
    const link = svg.append("g").selectAll("line")
        .data(links).join("line").attr("stroke", "#999");

    // Create SVG elements for nodes (circles)
    const node = svg.append("g").selectAll("circle")
        .data(nodes).join("circle")
        .attr("r", 10)
        // Color node based on score or if it's pruned
        .attr("fill", d => d.is_pruned ? "red" : d3.interpolateViridis(d.score))
        .call(drag(simulation)); // Make nodes draggable

    // Add score text to each node
    const labels = svg.append("g").selectAll("text")
        .data(nodes).join("text")
        .text(d => d.score.toFixed(2))
        .attr("font-size", "10px");

    // Add click event listener to nodes
    node.on("click", (event, d) => {
        fetch(`/api/node/${d.id}`)
            .then(response => response.json())
            .then(nodeDetails => {
                // Display nodeDetails.text in a side panel
                document.getElementById("node-inspector").innerText = nodeDetails.text;
            });
    });

    // Update positions on each 'tick' of the simulation
    simulation.on("tick", () => {
        link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
        node.attr("cx", d => d.x).attr("cy", d => d.y);
        labels.attr("x", d => d.x + 12).attr("y", d => d.y + 4);
    });
}
```

---

## 5. Development Roadmap

1.  **Milestone 1: Backend Foundation.**
    *   Set up the FastAPI server and file structure.
    *   Implement `llm_interface.py` to successfully call your local LLM.
    *   Implement `vector_store.py` to connect to ChromaDB and perform basic add/get operations.
    *   Create the Pydantic data models.
    *   **Goal:** Be able to manually add a `Node` to the DB and retrieve it.

2.  **Milestone 2: Core Logic & First Trajectory.**
    *   Implement the `scoring.py` module with at least the logic-scoring part working.
    *   Implement the `agent.py` to generate a set of child nodes from a single parent node.
    *   Create a simple test script to verify that one node can produce scored children.
    *   **Goal:** A single-step expansion is working correctly.

3.  **Milestone 3: Basic UI and API.**
    *   Build the `frontend/index.html` and a basic `graph.js`.
    *   Implement the `/api/graph_data` and `/api/node/{node_id}` endpoints.
    *   Manually populate the database with a few test nodes and make the frontend render a static graph of them.
    *   **Goal:** A static graph of dummy data is displayed correctly in the browser.

4.  **Milestone 4: The Full Loop & Real-time Visualization.**
    *   Implement the `orchestrator.py` with its main `run_cycle` loop.
    *   Implement the `/api/start` endpoint and have it launch the orchestrator in the background.
    *   In `frontend/js/app.js`, create a `setInterval` function that calls `/api/graph_data` every 3-5 seconds and re-renders the graph.
    *   **Goal:** User can input a hypothesis, and the graph grows and updates automatically in the browser.

5.  **Milestone 5: Advanced Features & Polish.**
    *   Implement the trajectory pruning logic in the orchestrator.
    *   Implement the search-based `score_plausibility` function.
    *   At the end of a run, implement the final analysis (highest cumulative score with lowest variance).
    *   Refine the UI/UX.
    *   **Goal:** The full GOT-AI vision is implemented.