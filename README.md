# CS:GO Chat Bot 2.0

Rewrite of my csgo chat bot

A chatbot for CS:GO that reads the CS:GO console over telnet. The chat commands can be sent using the chat or the console.

Huge thanks to [@403-Fruit](https://github.com/403-Fruit) for sharing [this project](https://github.com/403-Fruit/csctl)! The project helped me a lot when figuring out how to do things.

## Setup

Add the following to the CS:GO launch options:

    -netconport 2121  
    
Add your Steam and faceit API keys to the `config.py` file to get the `!info` command to work fully:

    steam_api_key = '' # Steam web API key here to get steam/game stats
    faceit_api_key = '' # Faceit API key here to get faceit levels

Run the chat bot:

    python cscb.py

## Chat commands

    !help               - Prints out the list of avaible commands to the chat
    
    !info <name>        - Tries to get <name>'s game stats including: K/D ratio, Play time and 
                         total rounds played on the current map.
                         
    !github             - Prints a link to this repository
    
    !dz                 - Prints the current and next danger zone map
                      
    !calc <expression>  - Calculates the math expression in <math> and returns the answer
                         Example:
                           !calc (5 + 5) * 2
    
    !mute <string>      - Adds the string to the clear list
                          The bot will send a chat clear message when it detects the string in the chat name or message
    
    !unmute <string>    - Removes the string from the clear list
    
## Console commands

    !info               - Get the info table containing all the players manually
                          This prints the whole table in easy to read format to the cmd
                         
    !dz_map             - Toggles the auto notification for dz map changes
    
    !dz                 - Echoes the current and next danger zone map
    
    !zeus_shot          - Does the zeus shot visual bug where you can shoot the zeus wires from your currently held weapon
                          This is only visible for other players
                         
    !lowjump            - Performs the lowjump consistently for some pixelsurfs
