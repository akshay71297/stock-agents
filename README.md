# 🤖 Multi-Agent AI Assistant

A powerful, modular framework for deploying multiple AI agents with different capabilities, powered by Ollama and Streamlit.

## ✨ Features

- 🔍 **Web Search Agent**: Research and analyze web content in real-time
- 🤝 **Multi-Agent Architecture**: Extensible system for adding new specialized agents
- 🎯 **Model Flexibility**: Use any Ollama-compatible model
- 💻 **Modern UI**: Clean, responsive interface built with Streamlit
- 🔄 **Real-time Processing**: Asynchronous operations for smooth performance

## 🚀 Quick Start

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Install Ollama**
- Visit [Ollama's website](https://ollama.com/download)
- Follow installation instructions for your OS

3. **Pull Required Models**
```bash
ollama pull llama3  # or your preferred model
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Run the Application**
```bash
streamlit run src/main.py
```

## 🏗️ Project Structure

```
stock-agents/
├── src/
│   ├── agents/        # AI Agents implementations
│   ├── tools/         # Tools used by agents
│   ├── utils/         # Utility functions
│   ├── ui/           # UI components
│   ├── config.py     # Configuration management
│   └── main.py       # Application entry point
└── requirements.txt
```

## 🛠️ Adding New Agents

1. Create new agent in `src/agents/`
2. Inherit from `BaseAgent`
3. Implement required methods
4. Register in `AgentManager`

Example:
```python
class NewAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return "Your system prompt here"
```

## 📝 License

MIT License - feel free to use this in your own projects!

## 🤝 Contributing

Contributions welcome! Feel free to fork.

## 🙏 Acknowledgments

This project was heavily inspired by and builds upon:
- [AI Agents Masterclass](https://github.com/coleam00/ai-agents-masterclass) by [@coleam00](https://github.com/coleam00)
- Special thanks to Cole Murray ([@coleam00](https://github.com/coleam00)) for the excellent tutorial and codebase
- [Claude](https://anthropic.com/claude) by Anthropic for assistance in project structuring and development
- [Ollama](https://ollama.com/) for the amazing models
- [Streamlit](https://streamlit.io/) for the UI framework
- [Pydantic-AI](https://github.com/jxnl/pydantic-ai) for agent architecture

## 🎓 Educational Note

This project serves as a learning implementation and extension of concepts taught in Cole Murray's AI Agents Masterclass.