from flask import render_template, request, redirect, url_for, flash, session, make_response, jsonify
from flask_login import login_required, current_user
from app.routes import bp
from app.services.report_service import ReportService
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

@bp.route('/')
@login_required
def index():
    # Only clear report data, preserve login session
    if 'report_data' in session:
        del session['report_data']
    if 'report_id' in session:
        del session['report_id']
    
    # Render the template with no products or categories context
    return render_template('index.html')

@bp.route('/generate-report', methods=['POST'])
@login_required
def generate_report():
    try:
        # Generate a unique report ID
        report_id = str(uuid.uuid4())
        logger.info(f"Generating new report with ID: {report_id}")
        
        data = request.form
        
        # Extract form data
        origin_country = data.get('origin_country')
        destination_country = data.get('destination_country')
        hs6_code = data.get('hs6_code')
        sector = data.get('sector')
        
        logger.info(f"Processing report for Origin: {origin_country}, Destination: {destination_country}")
        logger.info(f"HS6 code: {hs6_code}")
        logger.info(f"Sector: {sector}")
        
        # Validate input
        if not all([origin_country, destination_country, hs6_code, sector]):
            flash('All fields are required', 'error')
            return redirect(url_for('main.index'))
        
        # Generate report
        report_service = ReportService()
        result = report_service.generate_report(
            origin_country=origin_country,
            destination_country=destination_country,
            hs6_codes=[hs6_code],  # Wrap in list for compatibility
            sectors=[sector]  # Wrap in list for compatibility
        )
        
        if result['status'] == 'error':
            flash(result['message'], 'error')
            return redirect(url_for('main.index'))
        
        # Store report data in session with unique ID
        report_data = {
            'report_id': report_id,
            'origin_country': result['data']['origin_country'],
            'destination_country': result['data']['destination_country'],
            'hs6_codes': result['data']['hs6_codes'],
            'sectors': result['data']['sectors'],
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info(f"Storing report data in session. Report ID: {report_id}")
        logger.info(f"Report data includes origin: {origin_country}, destination: {destination_country}")
        
        # Store in session
        session['report_data'] = report_data
        session.modified = True
        
        flash('Report generated successfully!', 'success')
        return redirect(url_for('main.view_report'))
        
    except Exception as e:
        logger.error(f"Error in generate_report: {str(e)}")
        flash('An unexpected error occurred while generating the report', 'error')
        return redirect(url_for('main.index'))

@bp.route('/report')
@login_required
def view_report():
    report_data = session.get('report_data')
    logger.info(f"Viewing report. Session data exists: {report_data is not None}")
    
    if not report_data:
        logger.warning("No report data found in session")
        flash('No report data found. Please generate a new report.', 'error')
        return redirect(url_for('main.index'))
    
    # Create a copy of the report data to prevent session modification
    report_data_copy = dict(report_data)
    logger.info(f"Report data copied. Origin: {report_data_copy.get('origin_country')}, Destination: {report_data_copy.get('destination_country')}")
    
    return render_template('report.html', report_data=report_data_copy)

@bp.route('/api/initialize-report', methods=['POST'])
@login_required
def api_initialize_report():
    try:
        data = request.get_json()
        country_code = data.get('country_code')
        if not country_code:
            return jsonify({'status': 'error', 'message': 'Missing country_code'}), 400
        
        report_service = ReportService()
        result = report_service.initialize_report_generation(country_code)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@bp.route('/api/generate-section', methods=['POST'])
@login_required
def api_generate_section():
    try:
        data = request.get_json()
        section_name = data.get('section_name')
        country_code = data.get('country_code')
        origin_country = data.get('origin_country')
        if not section_name or not country_code:
            return jsonify({'status': 'error', 'message': 'Missing section_name or country_code'}), 400
        
        report_service = ReportService()
        result = report_service.generate_section(section_name, country_code)
        
        # Store section data in session
        if result['status'] == 'success':
            if 'report_sections' not in session:
                session['report_sections'] = {}
            session['report_sections'][section_name] = result
            session.modified = True
        
        # If this is the last section, clean up and prepare report data
        if section_name == 'international_business' and result['status'] == 'success':
            report_service.cleanup_report_generation()
            
            # Prepare complete report data
            report_data = {
                'report_id': str(uuid.uuid4()),
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'sections': session.get('report_sections', {}),
                'destination_country': country_code,  # Store as simple string
                'origin_country': origin_country,    # Store as simple string
                'report_type': 'Market Analysis Report'
            }
            session['report_data'] = report_data
            session.modified = True
            
            # Clear sections data
            if 'report_sections' in session:
                del session['report_sections']
            
            # Add redirect flag to response
            result['redirect'] = url_for('main.view_report')
            
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in generate_section: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}) 