#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from crew_project.crew import YouTubeScript

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': input("Write a topic for a YouTube video: "),
        'youtube_video_url': "",
        'current_year': str(datetime.now().year)
    }
    try:
        YouTubeScript().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "Cómo escribir unit tests en python con pytest",
        "current_year": str(datetime.now().year)
    }
    try:
        YouTubeScript().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         CrewProject().crew().replay(task_id=sys.argv[1])

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "Cómo escribir unit tests en python con pytest",
        "current_year": str(datetime.now().year),
        "youtube_video_url": "https://www.youtube.com/watch?v=JZ0TMkwMgp8"
    }
    try:
        YouTubeScript().crew().test(n_iterations=int(sys.argv[1]), eval_llm="gpt-4.1", inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
