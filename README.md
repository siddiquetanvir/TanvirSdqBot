# TanvirSdqBot – Wikimedia Automation Tools

Python-based bots and scripts I developed as part of NDEC WERT (Notre Dame College Wikimedia Education & Research Team) to support Wikipedia and Wikidata editing in 2024.

Main achievements using these tools:
- Structured the newly created Fulani Wikipedia (~10,000 articles) by adding ~25 core categories (people, places, events, etc.) based on English Wikipedia patterns
- Automated welcome messages for new editors
- Processed and visualized data for Wikimedia Commons events (Wiki Loves Folklore, Wiki Loves Earth, etc.)

All code was originally developed in JupyterLab notebooks and tested live on Wikimedia projects.

## Repository Structure
- **Category/** → Scripts for bulk category mapping and assignment (core of the Fulani Wikipedia categorization project)
- **Welcome/** → Bot code for sending welcome messages to new users
- **Survey/** → Tools related to Wiki Loves event data collection, analysis, or surveys (heatmaps, stats)

## Technologies Used
- Python
- pywikibot (official Wikimedia bot framework)
- pandas, matplotlib (for data viz in related event analysis)
- MediaWiki / Wikidata APIs

## License
MIT License – feel free to reuse or adapt.

## Note
These are production-tested scripts copied from my personal notebooks. Some may require your own pywikibot setup and credentials.

Questions or forks? Open an issue or reach out.
