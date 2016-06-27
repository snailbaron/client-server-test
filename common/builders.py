import xml.etree.ElementTree as ET
import json

#
# Basic class for working with data sent to or received by server.
#
# Data is stored in a list of hashes in the form:
#   [
#     { 'md5': <md5 value>, 'name': <string value> },
#     ...
#   ]
#
# Additionally, Content-Type can be provided, which helps to construct HTTP
# requests using contained data.
#
class BaseDataBuilder:
    def __init__(self, content_type=None, data=None):
        self.content_type = content_type
        self.data = []
        
        if data:
            self.read(data)
                
    # Fill object's data using provided list of hashes    
    def fill(self, data):
        for d in data:
            self.data.append({'md5': d['md5'], 'name': d['name']})
            
    # Remove all data contained in the object. Useful when re-using the object,
    # to save the existing Content-Type.
    def clear(self):
        self.data = []
        
    def add(self, md5, name):
        self.data.append({'md5': md5, 'name': name})
        
    def get_content_type(self):
        return self.content_type
        
        
#
# Builder for XML data
#
class XmlDataBuilder(BaseDataBuilder):
    def __init__(self, xml=None):
        BaseDataBuilder.__init__(self, 'application/xml')
        if xml:
            self.read(xml)    
        
    # Read an XML string, converting it to a list of hashes
    def read(self, xml):
        data = []
        root = ET.fromstring(xml)
        for d in root.findall('data'):
            md5_text = d.find('md5').text
            name_text = d.find('name').text
            data.append({'md5': md5_text, 'name': name_text})
        BaseDataBuilder.fill(self, data)
        
    # Generate an XML string from stored data
    def to_string(self):
        root = ET.Element('root')
        for d in self.data:
           data = ET.SubElement(root, 'data')
           md5 = ET.SubElement(data, 'md5')
           md5.text = d['md5']
           name = ET.SubElement(data, 'name')
           name.text = d['name']
        return ET.tostring(root)

#
# Builder for JSON data
#
class JsonDataBuilder(BaseDataBuilder):
    def __init__(self, json=None):
        BaseDataBuilder.__init__(self, 'application/json')    
        if json:
            self.read(json)
        
    # Read a JSON string, converting it to a list of hashes
    def read(self, json):
        data = json.loads(json)
        BaseDataBuilder.fill(self, data)
        
    # Generate a JSON string from stored data
    def to_string(self):
        root = []
        for d in self.data:
            root.append({'md5': d['md5'], 'name': d['name']})
        return json.dumps(root)
