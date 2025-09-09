# Demo script

1. Basics
    1. Run Gemini-CLI in ~/projects/vibecoding/cloud-summit/demo
    1. Ask a generic question: How can you help me?
    1. Show basic options:
        1. About
        1. Help
        1. Tools
            1. /tools - in most cases Gemini CLI picks the right tool itself, you don’t have to tell it explicitly which tool to use
            1. Search with a question about current Weather
        1. ! command (note the not persistent shell)
            1. ! ls
            1. ! cat README.md
        1. Memory
            1. /memory add With every new feature update the [README.md](README.md) file to describe what it does. Don’t remove existing parts of the file such as the main title or author.
        1. [Gemini.md](Gemini.md) + hierarchy

2. Vibe coding
    1. Something simple, an ASCII art from prompt file

```
Create a single, full-screen HTML file containing a generative art piece using p5.js. The animation should be a dynamic, colorful, and continuously evolving geometric pattern that covers the entire browser window and resizes appropriately.
```
    1. Update colors, example:


```
Update @index.html to change colors to red and orange.
```

    1. Spec to app from diagram

```
Create a simple 3-tier newsfeed application based on the cloud-summit-demo.png diagram. Technical stack details are presented on the diagram.

Each item/news article should have following properties:
 - id
 - date
 - text
 - author

The UI should present a nicely formatted list of news, one under another with vertical scrolling. Use CSS to add distinct colors and make sure that the background is different between odd and even news items.

After creating the application, propagate the database with 10-15 sample news and start the backend service and connect the frontend to it, so I can test it from my browser.
```

```
Memory:
- When running Python code always use venv
```

1. MCP
    1. List servers
    1. Generate an image (?)

```
Generate a logo for this project that matches its spirit. Its purpose is to help users plan their day. Save it in img/logo.png file.
```

    1. Add the logo to the newly created application frontend
