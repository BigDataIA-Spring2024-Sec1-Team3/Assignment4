import xml.etree.ElementTree as ET
import os
import csv
from grobid_client.grobid_client import GrobidClient
import re
from lxml import etree
import configparser

def xml_to_text_and_metadata(xml_string):
    root = ET.fromstring(xml_string)
    text = ""

    for elem in root.iter():
        if elem.text:
                # Extract text content
                text += elem.text + "\n"
    return text.strip()

def pdf_to_xml_using_grobid(input_directory, output_directory):
    config = configparser.ConfigParser()
    config.read('../configuration.properties') 

    bucket_name = config['s3-bucket']['bucket']
    
    client = GrobidClient(config_path="./config.json")
    client.process("processFulltextDocument", input_directory, output_directory, n=1, 
                   consolidate_header=True, consolidate_citations=True, include_raw_citations=True,
                   include_raw_affiliations=True,force=True)
    
    """
    Extract TEI metadata including File language, File Size, version, and encoding.
    """
    metadata = {}
    try:
        tree = etree.parse(tei_file)
        root = tree.getroot()

        # Extract TEI Header metadata
        tei_header = root.find(".//{http://www.tei-c.org/ns/1.0}teiHeader")
        if tei_header is not None:
            metadata['language'] = tei_header.get('{http://www.w3.org/XML/1998/namespace}lang')

        # Extract version and encoding
        with open(tei_file, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            match = re.match(r'^<\?xml\s+version\s*=\s*(["\'])(.*?)\1\s+encoding\s*=\s*(["\'])(.*?)\3.*\?>', first_line)
            if match:
                metadata['version'] = match.group(2)
                metadata['encoding'] = match.group(4)
                
        file_stats = os.stat(tei_file)
        f_size = file_stats.st_size     # file size in bytes
        metadata['file_size'] = f_size

    except Exception as e:
        print(f"Error occurred while processing {tei_file}: {e}")

    return metadata

def write_metadata_to_csv(metadata_list, output_file):
    """
    Write metadata to a CSV file.
    """
    fieldnames = ['file_name', 'language', 'version', 'encoding','file_size', 's3_url']
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metadata_list)

def xml_data_to_csv():
    
    # Define the XML namespace
    namespace = {'tei': 'http://www.tei-c.org/ns/1.0'}
    input_directory = "data/input/grobid-files"
    csv_data = []

    try:
        for filename in os.listdir(input_directory):
            if filename.endswith('.xml'):
                # Parse the XML document
                tree = ET.parse(os.path.join(input_directory, filename))
                root = tree.getroot()
                year = filename.split('-')[0]
                level = filename.split('-')[1][1]

                # Initialize variables to store data
                title = ""
                topic_name = ""
                learning_outcome = ""

                title_element = root.find('.//tei:titleStmt/tei:title', namespace)

                # Iterate through each 'div' element in the XML
                for div in root.findall('.//tei:div', namespace):
                    # Get the 'head' element inside the current 'div'
                    head_element = div.find('.//tei:head', namespace)

                    # Rule 1: Set main_part to the text of the 'head' element in the previous 'div'
                    if head_element is not None and "LEARNING OUTCOMES" in head_element.text:
                        title = prev_head_text if prev_head_text else head_element.text
                        try:
                            csv_data.pop()
                        except:
                            continue

                    # Rule 2: Set sub_part to the text of the 'head' element in the current 'div'
                    topic_name = head_element.text if head_element is not None else ""

                    # Rule 3: Concatenate all text content within <p> elements
                    learning_outcome = ' '.join([p.text.strip() for p in div.findall('.//tei:p', namespace) if p.text is not None])

                    try:
                        if title == '' and "LEARNING OUTCOMES" in title_element.text:
                            head = title_element.text.replace(' LEARNING OUTCOMES', '')
                            title = head
                    except:
                        title = "N/A"

                    if topic_name != "LEARNING OUTCOMES":
                        csv_data.append([title, level, year, topic_name, learning_outcome])

                    # Save the 'head' text of the current 'div' for Rule 1 in the next iteration
                    prev_head_text = head_element.text if head_element is not None else ""

        # Write data to CSV file
        file_path = 'data/input/csv-input-files/pdf_content.csv'
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['title', 'level', 'year', 'topic_name', 'learning_outcome'])
            csv_writer.writerows(csv_data)

        print("CSV file generated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
