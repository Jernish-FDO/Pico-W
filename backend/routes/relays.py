"""
Relay control routes
Handles individual and bulk relay operations
"""

from flask import Blueprint, request, jsonify, g
from firebase_admin import db
from middleware.firebase_auth import require_auth, check_device_permissions, log_user_action
import logging
from datetime import datetime

relays_bp = Blueprint('relays', __name__)
logger = logging.getLogger(__name__)

@relays_bp.route('/<device_id>/<relay_id>', methods=['GET'])
@require_auth
def get_relay_status(device_id, relay_id):
    """Get status of a specific relay"""
    try:
        if not check_device_permissions(device_id):
            return jsonify({
                'error': 'Forbidden',
                'message': f'No permission to access device {device_id}'
            }), 403
        
        # Get relay data from Firebase
        relay_ref = db.reference(f'home_automation/devices/{device_id}/relays/{relay_id}')
        relay_data = relay_ref.get()
        
        if not relay_data:
            return jsonify({
                'error': 'Relay not found',
                'message': f'Relay {relay_id} not found on device {device_id}'
            }), 404
        
        relay_info = {
            'device_id': device_id,
            'relay_id': relay_id,
            'status': relay_data.get('status', False),
            'name': relay_data.get('name', relay_id),
            'power_usage': relay_data.get('power_usage', 0),
            'last_changed': relay_data.get('last_changed'),
            'total_runtime': relay_data.get('total_runtime', 0),
            'switch_count': relay_data.get('switch_count', 0)
        }
        
        return jsonify(relay_info)
        
    except Exception as e:
        logger.error(f"Error getting relay {relay_id} on device {device_id}: {e}")
        return jsonify({
            'error': 'Failed to retrieve relay status',
            'message': str(e)
        }), 500

@relays_bp.route('/<device_id>/<relay_id>', methods=['PUT'])
@require_auth
def control_relay(device_id, relay_id):
    """Control a specific relay (ON/OFF)"""
    try:
        if not check_device_permissions(device_id):
            return jsonify({
                'error': 'Forbidden',
                'message': f'No permission to control device {device_id}'
            }), 403
        
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Status field is required'
            }), 400
        
        new_status = bool(data['status'])
        
        # Update relay status in Firebase
        relay_ref = db.reference(f'home_automation/devices/{device_id}/relays/{relay_id}')
        
        # Get current relay data
        current_data = relay_ref.get() or {}
        
        # Prepare update data
        update_data = {
            'status': new_status,
            'last_changed': datetime.utcnow().isoformat(),
            'last_changed_by': g.current_user['uid']
        }
        
        # Increment switch count if status changed
        if current_data.get('status') != new_status:
            update_data['switch_count'] = current_data.get('switch_count', 0) + 1
        
        # Update relay
        relay_ref.update(update_data)
        
        # Update device last_update timestamp
        device_ref = db.reference(f'home_automation/devices/{device_id}')
        device_ref.update({'last_update': datetime.utcnow().isoformat()})
        
        log_user_action('CONTROL_RELAY', f'device:{device_id}/relay:{relay_id}', 
                       {'status': new_status})
        
        return jsonify({
            'message': f'Relay {relay_id} turned {"ON" if new_status else "OFF"}',
            'relay_id': relay_id,
            'device_id': device_id,
            'status': new_status,
            'timestamp': update_data['last_changed']
        })
        
    except Exception as e:
        logger.error(f"Error controlling relay {relay_id} on device {device_id}: {e}")
        return jsonify({
            'error': 'Failed to control relay',
            'message': str(e)
        }), 500

@relays_bp.route('/<device_id>/bulk', methods=['PUT'])
@require_auth
def bulk_control_relays(device_id):
    """Control multiple relays at once"""
    try:
        if not check_device_permissions(device_id):
            return jsonify({
                'error': 'Forbidden',
                'message': f'No permission to control device {device_id}'
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No data provided'
            }), 400
        
        # Handle bulk status change (all relays to same state)
        if 'status' in data:
            new_status = bool(data['status'])
            relay_ids = data.get('relay_ids', [])
            
            # If no specific relays specified, apply to all relays
            if not relay_ids:
                device_ref = db.reference(f'home_automation/devices/{device_id}/relays')
                all_relays = device_ref.get() or {}
                relay_ids = list(all_relays.keys())
            
            # Update each relay
            updates = {}
            timestamp = datetime.utcnow().isoformat()
            
            for relay_id in relay_ids:
                updates[f'home_automation/devices/{device_id}/relays/{relay_id}/status'] = new_status
                updates[f'home_automation/devices/{device_id}/relays/{relay_id}/last_changed'] = timestamp
                updates[f'home_automation/devices/{device_id}/relays/{relay_id}/last_changed_by'] = g.current_user['uid']
            
            # Update device timestamp
            updates[f'home_automation/devices/{device_id}/last_update'] = timestamp
            
            # Apply all updates atomically
            db.reference().update(updates)
            
            log_user_action('BULK_CONTROL_RELAYS', f'device:{device_id}', 
                           {'relay_count': len(relay_ids), 'status': new_status})
            
            return jsonify({
                'message': f'{len(relay_ids)} relays turned {"ON" if new_status else "OFF"}',
                'device_id': device_id,
                'affected_relays': relay_ids,
                'status': new_status,
                'timestamp': timestamp
            })
        
        # Handle individual relay updates
        elif 'relays' in data:
            updates = {}
            timestamp = datetime.utcnow().isoformat()
            updated_relays = []
            
            for relay_update in data['relays']:
                relay_id = relay_update.get('relay_id')
                status = relay_update.get('status')
                
                if relay_id and status is not None:
                    updates[f'home_automation/devices/{device_id}/relays/{relay_id}/status'] = bool(status)
                    updates[f'home_automation/devices/{device_id}/relays/{relay_id}/last_changed'] = timestamp
                    updates[f'home_automation/devices/{device_id}/relays/{relay_id}/last_changed_by'] = g.current_user['uid']
                    updated_relays.append({'relay_id': relay_id, 'status': bool(status)})
            
            if not updates:
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'No valid relay updates provided'
                }), 400
            
            # Update device timestamp
            updates[f'home_automation/devices/{device_id}/last_update'] = timestamp
            
            # Apply updates
            db.reference().update(updates)
            
            log_user_action('BULK_UPDATE_RELAYS', f'device:{device_id}', 
                           {'updates': updated_relays})
            
            return jsonify({
                'message': f'{len(updated_relays)} relays updated',
                'device_id': device_id,
                'updated_relays': updated_relays,
                'timestamp': timestamp
            })
        
        else:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Either "status" or "relays" field is required'
            }), 400
        
    except Exception as e:
        logger.error(f"Error in bulk relay control for device {device_id}: {e}")
        return jsonify({
            'error': 'Failed to control relays',
            'message': str(e)
        }), 500

