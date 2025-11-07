# Scaling the YC Scraper

## Overview

current YC scraper successfully:

- Loads a single batch page (e.g. `Fall 2025`)
- Scrapes the first set of companies
- Visits each company detail page
- Extracts project data (name, short/long description, metadata)
- Stores structured results into Supabase + embeddings

Now, we’ll **scale it** to handle:

- All pages in a batch (infinite scroll)
- Multiple batches automatically
- Duplicate prevention
- Rate limiting
- (Optional) Parallel scraping

---

## 1. Handle Infinite Scroll (Pagination)

YC’s startup list uses infinite scroll, not numbered pages.  
we need to simulate scrolling until all companies load.

## 2.
