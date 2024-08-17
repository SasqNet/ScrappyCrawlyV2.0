import requests
from bs4 import BeautifulSoup
import gc
import pandas as pd
import threading
from urllib.parse import urljoin, urlparse, urldefrag
import concurrent.futures
import time
import logging
import tkinter as tk  # Required for tk.END
from config import HEADERS, MAX_THREADS, RATE_LIMIT
from utils import is_valid_url, normalize_url, flash_paypal_button
from robots import load_robots_txt, can_fetch_url
from tkinter import filedialog, messagebox
import re

# Regular expressions for emails and phone numbers
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'\+?\(?\d{1,4}\)?[\d\s.-]{5,}')


stop_scan_flag = threading.Event()

def check_anti_scraping(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code in [403, 429]:
            return True, f"HTTP Status Code {response.status_code} detected. The site might be blocking scraping."
        if 'captcha' in response.text.lower():
            return True, "CAPTCHA detected. The site might be blocking scraping."
        return False, "No anti-scraping measures detected."
    except requests.exceptions.RequestException as e:
        return True, f"Request failed with exception: {e}"


def scrape_page(url, tags, classes, attribute, rp, search_emails_var, search_phones_var, scrape_images_var):
    if stop_scan_flag.is_set() or (rp and not can_fetch_url(rp, url)):
        return set()  # Return a set instead of a list

    try:
        time.sleep(RATE_LIMIT)  # Dynamic rate limiting
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve {url}: {e}")
        return set()  # Return an empty set on failure

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        data = set()  # Use a set to collect unique results

        # Extracting emails and phone numbers if requested
        if search_emails_var.get() == 1:
            emails = EMAIL_REGEX.findall(soup.get_text())
            for email in emails:
                data.add((url, email))

        if search_phones_var.get() == 1:
            print("Searching for phone numbers...")  # Debugging statement
            # Extract phone numbers from the href attributes
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if href.startswith('tel:'):
                    # Extract the phone number from the tel: href
                    phone_number = href.replace('tel:', '').strip()
                    print(f"Found phone number in href: {phone_number}")  # Debugging statement
                    data.add((url, phone_number))

            # Additionally, look for phone numbers in the text as before
            phone_numbers = PHONE_REGEX.findall(soup.get_text())
            for phone in phone_numbers:
                print(f"Found phone number in text: {phone}")  # Debugging statement
                data.add((url, phone))

        # Extracting specified tags and attributes
        for tag in tags:
            if classes:
                for cls in classes:
                    elements = soup.find_all(tag, class_=cls)
                    for element in elements:
                        if stop_scan_flag.is_set():
                            return set()
                        content = element.get_text(strip=True) if attribute == "text" else element.get(attribute)
                        if content:
                            data.add((url, content))
            else:
                elements = soup.find_all(tag)
                for element in elements:
                    if stop_scan_flag.is_set():
                        return set()
                    content = element.get_text(strip=True) if attribute == "text" else element.get(attribute)
                    if content:
                        data.add((url, content))

        # Scraping images if requested
        if scrape_images_var.get() == 1:
            images = soup.find_all("img")
            for img in images:
                src = img.get("src")
                if src:
                    full_src = urljoin(url, src)
                    data.add((url, full_src))

        return data

    finally:
        response.close()
        del response, soup
        gc.collect()  # Trigger garbage collection



def get_internal_links(url, soup, base_domain):
    links = set()
    for a_tag in soup.find_all('a', href=True):
        link = urljoin(url, a_tag['href'])
        parsed_link = urlparse(link)

        # Ensure the link is within the base domain and not malformed
        if parsed_link.netloc == base_domain and is_valid_url(link):
            normalized_link = normalize_url(link)
            links.add(normalized_link)
    return links

def crawl_site(url, tags, classes, attribute, crawl_links_only=False, rp=None, progress_bar=None, search_emails_var=None, search_phones_var=None, scrape_images_var=None):
    base_domain = urlparse(url).netloc
    visited = set()
    to_visit = set([normalize_url(url)])
    all_links = set()
    all_data = []
    total_pages = len(to_visit)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        while to_visit:
            current_url = to_visit.pop()
            if current_url in visited:
                continue
            visited.add(current_url)

            try:
                response = requests.get(current_url, headers=HEADERS, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                if crawl_links_only:
                    new_links = get_internal_links(current_url, soup, base_domain)
                    all_links.update(new_links)
                    to_visit.update(new_links)
                else:
                    page_data = scrape_page(current_url, tags, classes, attribute, rp, search_emails_var, search_phones_var, scrape_images_var)
                    all_data.extend(page_data)
                    new_links = get_internal_links(current_url, soup, base_domain)
                    to_visit.update(new_links)

                total_pages += len(new_links)
                if progress_bar:
                    progress = len(visited) / total_pages * 100
                    progress_bar['value'] = progress

            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to retrieve {current_url}: {e}")

    return all_links if crawl_links_only else all_data

def display_data(data, tree):
    if not data:
        messagebox.showwarning("No Data", "No data found with the specified parameters.")
        return

    df = pd.DataFrame(data, columns=["URL", "Content"])  # Ensure DataFrame is correctly structured
    df = df.drop_duplicates()  # Ensure only unique results are displayed
    max_content_width = max(df['Content'].apply(len)) * 10 if not df.empty else 100
    tree.column("Content", width=max_content_width)

    for i in tree.get_children():
        tree.delete(i)
    for index, row in df.iterrows():
        tree.insert("", "end", values=(row['URL'], row['Content']))

def display_links(links, tree):
    for i in tree.get_children():
        tree.delete(i)
    for link in sorted(links):
        tree.insert("", "end", values=(link, ""))

def scrape_data(url_entry, tags_combobox, classes_combobox, attribute_choice, crawl_option, crawl_links_var, scrape_images_var, load_robots_var, search_emails_var, search_phones_var, progress_bar, verbose_output, stats_label, tree, donate_button):
    stop_scan_flag.clear()
    progress_bar['value'] = 0

    thread = threading.Thread(target=_scrape_data_thread, args=(
        url_entry, tags_combobox, classes_combobox, attribute_choice, crawl_option, crawl_links_var, scrape_images_var, load_robots_var, search_emails_var, search_phones_var, progress_bar, verbose_output, stats_label, tree, donate_button
    ))
    thread.start()

def _scrape_data_thread(url_entry, tags_combobox, classes_combobox, attribute_choice, crawl_option, crawl_links_var, scrape_images_var, load_robots_var, search_emails_var, search_phones_var, progress_bar, verbose_output, stats_label, tree, donate_button):
    url = url_entry.get()
    
    # Check for anti-scraping measures
    is_blocked, message = check_anti_scraping(url)
    verbose_output.insert(tk.END, f"{message}\n")
    verbose_output.see(tk.END)
    if is_blocked:
        stats_label.config(text="Scraping aborted: Anti-scraping measures detected.")
        return
    
    tags = [tag.strip() for tag in tags_combobox.get().split(",")]
    classes = [cls.strip() for cls in classes_combobox.get().split(",") if cls.strip()]
    attribute = attribute_choice.get()
    crawl_links_only = crawl_links_var.get() == 1

    rp = load_robots_var.get() == 1 and load_robots_txt(url) or None

    start_time = time.time()
    all_data = set()

    if crawl_option.get() == 1:
        if crawl_links_only:
            all_links = crawl_site(url, tags, classes, attribute, crawl_links_only=True, rp=rp, progress_bar=progress_bar, search_emails_var=search_emails_var, search_phones_var=search_phones_var, scrape_images_var=scrape_images_var)
            display_links(all_links, tree)
        else:
            all_data.update(crawl_site(url, tags, classes, attribute, rp=rp, progress_bar=progress_bar, search_emails_var=search_emails_var, search_phones_var=search_phones_var, scrape_images_var=scrape_images_var))
            display_data(list(all_data), tree)
    else:
        all_data.update(scrape_page(url, tags, classes, attribute, rp, search_emails_var, search_phones_var, scrape_images_var))
        display_data(list(all_data), tree)

    end_time = time.time()
    elapsed_time = end_time - start_time

    stats_label.config(text=f"Pages crawled: {len(all_data) if not crawl_links_only else len(all_links)} | Time taken: {elapsed_time:.2f} seconds")

    flash_paypal_button(donate_button)

    progress_bar['value'] = 0


def export_data(export_format, url_entry, tags_combobox, classes_combobox, attribute_choice, crawl_option, crawl_links_var, scrape_images_var, load_robots_var, search_emails_var, search_phones_var, tree):
    df = scrape_data_for_export(url_entry, tags_combobox, classes_combobox, attribute_choice, crawl_option, crawl_links_var, scrape_images_var, load_robots_var, search_emails_var, search_phones_var)
    if df is not None and not df.empty:
        file_types = [("CSV files", "*.csv")] if export_format == "csv" else [("JSON files", "*.json")]
        file_path = filedialog.asksaveasfilename(defaultextension=f".{export_format}", filetypes=file_types)
        if file_path:
            if export_format == "csv":
                df.to_csv(file_path, index=False)
            elif export_format == "json":
                df.to_json(file_path, orient='records', lines=True)
            elif export_format == "excel":
                df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Data exported successfully as {export_format.upper()}.")

def scrape_data_for_export(url_entry, tags_combobox, classes_combobox, attribute_choice, crawl_option, crawl_links_var, scrape_images_var, load_robots_var, search_emails_var, search_phones_var):
    url = url_entry.get()
    tags = [tag.strip() for tag in tags_combobox.get().split(",")]
    classes = [cls.strip() for cls in classes_combobox.get().split(",") if cls.strip()]
    attribute = attribute_choice.get()
    crawl_links_only = crawl_links_var.get() == 1
    
    rp = load_robots_var.get() == 1 and load_robots_txt(url) or None
    
    if crawl_option.get() == 1:  # Crawl entire site
        if crawl_links_only:
            all_links = crawl_site(url, tags, classes, attribute, crawl_links_only=True, rp=rp, search_emails_var=search_emails_var, search_phones_var=search_phones_var, scrape_images_var=scrape_images_var)
            return pd.DataFrame({'URL': list(all_links)})
        else:
            return pd.DataFrame(crawl_site(url, tags, classes, attribute, rp=rp, search_emails_var=search_emails_var, search_phones_var=search_phones_var, scrape_images_var=scrape_images_var))
    else:  # Scrape single page
        return pd.DataFrame(scrape_page(url, tags, classes, attribute, rp, search_emails_var, search_phones_var, scrape_images_var))

def stop_scan(verbose_output):
    stop_scan_flag.set()  # Signal threads to stop
    verbose_output.insert(tk.END, "Stop button pressed, stopping scan...\n")
    verbose_output.see(tk.END)

def clear_results(tree, verbose_output):
    for i in tree.get_children():
        tree.delete(i)
    verbose_output.delete(1.0, tk.END)
    verbose_output.insert(tk.END, "Results cleared.\n")
