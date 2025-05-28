from langchain.agents import AgentType, initialize_agent
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from transformers.pipelines import pipeline  # Updated import

def create_agent():
    """Create LangChain agent with explicit pipeline import"""
    
    model_name = "ArsenKe/MT5_large_finetuned_chatbot"
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        # Create text generation pipeline
        text_gen_pipeline = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=512,
            temperature=0.7
        )
        
        llm = HuggingFacePipeline(pipeline=text_gen_pipeline)
        
        return initialize_agent(
            tools=[hotel_tool],
            llm=llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        
    except Exception as e:
        print(f"Error creating agent: {str(e)}")
        raise