from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import time
import logging
from typing import Dict, List
from functools import lru_cache
import os

logger = logging.getLogger(__name__)

class SantanderScraper:
    BASE_URL = "https://santandertrade.com"
    LOGIN_URL = f"{BASE_URL}/en/portal/login"
    
    # Mapping of country codes to their full names in URL format
    COUNTRY_URL_MAPPING = {
        'US': 'united-states',
        'CA': 'canada',
        'GB': 'united-kingdom',
        'DE': 'germany',
        'FR': 'france',
        'IT': 'italy',
        'ES': 'spain',
        'JP': 'japan',
        'CN': 'china',
        'IN': 'india'
    }
    
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self.setup_driver()
        # Initialize caches
        self._cache = {
            'general_info': {},
            'economic_data': {},
            'international_business': {}
        }
    
    def setup_driver(self):
        """Initialize the Chrome WebDriver with appropriate options."""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless=new")
                logger.info("Headless mode is enabled")
            
            # Add robust cross-platform options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-setuid-sandbox")
            chrome_options.add_argument("--disable-web-security")
            
            # Add logging preferences
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--v=1")
            
            # Increase timeouts and stability
            chrome_options.add_argument("--dns-prefetch-disable")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("Chrome WebDriver initialized successfully with ChromeDriverManager")
            except Exception as chrome_error:
                logger.warning(f"Failed to initialize with ChromeDriverManager: {str(chrome_error)}")
                logger.info("Attempting fallback to system ChromeDriver")
                
                # Fallback to system ChromeDriver
                try:
                    if os.name == 'posix':  # Linux/Unix
                        chromedriver_path = "/usr/bin/chromedriver"
                    else:  # Windows
                        chromedriver_path = "chromedriver.exe"
                    
                    self.driver = webdriver.Chrome(options=chrome_options)
                    logger.info("Chrome WebDriver initialized successfully with system ChromeDriver")
                except Exception as fallback_error:
                    logger.error(f"Fallback to system ChromeDriver failed: {str(fallback_error)}")
                    raise
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            
            # Add window size logging
            window_size = self.driver.get_window_size()
            logger.info(f"Browser window size: {window_size}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
            raise
    
    def format_country_url(self, country):
        """Format country name for URL."""
        # If country is a code (e.g., 'CA', 'US'), use the mapping
        if country in self.COUNTRY_URL_MAPPING:
            return self.COUNTRY_URL_MAPPING[country]
        
        # For full country names, convert to lowercase and replace spaces with hyphens
        return country.lower().replace(' ', '-')
    
    def handle_cookie_preferences(self):
        """Handle the cookie preferences popup."""
        try:
            # Wait a moment for any animations to complete
            time.sleep(2)
            
            # Try different cookie popup patterns
            cookie_patterns = [
                # Pattern 1: Standard cookie modal
                {
                    'modal': (By.CLASS_NAME, "modal-content"),
                    'button': (By.ID, "cookie-selection")
                },
                # Pattern 2: Alternative cookie modal
                {
                    'modal': (By.CLASS_NAME, "cookie-modal"),
                    'button': (By.CLASS_NAME, "cookie-accept")
                },
                # Pattern 3: Simple cookie banner
                {
                    'modal': (By.CLASS_NAME, "cookie-banner"),
                    'button': (By.CLASS_NAME, "cookie-button")
                }
            ]
            
            for pattern in cookie_patterns:
                try:
                    # Check if modal is present
                    modal = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(pattern['modal'])
                    )
                    
                    # Try to find and click the accept button
                    accept_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(pattern['button'])
                    )
                    accept_button.click()
                    logger.info("Cookie preferences accepted")
                    
                    # Wait for modal to disappear
                    WebDriverWait(self.driver, 5).until(
                        EC.invisibility_of_element_located(pattern['modal'])
                    )
                    return True
                    
                except TimeoutException:
                    logger.debug(f"Cookie pattern not found: {pattern}")
                    continue
                except Exception as e:
                    logger.debug(f"Error with cookie pattern {pattern}: {str(e)}")
                    continue
            
            # If we get here, no cookie popup was found or handled
            logger.info("No cookie popup found or already accepted")
            return True
            
        except Exception as e:
            logger.warning(f"Error handling cookie preferences: {str(e)}")
            return False
    
    def login(self, email, password):
        """Login to Santander Trade Portal."""
        try:
            # Navigate to homepage
            self.driver.get(self.BASE_URL)
            
            # Handle cookie preferences first
            self.handle_cookie_preferences()
            
            # Wait a moment for any animations to complete
            time.sleep(1)
            
            # Click login menu
            login_menu = self.driver.find_element(By.XPATH, '//*[@id="btn_login_menu"]')

            login_menu.click()
            
            # Fill login form
            email_input = self.driver.find_element(By.XPATH, '//*[@id="identification_identifiant"]')
            self.driver.execute_script("arguments[0].value = arguments[1];", email_input, email)

            password_input = self.driver.find_element(By.XPATH, '//*[@id="identification_mot_de_passe"]')
            self.driver.execute_script("arguments[0].value = arguments[1];", password_input, password)
            
            # Submit login form
            login_button = self.driver.find_element(By.XPATH, '//*[@id="identification_go"]')
            self.driver.execute_script("arguments[0].click();", login_button)
            
            # Wait for login to complete
            time.sleep(2)  # Add explicit wait for login completion
            
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def _safe_find_element(self, xpath: str, default: str = "Not found in data source") -> str:
        """Safely find an element and return its text or default value if not found."""
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            return element.text.strip()
        except NoSuchElementException:
            logger.warning(f"Element not found for XPath: {xpath}")
            return default
        except Exception as e:
            logger.warning(f"Error finding element for XPath {xpath}: {str(e)}")
            return default

    def get_country_general_info(self, country: str) -> Dict[str, str]:
        """Get general information data for a country."""
        # Check cache first
        if country in self._cache['general_info']:
            logger.info(f"Returning cached general info for {country}")
            return self._cache['general_info'][country]

        try:
            url = f"https://santandertrade.com/en/portal/analyse-markets/{self.format_country_url(country)}/general-presentation"
            logger.info(f"Accessing general info URL: {url}")
            self.driver.get(url)
            time.sleep(2)  # Wait for page load
            
            # Wait for the main content to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "contenu-contenu"))
            )

            self.driver.find_element(By.XPATH, '//*[@id="btn_header_select_language"]').click()

            self.driver.find_element(By.XPATH, '//*[@id="lnk_langue_en"]').click()
            
            # Extract data using XPath
            data = {
                'Official Name': self._safe_find_element('//h1[@id="pays_v1"]/span[@class="txt-h1_v1"]'),
                'Capital': self._safe_find_element('//p[@id="capitale"]/strong'),
                'Population': self._safe_find_element('//div[@id="donnees1"]//div[contains(@class, "titre-donnees")][1]'),
                'Area': self._safe_find_element('//div[@id="donnees1"]//div[contains(@class, "titre-donnees")][2]'),
                'Type of State': self._safe_find_element('//div[@id="donnees1"]//div[contains(@class, "titre-donnees")][3]'),
                'Head of State': self._safe_find_element('//div[@id="donnees1"]//div[contains(@class, "titre-donnees")][4]'),
                'Next Election': self._safe_find_element('//div[@id="donnees1"]//div[contains(@class, "titre-donnees")][5]'),
                'Currency': self._safe_find_element('//p[@id="monnaie"]'),
                'Exchange Rates': self._safe_find_element('//p[@id="monnaie"]/following-sibling::div[1]')
            }
            
            cleaned_data = self._clean_data(data)
            # Cache the result
            self._cache['general_info'][country] = cleaned_data
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error getting general info for {country}: {str(e)}")
            raise

    def get_country_economic_data(self, country: str) -> Dict:
        """Get country economic data from Santander Trade Portal."""
        # Check cache first
        if country in self._cache['economic_data']:
            logger.info(f"Returning cached economic data for {country}")
            return self._cache['economic_data'][country]

        try:
            # Navigate to the economic-political-outline page
            url = f"https://santandertrade.com/en/portal/analyse-markets/{self.format_country_url(country)}/economic-political-outline"
            logger.info(f"Accessing economic data URL: {url}")
            self.driver.get(url)

            self.driver.find_element(By.XPATH, '//*[@id="btn_header_select_language"]').click()

            self.driver.find_element(By.XPATH, '//*[@id="lnk_langue_en"]').click()

            time.sleep(2)


            self.driver.save_screenshot('screenshot.png')  
            
            # Wait for the content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "contenu"))
            )
            
            data = {}
            
            # Economic Overview
            data['Economic Overview'] = self._safe_find_element(
                "//div[@id='economique']//h3[text()='Economic Overview']/following-sibling::p[1]"
            )
            
            # Economic Freedom Indicators
            data['Economic Freedom Score'] = self._safe_find_element(
                "//div[@id='economique']//h3[text()='Indicator of Economic Freedom']/following-sibling::dl[contains(@class, 'informations')]//dt[text()='Score:']/following-sibling::dd[1]"
            )
            data['Economic Freedom World Rank'] = self._safe_find_element(
                "//div[@id='economique']//h3[text()='Indicator of Economic Freedom']/following-sibling::dl[contains(@class, 'informations')]//dt[text()='World Rank:']/following-sibling::dd[1]"
            )
            data['Economic Freedom Regional Rank'] = self._safe_find_element(
                "//div[@id='economique']//h3[text()='Indicator of Economic Freedom']/following-sibling::dl[contains(@class, 'informations')]//dt[text()='Regional Rank:']/following-sibling::dd[1]"
            )
            
            # Business Environment Ranking
            data['Business Environment Score'] = self._safe_find_element(
                "//div[@id='economique']//h3[text()='Business environment ranking']/following-sibling::dl[contains(@class, 'informations')]//dt[text()='Score:']/following-sibling::dd[1]"
            )
            data['Business Environment World Rank'] = self._safe_find_element(
                "//div[@id='economique']//h3[text()='Business environment ranking']/following-sibling::dl[contains(@class, 'informations')]//dt[text()='World Rank:']/following-sibling::dd[1]"
            )
            
            # Main Economic Indicators
            data['GDP'] = self._safe_find_element(
                "//table//th[contains(text(), 'GDP') and not(contains(text(), 'Constant Prices')) and not(contains(text(), 'per Capita'))]/following-sibling::td[1]"
            )
            data['GDP Growth'] = self._safe_find_element(
                "//table//th[contains(text(), 'GDP') and contains(text(), 'Constant Prices, Annual % Change')]/following-sibling::td[1]"
            )
            data['GDP per Capita'] = self._safe_find_element(
                "//table//th[contains(text(), 'GDP per Capita')]/following-sibling::td[1]"
            )
            data['Inflation Rate'] = self._safe_find_element(
                "//table//th[contains(text(), 'Inflation Rate')]/following-sibling::td[1]"
            )
            data['Unemployment Rate'] = self._safe_find_element(
                "//table//th[contains(text(), 'Unemployment Rate')]/following-sibling::td[1]"
            )
            data['Current Account'] = self._safe_find_element(
                "//table//th[contains(text(), 'Current Account') and not(contains(text(), '%'))]/following-sibling::td[1]"
            )
            
            # Main Sectors
            data['Main Sectors'] = self._safe_find_element(
                "//div[@id='economique']//h3[text()='Main Sectors of Industry']/following-sibling::p[1]"
            )
            
            # Employment by Sector
            data['Agriculture Employment'] = self._safe_find_element(
                "//table//th[contains(text(), 'Employment By Sector')]/following-sibling::td[1]"
            )
            data['Industry Employment'] = self._safe_find_element(
                "//table//th[contains(text(), 'Employment By Sector')]/following-sibling::td[2]"
            )
            data['Services Employment'] = self._safe_find_element(
                "//table//th[contains(text(), 'Employment By Sector')]/following-sibling::td[3]"
            )
            
            # Value Added by Sector
            data['Agriculture Value Added'] = self._safe_find_element(
                "//table//th[contains(text(), 'Value Added') and not(contains(text(), 'Annual'))]/following-sibling::td[1]"
            )
            data['Industry Value Added'] = self._safe_find_element(
                "//table//th[contains(text(), 'Value Added') and not(contains(text(), 'Annual'))]/following-sibling::td[2]"
            )
            data['Services Value Added'] = self._safe_find_element(
                "//table//th[contains(text(), 'Value Added') and not(contains(text(), 'Annual'))]/following-sibling::td[3]"
            )
            
            cleaned_data = self._clean_data(data)
            # Cache the result
            self._cache['economic_data'][country] = cleaned_data
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error getting economic data for {country}: {str(e)}")
            return {}

    def _clean_data(self, data: Dict[str, str]) -> Dict[str, str]:
        """Clean and format the scraped data."""
        cleaned_data = {}
        for key, value in data.items():
            if value and value != "Not found in data source":
                # Remove any extra whitespace
                value = ' '.join(value.split())
                # Remove any special characters or formatting
                value = value.replace('\n', ' ').replace('\r', '')
                # Remove label text if present (e.g., "Population: 1,000,000" -> "1,000,000")
                if ':' in value:
                    value = value.split(':', 1)[1].strip()
                cleaned_data[key] = value
            else:
                cleaned_data[key] = "Not found in data source"
        return cleaned_data

    def get_country_international_business(self, country: str) -> Dict:
        """Get international business data from Santander Trade Portal."""
        # Check cache first
        if country in self._cache['international_business']:
            logger.info(f"Returning cached international business data for {country}")
            return self._cache['international_business'][country]

        try:
            url = f"https://santandertrade.com/en/portal/analyse-markets/{self.format_country_url(country)}/foreign-trade-in-figures"
            logger.info(f"Accessing international business URL: {url}")
            self.driver.get(url)

            self.driver.find_element(By.XPATH, '//*[@id="btn_header_select_language"]').click()

            self.driver.find_element(By.XPATH, '//*[@id="lnk_langue_en"]').click()

            time.sleep(2)
            
              # Wait for page load

            data = {}
            
            # Define table XPaths and their corresponding "See More" link IDs
            tables = {
                'Foreign Trade Values': {
                    'xpath': '//*[@id="encart-theme-atlas"]/div[1]/div/div[2]/div[1]/table',
                    'alt_xpath': '//table[contains(., "Foreign Trade Values")]',
                    'see_more_id': 'atlas_pays_export_lien'
                },
                'Foreign Trade Indicators': {
                    'xpath': '//*[@id="encart-theme-atlas"]/div[1]/div/div[3]/div[1]/table',
                    'alt_xpath': '//table[contains(., "Foreign Trade Indicators")]',
                    'see_more_id': 'atlas_pays_import_lien'
                },
                'Foreign Trade Forecasts': {
                    'xpath': '//*[@id="encart-theme-atlas"]/div[1]/div/div[3]/div[1]/table',
                    'alt_xpath': '//table[contains(., "Foreign Trade Forecasts")]',
                    'see_more_id': 'atlas_export_lien'
                },
                'Main Customers': {
                    'xpath': '//*[@id="doubletableau"]/table[1]',
                    'alt_xpath': '//table[contains(., "Main Customers")]',
                    'see_more_id': 'atlas_import_lien'
                },
                'Main Suppliers': {
                    'xpath': '//*[@id="doubletableau"]/table[2]',
                    'alt_xpath': '//table[contains(., "Main Suppliers")]',
                    'see_more_id': 'atlas_import_lien'
                },
                'Main Services Exported': {
                    'xpath': '//*[@id="doubletableau"]/table[1]',
                    'alt_xpath': '//table[contains(., "Main Services")]',
                    'see_more_id': 'atlas_export_lien'
                },
                'Main Services Imported': {
                    'xpath': '//*[@id="doubletableau"]/table[2]',
                    'alt_xpath': '//table[contains(., "Main Services")]',
                    'see_more_id': 'atlas_import_lien'
                }
            }

            # Extract each table
            for table_name, table_info in tables.items():
                logger.info(f"\nExtracting {table_name}...")
                # Try primary XPath first
                table_data = self._extract_table_data(table_info['xpath'], table_info['see_more_id'])
                if not table_data:
                    logger.info(f"Primary XPath failed, trying alternative for {table_name}")
                    # Try alternative XPath if primary fails
                    table_data = self._extract_table_data(table_info['alt_xpath'], table_info['see_more_id'])
                
                if table_data:
                    data[table_name] = table_data
                else:
                    logger.warning(f"Failed to extract {table_name}")
                    data[table_name] = []

            # Add sources
            data['Sources'] = {
                'Foreign Trade Values': 'World Trade Organisation (WTO)',
                'Foreign Trade Indicators': 'World Bank',
                'Foreign Trade Forecasts': 'IMF, World Economic Outlook',
                'Main Partner Countries': 'Comtrade',
                'Main Services': 'United Nations Statistics Division'
            }

            # Cache the result
            self._cache['international_business'][country] = data
            return data

        except Exception as e:
            logger.error(f"Error getting international business data: {str(e)}")
            return {}
    
    def _extract_table_data(self, table_xpath: str, see_more_id: str = None) -> List[Dict]:
        """Extract data from a table using XPath."""
        try:
            logger.info(f"Looking for table with XPath: {table_xpath}")
            
            # Wait longer for table to be present
            try:
                table = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, table_xpath))
                )
                logger.info("Table found")
            except TimeoutException:
                logger.warning(f"Table not found with XPath: {table_xpath}")
                return []

            # Ensure table is visible
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", table)
                time.sleep(1)  # Wait for any animations
                
                # Check if table is actually visible
                if not table.is_displayed():
                    logger.warning("Table found but not visible")
                    return []
            except Exception as e:
                logger.warning(f"Error checking table visibility: {str(e)}")

            # Try to click the specific "See More" link if provided
            if see_more_id:
                try:
                    see_more = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.ID, see_more_id))
                    )
                    if see_more.is_displayed():
                        logger.info(f"Clicking 'See More' link: {see_more_id}")
                        # Scroll to the link
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", see_more)
                        time.sleep(1)
                        # Try multiple click methods
                        try:
                            see_more.click()
                        except:
                            try:
                                self.driver.execute_script("arguments[0].click();", see_more)
                            except Exception as click_error:
                                logger.warning(f"Failed to click 'See More' link: {str(click_error)}")
                        time.sleep(2)  # Wait longer for content to load
                except Exception as e:
                    logger.warning(f"No 'See More' link found with ID: {see_more_id}")

            # Get all rows with retry
            max_retries = 3
            for attempt in range(max_retries):
                rows = table.find_elements(By.TAG_NAME, "tr")
                if rows:
                    break
                logger.warning(f"No rows found, attempt {attempt + 1} of {max_retries}")
                time.sleep(1)
            
            if not rows:
                logger.warning("No rows found in table after all retries")
                return []

            # Get headers with better error handling
            headers = []
            header_cells = rows[0].find_elements(By.TAG_NAME, "th")
            if not header_cells:
                header_cells = rows[0].find_elements(By.TAG_NAME, "td")
            
            if not header_cells:
                logger.warning("No header cells found in table")
                return []
            
            headers = []
            for cell in header_cells:
                try:
                    text = cell.text.strip()
                    if text:
                        headers.append(text)
                except Exception as e:
                    logger.warning(f"Error getting header text: {str(e)}")
            
            if not headers:
                logger.warning("No valid headers found")
                return []
            
            logger.info(f"Found headers: {headers}")

            # Extract data from rows with better error handling
            data = []
            for row_index, row in enumerate(rows[1:], 1):  # Skip header row
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) == len(headers):
                        # Skip rows that contain "Close Extended List"
                        row_text = ' '.join(cell.text.strip() for cell in cells)
                        if "Close Extended List" in row_text:
                            continue
                            
                        row_data = {}
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                try:
                                    value = cell.text.strip()
                                    if value:  # Only add non-empty values
                                        row_data[headers[i]] = value
                                except Exception as cell_error:
                                    logger.warning(f"Error getting cell text at row {row_index}, column {i}: {str(cell_error)}")
                        
                        if row_data:  # Only add non-empty rows
                            data.append(row_data)
                except Exception as row_error:
                    logger.warning(f"Error processing row {row_index}: {str(row_error)}")
                    continue

            logger.info(f"Extracted {len(data)} rows of data")
            return data

        except Exception as e:
            logger.error(f"Error extracting table data: {str(e)}")
            return []

    def get_country_general_presentation(self, country: str) -> Dict[str, str]:
        """Get combined general and economic data for a country."""
        try:
            # Get general information
            general_data = self.get_country_general_info(country)
            
            # Get economic data
            economic_data = self.get_country_economic_data(country)
            
            # Get international business data
            international_data = self.get_country_international_business(country)
            
            # Combine the data
            combined_data = {
                **general_data,
                **economic_data,
                'international_business': international_data
            }
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error getting combined data for {country}: {str(e)}")
            raise
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache = {
            'general_info': {},
            'economic_data': {},
            'international_business': {}
        }
        logger.info("Cache cleared")

    def close(self):
        """Close the WebDriver and clear cache."""
        if self.driver:
            self.driver.quit()
        self.clear_cache() 