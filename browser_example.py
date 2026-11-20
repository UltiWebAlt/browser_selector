import webbrowser

# Define the URL you want to open
url = "https://example.com"

# Specify the path to Firefox or just 'firefox' if it's in your system path
# %s is a placeholder required by the webbrowser module for the URL
ff_path = "firefox"

try:
    # Register Firefox and open the URL
    webbrowser.get(ff_path).open(url)
except webbrowser.Error:
    # Fallback to the system's default browser if Firefox isn't registered
    webbrowser.open(url)
