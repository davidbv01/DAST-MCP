from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_html(soup, base_url):
    links = []
    inputs = []
    buttons = []
    forms = []

    for el in soup.find_all(["a", "input", "button", "form"]):
        if el.name == "a":
            href = el.get("href")
            text = el.get_text().strip()
            # Ensure the href is absolute
            if href:
                href = urljoin(base_url, href)  # Convert to absolute URL
            # Guardamos solo si tiene href y texto
            if href or text:
                links.append({
                    "href": href,
                    "text": text
                })

        elif el.name == "input":
            input_type = el.get("type")
            input_name = el.get("name")
            input_id = el.get("id")
            input_value = el.get("value")
            # Guardamos solo si tiene ID o NAME
            if input_id or input_name:
                inputs.append({
                    "type": input_type,
                    "name": input_name,
                    "id": input_id,
                    "value": input_value
                })

        elif el.name == "button":
            button_type = el.get("type")
            button_name = el.get("name")
            button_text = el.get_text().strip()
            # Guardamos solo si tiene texto o nombre
            if button_text or button_name:
                buttons.append({
                    "type": button_type,
                    "name": button_name,
                    "text": button_text
                })

        elif el.name == "form":
            form_action = el.get("action")
            form_method = el.get("method")
            form_fields = [input_el.get("name") for input_el in el.find_all("input") if input_el.get("name")]
            # Ensure the action is absolute
            if form_action:
                form_action = urljoin(base_url, form_action)  # Convert to absolute URL
            # Guardamos aunque no haya fields (algunos forms no tienen inputs directos)
            forms.append({
                "action": form_action,
                "method": form_method,
                "fields": form_fields
            })

    summary = {
        "links": links,
        "inputs": inputs,
        "buttons": buttons,
        "forms": forms
    }
    return summary

def cookies_changed(before, after):
    """Compares two cookie lists and returns True if they have changed."""
    # Convert the cookies to simpler dictionaries for comparison
    before_set = {cookie['name']: cookie['value'] for cookie in before}
    after_set = {cookie['name']: cookie['value'] for cookie in after}
    
    return before_set != after_set