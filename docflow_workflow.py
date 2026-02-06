"""
modules/workflow/engine.py - Workflow Execution Engine
DocFlow Pro - Enterprise Document Automation
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

class WorkflowState(Enum):
    """Workflow states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class NodeType(Enum):
    """Workflow node types"""
    START = "start"
    APPROVAL = "approval"
    ASSIGN = "assign"
    NOTIFY = "notify"
    CONDITION = "condition"
    END = "end"

class WorkflowNode:
    """Represents a workflow node"""
    
    def __init__(self, node_id: str, node_type: NodeType, config: Dict):
        self.node_id = node_id
        self.node_type = node_type
        self.config = config
        self.next_nodes = []
    
    def add_next_node(self, node_id: str, condition: str = None):
        """Add next node in workflow"""
        self.next_nodes.append({'node_id': node_id, 'condition': condition})
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'node_id': self.node_id,
            'node_type': self.node_type.value,
            'config': self.config,
            'next_nodes': self.next_nodes
        }

class WorkflowEngine:
    """Execute and manage workflows"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_workflow(self, name: str, description: str, 
                       workflow_type: str, nodes: List[WorkflowNode],
                       created_by: int) -> int:
        """Create new workflow"""
        # Convert nodes to configuration
        config = {
            'nodes': [node.to_dict() for node in nodes],
            'version': '1.0'
        }
        
        query = '''
            INSERT INTO workflows (name, description, workflow_type, configuration, created_by)
            VALUES (?, ?, ?, ?, ?)
        '''
        
        workflow_id = self.db.execute_update(
            query, 
            (name, description, workflow_type, json.dumps(config), created_by)
        )
        
        self.db.log_audit(created_by, f"Created workflow: {name}", "workflow", workflow_id)
        
        return workflow_id
    
    def start_workflow(self, workflow_id: int, document_id: int, 
                       initiated_by: int, initial_data: Dict = None) -> int:
        """Start workflow instance"""
        # Get workflow configuration
        workflow = self.db.execute_query(
            'SELECT * FROM workflows WHERE id = ?',
            (workflow_id,)
        )
        
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = workflow[0]
        config = json.loads(workflow['configuration'])
        
        # Create workflow instance
        query = '''
            INSERT INTO workflow_instances 
            (workflow_id, document_id, initiated_by, current_state, state_data)
            VALUES (?, ?, ?, ?, ?)
        '''
        
        state_data = {
            'current_node': 'start',
            'history': [],
            'data': initial_data or {}
        }
        
        instance_id = self.db.execute_update(
            query,
            (workflow_id, document_id, initiated_by, WorkflowState.PENDING.value, 
             json.dumps(state_data))
        )
        
        self.db.log_audit(initiated_by, f"Started workflow instance", 
                         "workflow_instance", instance_id)
        
        # Execute first node
        self._execute_next_node(instance_id, 'start')
        
        return instance_id
    
    def _execute_next_node(self, instance_id: int, current_node_id: str):
        """Execute next node in workflow"""
        # Get instance
        instance = self.db.execute_query(
            'SELECT * FROM workflow_instances WHERE id = ?',
            (instance_id,)
        )[0]
        
        # Get workflow config
        workflow = self.db.execute_query(
            'SELECT * FROM workflows WHERE id = ?',
            (instance['workflow_id'],)
        )[0]
        
        config = json.loads(workflow['configuration'])
        state_data = json.loads(instance['state_data'])
        
        # Find current node
        current_node = None
        for node in config['nodes']:
            if node['node_id'] == current_node_id:
                current_node = node
                break
        
        if not current_node:
            return
        
        # Find next node
        next_node_id = None
        for next_ref in current_node.get('next_nodes', []):
            # Check condition if exists
            condition = next_ref.get('condition')
            if condition is None or self._evaluate_condition(condition, state_data):
                next_node_id = next_ref['node_id']
                break
        
        if next_node_id:
            # Update state
            state_data['current_node'] = next_node_id
            state_data['history'].append({
                'node': current_node_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # Update instance
            self.db.execute_update(
                'UPDATE workflow_instances SET state_data = ? WHERE id = ?',
                (json.dumps(state_data), instance_id)
            )
            
            # Execute next node based on type
            next_node = None
            for node in config['nodes']:
                if node['node_id'] == next_node_id:
                    next_node = node
                    break
            
            if next_node:
                node_type = next_node['node_type']
                
                if node_type == 'approval':
                    self._handle_approval_node(instance_id, next_node)
                elif node_type == 'assign':
                    self._handle_assign_node(instance_id, next_node)
                elif node_type == 'notify':
                    self._handle_notify_node(instance_id, next_node)
                elif node_type == 'end':
                    self._handle_end_node(instance_id, next_node)
    
    def _handle_approval_node(self, instance_id: int, node: Dict):
        """Handle approval node"""
        # Get approver from node config
        approver_id = node['config'].get('approver_id')
        
        # Update instance state to waiting for approval
        self.db.execute_update(
            'UPDATE workflow_instances SET current_state = ? WHERE id = ?',
            (WorkflowState.IN_PROGRESS.value, instance_id)
        )
        
        # Create approval record
        query = '''
            INSERT INTO approvals (workflow_instance_id, approver_id, action, comments)
            VALUES (?, ?, ?, ?)
        '''
        self.db.execute_update(query, (instance_id, approver_id, 'pending', None))
    
    def _handle_assign_node(self, instance_id: int, node: Dict):
        """Handle assignment node"""
        assignee_id = node['config'].get('assignee_id')
        
        # Log assignment
        self.db.log_audit(assignee_id, f"Assigned task", "workflow_instance", instance_id)
        
        # Continue to next node
        self._execute_next_node(instance_id, node['node_id'])
    
    def _handle_notify_node(self, instance_id: int, node: Dict):
        """Handle notification node"""
        # Send notification (implementation depends on notification service)
        recipients = node['config'].get('recipients', [])
        message = node['config'].get('message', '')
        
        # Log notification
        for recipient in recipients:
            self.db.log_audit(recipient, f"Notification sent: {message}", 
                            "workflow_instance", instance_id)
        
        # Continue to next node
        self._execute_next_node(instance_id, node['node_id'])
    
    def _handle_end_node(self, instance_id: int, node: Dict):
        """Handle end node"""
        # Mark workflow as completed
        self.db.execute_update(
            '''UPDATE workflow_instances 
               SET current_state = ?, completed_at = CURRENT_TIMESTAMP 
               WHERE id = ?''',
            (WorkflowState.COMPLETED.value, instance_id)
        )
    
    def approve(self, workflow_instance_id: int, approver_id: int, 
                comments: str = None) -> bool:
        """Approve workflow"""
        # Update approval record
        query = '''
            UPDATE approvals 
            SET action = 'approved', comments = ?, approved_at = CURRENT_TIMESTAMP
            WHERE workflow_instance_id = ? AND approver_id = ?
        '''
        self.db.execute_update(query, (comments, workflow_instance_id, approver_id))
        
        # Update workflow state
        self.db.execute_update(
            'UPDATE workflow_instances SET current_state = ? WHERE id = ?',
            (WorkflowState.APPROVED.value, workflow_instance_id)
        )
        
        # Log audit
        self.db.log_audit(approver_id, "Approved workflow", 
                         "workflow_instance", workflow_instance_id)
        
        # Get current node and move to next
        instance = self.db.execute_query(
            'SELECT * FROM workflow_instances WHERE id = ?',
            (workflow_instance_id,)
        )[0]
        
        state_data = json.loads(instance['state_data'])
        current_node = state_data['current_node']
        
        self._execute_next_node(workflow_instance_id, current_node)
        
        return True
    
    def reject(self, workflow_instance_id: int, approver_id: int, 
               comments: str = None) -> bool:
        """Reject workflow"""
        # Update approval record
        query = '''
            UPDATE approvals 
            SET action = 'rejected', comments = ?, approved_at = CURRENT_TIMESTAMP
            WHERE workflow_instance_id = ? AND approver_id = ?
        '''
        self.db.execute_update(query, (comments, workflow_instance_id, approver_id))
        
        # Update workflow state
        self.db.execute_update(
            'UPDATE workflow_instances SET current_state = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?',
            (WorkflowState.REJECTED.value, workflow_instance_id)
        )
        
        # Log audit
        self.db.log_audit(approver_id, "Rejected workflow", 
                         "workflow_instance", workflow_instance_id)
        
        return True
    
    def _evaluate_condition(self, condition: str, state_data: Dict) -> bool:
        """Evaluate workflow condition"""
        # Simple condition evaluation
        # In production, use a proper expression evaluator
        try:
            return eval(condition, {"__builtins__": {}}, state_data.get('data', {}))
        except:
            return True
    
    def get_pending_approvals(self, user_id: int) -> List[Dict]:
        """Get pending approvals for user"""
        query = '''
            SELECT wi.*, w.name as workflow_name, d.filename, a.comments
            FROM workflow_instances wi
            JOIN workflows w ON wi.workflow_id = w.id
            LEFT JOIN documents d ON wi.document_id = d.id
            LEFT JOIN approvals a ON a.workflow_instance_id = wi.id
            WHERE a.approver_id = ? AND a.action = 'pending'
            ORDER BY wi.started_at DESC
        '''
        return self.db.execute_query(query, (user_id,))