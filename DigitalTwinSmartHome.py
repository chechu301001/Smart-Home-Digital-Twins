import json
import os
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential
from datetime import datetime
import pandas as pd
import random
import time


class DigitalTwinSmartHome:
    current_timestamp = datetime.now().timestamp()
    def __init__(self,dtHostName,excel_path,dump_path,model_path) -> None:
        self.dt_client = None 
        self.dtHostName = dtHostName
        self.excel_path = excel_path
        self.dump_path = dump_path
        self.model_path = model_path

    def load_excel(self):
        df = pd.read_excel(self.excel_path)
        return df

    def connection(self):
        try:
            self.dt_client = DigitalTwinsClient(f"{self.dtHostName}", DefaultAzureCredential())
            print("Service client created at: ",self.current_timestamp)
        except Exception as e:
            print("Error establishing donnection:", e)

    def delete_models(self):
        try:
            existing_models = self.dt_client.list_models()
            for model in existing_models:
                self.dt_client.delete_model(model.id)
            print("Existing models deleted! ")
        except Exception as e:
            print("Error deleting existing models:", e)

    def upload_models(self):
        self.delete_models()
        list_of_models = []
        for filename in os.listdir(self.model_path):
            if filename.endswith(".json"):
                file_path = os.path.join(self.model_path, filename)
                with open(file_path, 'r') as f:
                    model = json.load(f)
                    list_of_models.append(model)
        print(f"Models Loaded from {self.model_path}: ",len(list_of_models))
        try:
            self.dt_client.create_models(list_of_models)
            print(f"Models Upoaded!")
        except Exception as e:
            print("Error uploading models:", e)

    def delete_relationships(self):
        try:
            query_expression = 'SELECT * FROM digitaltwins'
            query_result = self.dt_client.query_twins(query_expression)
            total_relation = 0
            for twin in query_result:
                digital_twin_id = twin['$dtId']
                relationships = self.dt_client.list_relationships(digital_twin_id)
                for relationship in relationships:
                    relationship_id = relationship['$relationshipId']
                    total_relation+=1
                    self.dt_client.delete_relationship(digital_twin_id, relationship_id)
            print(f'Deleted {total_relation} relationships!')
        except Exception as e:
            print("Error deleteing relationships:", e)

    def delete_digital_twins(self):
        try:
            query_expression = 'SELECT * FROM digitaltwins'
            query_result = self.dt_client.query_twins(query_expression)
            total_twins = 0
            for twin in query_result:
                digital_twin_id = twin['$dtId']
                self.dt_client.delete_digital_twin(digital_twin_id)
                total_twins+=1
            print(f'Deleted {total_twins} twins!')
        except Exception as e:
            print("Error deleteing digital twins:", e)
    
    def create_digital_twins(self):
        try:
            self.delete_relationships()
            self.delete_digital_twins()
            df = self.load_excel()
            for index, row in df.iterrows():
                model_id = row['ModelID']
                digital_twin_id = row['ID (must be unique)']
                metadata = {
                    "$metadata": {
                        "$model": model_id
                    },
                    "$dtId": digital_twin_id
                }
                created_twin = self.dt_client.upsert_digital_twin(digital_twin_id, metadata)
                print(f"Created Digital twin ID: {digital_twin_id} from {model_id}")
        except Exception as e:
            print("Error deleteing digital twins:", e)

    def create_relationships(self):
        try:
            df = pd.read_excel(self.excel_path)
            all_relationships = []
            for index, row in df.iterrows():
                relationship = {
                    "$relationshipId": f"RoomContains{row['ID (must be unique)']}",
                    "$sourceId": row['Relationship (From)'],
                    "$relationshipName": row['Relationship Name'],
                    "$targetId": row['ID (must be unique)'],
                }
                all_relationships.append(relationship)
            for relationship in all_relationships[1:]:
                self.dt_client.upsert_relationship(
                    relationship["$sourceId"],
                    relationship["$relationshipId"],
                    relationship
                )
                print("Created relationship", {relationship["$sourceId"]} ," > ",  {relationship["$targetId"]})
        except Exception as e:
            print("Error deleteing digital twins:", e)
        
    def display_all(self):
        try:
            query_expression = 'SELECT * FROM digitaltwins'
            query_result = self.dt_client.query_twins(query_expression)
            all_twins = []
            all_relationships = set()
            for twin in query_result:
                all_twins.append(twin['$dtId'])
                digital_twin_id = twin['$dtId']
                relationships = self.dt_client.list_relationships(digital_twin_id)
                for relationship in relationships:
                    relationship_id = relationship['$relationshipId']
                    all_relationships.add(relationship_id)

            print('DigitalTwins: ',all_twins)
            print('Relationships:',all_relationships)
        except Exception as e:
            print("Error displaying all digital twins & relationships:", e)

    
    

    def generate_telemtry(self):
        def update_parameters(df):
            for index, row in df.iterrows():
                init_data = json.loads(row['Init Data'])
                for key in init_data.keys():
                    # Update only the values of Init Data parameters
                    init_data[key] = get_random_value(key)
                df.at[index, 'Init Data'] = json.dumps(init_data)
            return df
        
        def get_random_value(key):
            if key == 'temperature':
                return random.randint(18, 23)
            elif key == 'mode':
                return random.choice(["Cool", "Normal", "Heat"])
            elif key == 'fanSpeed':
                return random.randint(0, 3)
            elif key == 'onOff':
                return random.choice([True, False])
            elif key == 'occupancy':
                return random.choice([True, False])
            elif key == 'powerConsumed':
                return random.uniform(0, 1)
            elif key == 'volume':
                return random.randint(0, 1)
            elif key == 'channel':
                return random.choice(["BBC", "CNN", "FOX", "ABC"])
            elif key == 'brightness':
                return random.randint(0, 100)
            elif key == 'lighting':
                return random.randint(0, 100)
            elif key == 'humidity':
                return random.randint(0, 100)
            elif key == 'speed':
                return random.randint(0, 5)
            elif key == 'color':
                return random.choice(["White", "Red", "Green", "Blue"])
            elif key == 'status':
                return random.choice(["Running", "Stopped", "Paused"])
            
        def append_to_datadump(updated_values, file_path):
            updated_values['Date'] = datetime.now().strftime('%Y-%m-%d')
            updated_values['Time'] = datetime.now().strftime('%H:%M:%S')
            if os.path.exists(file_path):
                existing_data = pd.read_excel(file_path)
                updated_values = pd.concat([existing_data, updated_values], ignore_index=True)
            updated_values.to_excel(file_path, index=False)

        df = self.load_excel()
        updated_df = update_parameters(df)
        updated_df.to_excel(self.excel_path, index=False)
        append_to_datadump(updated_df, self.dump_path)
        print("Genrated new telemtry!")

    def upload_telemtry(self):
        df = self.load_excel()
        digital_twin_data = []
        for index, row in df.iterrows():
            digital_twin_id = row['ID (must be unique)']
            init_data = json.loads(row['Init Data'])
            data_update = {
                "$metadata": {
                    "$model": row['ModelID']
                }
            }
            data_update.update(init_data)
            digital_twin_data.append((digital_twin_id, data_update))
        for digital_twin_id, data_update in digital_twin_data[1:]:
            self.dt_client.upsert_digital_twin(digital_twin_id, data_update)
        print("Connection established at: ",self.current_timestamp)
        print("Uploaded telemtry successfully at: ",datetime.now().timestamp())


        

