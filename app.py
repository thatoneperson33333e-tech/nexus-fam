from flask import Flask, request, jsonify
import re
import random
import os

app = Flask(__name__)

class UPIHandler:
    def __init__(self):
        self.vpa_handles = ['@fam', '@okfam', '@axl', '@ybl']
    
    def validate_phone(self, phone):
        """Advanced phone number validation"""
        if not phone:
            return False, "Phone number is required"
        
        # Clean the phone number
        clean_phone = re.sub(r'[^\d]', '', str(phone))
        
        # Validate Indian phone numbers (10 digits starting with 6-9)
        if len(clean_phone) == 10 and clean_phone[0] in '6789':
            return True, clean_phone
        elif len(clean_phone) == 12 and clean_phone.startswith('91'):
            return True, clean_phone[2:]
        else:
            return False, "Invalid Indian phone number format"

    def generate_upi_id(self, phone):
        """Generate unique UPI ID for phone number"""
        valid, result = self.validate_phone(phone)
        if not valid:
            return {"error": result}
        
        phone_num = result
        handle = random.choice(self.vpa_handles)
        
        # Multiple UPI ID formats for variety
        formats = [
            f"fampay.user{phone_num[-4:]}{handle}",
            f"fam{phone_num}{handle}",
            f"fampay{phone_num[-6:]}{handle}",
            f"user.phone{phone_num[-4:]}{handle}"
        ]
        
        upi_id = random.choice(formats)
        
        return {
            "status": "success",
            "phone": phone_num,
            "upi_id": upi_id,
            "qr_data": f"upi://pay?pa={upi_id}&pn=FamPay%20User&am=&cu=INR",
            "message": "UPI ID generated successfully"
        }

# Initialize UPI handler
upi_handler = UPIHandler()

@app.route('/')
def home():
    return jsonify({
        "message": "FamPay UPI API is running",
        "version": "1.0",
        "endpoints": {
            "/fam": "POST - Generate UPI ID from phone number",
            "/health": "GET - API health check"
        }
    })

@app.route('/fam', methods=['POST', 'GET'])
def generate_fam_upi():
    """Generate FamPay UPI ID from phone number"""
    
    try:
        # Handle both POST and GET requests
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                phone = data.get('phone')
            else:
                phone = request.form.get('phone')
        else:  # GET request
            phone = request.args.get('phone')
        
        if not phone:
            return jsonify({
                "status": "error",
                "message": "Phone number parameter is required. Use 'phone' parameter."
            }), 400
        
        result = upi_handler.generate_upi_id(phone)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "FamPay UPI API",
        "timestamp": "2024-01-01T00:00:00Z"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
