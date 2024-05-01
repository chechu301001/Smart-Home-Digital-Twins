from DigitalTwinSmartHome import *


class src:
    def __init__(self,maxRuns,sleepDuration) -> None:
        self.maxRuns = maxRuns
        self.sleepDuration = sleepDuration
        self.help = DigitalTwinSmartHome(
            dtHostName = "https://ADT-FYP-smarthomes-name.api.wcus.digitaltwins.azure.net",
            excel_path = "./assests/RoomScenario-smarthome.xlsx",
            dump_path = "./assests/datadump.xlsx",
            model_path = "./assests/")
        #Establish Connection
        self.help.connection()

    def run(self):    
        

        #Models
        self.help.upload_models()

        #Twins & relationships
        self.help.create_digital_twins()
        self.help.create_relationships()

        #Validate
        self.help.display_all()

    def simulate(self):
        #Real Time Simulation
        for i in range(self.maxRuns):
            self.help.generate_telemtry()
            self.help.upload_telemtry()
            print(f"Run Successfull. next run in {self.sleepDuration} seconds")
            time.sleep(self.sleepDuration)

# Usage
s = src(maxRuns=20,sleepDuration=10)
s.run()    
s.simulate()    





