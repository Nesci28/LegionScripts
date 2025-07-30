import uuid

class Python:
    @staticmethod
    def find(value, arr, path):
        option = next((x for x in arr if x[path] == value), None)
        return option
    
    @staticmethod
    def findIndex(value, arr, path):
        for i, obj in enumerate(arr):
            if obj.get(path) == value:
                return i
        return -1
    
    @staticmethod
    def v4():
        return str(uuid.uuid4())
