---
title: RLHF External APIs
emoji: 💬
colorFrom: yellow
colorTo: purple
sdk: gradio
sdk_version: 5.0.1
app_file: app.py
pinned: false
license: mit
short_description: RLHF with external APIs
---

An example chatbot using [Gradio](https://gradio.app), [`huggingface_hub`](https://huggingface.co/docs/huggingface_hub/v0.22.2/en/index), and the [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index).

# LangChain RLHF Project

This project implements a Reinforcement Learning from Human Feedback (RLHF) application using LangChain. It includes tools for interacting with external APIs, setting up agents, managing model configurations, and storing feedback.

## Usage

- **Tools:** The `tourism_tools.py` file contains methods for checking hotel availability and retrieving weather information.
- **Agents:** The `agent_setup.py` file sets up the LangChain agent to interact with the defined tools.
- **Models:** The `model_config.py` file contains configurations for the models used in the RLHF project.
- **Feedback Storage:** The `firebase-credentials.py` file handles storing and retrieving feedback data in Firebase.


## License

This project is licensed under the MIT License. See the LICENSE file for more details.