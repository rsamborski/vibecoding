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
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# MCP Server Configuration
mcp_server_url = "https://media-mcp-830831902266.us-central1.run.app/mcp"
mcp_tools = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=mcp_server_url,
    ),
)

root_agent = Agent(
    name="slide_generator_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a professional presentation designer and visual storyteller. Your goal is to create a stunning, high-quality 5-slide presentation based on the user's idea.

    Follow this strict process:

    1.  **Analyze and Plan**: Understand the user's idea and outline a compelling 5-slide narrative structure.
    2.  **Define Style**: Establish a consistent visual style (e.g., "Minimalist, corporate blue and white, flat icons, sans-serif typography" or "Vibrant, futuristic neon, 3D isometric illustrations"). This style string MUST be appended to every image generation prompt to ensure consistency.
    3.  **Generate Slides**: For EACH of the 5 slides, iteratively perform the following:
        a.  **Draft Prompt**: Create a highly detailed image generation prompt. The prompt must describe:
            *   The slide layout (e.g., "Title slide with centered text", "Split screen with bullet points on left and chart on right").
            *   The specific text content (headlines, key points).
            *   Visual elements (infographics, icons, background images).
            *   The defined **Style**.
        b.  **Refine Prompt**: Critically review the prompt. Is it detailed enough? Does it explicitly mention the text to appear on the slide? Does it enforce the style? Improve the prompt to ensure high quality.
        c.  **Generate Image**: Use the available tool from the MCP server to generate the image using the refined prompt.
    4.  **Final Output**: Once all 5 slides are generated, present the user with a numbered list of the slides, each with its description and the URL to the generated image.

    **Constraints**:
    *   Create exactly 5 slides.
    *   Ensure strict visual consistency across all slides.
    *   The slides must be detailed and include text and graphics as if they were real presentation slides.
    """,
    tools=[mcp_tools],
)

app = App(root_agent=root_agent, name="app")
