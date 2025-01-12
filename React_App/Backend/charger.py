import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import json

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HEADERS = {
    'X-M2M-Origin': 'dev_guest:dev_guest',
    'Accept': 'application/json'
}

# URLs for Charger 1
CHARGER_1_DESCRIPTOR_URL = "http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/AE-EV/CHARGER/EV-L001-1/Descriptor/?rcn=4"
CHARGER_1_TRANSACTIONS_URL = "http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/AE-EV/CHARGER/EV-L001-1/Transactions/?rcn=4"

# URLs for Charger 2
CHARGER_2_DESCRIPTOR_URL = "http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/AE-EV/CHARGER/EV-L001-2/Descriptor/?rcn=4"
CHARGER_2_TRANSACTIONS_URL = "http://dev-onem2m.iiit.ac.in:443/~/in-cse/in-name/AE-EV/CHARGER/EV-L001-2/Transactions/?rcn=4"

# Initialize FastAPI
charger_app = FastAPI()

# Enable CORS
charger_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def fetch_data(url, headers):
    """Fetch data from the given URL."""
    try:
        logger.info(f"Fetching data from URL: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.info(f"Data fetched successfully from {url}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching data from {url}: {e}")
        return None

def extract_json_from_string(data_string, start_marker, end_marker):
    """Extract a JSON-like substring from a larger string."""
    try:
        start = data_string.find(start_marker)
        end = data_string.find(end_marker, start) + 1
        return json.loads(data_string[start:end].replace("'", '"'))
    except (ValueError, json.JSONDecodeError) as e:
        logger.error(f"Error extracting JSON from string: {e}")
        return []

def map_descriptor_data(descriptor):
    """Extract and map descriptor data."""
    try:
        logger.info("Mapping descriptor data...")
        if 'm2m:cnt' in descriptor:
            descriptor_content = descriptor['m2m:cnt']
            cin_content = descriptor_content.get('m2m:cin', [])

            if cin_content:
                con = cin_content[0].get('con', '')
                logger.debug(f"Descriptor 'con' content: {con}")
                return extract_json_from_string(con, "[", "]")
        logger.warning("No descriptor data found")
        return []
    except Exception as e:
        logger.error(f"Error mapping descriptor data: {e}")
        return []

def map_transaction_data(transactions, data_keys):
    """Map transactions to their respective keys."""
    try:
        logger.info("Mapping transaction data...")
        mapped_transactions = []
        if 'm2m:cnt' in transactions:
            transaction_content = transactions['m2m:cnt']
            cin_list = transaction_content.get('m2m:cin', [])
            for cin in cin_list:
                con_values = cin.get('con', '')
                logger.debug(f"Transaction 'con' content: {con_values}")
                try:
                    values = json.loads(con_values.replace("'", '"'))
                    if len(values) == len(data_keys):
                        transaction_mapping = dict(zip(data_keys, values))
                        mapped_transactions.append(transaction_mapping)
                    else:
                        logger.warning(f"Mismatch in number of values. Expected {len(data_keys)} but got {len(values)}")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Error parsing transaction content: {e}")
        logger.info(f"Mapped transactions: {json.dumps(mapped_transactions, indent=4)}")
        return mapped_transactions
    except Exception as e:
        logger.error(f"Error mapping transaction data: {e}")
        return []

@charger_app.get("/get-transactions")
def get_transactions():
    """Endpoint to fetch and map transactions for Charger 1."""
    logger.info("GET /get-transactions called")

    descriptor_data = fetch_data(CHARGER_1_DESCRIPTOR_URL, HEADERS)
    if not descriptor_data:
        return {"error": "Failed to fetch descriptor data"}

    transactions_data = fetch_data(CHARGER_1_TRANSACTIONS_URL, HEADERS)
    if not transactions_data:
        return {"error": "Failed to fetch transactions data"}

    data_keys = map_descriptor_data(descriptor_data)
    if not data_keys:
        return {"error": "Descriptor data keys not found"}

    mapped_transactions = map_transaction_data(transactions_data, data_keys)
    return {"transactions": mapped_transactions}

@charger_app.get("/get-transactions-2")
def get_transactions_2():
    """Endpoint to fetch and map transactions for Charger 2."""
    logger.info("GET /get-transactions-2 called")

    descriptor_data = fetch_data(CHARGER_2_DESCRIPTOR_URL, HEADERS)
    if not descriptor_data:
        return {"error": "Failed to fetch descriptor data"}

    transactions_data = fetch_data(CHARGER_2_TRANSACTIONS_URL, HEADERS)
    if not transactions_data:
        return {"error": "Failed to fetch transactions data"}

    data_keys = map_descriptor_data(descriptor_data)
    if not data_keys:
        return {"error": "Descriptor data keys not found"}

    mapped_transactions = map_transaction_data(transactions_data, data_keys)
    return {"transactions": mapped_transactions}
