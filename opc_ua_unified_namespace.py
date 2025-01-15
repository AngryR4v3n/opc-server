import json
from opcua import ua, Server, Node
import random
import time
import os

class UnifiedNamespaceOpcUaServer:
    def __init__(self, endpoint="opc.tcp://0.0.0.0:4840/", json_file="uns.json", frequency=1):
        self.server = Server()
        self.server.set_endpoint(endpoint)
        self.frequency = frequency
        
        self.uri = "http://examples.freeopcua.github.io"
        self.server.register_namespace(self.uri)
        
        with open(json_file, 'r') as f:
            self.structure = json.load(f)
        
        self.my_idx = self.server.register_namespace("SmartCompany")
        
        self.objects = self.server.get_objects_node()
        
        # variable references -> to simulate
        self.variables = {}

    def get_or_create_folder(self, parent_node, folder_name) -> Node:
        try:
            folder = parent_node.get_child(f"ns={self.my_idx};s={folder_name}")
            return folder
        except ua.uaerrors.BadNoMatch:
            return parent_node.add_folder(self.my_idx, folder_name)
        

    def populate_address_space(self):
        sites_map = self.structure.get("sitesMap", [])
        
        company_folder = self.get_or_create_folder(self.objects, "SmartCompany")
        for site in sites_map:
            site_name = site.get("site")
            site_folder = self.get_or_create_folder(company_folder, site_name)
            
            assets = site.get("assets", {})
            self.process_structure(site_folder, assets, [site_name])

    def process_structure(self, parent_node, structure, path):
        for key, value in structure.items():
            new_path = path + [key]
            if isinstance(value, dict):
                folder = self.get_or_create_folder(parent_node, key)
                self.process_structure(folder, value, new_path)
            elif isinstance(value, list):
                # Create folder for the machine
                machine_node = self.get_or_create_folder(parent_node, new_path[-1])
                for item in value:
                    var_name = f"{'.'.join(new_path)}.{item}"
                    if var_name not in self.variables:
                        var = machine_node.add_variable(self.my_idx, item, 0.0)
                        var.set_writable()
                        self.variables[var_name] = var
                        print(f"Created {var_name} in {var}")

    def simulate_values(self):
        for var_name, var in self.variables.items():
            if var_name.endswith("amps"):
                new_value = random.uniform(0, 250)
            elif var_name.endswith("voltage"):
                new_value = random.uniform(200, 240)
            elif var_name.endswith("powerAcc"):
                sibling_nodes = self.get_siblings(var)
                # calculate power.. Assuming that siblings are only amps and voltage
                new_value = ((sibling_nodes[0].get_value() * sibling_nodes[1].get_value()) / 1000) + var.get_value()

            else:
                new_value = random.random() * 100
            
            var.set_value(new_value)
            print(f"{var_name}: {new_value:.2f}")

    def get_siblings(self, var: Node) -> list:
        children = var.get_parent().get_children()
        # Get rid of myself
        children.remove(var)
        return list(children)




    def start(self):
        self.server.start()
        self.populate_address_space()
        print(f"Server started at {self.server.endpoint}")
        
        try:
            while True:
                self.simulate_values()
                time.sleep(self.frequency)
        finally:
            self.server.stop()

if __name__ == "__main__":
    server = UnifiedNamespaceOpcUaServer(json_file=os.environ["OPC_STRUCTURE"])
    server.start()