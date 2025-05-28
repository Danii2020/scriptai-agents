import re
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, YoutubeVideoSearchTool

from .tools.notion_tool import NotionTool
from .tools.docx_read_tool import DocxReadTool


# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class YouTubeScript():
	"""YouTubeScript crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def youtuber_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['youtuber_manager'],
			verbose=True,
			allow_delegation=True,
        )

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=True,
			tools=[SerperDevTool()]
		)

	# @agent
	# def youtube_video_researcher(self) -> Agent:
	# 	youtube_search_tool = YoutubeVideoSearchTool()
	# 	return Agent(
	# 		config=self.agents_config['youtube_video_researcher'],
	# 		verbose=True,
	# 		tools=[youtube_search_tool]
	# 	)

	@agent
	def screenwriter(self) -> Agent:
		return Agent(
			config=self.agents_config['screenwriter'],
			verbose=True,
			tools=[DocxReadTool("/Users/danielerazo/Documents/yt-scripts/script-template-en.docx")],
			allow_delegation=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			output_key="research_output"
		)

	# @task
	# def youtube_research_task(self) -> Task:
	# 	def extract_youtube_link(context):
	# 		research_output = context["research_output"]
	# 		match = re.search(r"(https?://(?:www\.)?youtube\.com/\S+)", research_output)
	# 		if match:
	# 			return { "youtube_video_url": match.group(1) }
	# 		else:
	# 			raise ValueError("No YouTube URL found in research output!")
	# 	return Task(
	# 		config=self.tasks_config['youtube_research_task'],
	# 		context_callback=extract_youtube_link,
	# 		output_key="youtube_research_output"
	# 	)

	@task
	def screenwriting_task(self) -> Task:
		return Task(
			config=self.tasks_config['screenwriting_task']
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the LatestTechAnalysis crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge
		manager = self.youtuber_manager()
		agents = [agent for agent in self.agents if agent is not manager]
		return Crew(
			agents=agents,
			tasks=self.tasks,
			process=Process.hierarchical,
			manager_agent=manager,
			verbose=True,
		)
