from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class DocsAPI:
    CLIENT_SECRETS_FILE = "./token.json"

    # Các quyền cần cấp để đảm bảo được đọc ghi file docs, còn vài quyền nữa mà nhiêu đây đủ test rồi
    SCOPES = [
        "https://www.googleapis.com/auth/documents", 
        "https://www.googleapis.com/auth/drive", 
        "https://www.googleapis.com/auth/drive.metadata.readonly", 
        "https://www.googleapis.com/auth/userinfo.profile", 
        "https://www.googleapis.com/auth/userinfo.email", 
        "https://www.googleapis.com/auth/drive.file", 
        "https://www.googleapis.com/auth/documents.readonly", 
        "https://www.googleapis.com/auth/drive.readonly", 
        "openid"]

    CONTRACTS_ID = [
        "",
        "10iOAFtf4ZkJ3eRdTPNOAtiqF4YunltKhn38rWkz2RRY",
        "1aJjgmeJDNDImgEQy7g_XQKhHjdoZvnx6mFfF0y8XnXU",
        "158SSDMFLfjM12EDfictQS9Y7e8VIrRBFxZt8aprQWsA",
        "1YHbofFmECgYF9yJxqsZYo7HfGoijTCdsypfjr-1VKzM",
        "1nl99UEBym2i2BLAruN8sCnG-KBs_ntv2MV0CtKZe9qI",
        "1uUyO01U2z7mEmV7nGXpDADc3ytN2laQF4uLhys5px3c",
        "14BrYoygnzPQVz1xuDij3tUCVZqbrA8DgVUZq8ugIyAg",
        "1mLHyQnNRM9_u1MGVn3mL_WzLfvhCFtPPMiHiXO4xh0w",
        "1LKB7negTFBmPsaak7Sjd5kolmk23FgMCZ4r9PActGLk",
        "1jimIW-3SkueYFeYmY0anfjyBheTumvzozHC4ywaUgIQ",
        "1McH84i5ZMYfKl6gbkYL-jRGZWT8uKGdHyiBV-kIgXnc",
        "1VW4gQzUG8IkvYrYIy7zxCYlKJ_kowkiklQjjbfVKyCs"]

    # Index table của từng hợp đồng 
    INDEX_TABLE = [
        0, 957, 1464, 1218, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ]

    # Số lượng row của table trong từng hợp đồng
    ROWS_NUMBER = [
        0, 16, 18, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ]

    # Index cell của table trong từng hợp đồng
    CELLS_SETTING = [
        {
            "start": 0,
            "step_cell": 0,
            "step_new_row": 0
        },
        {
            "start": 1123,
            "step_cell": 2,
            "step_new_row": 1
        },
        {
            "start": 1553,
            "step_cell": 2,
            "step_new_row": 1
        },
        {
            "start": 1220,
            "step_cell": 2,
            "step_new_row": 1
        },
        {
            "start": 0,
            "step_cell": 0,
            "step_new_row": 0
        },
        {
            "start": 0,
            "step_cell": 0,
            "step_new_row": 0
        },
        {
            "start": 0,
            "step_cell": 0,
            "step_new_row": 0
        },
        {
            "start": 0,
            "step_cell": 0,
            "step_new_row": 0
        },
        {
            "start": 0,
            "step_cell": 0,
            "step_new_row": 0
        },
        {
            "start": 0,
            "step_cell": 0,
            "step_new_row": 0
        },
        {
            "start": 0,
            "step_cell": 0,
            "step_new_row": 0
        },
        {
            "start": 0,
            "step_cell": 0,
            "step_new_row": 0
        },
        {
            "start": 0,
            "step_cell": 0,
            "step_new_row": 0
        },
    ]


    def __init__(self, path_creds_file) -> None:
        creds = Credentials.from_authorized_user_file(path_creds_file, self.SCOPES)
        self.docs_service = build('docs', 'v1', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)
    

    def update_service(self, path_creds_file):
        creds = Credentials.from_authorized_user_file(path_creds_file, self.SCOPES)
        self.docs_service = build('docs', 'v1', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)

    
    def copy_template(self, contract_index, contract_name):
        body = {
            'name': contract_name
        }

        drive_response = self.drive_service.files().copy(
            fileId=self.CONTRACTS_ID[contract_index] , body=body).execute()
        return drive_response.get('id')


    def replace_text(self, contract):
        requests = []
        key_in_contract = list(contract.keys())
        for index in range(len(key_in_contract)):
            item = key_in_contract[index]
        requests = [None]*len(key_in_contract)

        for index in range(len(requests)):
            item = key_in_contract[index]
            replace_item = contract[item]
            requests.append({
                'replaceAllText': {
                    'containsText': {
                        'text': "<" + item + ">",
                        'matchCase': 'true'
                    },
                    'replaceText': replace_item,
                }
            })
        return requests


    def delete_fixed_row(self, contract_index):
        row_number = self.ROWS_NUMBER[contract_index]
        table_index = self.INDEX_TABLE[contract_index]
        requests = []
        row_del = 1
        if contract_index == 3:
            row_del = 0
        for _ in range(row_number):
            requests.append({
                'deleteTableRow': {
                    'tableCellLocation': {
                        'tableStartLocation': {
                                'index': table_index
                        },
                        'rowIndex': row_del,
                        'columnIndex': 1
                    }
                }
            })
        return requests
    
    
    def insert_row(self, contract_index, number_row_insert):
        table_index = self.INDEX_TABLE[contract_index] 
        requests = []
        for _ in range(number_row_insert):
            requests.append({
                'insertTableRow': {
                    'tableCellLocation': {
                        'tableStartLocation': {
                                'index': table_index
                        },
                        'rowIndex': 0,
                        'columnIndex': 1
                    },
                    'insertBelow': 'true'
                }
            })
        return requests


    def insert_text_into_table(self, contract_index, table):
        row_number = table["rowNumber"]
        cell_info = self.CELLS_SETTING[contract_index]
        current_index = cell_info["start"]
        requests = []
        items = []
        for row in range(row_number):
            for col in range(len(table["dataColumn"][0])):
                items.append([current_index+1, table["dataColumn"][row][col]])
                current_index += cell_info["step_cell"]
            current_index += cell_info["step_new_row"]
        items = sorted(items, key=lambda x: x[0])
        for item in items[-1::-1]:
            requests.append({
                'insertText': {
                    'location': {
                        'index': item[0]
                    },
                    'text': str(item[1])
                }
            })

        return requests


    def run(self, contract_index, contract_name, requests):
        docs_id = self.copy_template(contract_index, contract_name)
        self.docs_service.documents().batchUpdate(
            documentId=docs_id, body={'requests': requests}).execute()
        
        link_contract = "https://docs.google.com/document/d/{}/edit".format(docs_id)

        return link_contract
        

    def get_json(self):
        result = self.docs_service.documents().get(documentId="13AqFOj3mq21_G53H58vOkx3uRFNFOU_XxWhgNUh2s3s").execute()
        return result