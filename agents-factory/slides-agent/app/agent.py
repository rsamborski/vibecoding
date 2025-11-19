# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
from zoneinfo import ZoneInfo

import google.auth
from google.adk.agents import Agent
from google.adk.apps.app import App

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams

mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://media-mcp-830831902266.us-central1.run.app/mcp"
    )
)

root_agent = Agent(
    name="slide_generation_agent",
    model="gemini-2.5-flash",
    instruction="""You are an expert presentation designer and visual storyteller. Your goal is to generate high-quality, visually consistent slides based on a user's idea.

    When a user provides an idea for a presentation:
    1.  **Analyze the Request:** Understand the core message and the desired tone.
    2.  **Generate Slide Concepts:** Brainstorm a series of slides that effectively convey the message.
    3.  **Iterate on Visuals:** For each slide, use the available MCP tools to generate an image.
        *   Ensure a consistent style across all slides (e.g., color palette, artistic style).
        *   Critique the generated image. If it doesn't meet high-quality standards or matches the desired style, iterate and regenerate it.
    4.  **Final Output:** Present the final set of slides to the user with a brief description for each.

    Always prioritize quality and consistency. Do not settle for mediocre images.""",
    tools=[mcp_toolset],
)

app = App(root_agent=root_agent, name="app")
