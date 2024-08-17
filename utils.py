import re

def is_valid_url(url):
    VALID_URL_REGEX = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(VALID_URL_REGEX, url) is not None

def normalize_url(url):
    from urllib.parse import urlparse, urldefrag
    parsed_url = urlparse(url)
    cleaned_url, _ = urldefrag(parsed_url.geturl())
    return cleaned_url.lower().rstrip('/')

def flash_paypal_button(donate_button, count=10):
    if count > 0:
        current_color = donate_button.cget("bg")
        new_color = "red" if current_color == "gold" else "gold"
        donate_button.config(bg=new_color)
        donate_button.after(300, flash_paypal_button, donate_button, count - 1)


def copy_to_clipboard(event):
    selected_items = tree.selection()
    selected_text = ""
    for item in selected_items:
        selected_values = tree.item(item, 'values')
        selected_text += "\t".join(selected_values) + "\n"
    root.clipboard_clear()
    root.clipboard_append(selected_text)
