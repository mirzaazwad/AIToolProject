"""The application startup file"""
import argparse
import time
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .lib.agents.gemini import GeminiAgent
from .lib.agents.openai import OpenAIAgent
from tests.stubs.agent import AgentStub
from dotenv import load_dotenv
from .lib.loggers import api_logger, tool_logger, agent_logger
from .lib.agents.base import Agent

class Application:
    """The application class"""
    def __init__(self):
        """Initialize the application"""
        load_dotenv()
        self.agent = None
        self.question = None
        self.verbose = False
        self.parser = None
        self.agent_type = None

    def run(self):
        """Run the application"""
        self.parse_arguments()
        self.preprocess_args()
        self.validate_arguments()
        self.initialize_agent()
        answer, processing_time = self.run_agent()
        if self.verbose:
            self.print_metrics(processing_time)
            print("=== Answer ===")
        print(answer)

    def preprocess_args(self):
        """Preprocess the command line arguments"""
        args = self.parser.parse_args()
        self.question = " ".join(args.question).strip()
        self.agent_type = args.agent.lower()
        self.verbose = args.verbose
        

    def parse_arguments(self):
        """Parse the command line arguments"""
        self.parser = argparse.ArgumentParser(
        description="""AI Tool-Using Agent System

        The following tools are available for use:

        1. calculator - for mathematical calculations (args: {"expr": "expression"})
        2. weather - for weather information (args: {"city": "city_name"})
        3. knowledge_base - for factual information (args: {"query": "query"})
        4. currency_converter - for currency conversion (args: {"from": "FROM_CURRENCY", "to": "TO_CURRENCY", "amount": number})

        Type 'python main.py -h' for more information.""",
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
        self.parser.add_argument(
            "question",
            type=str,
            nargs="?",
            help="""The question you want to ask the agent.

            Examples:
            "What is 12.5%% of 243?"
            "Who is Ada Lovelace?"
            "What's the weather in Paris?"
            "Convert 100 USD to EUR" """
        )
        self.parser.add_argument(
            "-a", "--agent",
            type=str,
            default="gemini",
            help="The agent to use. Options: gemini, openai, stub"
        )
        self.parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="""Print detailed execution metrics including:
                - Execution time
                - API call statistics
                - Tool usage metrics"""
        )

    def validate_arguments(self):
        """Validate the command line arguments"""
        if not self.question:
            print("No question provided. Please ask a question.")
            print(self.parser.format_help())
            exit(1)

    def initialize_agent(self):
        """Initialize the agent"""
        if self.agent_type == "gemini":
            self.agent = GeminiAgent()
        elif self.agent_type == "openai":
            self.agent = OpenAIAgent()
        elif self.agent_type == "stub":
            self.agent = AgentStub()
        else:
            print(f"Unknown agent type: {self.agent_type}")
            print(self.parser.format_help())
            exit(1)

    def run_agent(self):
        """Run the agent"""
        start_time = time.time()
        answer = self.agent.answer(self.question)
        end_time = time.time()
        return answer, end_time - start_time
    
    def print_metrics(self, processing_time: float) -> None:
        """Print the execution metrics"""
        api_metrics = api_logger.get_metrics()
        tool_metrics = tool_logger.get_metrics()
        agent_metrics = agent_logger.get_metrics()
        print(f"""
            === Execution Metrics ===
            Execution time: {processing_time:.2f} seconds
            Successful API calls: {api_metrics.successful_calls}
            Failed API calls: {api_metrics.failed_calls}
            Tool calls: {tool_metrics.tool_calls}
            Average LLM Processing Time: {agent_metrics.average_processing_time:.2f}s
            Total LLM Processing Time: {agent_metrics.total_processing_time:.2f}s
            LLM Queries Processed: {agent_metrics.queries_processed}
            For More Details check the logs in the logs folder.
        """)
        



def run_agent(question: str, agent_type: str = "gemini"):
    """Run the agent with the given question and return the answer."""
    agent: Agent = None
    if agent_type == "gemini":
        agent = GeminiAgent()
    elif agent_type == "openai":
        agent = OpenAIAgent()
    elif agent_type == "stub":
        agent = AgentStub()
    else:
        return f"Unknown agent type: {agent_type}"
    return agent.answer(question)






