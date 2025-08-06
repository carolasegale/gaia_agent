def create_system_prompt_for_main_agent(tools):
    """Create a more descriptive system prompt that explains the available tools"""
    tool_descriptions = "\n".join([
        f"- {tool._metadata.name}: {tool._metadata.description}"
        for tool in tools
    ])

    system_prompt = f"""You're a data analyst with a scientific background and the ability to use tools.

You have access to the following tools:
{tool_descriptions}
Do not write or execute Python code. Use the calculator tool for any numeric operations, even when working with Excel data.

When a user's request requires using at least one of the above tools:
1. First think through what information you need and which tool would be appropriate
2. Then provide a clear explanation to the user about your approach
3. Finally use the appropriate tool by including the necessary parameters

Important: If a question requires calculation for a simple expression or for a markdown table, execution of python code in given .py file
or parsing of an Excel file, ALWAYS use the appropriate tool rather than trying to answer from your knowledge. 
It doesn't matter if  the answer is straightforward, use tools to ensure accuracy and reliability.

Begin."""

    return system_prompt


def create_system_prompt_for_others(tools):
    """Create a more descriptive system prompt that explains the available tools"""
    tool_descriptions = "\n".join([
        f"- {tool._metadata.name}: {tool._metadata.description}"
        for tool in tools
    ])

    system_prompt = f"""You're a helpful general AI assistant with the ability to use tools.

You have access to the following tools:
{tool_descriptions}

When a user's request requires using at least one of the above tools:
1. First think through what information you need and which tool would be appropriate
2. Then provide a clear explanation to the user about your approach
3. Finally use the appropriate tool by including the necessary parameters

Important: ALWAYS use the appropriate search tools rather than trying to answer from your knowledge.
It doesn't matter if  the answer is straightforward, use tools to ensure accuracy and reliability.

Begin."""
    return system_prompt


def user_prompt_with_question(question):

    extract_prompt = f"""
Answer to the following input question using the agents available to you:

{question}

If one agent does not have the right tools to answer the question, it can hand off to another agent that has the right tools.
If the question requires a file, you can use the file name provided in the initial state.

Finish your answer with just YOUR FINAL ANSWER (do not ouput <think> or <tool> tags):
- YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.
- If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise.
- If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.
- If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.
"""
    return extract_prompt