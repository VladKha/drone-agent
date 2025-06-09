import os

from PIL import Image
from dotenv import load_dotenv
from smolagents import CodeAgent, PythonInterpreterTool, FinalAnswerTool
from smolagents.agents import ActionStep

from drone_agent.rate_limit_models import ExponentialBackoffOpenAIServerModel
from drone_agent.tools import (takeoff, land, take_picture, move_forward, move_backward, move_left, move_right,
                               move_up, move_down, turn_left, turn_right, get_battery)
from drone_agent.observability import setup_observability


# setup env
load_dotenv()
setup_observability()

# model
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = 'gemini-2.0-flash'
model = ExponentialBackoffOpenAIServerModel(GEMINI_MODEL,
                                            api_base='https://generativelanguage.googleapis.com/v1beta/openai/',
                                            api_key=GEMINI_API_KEY,
                                            max_tokens=8096 * 2)

def save_picture(step_log: ActionStep, agent: CodeAgent) -> None:
    current_step = step_log.step_number

    # Remove previous screenshots from logs for lean processing
    for memory_step in agent.memory.steps:
        if isinstance(step_log, ActionStep) and step_log.step_number <= current_step - 2:
            memory_step.observations_images = None
    frame = take_picture()
    image = Image.fromarray(frame)
    print(f"Captured a picture: {image.size} pixels")
    step_log.observations_images = [image.copy()]  # Create a copy to ensure it persists, important!

agent = CodeAgent(
    model=model,
    tools=[
        takeoff,
        land,
        take_picture,
        move_forward,
        move_backward,
        move_left,
        move_right,
        move_up,
        move_down,
        turn_left,
        turn_right,
        PythonInterpreterTool(),
        FinalAnswerTool()
    ],
    step_callbacks=[save_picture],
    additional_authorized_imports=[
        "pandas",
        "json",
        "pandas",
        "numpy"],
    max_steps=30,
    verbosity_level=10
)

drone_instruction = f"""
You are navigating a drone. You should follow the user's instructions to fulfill the mission or give advice on user's input if it's not clear or not reasonable.
First create a detailed plan. Then execute it.
Use provided tools for navigation and exploration of the surrounding environment.
Actively use the turning tools to change the direction of the drone and explore more around you.
If you find some object right away - you can use the navigation tools to move the drone around.
Any drone mission should start from takeoff and end with land.
In case of multiple failures - land the drone and restart from the beginning.

First you need to take off the drone.
Code:
```py
takeoff()
```<end_code>

You can directly move the drone around forward, backward, left, right, up and down.
Code:
```py
move_forward(100) # move forward by 100 cm
move_backward(100) # move backward by 100 cm
move_left(100) # move left by 100 cm
move_right(100) # move right by 100 cm
move_up(100) # move up by 100 cm
move_down(100) # move down by 100 cm
```<end_code>

You can also turn the drone left and right to see more around you.
Code:
```py
turn_left(90) # turn left by 90 degrees
turn_right(90) # turn right by 90 degrees
```<end_code>

You can also take a picture and analyze later.
Code:
```py
take_picture() # take a picture
```<end_code>

After the end of mission - land the drone.
Code:
```py
land()
```<end_code>
""".strip()


while True:
    print(get_battery())
    task = input("Enter your mission: ")

    if task in ['exit', 'q']:
        print(get_battery())
        break

    task = f"""{drone_instruction}\n\nUser task: {task}""".strip()
    mission_log = agent.run(task, images=[Image.fromarray(take_picture())])
    print(mission_log)
    print(get_battery())

# tests
# demo_tasks = [
#     # Basic tasks
#     "Take off the drone.",
#     "Land the drone.",
#     "Take off the drone. Wait for 3 seconds, then land it back.",
#     "Move the drone forward by 100 cm.",
#     "Move the drone backward by 100 cm.",
#     "Move the drone left by 100 cm.",
#     "Move the drone right by 100 cm.",
#     "Move the drone up by 100 cm.",
#     "Move the drone down by 100 cm.",
#     "Turn the drone counter-clockwise by 90 degrees.",
#
#     # More complex tasks
#     "Describe the environment around you",
#     "Describe the environment 360 degrees around you",
#     "What do you see?",
#     "Find something I can eat.",
#     "Find a chair for me.",
#     "Find an apple and move closer to it.",
#     "Find a person in military-like clothes.",
#     "Explore the territory 1 meter around you.",
#     "Explore territory 1 meter 360 degrees around you and summarize the important details you've noticed",
# ]
# for task in demo_tasks:
#     task = f"""{drone_instruction}\n\nUser task: {task}""".strip()
#     mission_log = agent.run(task, images=[Image.fromarray(take_picture())])
#     print(mission_log)
#     print('\n\n' + '-'*80 + '\n\n')
