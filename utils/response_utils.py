from flask import jsonify

def success_response(data=None, message=None, status=200):
    """Standard success response"""
    response = {'success': True}
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return jsonify(response), status

def error_response(message, status=400):
    """Standard error response"""
    return jsonify({'success': False, 'error': message}), status

def paginated_response(data, page, per_page, total):
    """Paginated response"""
    return jsonify({
        'success': True,
        'data': data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }), 200