@relays_bp.route('/<device_id>/toggle-all', methods=['POST'])
@require_auth
def toggle_all_relays(device_id):
    """Toggle all relays (ON becomes OFF, OFF becomes ON)"""
    try:
        if not check_device_permissions(device_id):
            return jsonify({
                'error': 'Forbidden',
                'message': f'No permission to control device {device_id}'
            }), 403
        
        # Get current relay states
        relays_ref = db.reference(f'home_automation/devices/{device_id}/relays')
        current_relays = relays_ref.get() or {}
        
        if not current_relays:
            return jsonify({
                'error': 'No relays found',
                'message': f'No relays found on device {device_id}'
            }), 404
        
        # Prepare toggle updates
        updates = {}
        timestamp = datetime.utcnow().isoformat()
        toggled_relays = []
        
        for relay_id, relay_data in current_relays.items():
            current_status = relay_data.get('status', False)
            new_status = not current_status
            
            updates[f'home_automation/devices/{device_id}/relays/{relay_id}/status'] = new_status
            updates[f'home_automation/devices/{device_id}/relays/{relay_id}/last_changed'] = timestamp
            updates[f'home_automation/devices/{device_id}/relays/{relay_id}/last_changed_by'] = g.current_user['uid']
            
            toggled_relays.append({
                'relay_id': relay_id,
                'previous_status': current_status,
                'new_status': new_status
            })
        
        # Update device timestamp
        updates[f'home_automation/devices/{device_id}/last_update'] = timestamp
        
        # Apply all updates
        db.reference().update(updates)
        
        log_user_action('TOGGLE_ALL_RELAYS', f'device:{device_id}', 
                       {'relay_count': len(toggled_relays)})
        
        return jsonify({
            'message': f'All {len(toggled_relays)} relays toggled',
            'device_id': device_id,
            'toggled_relays': toggled_relays,
            'timestamp': timestamp
        })
        
    except Exception as e:
        logger.error(f"Error toggling all relays on device {device_id}: {e}")
        return jsonify({
            'error': 'Failed to toggle relays',
            'message': str(e)
        }), 500

@relays_bp.route('/<device_id>/schedule', methods=['POST'])
@require_auth
def schedule_relay_action(device_id):
    """Schedule a relay action for future execution"""
    try:
        if not check_device_permissions(device_id):
            return jsonify({
                'error': 'Forbidden',
                'message': f'No permission to control device {device_id}'
            }), 403
        
        data = request.get_json()
        required_fields = ['relay_id', 'status', 'scheduled_time']
        
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Bad Request',
                'message': f'Required fields: {", ".join(required_fields)}'
            }), 400
        
        relay_id = data['relay_id']
        status = bool(data['status'])
        scheduled_time = data['scheduled_time']
        
        # Validate scheduled time
        try:
            scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            if scheduled_datetime <= datetime.utcnow():
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Scheduled time must be in the future'
                }), 400
        except ValueError:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Invalid datetime format'
            }), 400
        
        # Create scheduled action
        schedule_ref = db.reference(f'home_automation/devices/{device_id}/scheduled_actions')
        action_id = schedule_ref.push({
            'relay_id': relay_id,
            'status': status,
            'scheduled_time': scheduled_time,
            'created_by': g.current_user['uid'],
            'created_at': datetime.utcnow().isoformat(),
            'executed': False
        }).key
        
        log_user_action('SCHEDULE_RELAY', f'device:{device_id}/relay:{relay_id}', 
                       {'scheduled_time': scheduled_time, 'status': status})
        
        return jsonify({
            'message': 'Relay action scheduled successfully',
            'action_id': action_id,
            'device_id': device_id,
            'relay_id': relay_id,
            'status': status,
            'scheduled_time': scheduled_time
        })
        
    except Exception as e:
        logger.error(f"Error scheduling relay action on device {device_id}: {e}")
        return jsonify({
            'error': 'Failed to schedule relay action',
            'message': str(e)
        }), 500
