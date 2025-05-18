import os
import openai
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service to generate dynamic content using OpenAI."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        openai.api_key = self.api_key

    def is_configured(self) -> bool:
        """Check if the OpenAI service is properly configured."""
        return self.api_key is not None
    
    def generate_section_introduction(self, country: str, section_name: str, section_data: Dict) -> str:
        """Generate a dynamic introduction for a section of the report.
        
        Args:
            country: The name of the country
            section_name: The name of the section (e.g., 'General Information', 'Economic Overview')
            section_data: Dictionary containing the data for this section
            
        Returns:
            A generated introduction paragraph for the section
        """
        if not self.is_configured():
            logger.warning("OpenAI service not configured. Using default introduction.")
            return f"This section provides information about {section_name} for {country}."
        
        try:
            # Format the section data for the prompt
            formatted_data = "\n".join([f"{key}: {value}" for key, value in section_data.items()])
            
            prompt = f"""
            You are an expert market research analyst. Generate a concise, informative, and professional introduction 
            for the '{section_name}' section of a market report for {country}.
            
            Here is the data for this section:
            {formatted_data}
            
            Write a paragraph (3-5 sentences) that introduces this section, explains why this data is important 
            for businesses looking to enter the market, and highlights 1-2 key insights from the data.
            Be specific about {country} and use actual values from the data.
            Keep your response under 150 words and use professional business language.
            Do not use placeholders or variables - incorporate the actual data values into your text.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional market analyst writing a report section."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            introduction = response.choices[0].message.content.strip()
            logger.info(f"Generated introduction for {section_name} section for {country}")
            return introduction
            
        except Exception as e:
            logger.error(f"Error generating section introduction: {str(e)}")
            return f"This section provides key information about {section_name} for {country}, which is essential for market analysis and business planning."
    
    def generate_section_insights(self, country: str, section_name: str, section_data: Dict) -> str:
        """Generate insights and recommendations based on section data.
        
        Args:
            country: The name of the country
            section_name: The name of the section
            section_data: Dictionary containing the data for this section
            
        Returns:
            Generated insights and recommendations
        """
        if not self.is_configured():
            logger.warning("OpenAI service not configured. Using default insights.")
            return f"Based on the {section_name} data, consider key metrics when planning your market entry strategy."
        
        try:
            # Format the section data for the prompt
            formatted_data = "\n".join([f"{key}: {value}" for key, value in section_data.items()])
            
            prompt = f"""
            As a market research expert, analyze the following '{section_name}' data for {country} and provide 
            2-3 specific business insights or recommendations based on this data.
            
            Data:
            {formatted_data}
            
            Provide practical, actionable insights that would help a business understand the implications of this data 
            for market entry or expansion. Reference specific metrics and explain their significance.
            Keep your response under 100 words and focus on concrete takeaways.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional market analyst writing a report section."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            insights = response.choices[0].message.content.strip()
            logger.info(f"Generated insights for {section_name} section for {country}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating section insights: {str(e)}")
            return f"Based on the {section_name} data, businesses should closely monitor key metrics and trends when planning market entry or expansion strategies."
    
    def generate_country_recommendations(self, country: str, country_data: Dict) -> List[str]:
        """Generate country-specific recommendations based on all data.
        
        Args:
            country: The name of the country
            country_data: All the data for this country
            
        Returns:
            List of recommendation strings
        """
        if not self.is_configured():
            logger.warning("OpenAI service not configured. Using default recommendations.")
            return [
                f"Consider key economic indicators when planning your market entry strategy in {country}",
                f"Evaluate the business environment score for regulatory compliance planning",
                f"Monitor political developments and upcoming elections for potential policy changes",
                f"Focus on sectors with highest value-added contribution to GDP"
            ]
        
        try:
            # Format the country data for the prompt - simplified version to keep within token limits
            key_metrics = {
                "GDP": country_data.get("GDP", "Not available"),
                "GDP Growth": country_data.get("GDP Growth", "Not available"),
                "Inflation Rate": country_data.get("Inflation Rate", "Not available"),
                "Unemployment Rate": country_data.get("Unemployment Rate", "Not available"),
                "Economic Freedom Score": country_data.get("Economic Freedom Score", "Not available"),
                "Business Environment Score": country_data.get("Business Environment Score", "Not available"),
                "Type of State": country_data.get("Type of State", "Not available"),
                "Next Election": country_data.get("Next Election", "Not available"),
                "Services Value Added": country_data.get("Services Value Added", "Not available"),
                "Industry Value Added": country_data.get("Industry Value Added", "Not available")
            }
            
            formatted_data = "\n".join([f"{key}: {value}" for key, value in key_metrics.items()])
            
            prompt = f"""
            As a market research expert, provide 5 specific, actionable recommendations for a business 
            considering market entry or expansion in {country} based on the following data:
            
            {formatted_data}
            
            Generate 5 concise, bullet-point recommendations that address:
            1. Market entry strategy
            2. Risk management
            3. Sector focus
            4. Regulatory/political considerations
            5. Economic conditions
            
            Each recommendation should be 1-2 sentences long, specific to {country}, and reference actual data points.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional market analyst writing a report section."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            recommendations_text = response.choices[0].message.content.strip()
            
            # Parse bullet points into a list
            recommendations = []
            for line in recommendations_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or (len(line) > 2 and line[0].isdigit() and line[1] == '.')):
                    recommendations.append(line.lstrip('-•0123456789. '))
                elif line and not any(char in line for char in '-•0123456789.'):
                    recommendations.append(line)
            
            # Filter out empty strings and limit to 5 recommendations
            recommendations = [r for r in recommendations if r][:5]
            
            logger.info(f"Generated {len(recommendations)} recommendations for {country}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating country recommendations: {str(e)}")
            return [
                f"Consider key economic indicators when planning your market entry strategy in {country}",
                f"Evaluate the business environment score for regulatory compliance planning",
                f"Monitor political developments and upcoming elections for potential policy changes",
                f"Focus on sectors with highest value-added contribution to GDP",
                f"Develop contingency plans to address economic volatility and inflation risks"
            ]
    
    def generate_overall_recommendations(self, report_data: Dict) -> Dict[str, List[str]]:
        """Generate overall recommendations based on the entire report.
        
        Args:
            report_data: The complete report data
            
        Returns:
            Dictionary with recommendation categories and lists of recommendation strings
        """
        if not self.is_configured():
            logger.warning("OpenAI service not configured. Using default overall recommendations.")
            return {
                "Market Entry Strategy": [
                    "Prioritize countries with higher economic freedom scores",
                    "Consider joint ventures in countries with complex regulatory environments",
                    "Focus on sectors with highest value-added contribution"
                ],
                "Risk Management": [
                    "Monitor political developments, especially around election periods",
                    "Account for currency fluctuations in financial planning",
                    "Develop contingency plans for economic volatility"
                ],
                "Operational Considerations": [
                    "Adapt business models to local market conditions",
                    "Consider local employment regulations and labor market conditions",
                    "Develop strong local partnerships"
                ]
            }
        
        try:
            # Create a summary of the report data for the prompt
            origin_country = report_data.get('origin_country', 'Not specified')
            countries = list(report_data.get('country_data', {}).keys())
            sectors = report_data.get('sectors', [])
            hs6_codes = report_data.get('hs6_codes', [])
            
            country_metrics = {}
            for country, data in report_data.get('country_data', {}).items():
                country_metrics[country] = {
                    "GDP Growth": data.get("GDP Growth", "Not available"),
                    "Economic Freedom Score": data.get("Economic Freedom Score", "Not available"),
                    "Business Environment Score": data.get("Business Environment Score", "Not available")
                }
            
            summary = f"""
            Report Summary:
            - Origin Country: {origin_country}
            - Destination Countries: {', '.join(countries)}
            - Sectors: {', '.join(sectors)}
            - HS6 Codes: {', '.join(hs6_codes)}
            
            Key Metrics by Country:
            """
            
            for country, metrics in country_metrics.items():
                summary += f"\n{country}:\n"
                for key, value in metrics.items():
                    summary += f"- {key}: {value}\n"
            
            prompt = f"""
            As a market research expert, provide strategic recommendations for a business 
            based in {origin_country} looking to expand into these markets:
            
            {summary}
            
            Generate 3-4 specific recommendations for each of these categories:
            1. Market Entry Strategy
            2. Risk Management
            3. Operational Considerations
            
            Each recommendation should be one sentence, actionable, and based on the data provided.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional market analyst writing a report section."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            recommendations_text = response.choices[0].message.content.strip()
            
            # Parse the recommendations by category
            categories = {
                "Market Entry Strategy": [],
                "Risk Management": [],
                "Operational Considerations": []
            }
            
            current_category = None
            for line in recommendations_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if any(category.lower() in line.lower() for category in categories.keys()):
                    for category in categories.keys():
                        if category.lower() in line.lower():
                            current_category = category
                            break
                elif current_category and (line.startswith('-') or line.startswith('•') or (len(line) > 2 and line[0].isdigit() and line[1] == '.')):
                    categories[current_category].append(line.lstrip('-•0123456789. '))
                elif current_category and line:
                    # Handle case where bullet points might be missing
                    categories[current_category].append(line)
            
            # Ensure we have at least some recommendations for each category
            for category, recs in categories.items():
                if not recs:
                    if category == "Market Entry Strategy":
                        categories[category] = [
                            "Prioritize countries with higher economic freedom scores",
                            "Consider joint ventures in countries with complex regulatory environments",
                            "Focus on sectors with highest value-added contribution"
                        ]
                    elif category == "Risk Management":
                        categories[category] = [
                            "Monitor political developments, especially around election periods",
                            "Account for currency fluctuations in financial planning",
                            "Develop contingency plans for economic volatility"
                        ]
                    else:  # Operational Considerations
                        categories[category] = [
                            "Adapt business models to local market conditions",
                            "Consider local employment regulations and labor market conditions",
                            "Develop strong local partnerships"
                        ]
            
            logger.info(f"Generated overall recommendations with {sum(len(v) for v in categories.values())} total recommendations")
            return categories
            
        except Exception as e:
            logger.error(f"Error generating overall recommendations: {str(e)}")
            return {
                "Market Entry Strategy": [
                    "Prioritize countries with higher economic freedom scores",
                    "Consider joint ventures in countries with complex regulatory environments",
                    "Focus on sectors with highest value-added contribution"
                ],
                "Risk Management": [
                    "Monitor political developments, especially around election periods",
                    "Account for currency fluctuations in financial planning",
                    "Develop contingency plans for economic volatility"
                ],
                "Operational Considerations": [
                    "Adapt business models to local market conditions",
                    "Consider local employment regulations and labor market conditions",
                    "Develop strong local partnerships"
                ]
            }

    def generate_report_sections(self, report_data: Dict) -> Dict[str, str]:
        """Generate introduction and conclusion sections for the report using OpenAI."""
        try:
            # Extract relevant data for the prompt
            country = report_data['country']['code']
            country_data = report_data['country']['data']
            origin_country = report_data['origin_country_code']

            # Create the introduction prompt
            intro_prompt = f"""
            Write a professional and engaging introduction for a market analysis report about {country}. 
            The report is being generated for a company from {origin_country} interested in understanding the market.
            
            Include the following key points:
            - Brief overview of {country}'s economic status
            - Key strengths of the market
            - Potential opportunities for international business
            
            Use this economic data in your introduction:
            GDP: {country_data.get('GDP', 'N/A')}
            GDP Growth: {country_data.get('GDP Growth', 'N/A')}
            Population: {country_data.get('Population', 'N/A')}
            
            Keep the tone professional and the length to about 250 words.
            """

            # Create the conclusion prompt
            conclusion_prompt = f"""
            Write a professional conclusion for a market analysis report about {country}.
            This conclusion is for a company from {origin_country} considering market entry.
            
            Include:
            - Summary of key findings
            - Main opportunities and challenges
            - Strategic recommendations for market entry
            
            Base your conclusion on these indicators:
            Business Environment Score: {country_data.get('Business Environment Score', 'N/A')}
            Economic Freedom Score: {country_data.get('Economic Freedom Score', 'N/A')}
            Current Economic Overview: {country_data.get('Economic Overview', 'N/A')}
            
            Keep the tone professional and actionable, with a length of about 250 words.
            """

            # Generate introduction
            intro_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional market analyst writing a report section."},
                    {"role": "user", "content": intro_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            # Generate conclusion
            conclusion_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional market analyst writing a report section."},
                    {"role": "user", "content": conclusion_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return {
                'introduction': intro_response.choices[0].message.content.strip(),
                'conclusion': conclusion_response.choices[0].message.content.strip()
            }

        except Exception as e:
            logger.error(f"Error generating report sections with OpenAI: {str(e)}")
            return {
                'introduction': f"Error generating introduction: {str(e)}",
                'conclusion': f"Error generating conclusion: {str(e)}"
            }

    def generate_executive_summary(self, report_data: Dict) -> Optional[str]:
        """Generate an executive summary for the report using OpenAI."""
        try:
            # Extract relevant data
            country = report_data['country']['code']
            country_data = report_data['country']['data']
            origin_country = report_data['origin_country_code']

            # Create the executive summary prompt
            summary_prompt = f"""
            Create a concise executive summary for a market analysis report about {country}.
            This report is prepared for a company from {origin_country}.

            Key data points:
            - GDP: {country_data.get('GDP', 'N/A')}
            - Population: {country_data.get('Population', 'N/A')}
            - Business Environment Score: {country_data.get('Business Environment Score', 'N/A')}
            - Economic Freedom Score: {country_data.get('Economic Freedom Score', 'N/A')}

            The summary should:
            1. Highlight key market opportunities
            2. Summarize main economic indicators
            3. Provide a brief market entry recommendation
            
            Keep it professional and concise, around 150 words.
            """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional market analyst writing an executive summary."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating executive summary with OpenAI: {str(e)}")
            return None 