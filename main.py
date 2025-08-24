import argparse
import time
from lib.agents.gemini import GeminiAgent as Agent
from dotenv import load_dotenv
from lib.loggers import api_logger, tool_logger

def run_agent(question: str):
    """Run the agent with the given question and return the answer."""
    agent = Agent()
    return agent.answer(question)

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="CLI tool for Agentic System"
    )
    parser.add_argument(
        "question",
        type=str,
        nargs="+",
        help="The question you want to ask the agent"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed execution metrics"
    )

    args = parser.parse_args()
    question = " ".join(args.question)

    start_time = time.time()
    answer = run_agent(question)
    end_time = time.time()
    print(answer)


    if args.verbose:
        print("\n=== Execution Metrics ===")
        print(f"Execution time: {end_time - start_time:.2f} seconds")

        api_metrics = api_logger.get_metrics()
        tool_metrics = tool_logger.get_metrics()

        print(f"Successful API calls: {api_metrics['successful_calls']}")
        print(f"Failed API calls: {api_metrics['failed_calls']}")
        print(f"Tool calls: {tool_metrics['tool_calls']}")

if __name__ == "__main__":
    main()
