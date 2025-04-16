import pandas as pd
import re
import os


def slugify(string):
    string = clean_text(string)
    # Remove special characters
    string = re.sub(r'[^\w\s-]', '', string)
    # Replace spaces with hyphens
    string = re.sub(r'\s+', '-', string)
    # Convert to lowercase
    string = string.lower()
    return string


def clean_text(string):
    # Remove URL prefixes like http:// or https://
    # string = re.sub(r'http[s]?://', '', string)
    # Remove escape strings like \n
    string = string.replace('\n', '').replace('\r', '').replace('\t', '')
    # Remove leading '-'
    string = re.sub(r'^-', '', string)
    # Replace ':' with '-'
    string = string.replace(':', '')
    return string


def remove_files_os(dir_path):
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def get_dataset_category(agency):
    return agency_to_category[agency]


agency_to_category = {
    'Department of Health and Human Services': 'Health / Human Services',
    'Department of Commerce': 'Economy',
    'Department of Housing and Urban Development': 'Real Estate / Land Records',
    'Department of Veterans Affairs': 'Health / Human Services',
    'National Endowment for the Humanities': 'Arts / Culture / History',
    'AmeriCorps': 'Public Safety',
    'Department of Education': 'Education',
    'Federal Mediation and Conciliation Service': 'Economy',
    'Department of Homeland Security': 'Public Safety',
    'Department of Energy': 'Environment',
    'National Labor Relations Board': 'Economy',
    'Environmental Protection Agency': 'Environment',
    'Consumer Financial Protection Bureau': 'Budget / Finance',
    'Federal Housing Finance Agency': 'Real Estate / Land Records',
    'Department of the Treasury': 'Budget / Finance',
    'Institute of Museum and Library Services': 'Arts / Culture / History',
    'Department of the Interior': 'Parks / Recreation',
    'General Services Administration': 'Economy',
    'Department of Labor': 'Economy',
    'U.S. Agency for International Development': 'Health / Human Services',
    'Department of Transportation': 'Transportation',
    'National Aeronautics and Space Administration': 'Environment',
    '': 'Uncategorized',
    'Department of Justice': 'Public Safety',
    'Department of the Interior, National Parks Service': 'Parks / Recreation',
    'Department of State': 'Elections / Politics',
    'National Science Foundation': 'Education',
    'Department of Health and Human Services, Department of Commerce': 'Health / Human Services',
    'Consumer Financial Protection Bureau, Federal Housing Finance Agency': 'Budget / Finance',
    'U.S. Department of Agriculture': 'Food',
    'Office of Management and Budget': 'Budget / Finance'
}


def get_metadata_availability(dataset_id, data_backups):
    """
    This function checks the metadata availability for dataset_id 432 in the backups dataframe.
    It returns "Yes" if metadata is available, "Under Review" if it needs review, and "No" otherwise.
    """
    md_avl = data_backups[data_backups.dataset_id == dataset_id].metadata_available.values
    if "yes" in md_avl:
        return "Yes", data_backups[data_backups.dataset_id == dataset_id].metadata_url.values[0]
    elif "needs review" in md_avl:
        return "Under Review", ""
    else:
        return "No", ""


def create_dataset_md(row, backups):
    if row['organization'] == '':
        row['organization'] = 'Unknown'
    # Defining the schema, filename and path
    schema = 'data_rescue_project'
    dataset_filename = slugify(row['dataset'])
    dataset_path = "_datasets"
    org_filename = slugify(row['organization'])
    org_path = "_organizations"

    # Get backups for each dataset
    data_backups = backups[backups.dataset == row['dataset']]
    metadata_available, metadata_url = get_metadata_availability(row['dataset_id'], data_backups)
    # Creating the dataset markdown file
    # Dataset-level information
    dataset_md = "---\n"
    dataset_md += f"schema: {schema} \n"
    dataset_md += f"title: {clean_text(row['dataset'])}\n"
    dataset_md += f"organization: {clean_text(row['organization'])}\n"
    dataset_md += f"agency: {clean_text(row['agency'])}\n"
    dataset_md += f"websites: {row['websites']}\n"
    dataset_md += f"data_source: {row['url']}\n"
    dataset_md += f"description: {clean_text(row['notes'])}\n"
    dataset_md += f"last_modified: {row['last_modified']}\n"
    # Check if any backups have metadata available and populate
    dataset_md += f"metadata_available: {metadata_available}\n"
    dataset_md += f"metadata_url: {metadata_url}\n"
    dataset_md += "category:\n"
    dataset_md += f"  - {get_dataset_category(clean_text(row['agency']))}\n"

    dataset_md += "resources:\n"
    # Resource-level information
    for index, backup_row in data_backups.iterrows():
        dataset_md += f"  - id: {index}\n"
        dataset_md += f"    url: {backup_row['download_location']}\n"
        dataset_md += f"    format: {clean_text(backup_row['file_type'])}\n"
        dataset_md += f"    status: {clean_text(backup_row['status'])}\n"
        dataset_md += f"    size: {backup_row['size']}\n"
        dataset_md += f"    download_date: {backup_row['download_date']}\n"
        dataset_md += f"    maintainer: {clean_text(backup_row['maintainer'])}\n"
        dataset_md += f"    notes: {clean_text(backup_row['notes'])}\n"
    dataset_md += "---\n"
     
    # Writing the dataset markdown file
    with open(f'{dataset_path}/{dataset_filename}.md', 'w') as output:
        output.write(dataset_md)

    # Creating the organization markdown file
    org_md = "---\n"
    org_md += f"title: {clean_text(row['organization'])} \n" 
    org_md += "description: \n" 
    org_md += "---\n"

    # Writing the organization markdown file
    with open(f'{org_path}/{org_filename}.md', 'w') as output:
        output.write(org_md)


def create_markdowns():
    """
    This function creates markdown files for each dataset and organization.
    """
    backups = pd.read_csv("https://raw.githubusercontent.com/datarescueproject/portal/refs/heads/main/baserow_exports/datarescue_backups.csv")
    datasets = pd.read_csv("https://raw.githubusercontent.com/datarescueproject/portal/refs/heads/main/baserow_exports/datarescue_datasets.csv")

    backups.columns = backups.columns.str.lower()
    backups = backups.fillna('')
    backups.head()

    datasets.columns = datasets.columns.str.lower()
    datasets = datasets.fillna('')
    datasets.head()

    # Remove files in _datasets and _organizations
    remove_files_os('./_datasets')
    remove_files_os('./_organizations')

    datasets.apply(create_dataset_md, axis=1, args=(backups,))
