class Legacy:
 table='archives'
 def write(self,payload):return self.table,payload
class Journal:
 table='archive_entries_v3'
 def write(self,payload):return self.table,payload
