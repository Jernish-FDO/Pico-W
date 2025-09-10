"""
Device management routes
Handles device status, configuration, and monitoring
"""

from flask import Blueprint, request, jsonify, g
from firebase_admin import db
from middleware.firebase_auth import require_auth, check_device_permissions, log_user_action
import logging
from datetime import datetime

devices_bp = Blueprint('devices', __name__)
logger = logging.getLogger(__name__)

@devices_bp.route('/', methods=['GET'])
@require_auth
def get_devices():
    """Get list of all devices accessible to current user"""
    try:
        # Get devices from Firebase
        devices_ref = db.reference('home_automation/devices')
        devices_data = devices_ref.get() or {}
        
        # Filter devices based on user permissions
        accessible_devices = {}
        
        for device_id, device_data in devices_data.items():
            if check_device_permissions(device_id):
                accessible_devices[device_id] = {
                    'id': device_id,
                    'name': device_data.get('name', device_id),
                    'online': device_data.get('online', False),
                    'last_update': device_data.get('last_update'),
                    'relay_count': len(device_data.get('relays', {})),
                    'active_relays': sum(1 for relay in device_data.get('relays', {}).values() 
                                       if relay.get('status', False)),
                    'type': device_data.get('type', 'pico_w'),
                    'firmware_version': device_data.get('firmware_version', '1.0.0')
                }
        
        log_user_action('GET_DEVICES', 'devices', {'count': len(accessible_devices)})
        
        return jsonify({
            'devices': accessible_devices,
            'total': len(accessible_devices)
        })
        
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return jsonify({
            'error': 'Failed to retrieve devices',
            'message': str(e)
        }), 500

@devices_bp.route('/<device_id>', methods=['GET'])
@require_auth
def get_device(device_id):
    """Get detailed information about a specific device"""
    try:
        if not check_device_permissions(device_id):
            return jsonify({
                'error': 'Forbidden',
                'message': f'No permission to access device {device_id}'
            }), 403
        
        # Get device data from Firebase
        device_ref = db.reference(f'home_automation/devices/{device_id}')
        device_data = device_ref.get()
        
        if not device_data:
            return jsonify({
                'error': 'Device not found',
                'message': f'Device {device_id} does not exist'
            }), 404
        
        # Calculate additional metrics
        relays = device_data.get('relays', {})
        active_relays = sum(1 for relay in relays.values() if relay.get('status', False))
        total_power = sum(relay.get('power_usage', 0) for relay in relays.values())
        
        device_info = {
            'id': device_id,
            'name': device_data.get('name', device_id),
            'online': device_data.get('online', False),
            'last_update': device_data.get('last_update'),
            'created_at': device_data.get('created_at'),
            'type': device_data.get('type', 'pico_w'),
            'firmware_version': device_data.get('firmware_version', '1.0.0'),
            'ip_address': device_data.get('ip_address'),
            'mac_address': device_data.get('mac_address'),
            'relays': relays,
            'statistics': {
                'total_relays': len(relays),
                'active_relays': active_relays,
                'total_power_usage': total_power,
                'uptime': device_data.get('uptime', 0),
                'system_load': device_data.get('system_load', 0)
            }
        }
        
        log_user_action('GET_DEVICE', f'device:{device_id}')
        
        return jsonify(device_info)
        
    except Exception as e:
        logger.error(f"Error getting device {device_id}: {e}")
        return jsonify({
            'error': 'Failed to retrieve device',
            'message': str(e)
        }), 500

@devices_bp.route('/<device_id>', methods=['PUT'])
@require_auth
def update_device(device_id):
    """Update device configuration"""
    try:
        if not check_device_permissions(device_id):
            return jsonify({
                'error': 'Forbidden',
                'message': f'No permission to modify device {device_id}'
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No data provided'
            }), 400
        
        # Validate input data
        allowed_fields = ['name', 'location', 'description']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No valid fields to update'
            }), 400
        
        # Update device in Firebase
        device_ref = db.reference(f'home_automation/devices/{device_id}')
        update_data['last_modified'] = datetime.utcnow().isoformat()
        device_ref.update(update_data)
        
        log_user_action('UPDATE_DEVICE', f'device:{device_id}', {'fields': list(update_data.keys())})
        
        return jsonify({
            'message': 'Device updated successfully',
            'updated_fields': list(update_data.keys())
        })
        
    except Exception as e:
        logger.error(f"Error updating device {device_id}: {e}")
        return jsonify({
            'error': 'Failed to update device',
            'message': str(e)
        }), 500

