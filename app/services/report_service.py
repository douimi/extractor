from app.scrapers.santander import SantanderScraper
from app.services.openai_service import OpenAIService
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self):
        self.santander_scraper = None
        self.openai_service = OpenAIService()
    
    def initialize_scrapers(self):
        """Initialize all scrapers."""
        try:
            # Always create a new scraper instance
            if self.santander_scraper:
                self.santander_scraper.close()
                self.santander_scraper = None
                
            self.santander_scraper = SantanderScraper(headless=True)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize scrapers: {str(e)}")
            return False
    
    def login_to_santander(self, email: str, password: str) -> bool:
        """Login to Santander Trade Portal."""
        if not self.santander_scraper:
            if not self.initialize_scrapers():
                return False
        return self.santander_scraper.login(email, password)
    
    def get_country_data(self, country: str) -> Optional[Dict]:
        """Get country data from Santander Trade Portal."""
        if not self.santander_scraper:
            return None
        try:
            return self.santander_scraper.get_country_general_presentation(country)
        except Exception as e:
            logger.error(f"Error getting data for {country}: {str(e)}")
            return None
    
    def generate_report(self, origin_country: str, destination_country: str, hs6_codes: List[str], sectors: List[str]) -> Dict:
        """Generate a complete report for the given parameters."""
        try:
            # Initialize scrapers if not already done
            if not self.santander_scraper:
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
            if self.santander_scraper:
                self.santander_scraper.close()
                self.santander_scraper = None 