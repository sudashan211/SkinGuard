"""
Alerting System for SkinGuard Platform
Sends alerts via multiple channels based on configured rules
"""

import yaml
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)


class AlertManager:
    """
    Manages alert rules and sends notifications via configured channels
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize AlertManager with configuration
        
        Args:
            config_path: Path to alerts configuration file
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                "alerts.config.yaml"
            )
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.channels = self.config.get('channels', {})
        self.rules = self.config.get('rules', [])
        self.templates = self.config.get('templates', {})
        
        # Track last alert times for cooldown
        self.last_alert_times: Dict[str, datetime] = {}
        
        logger.info(f"AlertManager initialized with {len(self.rules)} rules")
    
    def check_rule(self, rule_name: str, current_value: float) -> bool:
        """
        Check if a rule condition is met
        
        Args:
            rule_name: Name of the rule to check
            current_value: Current metric value
        
        Returns:
            True if alert should be triggered
        """
        rule = self._get_rule(rule_name)
        if not rule:
            logger.warning(f"Rule not found: {rule_name}")
            return False
        
        # Check cooldown
        if not self._check_cooldown(rule_name, rule.get('cooldown', '15m')):
            return False
        
        # Check condition
        condition = rule['condition']
        threshold = condition['threshold']
        operator = condition['operator']
        
        if operator == '>':
            return current_value > threshold
        elif operator == '<':
            return current_value < threshold
        elif operator == '>=':
            return current_value >= threshold
        elif operator == '<=':
            return current_value <= threshold
        elif operator == '==':
            return current_value == threshold
        elif operator == '!=':
            return current_value != threshold
        
        return False
    
    def trigger_alert(self, rule_name: str, current_value: float, details: Optional[Dict] = None):
        """
        Trigger an alert for a specific rule
        
        Args:
            rule_name: Name of the rule
            current_value: Current metric value
            details: Additional details to include in alert
        """
        rule = self._get_rule(rule_name)
        if not rule:
            logger.error(f"Cannot trigger alert: Rule not found: {rule_name}")
            return
        
        # Update last alert time
        self.last_alert_times[rule_name] = datetime.utcnow()
        
        # Prepare alert context
        context = {
            'rule_name': rule['name'],
            'severity': rule['severity'],
            'description': rule['description'],
            'metric': rule['condition']['metric'],
            'operator': rule['condition']['operator'],
            'threshold': rule['condition']['threshold'],
            'current_value': current_value,
            'window': rule['condition']['window'],
            'timestamp': datetime.utcnow().isoformat(),
            'environment': os.getenv('ENVIRONMENT', 'production'),
            'details': details or {}
        }
        
        # Send to configured channels
        channels = rule.get('channels', [])
        for channel in channels:
            try:
                self._send_to_channel(channel, context)
            except Exception as e:
                logger.error(f"Failed to send alert to {channel}: {e}")
        
        logger.info(f"Alert triggered: {rule_name} (value: {current_value})")
    
    def _get_rule(self, rule_name: str) -> Optional[Dict]:
        """Get rule configuration by name"""
        for rule in self.rules:
            if rule['name'] == rule_name:
                return rule
        return None
    
    def _check_cooldown(self, rule_name: str, cooldown: str) -> bool:
        """
        Check if cooldown period has passed
        
        Args:
            rule_name: Name of the rule
            cooldown: Cooldown period (e.g., '15m', '1h')
        
        Returns:
            True if cooldown has passed
        """
        if rule_name not in self.last_alert_times:
            return True
        
        last_alert = self.last_alert_times[rule_name]
        cooldown_delta = self._parse_duration(cooldown)
        
        return datetime.utcnow() - last_alert > cooldown_delta
    
    def _parse_duration(self, duration: str) -> timedelta:
        """Parse duration string (e.g., '15m', '1h', '2d')"""
        unit = duration[-1]
        value = int(duration[:-1])
        
        if unit == 's':
            return timedelta(seconds=value)
        elif unit == 'm':
            return timedelta(minutes=value)
        elif unit == 'h':
            return timedelta(hours=value)
        elif unit == 'd':
            return timedelta(days=value)
        
        return timedelta(minutes=15)  # Default
    
    def _send_to_channel(self, channel: str, context: Dict):
        """Send alert to specific channel"""
        if channel == 'email':
            self._send_email(context)
        elif channel == 'slack':
            self._send_slack(context)
        elif channel == 'pagerduty':
            self._send_pagerduty(context)
        elif channel == 'sms':
            self._send_sms(context)
    
    def _send_email(self, context: Dict):
        """Send email alert"""
        config = self.channels.get('email', {})
        if not config.get('enabled', False):
            return
        
        # Render template
        template = Template(self.templates['email']['subject'])
        subject = template.render(**context)
        
        template = Template(self.templates['email']['body'])
        body = template.render(**context)
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = config['from_address']
        msg['To'] = ', '.join(config['recipients'])
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        try:
            with smtplib.SMTP(config['smtp_host'], config['smtp_port']) as server:
                server.starttls()
                server.login(config['smtp_user'], config['smtp_password'])
                server.send_message(msg)
            
            logger.info(f"Email alert sent to {len(config['recipients'])} recipients")
        
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            raise
    
    def _send_slack(self, context: Dict):
        """Send Slack alert"""
        config = self.channels.get('slack', {})
        if not config.get('enabled', False):
            return
        
        # Render template
        template = Template(self.templates['slack']['message'])
        message = template.render(**context)
        
        # Prepare payload
        payload = {
            'channel': config['channel'],
            'username': config['username'],
            'icon_emoji': config['icon_emoji'],
            'text': message
        }
        
        # Send to Slack
        try:
            response = requests.post(
                config['webhook_url'],
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("Slack alert sent successfully")
        
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            raise
    
    def _send_pagerduty(self, context: Dict):
        """Send PagerDuty alert"""
        config = self.channels.get('pagerduty', {})
        if not config.get('enabled', False):
            return
        
        # Map severity
        severity_mapping = config.get('severity_mapping', {})
        severity = severity_mapping.get(context['severity'], 'error')
        
        # Prepare payload
        payload = {
            'routing_key': config['integration_key'],
            'event_action': 'trigger',
            'payload': {
                'summary': f"{context['rule_name']}: {context['description']}",
                'severity': severity,
                'source': 'skinguard-monitoring',
                'custom_details': context
            }
        }
        
        # Send to PagerDuty
        try:
            response = requests.post(
                'https://events.pagerduty.com/v2/enqueue',
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("PagerDuty alert sent successfully")
        
        except Exception as e:
            logger.error(f"Failed to send PagerDuty alert: {e}")
            raise
    
    def _send_sms(self, context: Dict):
        """Send SMS alert via Twilio"""
        config = self.channels.get('sms', {})
        if not config.get('enabled', False):
            return
        
        # Render template
        template = Template(self.templates['sms']['message'])
        message = template.render(**context)
        
        # Send via Twilio
        try:
            from twilio.rest import Client
            
            client = Client(config['account_sid'], config['auth_token'])
            
            for phone_number in config['phone_numbers']:
                client.messages.create(
                    body=message,
                    from_=config['from_number'],
                    to=phone_number
                )
            
            logger.info(f"SMS alert sent to {len(config['phone_numbers'])} recipients")
        
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {e}")
            raise


# Convenience functions for common alerts
def alert_high_error_rate(error_rate: float):
    """Alert for high error rate"""
    manager = AlertManager()
    if manager.check_rule("High Error Rate", error_rate):
        manager.trigger_alert("High Error Rate", error_rate)


def alert_slow_response(response_time_ms: float):
    """Alert for slow API response"""
    manager = AlertManager()
    if manager.check_rule("Slow API Response Time", response_time_ms):
        manager.trigger_alert("Slow API Response Time", response_time_ms)


def alert_urgent_case_unreviewed(count: int):
    """Alert for unreviewed urgent cases"""
    manager = AlertManager()
    if manager.check_rule("Urgent Case Unreviewed", count):
        manager.trigger_alert("Urgent Case Unreviewed", count)


def alert_database_failure():
    """Alert for database connection failure"""
    manager = AlertManager()
    manager.trigger_alert("Database Connection Failure", 1)


def alert_suspicious_activity(user_id: str, activity: str):
    """Alert for suspicious activity"""
    manager = AlertManager()
    manager.trigger_alert(
        "Suspicious Activity Detected",
        1,
        details={'user_id': user_id, 'activity': activity}
    )
