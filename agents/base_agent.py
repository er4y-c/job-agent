from agno.agent import Agent
from openai import OpenAI
from utils.config import OPENAI_API_KEY
from typing import List, Optional

class BaseAgent:
    def __init__(self, name: str, description: str, tools: Optional[List] = None):
        self.name = name
        self.description = description
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Collect tools from subclass
        agent_tools = []
        if tools:
            agent_tools.extend(tools)
        
        # Check if subclass has defined any function attributes
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, '__class__') and attr.__class__.__name__ == 'Function':
                agent_tools.append(attr)
        
        self.agent = Agent(
            name=name,
            description=description,
            tools=agent_tools if agent_tools else None
        )
    
    def run(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement run method")