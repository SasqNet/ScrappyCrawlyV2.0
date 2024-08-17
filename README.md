Here is a `README.md` for your project:

```markdown
# ScrappyCrawly - Advanced Web Scraper

ScrappyCrawly is a Python-based advanced web scraping tool that can scrape data from single pages or crawl entire websites. It uses `Selenium` to handle JavaScript-rendered content, making it suitable for modern websites. Additionally, it can extract emails, phone numbers, images, and specific HTML elements.

## Features

- **Single Page Scraping**: Scrape data from a single web page.
- **Site Crawling**: Crawl and scrape data from multiple pages of a website.
- **Data Extraction**: Extract specific HTML elements by tag, class, and attribute.
- **Email and Phone Number Extraction**: Automatically find and extract emails and phone numbers.
- **Image Scraping**: Scrape images from websites.
- **Rate Limiting**: Adjustable rate limiting to avoid server overloads.
- **robots.txt Compliance**: Option to respect `robots.txt` directives.

## Requirements

- Python 3.8+
- Google Chrome browser
- ChromeDriver (corresponding to your Chrome version)

## Installation

1. Clone the repository:

   ```bash
   https://github.com/SasqNet/ScrappyCrawlyV2.0.git)
   cd scrappycrawly
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Download ChromeDriver and place it in the `drivers` directory within the project folder. Update the `CHROME_DRIVER_PATH` in `scraper.py` to point to this location.

5. Run the application:

   ```bash
   python app.py
   ```

## Usage

1. **URL**: Enter the URL of the website you want to scrape.
2. **HTML Tags**: Specify the HTML tags to scrape (e.g., `div`, `span`, `img`).
3. **HTML Classes**: Optionally, specify the classes of the elements to scrape.
4. **Attribute to Scrape**: Choose the attribute you want to scrape (e.g., `text`, `href`, `src`).
5. **Crawl Options**: Select whether to scrape a single page or crawl the entire site.
6. **Crawl Only for Links**: Option to only collect internal links.
7. **Scrape Images**: Check this option to scrape images from the site.
8. **Respect robots.txt**: Respect the site's `robots.txt` rules.
9. **Search for Emails/Phone Numbers**: Extract emails and phone numbers from the site.
10. **Export Data**: Export the scraped data to CSV, JSON, or Excel formats.

## PyInstaller Packaging

To package the application as a standalone executable using PyInstaller:

1. Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```

2. Create a `pyinstaller.spec` file to include the ChromeDriver:

   ```python
   # scraper.spec
   from PyInstaller.utils.hooks import collect_submodules

   hiddenimports = collect_submodules('selenium')

   a = Analysis(['app.py'],
                pathex=['.'],
                binaries=[('drivers/chromedriver', 'drivers')],
                hiddenimports=hiddenimports,
                ...)
   ```

3. Run the following command to generate the executable:

   ```bash
   pyinstaller --onefile --add-binary "drivers/chromedriver;drivers" app.py
   ```

   This will package the application along with the necessary ChromeDriver.

## Troubleshooting

- **Selenium Errors**: Ensure the correct version of ChromeDriver is installed for your Chrome browser version.
- **ModuleNotFoundError**: Make sure all dependencies are installed and the virtual environment is activated.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

Contributions are welcome! Please submit a pull request or create an issue to discuss your ideas.

## Acknowledgements

Special thanks to the open-source community for providing the tools and libraries used in this project.

```

This `README.md` provides a comprehensive overview of your project, including setup instructions, usage guidelines, and packaging with PyInstaller.
