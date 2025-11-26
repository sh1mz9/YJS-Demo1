"""Utility functions for MVP demo"""

import streamlit as st
from datetime import datetime
import json

def log_activity(agent_name: str, action: str, status: str = "success"):
    """Log agent activity"""
    if "activity_log" not in st.session_state:
        st.session_state.activity_log = []
    
    st.session_state.activity_log.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "agent": agent_name,
        "action": action,
        "status": status
    })

def format_json_response(data: dict, title: str = "Result"):
    """Format JSON response for display"""
    st.success(f"✅ {title} Generated!")
    st.json(data)

def get_api_key():
    """Get OpenAI API key from secrets"""
    return st.secrets.get("OPENAI_API_KEY", "")

def check_api_status():
    """Check if API is configured"""
    api_key = get_api_key()
    if api_key:
        return True, "Connected"
    return False, "Not Configured"
