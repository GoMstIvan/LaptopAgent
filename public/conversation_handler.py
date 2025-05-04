import os
import datetime
import re
from pathlib import Path

class ConversationHandler:
    def __init__(self, base_path="conversations"):
        self.base_path = base_path
        self.current_id = None
        self.current_conversation = []
        self.model_name = None
        
        # Create conversations directory if it doesn't exist
        os.makedirs(self.base_path, exist_ok=True)
        
    def new_conversation(self, model_name):
        """Start a new conversation and save the current one if exists"""
        if self.current_id:
            self.save_conversation()
            
        # Generate new conversation ID with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hex = os.urandom(4).hex()
        self.current_id = f"{timestamp}_{random_hex}"
        self.current_conversation = []
        self.model_name = model_name
        return self.current_id
    
    def add_message(self, role, content):
        """Add a message to the current conversation"""
        self.current_conversation.append({"role": role, "content": content})
    
    def save_conversation(self):
        """Save the current conversation to a file"""
        if not self.current_id or not self.current_conversation:
            return False
        
        filepath = os.path.join(self.base_path, f"{self.current_id}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            # Write header
            f.write(f"# Conversation with {self.model_name} (ID: {self.current_id})\n\n")
            f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write messages using XML-style tags
            for message in self.current_conversation:
                role = message["role"].title()
                content = message["content"]
                f.write(f"<{role}>\n{content}\n</{role}>\n\n")
        
        return True
    
    def load_conversation(self, conversation_id):
        """Load a conversation by ID"""
        # First try with exact ID
        filepath = os.path.join(self.base_path, f"{conversation_id}.md")
        
        # If that doesn't exist, try with legacy "conversation_" prefix
        if not os.path.exists(filepath):
            legacy_filepath = os.path.join(self.base_path, f"conversation_{conversation_id}.md")
            if os.path.exists(legacy_filepath):
                filepath = legacy_filepath
            else:
                return False
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Extract model name and ID from header
            model_match = re.search(r"# Conversation with (.*?) \(ID: (.*?)\)", content)
            if model_match:
                self.model_name = model_match.group(1)
                self.current_id = model_match.group(2)
            else:
                # Fallback if header format is different
                self.model_name = "unknown"
                self.current_id = conversation_id
            
            # Clear existing conversation
            self.current_conversation = []
            
            # Extract messages using XML-style tags
            roles = ["User", "System", "Assistant"]
            
            for role in roles:
                pattern = re.compile(f"<{role}>\n(.*?)\n</{role}>", re.DOTALL)
                for match in pattern.finditer(content):
                    message_content = match.group(1).strip()
                    self.add_message(role.lower(), message_content)
            
            # If no messages found with XML tags, try legacy format (if any)
            if not self.current_conversation:
                # Example of legacy format parsing - adjust as needed
                user_pattern = re.compile(r"## User\n\n(.*?)(?=\n##|\Z)", re.DOTALL)
                assistant_pattern = re.compile(r"## Assistant\n\n(.*?)(?=\n##|\Z)", re.DOTALL)
                
                for user_match in user_pattern.finditer(content):
                    self.add_message("user", user_match.group(1).strip())
                
                for assistant_match in assistant_pattern.finditer(content):
                    self.add_message("assistant", assistant_match.group(1).strip())
            
            return len(self.current_conversation) > 0
        
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return False
    
    def get_conversation_history(self):
        """Return the conversation history in a format ready for the model"""
        return self.current_conversation
    
    def list_conversations(self):
        """List all available conversations"""
        conversations = []
        
        # Look for .md files in the conversation directory
        for filename in os.listdir(self.base_path):
            if filename.endswith('.md'):
                # Extract ID from filename
                conv_id = filename.replace('conversation_', '').replace('.md', '')
                
                # Get creation time
                filepath = os.path.join(self.base_path, filename)
                timestamp = os.path.getctime(filepath)
                date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
                # Try to extract model name from file
                model_name = "unknown"
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        model_match = re.search(r"# Conversation with (.*?) \(ID:", first_line)
                        if model_match:
                            model_name = model_match.group(1)
                except:
                    pass
                
                conversations.append({
                    'id': conv_id,
                    'date': date,
                    'model': model_name
                })
        
        return sorted(conversations, key=lambda x: x['date'], reverse=True)
