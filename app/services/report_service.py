from app.scrapers.santander import SantanderScraper
from app.services.openai_service import OpenAIService
import logging
from typing import Dict, List, Optional
from flask import session

logger = logging.getLogger(__name__)

class ScraperManager:
    _instance = None
    _scraper = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_scraper(cls):
        return cls._scraper

    @classmethod
    def set_scraper(cls, scraper):
        if cls._scraper is not None:
            cls._scraper.close()
        cls._scraper = scraper

    @classmethod
    def cleanup(cls):
        if cls._scraper is not None:
            cls._scraper.close()
            cls._scraper = None

class ReportService:
    def __init__(self):
        self.openai_service = OpenAIService()
    
    def initialize_scrapers(self):
        """Initialize all scrapers."""
        try:
            # Create a new scraper instance
            scraper = SantanderScraper(headless=True)
            ScraperManager.set_scraper(scraper)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize scrapers: {str(e)}")
            return False
    
    def login_to_santander(self, email: str, password: str) -> bool:
        """Login to Santander Trade Portal."""
        scraper = ScraperManager.get_scraper()
        if not scraper:
            if not self.initialize_scrapers():
                return False
            scraper = ScraperManager.get_scraper()
        return scraper.login(email, password)

    def generate_section(self, section_name: str, country_code: str) -> Dict:
        """Scrape and generate AI content for a single section (3 sections, 3 URLs)."""
        try:
            scraper = ScraperManager.get_scraper()
            if not scraper:
                return {'status': 'error', 'message': 'Scraper not initialized'}

            # Get data using the existing scraper instance
            if section_name == 'general_info':
                data = scraper.get_country_general_info(country_code)
            elif section_name == 'economic_data':
                data = scraper.get_country_economic_data(country_code)
            elif section_name == 'international_business':
                raw_data = scraper.get_country_international_business(country_code)
                
                # Structure the international business data
                data = {
                    'foreign_trade_values': [],
                    'foreign_trade_indicators': [],
                    'main_customers': [],
                    'main_suppliers': [],
                    'main_services_exported': [],
                    'main_services_imported': []
                }
                
                # Process each data point and add to appropriate category
                for key, value in raw_data.items():
                    if isinstance(value, list):
                        for item in value:
                            if 'Foreign Trade Values' in item:
                                data['foreign_trade_values'].append(item)
                            elif 'Foreign Trade Indicators' in item:
                                data['foreign_trade_indicators'].append(item)
                            elif 'Main Customers' in str(item):
                                data['main_customers'].append(item)
                            elif 'Main Suppliers' in str(item):
                                data['main_suppliers'].append(item)
                            elif 'Main Services Exported' in str(item):
                                data['main_services_exported'].append(item)
                            elif 'Main Services Imported' in str(item):
                                data['main_services_imported'].append(item)
            else:
                return {'status': 'error', 'message': f'Unknown section: {section_name}'}

            # Generate AI content
            intro = self.openai_service.generate_section_introduction(country_code, section_name, data)
            conclusion = self.openai_service.generate_section_insights(country_code, section_name, data)
            
            return {
                'status': 'success',
                'section': section_name,
                'data': data,
                'intro': intro,
                'conclusion': conclusion
            }
        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def initialize_report_generation(self, country_code: str) -> Dict:
        """Initialize scraper and login for a new report generation session."""
        try:
            # Initialize scraper if needed
            if not self.initialize_scrapers():
                return {'status': 'error', 'message': 'Failed to initialize scrapers'}
            
            # Login to Santander
            if not self.login_to_santander("edgarcayuelas@indegate.com", "Indegate@2020"):
                return {'status': 'error', 'message': 'Failed to login to Santander Trade Portal'}
            
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def cleanup_report_generation(self):
        """Clean up resources after report generation is complete."""
        ScraperManager.cleanup()

    def get_country_data(self, country: str) -> Optional[Dict]:
        """Get country data from Santander Trade Portal."""
        scraper = ScraperManager.get_scraper()
        if not scraper:
            return None
        try:
            data = scraper.get_country_general_presentation(country)
            if data:
                # Generate section-specific content
                sections = {
                    'general_info': {
                        'Official Name': data.get('Official Name'),
                        'Capital': data.get('Capital'),
                        'Population': data.get('Population'),
                        'Area': data.get('Area'),
                        'Type of State': data.get('Type of State'),
                        'Head of State': data.get('Head of State')
                    },
                    'economic_overview': {
                        'Economic Overview': data.get('Economic Overview')
                    },
                    'economic_indicators': {
                        'GDP': data.get('GDP'),
                        'GDP Growth': data.get('GDP Growth'),
                        'GDP per Capita': data.get('GDP per Capita'),
                        'Inflation Rate': data.get('Inflation Rate'),
                        'Unemployment Rate': data.get('Unemployment Rate'),
                        'Current Account': data.get('Current Account')
                    },
                    'business_environment': {
                        'Business Environment Score': data.get('Business Environment Score'),
                        'Business Environment World Rank': data.get('Business Environment World Rank'),
                        'Economic Freedom Score': data.get('Economic Freedom Score'),
                        'Economic Freedom World Rank': data.get('Economic Freedom World Rank')
                    },
                    'trade_profile': data.get('international_business', {})
                }

                # Generate content for each section
                for section_name, section_data in sections.items():
                    try:
                        intro = self.openai_service.generate_section_introduction(country, section_name, section_data)
                        conclusion = self.openai_service.generate_section_insights(country, section_name, section_data)
                        data[f'{section_name}_intro'] = intro
                        data[f'{section_name}_conclusion'] = conclusion
                    except Exception as e:
                        logger.error(f"Error generating content for {section_name}: {str(e)}")
                        data[f'{section_name}_intro'] = f"Error generating introduction for {section_name}"
                        data[f'{section_name}_conclusion'] = f"Error generating conclusion for {section_name}"

            return data
        except Exception as e:
            logger.error(f"Error getting data for {country}: {str(e)}")
            return None
    
    def generate_report(self, origin_country: str, destination_country: str, hs6_codes: List[str], sectors: List[str]) -> Dict:
        """Generate a complete report for the given parameters."""
        try:
            # Initialize scrapers if not already done
            if not self.initialize_scrapers():
                raise Exception("Failed to initialize scrapers")
            
            # Login to Santander
            if not self.login_to_santander("edgarcayuelas@indegate.com", "Indegate@2020"):
                raise Exception("Failed to login to Santander Trade Portal")
            
            # Get data for destination country
            logger.info(f"Fetching data for destination country: {destination_country}")
            destination_data = self.get_country_data(destination_country)
            
            if not destination_data:
                raise Exception(f"Failed to fetch data for destination country: {destination_country}")
            
            # Prepare the result data
            result_data = {
                'country': {
                    'code': destination_country,
                    'data': destination_data
                },
                'origin_country_code': origin_country,
                'origin_country': origin_country,
                'destination_country': destination_country,
                'hs6_codes': hs6_codes,
                'sectors': sectors,
                'report_type': 'Market Analysis Report'
            }
            
            # Generate AI content
            logger.info("Generating AI content for the report...")
            try:
                ai_sections = self.openai_service.generate_report_sections(result_data)
                executive_summary = self.openai_service.generate_executive_summary(result_data)
                
                result_data['ai_content'] = {
                    'introduction': ai_sections['introduction'],
                    'conclusion': ai_sections['conclusion'],
                    'executive_summary': executive_summary
                }
                logger.info("Successfully generated AI content")
            except Exception as e:
                logger.error(f"Error generating AI content: {str(e)}")
                result_data['ai_content'] = {
                    'introduction': "Error generating introduction",
                    'conclusion': "Error generating conclusion",
                    'executive_summary': "Error generating executive summary"
                }
            
            logger.info(f"Generated report data for destination country: {destination_country}")
            
            return {
                'status': 'success',
                'data': result_data
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
        finally:
            # Clean up
            self.cleanup_report_generation() 