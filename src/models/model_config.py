class ModelConfig:
    def __init__(self):
        self.model_name = "ArsenKe/MT5_large_finetuned_chatbot"  # Replace with your model
        self.learning_rate = 0.001
        self.batch_size = 32
        self.epochs = 10
        self.input_shape = (128, 128, 3)
        self.output_shape = 10
        
        # Add LLM-specific configurations
        self.max_length = 512
        self.temperature = 0.7
        self.top_p = 0.9
        self.do_sample = True

    def display_config(self):
        config = {
            "Model Name": self.model_name,
            "Learning Rate": self.learning_rate,
            "Batch Size": self.batch_size,
            "Epochs": self.epochs,
            "Input Shape": self.input_shape,
            "Output Shape": self.output_shape,
        }
        for key, value in config.items():
            print(f"{key}: {value}")