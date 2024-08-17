import tkinter as tk
from tkinter import font, messagebox, filedialog, ttk
import threading
import pandas as pd
import webbrowser
from utils import flash_paypal_button, copy_to_clipboard
from scraper import scrape_data, export_data, stop_scan, clear_results
from logging_config import configure_logging
from config import RATE_LIMIT

def open_paypal():
    paypal_url = "https://www.paypal.com/donate/?hosted_button_id=VST8PNC48TKX2"
    webbrowser.open(paypal_url)

def update_rate_limit_label(value):
    rate_limit_label.config(text=f"Rate Limit: {value} seconds")

def main():
    root = tk.Tk()
    root.title("Advanced Web Scraper")
    root.geometry("1000x750")
    root.resizable(True, True)

    # Define style
    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 10))
    style.configure("TButton", font=("Helvetica", 12), padding=5)
    style.configure("TFrame", background="#f0f0f0")

    # Create a header frame
    header_frame = ttk.Frame(root, padding="10 10 10 10")
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    header_frame.columnconfigure(0, weight=1)

    # Header Label
    header_label = ttk.Label(header_frame, text="Advanced Web Scraper", font=("Helvetica", 16, "bold"), anchor="center")
    header_label.grid(row=0, column=0, sticky="ew")

    # Create a main content frame
    content_frame = ttk.Frame(root, padding="10 10 10 10")
    content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # URL Entry
    ttk.Label(content_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    url_entry = ttk.Entry(content_frame, width=50)
    url_entry.grid(row=0, column=1, padx=5, pady=5)
    url_entry.insert(0, "https://www.sasqnet.com")  # Default URL

    # HTML Tags Entry with common options
    ttk.Label(content_frame, text="HTML Tags:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    common_tags = ["a", "div", "span", "img", "p", "h1", "h2", "h3", "ul", "li", "table"]
    tags_combobox = ttk.Combobox(content_frame, values=common_tags, width=47)
    tags_combobox.grid(row=1, column=1, padx=5, pady=5)
    tags_combobox.set("div")  # Default value

    # HTML Classes Entry with common options
    ttk.Label(content_frame, text="HTML Classes:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    common_classes = ["container", "header", "footer", "nav", "content", "article", "section", "title", "text-center"]
    classes_combobox = ttk.Combobox(content_frame, values=common_classes, width=47)
    classes_combobox.grid(row=2, column=1, padx=5, pady=5)

    # Attribute Choice Combobox
    ttk.Label(content_frame, text="Attribute to Scrape:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
    attribute_choice = ttk.Combobox(content_frame, values=["text", "href", "src", "alt"], width=47)
    attribute_choice.grid(row=3, column=1, padx=5, pady=5)
    attribute_choice.current(0)  # Default to 'text'

    # Crawl Options
    crawl_option = tk.IntVar(value=0)
    ttk.Radiobutton(content_frame, text="Scrape Single Page", variable=crawl_option, value=0).grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
    ttk.Radiobutton(content_frame, text="Crawl Entire Site", variable=crawl_option, value=1).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

    # Crawl Links Only Option
    crawl_links_var = tk.IntVar(value=0)
    ttk.Checkbutton(content_frame, text="Crawl Only for Links", variable=crawl_links_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

    # Scrape Images Option
    scrape_images_var = tk.IntVar(value=0)
    ttk.Checkbutton(content_frame, text="Scrape Images", variable=scrape_images_var).grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

    # Rate Limit Slider
    global rate_limit_label
    rate_limit_label = ttk.Label(content_frame, text=f"Rate Limit: {RATE_LIMIT} seconds")
    rate_limit_label.grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
    rate_limit_scale = ttk.Scale(content_frame, from_=0.1, to=10.0, orient=tk.HORIZONTAL, command=update_rate_limit_label)
    rate_limit_scale.set(RATE_LIMIT)
    rate_limit_scale.grid(row=7, column=1, padx=5, pady=5)

    # Respect robots.txt Option
    load_robots_var = tk.IntVar(value=0)
    ttk.Checkbutton(content_frame, text="Respect robots.txt", variable=load_robots_var).grid(row=8, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

    # Email and Phone Number Search Options
    search_emails_var = tk.IntVar(value=0)
    ttk.Checkbutton(content_frame, text="Search for Emails", variable=search_emails_var).grid(row=9, column=0, sticky=tk.W, padx=5, pady=5)

    search_phones_var = tk.IntVar(value=0)
    ttk.Checkbutton(content_frame, text="Search for Phone Numbers", variable=search_phones_var).grid(row=9, column=1, sticky=tk.W, padx=5, pady=5)

    # Progress Bar
    global progress_bar
    progress_bar = ttk.Progressbar(content_frame, orient='horizontal', mode='determinate', length=400)
    progress_bar.grid(row=10, column=0, columnspan=2, pady=10)

    # Control Buttons Frame
    button_frame = ttk.Frame(content_frame)
    button_frame.grid(row=11, column=0, columnspan=2, pady=10)

    # Control Buttons
    scrape_button = ttk.Button(button_frame, text="Scrape Data", command=lambda: scrape_data(
        url_entry, 
        tags_combobox, 
        classes_combobox, 
        attribute_choice, 
        crawl_option, 
        crawl_links_var, 
        scrape_images_var, 
        load_robots_var, 
        search_emails_var, 
        search_phones_var, 
        progress_bar, 
        verbose_output, 
        stats_label, 
        tree, 
        donate_button  # Pass donate_button here
    ))

    scrape_button.grid(row=0, column=0, padx=5)

    stop_button = ttk.Button(button_frame, text="Stop Scan", command=lambda: stop_scan(verbose_output))
    stop_button.grid(row=0, column=1, padx=5)

    clear_button = ttk.Button(button_frame, text="Clear Results", command=lambda: clear_results(tree, verbose_output))
    clear_button.grid(row=0, column=2, padx=5)

    # Export Buttons Frame
    export_button_frame = ttk.Frame(content_frame)
    export_button_frame.grid(row=12, column=0, columnspan=2, pady=10)

    # Export Buttons
    export_csv_button = ttk.Button(export_button_frame, text="Export to CSV", command=lambda: export_data("csv", url_entry, tags_combobox, classes_combobox, attribute_choice, crawl_option, crawl_links_var, scrape_images_var, load_robots_var, search_emails_var, search_phones_var, tree))
    export_csv_button.grid(row=0, column=0, padx=5)

    export_json_button = ttk.Button(export_button_frame, text="Export to JSON", command=lambda: export_data("json", url_entry, tags_combobox, classes_combobox, attribute_choice, crawl_option, crawl_links_var, scrape_images_var, load_robots_var, search_emails_var, search_phones_var, tree))
    export_json_button.grid(row=0, column=1, padx=5)

    export_excel_button = ttk.Button(export_button_frame, text="Export to Excel", command=lambda: export_data("excel", url_entry, tags_combobox, classes_combobox, attribute_choice, crawl_option, crawl_links_var, scrape_images_var, load_robots_var, search_emails_var, search_phones_var, tree))
    export_excel_button.grid(row=0, column=2, padx=5)

    # Treeview for displaying scraped data or links
    global tree
    tree = ttk.Treeview(content_frame, columns=("URL", "Content"), show="headings", selectmode="extended")
    tree.heading("URL", text="URL")
    tree.heading("Content", text="Scraped Content")
    tree.column("URL", width=300, anchor=tk.W)
    tree.column("Content", width=300, anchor=tk.W)
    tree.grid(row=13, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

    # Enable selection and copying from Treeview
    tree.bind("<Control-c>", copy_to_clipboard)

    # Create a bold font
    bold_font = font.Font(weight="bold")

    # Text widget for verbose output
    global verbose_output
    verbose_output = tk.Text(content_frame, height=5, wrap=tk.WORD, bg="black", fg="green", font=bold_font)
    verbose_output.grid(row=14, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

    # Add scrollbars
    scrollbar_y = ttk.Scrollbar(content_frame, orient="vertical", command=tree.yview)
    scrollbar_y.grid(row=13, column=2, sticky='ns')
    tree.configure(yscrollcommand=scrollbar_y.set)

    scrollbar_x = ttk.Scrollbar(content_frame, orient="horizontal", command=tree.xview)
    scrollbar_x.grid(row=15, column=0, columnspan=2, sticky='ew')
    tree.configure(xscrollcommand=scrollbar_x.set)

    # Configure grid weights for resizing
    content_frame.grid_rowconfigure(13, weight=1)
    content_frame.grid_columnconfigure(1, weight=1)

    # Create a footer frame
    footer_frame = ttk.Frame(root, padding="10 10 10 10")
    footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

    # Stats label
    global stats_label
    stats_label = ttk.Label(footer_frame, text="Pages crawled: 0 | Time taken: 0 seconds", font=("Helvetica", 10))
    stats_label.grid(row=0, column=0, pady=5)

    # Donation Button (Use tk.Button instead of ttk.Button for background color control)
    donate_button = tk.Button(footer_frame, text="Donate with PayPal", command=open_paypal, bg="gold", fg="black", font=("Helvetica", 12, "bold"))
    donate_button.grid(row=1, column=0, pady=5)

    # Footer text
    footer_label = ttk.Label(footer_frame, text="Thank you for supporting this project!", font=("Helvetica", 10))
    footer_label.grid(row=2, column=0, pady=5)

    root.mainloop()

if __name__ == "__main__":
    configure_logging()
    main()
