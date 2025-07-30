import uuid

class Python:
    @staticmethod
    def find(name, arr, path):
        option = next((x for x in arr if x[path] == name), None)
        return option
    
    @staticmethod
    def findIndex(name, arr, path):
        for i, obj in enumerate(arr):
            if obj.get(path) == name:
                return i
        return -1
    
    @staticmethod
    def v4():
        return str(uuid.uuid4())