@devices_bp.route('/<device_id>/status', methods=['GET'])
@require_auth
def get_device_status(device_id):
    """Get real-time device status"""
    try:
        if not check_device_permissions(device_id):
            return jsonify({
                'error': 'Forbidden',
                'message': f'No permission to access device {device_id}'
            }), 403
        
        # Get device status from Firebase
        device_ref = db.reference(f'home_automation/devices/{device_id}')
        device_data = device_ref.get()
        
        if not device_data:
            return jsonify({
                'error': 'Device not found',
                'message': f'Device {device_id} does not exist'
            }), 404
        
        # Calculate system metrics
        relays = device_data.get('relays', {})
        active_relays = sum(1 for relay in relays.values() if relay.get('status', False))
        total_power = sum(relay.get('power_usage', 0) for relay in relays.values())
        
        last_update = device_data.get('last_update')
        is_recent = False
        if last_update:
            try:
                last_update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                time_diff = (datetime.utcnow() - last_update_time.replace(tzinfo=None)).total_seconds()
                is_recent = time_diff < 60  # Consider recent if updated within last minute
            except:
                pass
        
        status = {
            'device_id': device_id,
            'online': device_data.get('online', False) and is_recent,
            'last_update': last_update,
            'uptime': device_data.get('uptime', 0),
            'system_load': device_data.get('system_load', 0),
            'memory_usage': device_data.get('memory_usage', 0),
            'temperature': device_data.get('temperature'),
            'wifi_strength': device_data.get('wifi_strength'),
            'relay_summary': {
                'total': len(relays),
                'active': active_relays,
                'inactive': len(relays) - active_relays,
                'total_power': total_power
            },
            'health_status': 'healthy' if device_data.get('online', False) and is_recent else 'offline'
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting device status {device_id}: {e}")
        return jsonify({
            'error': 'Failed to retrieve device status',
            'message': str(e)
        }), 500

@devices_bp.route('/<device_id>/reboot', methods=['POST'])
@require_auth
def reboot_device(device_id):
    """Send reboot command to device"""
    try:
        if not check_device_permissions(device_id):
            return jsonify({
                'error': 'Forbidden',
                'message': f'No permission to reboot device {device_id}'
            }), 403
        
        # Send reboot command through Firebase
        command_ref = db.reference(f'home_automation/devices/{device_id}/commands')
        command_ref.push({
            'command': 'reboot',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': g.current_user['uid'],
            'status': 'pending'
        })
        
        log_user_action('REBOOT_DEVICE', f'device:{device_id}')
        
        return jsonify({
            'message': f'Reboot command sent to device {device_id}',
            'status': 'command_queued'
        })
        
    except Exception as e:
        logger.error(f"Error rebooting device {device_id}: {e}")
        return jsonify({
            'error': 'Failed to reboot device',
            'message': str(e)
        }), 500

@devices_bp.route('/<device_id>/logs', methods=['GET'])
@require_auth
def get_device_logs(device_id):
    """Get device logs"""
    try:
        if not check_device_permissions(device_id):
            return jsonify({
                'error': 'Forbidden',
                'message': f'No permission to access logs for device {device_id}'
            }), 403
        
        # Get pagination parameters
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = int(request.args.get('offset', 0))
        
        # Get logs from Firebase
        logs_ref = db.reference(f'home_automation/devices/{device_id}/logs')
        logs_data = logs_ref.order_by_key().limit_to_last(limit + offset).get() or {}
        
        # Convert to list and apply pagination
        logs_list = []
        for log_id, log_data in logs_data.items():
            logs_list.append({
                'id': log_id,
                'timestamp': log_data.get('timestamp'),
                'level': log_data.get('level', 'info'),
                'message': log_data.get('message'),
                'source': log_data.get('source')
            })
        
        # Sort by timestamp (newest first) and apply offset
        logs_list.sort(key=lambda x: x['timestamp'], reverse=True)
        paginated_logs = logs_list[offset:offset + limit]
        
        return jsonify({
            'logs': paginated_logs,
            'total': len(logs_list),
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Error getting logs for device {device_id}: {e}")
        return jsonify({
            'error': 'Failed to retrieve device logs',
            'message': str(e)
        }), 500
