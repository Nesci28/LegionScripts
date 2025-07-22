class Python:
    @staticmethod
    def find(name, arr, path):
        option = next((x for x in arr if x[path] == name), None)
        return option