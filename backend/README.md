## Getting Started

to run our scraper you will need to

`brew install chromedrive`

Have a stable version of UV downloaded

`uv sync`

### Running the scrapers

`uv run python -m app.services.scraper.yc`
`uv run python -m app.services.scraper.topstartups`
`uv run python -m app.services.scraper.productHunt`
`uv run python -m app.services.scraper.devpost`

### Running the fastapi

`uv run python -m uvicorn app.main:app --reload`

## Visualize the embeddings

`uv run python -m app.services.visualizer.visualize`

# For DEVS

The basic run down:  
scrape YC/DevPost/Other Startup Incubators --> Embed Important project data --> Store in supabase with data + embedding -->
search with NL and get similar projects!!

## ENV Information:

OPENAI_API_KEY="API KEY HERE"
SUPABASE_URL="SUPABASE URL HERE"
SUPABASE_KEY="SUPABASE KEY HERE"
GEMINI_API_KEY="API KEY HERE"

#### Notes

Currently the YC scraper only grabs 10 projects from the bath you direct ex "Fall 2025" "Summer 2024"
it embeds these and stores relevant data in the supabase.

Product hunt scraper takes in `year, month, day` in order to run on a specific date to scrape.

You can use the model for projects, but it is primarly buily for the YC scrape, feel free to create different files for other scrapers!
