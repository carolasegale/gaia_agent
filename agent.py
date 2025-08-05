from llama_index.core.agent.workflow import AgentWorkflow, ReActAgent
import whisper

class GAIA_Agent:
    def __init__(self, llm, tavily_api_key):
        self.llm = llm
        self.tavily_api_key = tavily_api_key
        
        # Setup tools
        self.model_whisper = whisper.load_model("base")  # Load Whisper model once
        self._setup_tools()

        # Setup agents
        self._setup_agents()


    def _setup_tools(self):
        from llama_index.core.tools import FunctionTool
        from tools import calculate, run_python_file, get_info_from_excel, get_audio_transcript #, get_youtube_transcript
        from llama_index.tools.wikipedia import WikipediaToolSpec
        from llama_index.tools.tavily_research.base import TavilyToolSpec

        # define tools 
        self.calculator_tool = FunctionTool.from_defaults(
            fn=calculate,
            name="calculator",
            description="A calculator that performs basic arithmetic operations."
        )

        '''
        self.youtube_tool = FunctionTool.from_defaults(
            fn=get_youtube_transcript,
            name="youtube_video_parser",
            description="A transcript extractor for youtube videos based on video path."
        )
        '''
        
        self.audio_tool = FunctionTool.from_defaults(
            fn=lambda file_path: get_audio_transcript(file_path, model_whisper=self.model_whisper),
            name="audio_parser",
            description="A simple transcript extractor for audio based on file."
        )

        self.run_python_tool = FunctionTool.from_defaults(
            fn=run_python_file,
            name="python_code_executor",
            description="Executes a .py file and returns the final printed numeric result."
        )

        self.excel_tool = FunctionTool.from_defaults(
            fn=get_info_from_excel,
            name="excel_parser",
            description="A simple tool to extract information from an Excel file and trasform it into markdown text."
        )

        self.created_tools = [
            self.calculator_tool,
            self.audio_tool,
            self.run_python_tool,
            self.excel_tool
        ] #youtube_tool

        self.wikipedia_tool_spec = WikipediaToolSpec()
        self.tavily_tool_spec = TavilyToolSpec(api_key=self.tavily_api_key)

    def _setup_agents(self):
        from prompts import create_system_prompt_for_main_agent, create_system_prompt_for_others

        self.multi_agent = ReActAgent(
            name='multi_functional_agent',
            description="A general AI assistant that can use perform calculation, parse files, and execute code.",
            system_prompt=create_system_prompt_for_main_agent(self.created_tools),
            tools=self.created_tools,
            llm=self.llm,
            verbose=False,
            can_handoff_to=['wikipedia_agent', 'search_agent']
        )

        self.wiki_agent = ReActAgent(
            name='wikipedia_agent',
            description="A general AI assistant that can search Wikipedia for information.",
            system_prompt=create_system_prompt_for_others(self.wikipedia_tool_spec.to_tool_list()),
            tools=self.wikipedia_tool_spec.to_tool_list(),
            llm=self.llm,
            verbose=False,
            can_handoff_to=['multi_functional_agent', 'search_agent']
        )

        self.search_agent = ReActAgent(
            name='search_agent',
            description="A general AI assistant that can search the web for information.",
            system_prompt=create_system_prompt_for_others(self.tavily_tool_spec.to_tool_list()),
            tools=self.tavily_tool_spec.to_tool_list(),
            llm=self.llm,
            verbose=False,
            can_handoff_to=['multi_functional_agent', 'wiki_agent']
        )

    # Create AgentWorkflow
    def build_workflow(self, file_name_dict):
        return AgentWorkflow(
            agents=[self.multi_agent, self.wiki_agent, self.search_agent],
            root_agent="multi_functional_agent",
            initial_state=file_name_dict  # equal to {'file_path': file_name} or {}
        )

    def get_answer(self, input, file_name_dict, memory=None):
        workflow = self.build_workflow(file_name_dict)
        return workflow.run(user_msg=input, memory=memory)