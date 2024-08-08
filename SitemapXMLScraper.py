import tkinter as tk
from tkinter import messagebox, filedialog
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk


def fetch_sitemap_data(url):
    try:
        # Send a GET request to the sitemap XML file
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Parse the XML content
        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()

        print(f"Root tag: {root.tag}")

        # Determine if it's a sitemap index or a regular sitemap
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        products = []

        if root.tag.endswith("sitemapindex"):
            print("Detected sitemap index")
            for sitemap_elem in root.findall('ns:sitemap', namespaces):
                loc = sitemap_elem.find('ns:loc', namespaces).text
                print(f"Found nested sitemap: {loc}")
                products.extend(fetch_sitemap_data(loc))  # Recursive call for nested sitemaps
        else:
            print("Detected regular sitemap")
            for url_elem in root.findall('ns:url', namespaces):
                loc = url_elem.find('ns:loc', namespaces).text
                lastmod_elem = url_elem.find('ns:lastmod', namespaces)
                lastmod = lastmod_elem.text if lastmod_elem is not None else 'N/A'
                products.append({'URL': loc, 'Last Modified': lastmod})

        return products

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []
    except ET.ParseError as e:
        print(f"Error parsing XML from {url}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error processing {url}: {e}")
        return []


def save_data(df):
    # Ask the user where to save the file
    filetypes = [('CSV Files', '*.csv'), ('Excel Files', '*.xlsx')]
    file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=filetypes)

    if file_path:
        # Save the DataFrame to the selected file
        try:
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Data saved successfully to {file_path}")
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")
            messagebox.showerror("Error", f"Failed to save the file:\n{e}")


def on_fetch_data():
    url = url_entry.get()
    products = fetch_sitemap_data(url)

    if products:
        df = pd.DataFrame(products)
        save_data(df)
    else:
        messagebox.showinfo("Info", "No products found.")


# Set up the main application window
root = tk.Tk()
root.title("Sitemap XML Scraper v1.0.0")
root.geometry("400x300")  # Increase the window size to accommodate the logo

# Center the window on the screen
root.eval('tk::PlaceWindow . center')

# Load and display the logo
logo_path = r"D:\Python Playground\iBetHubTelegramBot\assets\Clubs_120.png"
logo_image = Image.open(logo_path)
logo_image = logo_image.resize((50, 50), Image.LANCZOS)  # Resize the logo to 50x50 pixels
logo_photo = ImageTk.PhotoImage(logo_image)

logo_label = tk.Label(root, image=logo_photo)
logo_label.image = logo_photo  # Keep a reference to avoid garbage collection
logo_label.pack(pady=(30, 20))  # Add padding to position the logo

# Create a main frame to hold all widgets with padding
main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(expand=True, fill='both')

# Create a label and entry for the URL, center-aligned
url_label = tk.Label(main_frame, text="Enter URL of Sitemap XML:", font=("Arial", 12))
url_label.pack(pady=(0, 10))

url_entry = tk.Entry(main_frame, width=50, font=("Arial", 10))
url_entry.pack(pady=(0, 20))

# Create a button to fetch the sitemap data, center-aligned
get_data_button = tk.Button(main_frame, text="Get Sitemap Data", command=on_fetch_data, bg="#4CAF50", fg="white",
                            font=("Arial", 12))
get_data_button.pack()

# Start the GUI event loop
root.mainloop()
