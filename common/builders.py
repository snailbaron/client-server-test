import xml.etree.ElementTree as ET
import json

#
# Basic class for working with data sent to or received by server
#
class BaseDataBuilder:
    def __init__(self, content_type=None, data=None):
        self.content_type = content_type
        self.data = []
        
        if data:
            self.read(data)
                
    def fill(self, data):
        for d in data:
            # TODO: Check that each data piece is valid
            self.data.append({'md5': d['md5'], 'name': d['name']})
            
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
        
    def read(self, xml):
        data = []
        root = ET.fromstring(xml)
        for d in root.findall('data'):
            md5_text = d.find('md5').text
            name_text = d.find('name').text
            data.append({'md5': md5_text, 'name': name_text})
        BaseDataBuilder.fill(self, data)
        
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
        
    def read(self, json):
        data = json.loads(json)
        BaseDataBuilder.fill(self, data)
        
    def to_string(self):
        root = []
        for d in self.data:
            root.append({'md5': d['md5'], 'name': d['name']})
        return json.dumps(root)
