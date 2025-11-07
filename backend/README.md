## Getting Started

to run our scraper you will need to

`brew install chromedrive`

Have a stable version of UV downloaded

`uv synv`

### Running the current scraper

`uv run python -m app.services.scraper.yc`

### Running the fastapi

`uv run python -m uvicorn app.main:app --reload`

# For DEVS

The basic run down:  
scrape YC/DevPost/Other Startup Incubators --> Embed Important project data --> Store in supabase with data + embedding -->
search with NL and get similar projects!!

#### Notes

Currently the scraper only grabs 10 projects from the bath you direct ex "Fall 2025" "Summer 2024"
it embeds these and stores relevant data in the supabase,

All routes & models & services are built for yc scraped data so create different files for other scraping!
