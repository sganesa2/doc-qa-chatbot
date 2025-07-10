# doc-qa-chatbot

A simple and extensible "Chat with Doc" interface built using [Langgraph](https://github.com/langchain-ai/langgraph). This project enables users to interact with documentation or custom text sources in a conversational manner, leveraging modern language models and modular workflows.

## Project Description

**doc-qa-chatbot** is designed to help users query and explore documentation or text files using natural language. It uses Langgraph to orchestrate workflows, making it easy to customize data extraction, document ingestion, and conversational logic. The project is modular, allowing you to adapt it for different document types or knowledge sources.

## Project Structure

```
doc-qa-chatbot/
├── src/
│   ├── chatbot/
│   │   ├── agent.py           # Main chatbot agent logic
│   │   ├── utils/
│   │   │   ├── data_extraction_tool.py  # Utilities for extracting and processing documents
│   │   │   └── ...            # Additional utility scripts
│   ├── requirements.txt       # Python dependencies
│   ├── a.yaml                 # Example workflow configuration (YAML)
│   └── langgraph.json         # Langgraph workflow definition (JSON)
├── tests/                     # Unit and integration tests
├── README.md                  # Project documentation
├── LICENSE                    # License file
└── .vscode/                   # VS Code settings (optional)
```

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/doc-qa-chatbot.git
   cd doc-qa-chatbot
   ```

2. **(Optional) Create a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r src/requirements.txt
   ```

## Usage

### Running the Chatbot

To start the chatbot interface, run:

```sh
python src/chatbot/agent.py
```

This will launch a command-line interface where you can ask questions about your documents.

### Customizing Workflows

- **Workflow Configuration:**  
  Modify `src/a.yaml` or `src/langgraph.json` to define or adjust the workflow steps, such as document ingestion, preprocessing, and response generation.
- **Adding Utilities:**  
  Place custom data extraction or processing scripts in `src/chatbot/utils/` and import them as needed in your workflow or agent.

### Example: Extracting Data

To run a data extraction utility:

```sh
python src/chatbot/utils/data_extraction_tool.py
```

## Testing

Run all tests with:

```sh
python -m unittest discover tests
```

## Configuration

- **Dependencies:**  
  Manage Python packages in `src/requirements.txt`.
- **VS Code Settings:**  
  Customize your development environment in `.vscode/settings.json`.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.