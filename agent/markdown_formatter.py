import re
import logging
import html

logger = logging.getLogger(__name__)

class MarkdownFormatter:
    """
    Utility class for converting markdown to HTML for Telegram
    """
    
    @staticmethod
    def markdown_to_plaintext(text):
        """
        Convert markdown to plain text
        
        Args:
            text (str): Text with markdown formatting
            
        Returns:
            str: Text with markdown formatting converted to plain text
        """
        try:
            # Remove bold formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            
            # Remove italic formatting
            text = re.sub(r'_(.*?)_', r'\1', text)
            
            # Remove code formatting
            text = re.sub(r'```(.*?)```', r'\1', text, flags=re.DOTALL)
            text = re.sub(r'`(.*?)`', r'\1', text)
            
            # Convert links
            text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 (\2)', text)
            
            return text
        except Exception as e:
            logger.error(f"Error converting markdown to plaintext: {e}")
            return text
    
    @staticmethod
    def markdown_to_html(text):
        """
        Convert markdown to HTML for Telegram display
        
        Args:
            text (str): Text with markdown formatting
            
        Returns:
            str: Text with markdown formatting converted to HTML
            bool: Whether the conversion was successful
        """
        try:
            # First escape HTML special characters to prevent injection
            text = html.escape(text)
            
            # Headers (## Header -> <b>Header</b>)
            text = re.sub(r'^##\s+(.*?)$', r'<b>\1</b>', text, flags=re.MULTILINE)
            text = re.sub(r'^#\s+(.*?)$', r'<b><u>\1</u></b>', text, flags=re.MULTILINE)
            
            # Bold formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'\*(.*?)\*', r'<b>\1</b>', text)
            
            # Italic formatting
            text = re.sub(r'_(.*?)_', r'<i>\1</i>', text)
            
            # Code formatting
            text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', text, flags=re.DOTALL)
            text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
            
            # Links
            text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
            
            # Bullet points
            text = re.sub(r'^-\s+(.*?)$', r'• \1', text, flags=re.MULTILINE)
            
            # Numbered lists (preserve numbers)
            text = re.sub(r'^(\d+)\.\s+(.*?)$', r'\1. \2', text, flags=re.MULTILINE)
            
            return text, True
        except Exception as e:
            logger.error(f"Error converting markdown to HTML: {e}")
            # If conversion fails, return the original text as plaintext
            return MarkdownFormatter.markdown_to_plaintext(text), False 