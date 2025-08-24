"""Constants for LLM Sending and Receiving Messages"""

FAILED_AGENT_MESSAGE = "Sorry I am unable to answer your query at this moment."

TOOL_SUGGESTION_FORMAT = """
        [
            {{
                "tool": "tool_name",
                "args": {{
                    "arg_name": "arg_value"
                }},
                "depends_on": [
                    "tool_name_1",
                    "tool_name_2"
                    ...
                    ]
                }}
        ]"""
