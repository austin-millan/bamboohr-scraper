"""Wrapper module that runs BambooHR scraper locally."""

from bamboohr_scraper import bamboohr_scraper
scraper = bamboohr_scraper.BambooHRScraper()
scraper.run()
