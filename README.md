# Digimon Scrapper and Graph

Personal project in which I use BeautifulSoup to scrap the from a list of Digimon and Appmon from https://digimon.fandom.com/ and save the information in .json.
Scrapped data is not 100% foolproof so needed to manually change some parts. The completed .json files are included.

## Graph of Digivolutions

The main goal of this project. I used my scrapped data which includes evo paths and used pyvis to plot a graph.
<p>
Legend for graph

- Blue edge = Normal and Jogress/Fusion
- Red edge = Slide evo
- Yellow edge = DigiXros
- Purple/Black edge = X-antibody

</p>

Just run digimon_graph_web.html or appmon_graph.html.

## Pre-requisites
- If you wanted to run the scripts, first run python -m  pip: -r requirements.txt
- Some parts of the script have to be uncommented to use them
