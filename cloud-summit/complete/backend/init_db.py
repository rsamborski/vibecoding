import sqlite3
import datetime

# Connect to the database (creates the file if it doesn't exist)
connection = sqlite3.connect('news.db')
cursor = connection.cursor()

# Create the news table
cursor.execute('''CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    text TEXT NOT NULL,
    author TEXT NOT NULL
)''')

# Sample data
sample_news = [
    ('2025-09-08', 'Tech Giant Announces Breakthrough in AI Development.', 'Jane Doe'),
    ('2025-09-08', 'New Study Reveals Surprising Benefits of a Four-Day Work Week.', 'John Smith'),
    ('2025-09-07', 'Global Markets React to Unexpected Economic Shift.', 'Emily White'),
    ('2025-09-07', 'The Future of Space Exploration: A Look at the Next Decade.', 'Chris Green'),
    ('2025-09-06', 'Local Artist Wins Prestigious International Award.', 'Maria Garcia'),
    ('2025-09-06', 'Advancements in Renewable Energy Technology Unveiled.', 'David Lee'),
    ('2025-09-05', 'How Quantum Computing Will Change Everything.', 'Sarah Jones'),
    ('2025-09-05', 'New Health Initiative Launched to Promote Wellness.', 'Michael Brown'),
    ('2025-09-04', 'The Rise of a New Programming Language: A Developer\'s Guide.', 'Anna Williams'),
    ('2025-09-04', 'Exploring the Deep Sea: New Species Discovered.', 'Robert Taylor'),
    ('2025-09-03', 'A City\'s Transformation Through Urban Renewal Projects.', 'Linda Martinez'),
    ('2025-09-03', 'The Impact of a Hit New TV Series on Pop Culture.', 'James Wilson'),
    ('2025-09-02', 'Breakthrough in Medical Research Could Save Millions.', 'Patricia Anderson'),
    ('2025-09-02', 'How to Secure Your Digital Life in an Insecure World.', 'Richard Thomas'),
    ('2025-09-01', 'The Culinary World is Buzzing About This New Fusion Cuisine.', 'Jessica Hernandez')
]

# Insert sample data
cursor.executemany('INSERT INTO news (date, text, author) VALUES (?,?,?)', sample_news)

# Commit changes and close the connection
connection.commit()
connection.close()

print("Database initialized and populated with sample news.")
