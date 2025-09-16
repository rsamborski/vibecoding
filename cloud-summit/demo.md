# Demo script

1. Basics

* Run Gemini-CLI in ~/projects/vibecoding/cloud-summit/demo
* Ask a generic question: How can you help me?
* Show basic options:
    * About
    * Help
    * Tools
        * /tools - in most cases Gemini CLI picks the right tool itself, you don’t have to tell it explicitly which tool to use
        * Search with a question about current Weather
    * ! command (note the not persistent shell)
        * ! ls
            * ! cat README.md
    * Memory
        * /memory add When running Python code always use venv 
    * [Gemini.md](Gemini.md) + hierarchy

2. Vibe coding

* Something simple, an ASCII art from prompt file

```
Create a single, full-screen HTML file containing a generative art piece using p5.js. The animation should be a dynamic, colorful, and continuously evolving geometric pattern that covers the entire browser window and resizes appropriately.
```

* Update colors, example:

```
Update @index.html to change colors to red and orange.
```


* Spec to app from diagram

```
Create a simple 3-tier newsfeed application based on the @cloud-summit-demo.png diagram. Technical stack details are presented on the diagram.

Each item/news article should have following properties:
 - id
 - date
 - text
 - author

The UI should present a nicely formatted list of news, one under another with vertical scrolling.

After creating the application, propagate the database with 10-15 sample news and start the backend service and connect the frontend to it, so I can test it from my browser.
```

It takes time to generate, so show an app prepared earlier by Gemini:
```
# Shell 1
cd complete
venv/bin/python3 backend/app.py 

# Shell 2
cd complete/frontend
npm run dev
```

3. MCP

* List servers
* Generate an image (?)

```
Generate a logo for this project that matches its spirit. Its aspiring to be a main source of news for its users. Save it in a folder accessible by the frontend app. The logo should have a maximum height of 50px.
```

* (if not added automatically) Add the logo to the newly created application frontend

```
Update the frontend application to show the newly generated logo at the top.
```

4. README

```
Update @README.md to reflect the newly added features.
```
