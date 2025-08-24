"""Constants for LLMs"""

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_MODEL = "gemini-2.0-flash"
OPENAI_API_URL = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-3.5-turbo"

FUSE_FORMAT_MESSAGE = """
            - For calculations: return only the numeric result (float or int).
            - For knowledge base queries: return short factual answers.
            - For weather: return temperature and/or conditions with units.
            - For currency conversion: return only the converted amount with currency.
            - For mixed queries: combine results into the most direct final answer.

            Examples:
            Prompt: What is 12.5% of 243?
            Answer: 30.375
            Format: float|int

            Prompt: What is 2+2?
            Answer: 4
            Format: int|float

            Prompt: Summarize today’s weather in Paris in 3 words.
            Answer: Mild and cloudy.
            Format: string

            Prompt: Who is Ada Lovelace?
            Answer: English mathematician and writer, pioneer of computing.
            Format: string

            Prompt: Add 10 to the average temperature in Paris and London right now.
            Answer: 28.0°C
            Format: string, [float]°C
            Validation: string ends with °C, °F or K

            Prompt: Convert the average of 10 and 20 USD into EUR.
            Answer: 13.6 EUR
            Format: string, [float] [string]
            Validation: string is three characters in capitals

            IMPORTANT:
            - Only return the [Answer] and nothing else
            - Do not include tool names or raw response text in the final answer.
            - Provide only the fused result in the correct format.
"""

TOOL_SYSTEM_ROLE = """
        You are an agent tasked with suggesting appropriate tools to answer the query.
        """

SYSTEM_PROMPT_CONTEXT = """
        For the prompt provided, you have to suggest appropriate tools to answer the query.
        The tools available are:
        1. calculator - for mathematical calculations (args: {{"expr": "expression"}})
        2. weather - for weather information (args: {{"city": "city_name"}})
        3. knowledge_base - for factual information (args: {{"query": "query"}})
        4. currency_converter - for currency conversion (args: {{"from": "FROM_CURRENCY", "to": "TO_CURRENCY", "amount": number}})
"""

TOOL_SUGGESTION_EXAMPLES = """        - For 'What is 1 + 1?': [{{ "tool": "calculator", "args": {{ "expr": "1 + 1" }}, "depends_on": [] }}]
        - For 'Weather in Paris?': [{{ "tool": "weather", "args": {{ "city": "paris" }}, "depends_on": [] }}]
        - For 'Who is Ada Lovelace?': [{{ "tool": "knowledge_base", "args": {{ "query": "Ada Lovelace" }}, "depends_on": [] }}]
        - For '100 USD to INR?': [{{ "tool": "currency_converter", "args": {{ "from": "USD", "to": "INR", "amount": 100 }}, "depends_on": [] }}]
        - For 'Weather in Paris and calculate 2+2?': [{{ "tool": "weather", "args": {{ "city": "paris" }}, "depends_on": [] }}, {{ "tool": "calculator", "args": {{ "expr": "2+2" }}, "depends_on": ["weather"] }}]

        You can suggest multiple tools if needed. Remember: calculator tool must be LAST when multiple tools are used. Calculator tool can take results from other tools as input using 'depends_on' key. Return ONLY the JSON array, no other text."""
