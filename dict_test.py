files = dict()

files[""] = []
print(files)
print(files.get(""))
if files.get(""):
    print("YES")
else:
    print("NO")

files[""] = [1]
print(files)
print(files.get(""))
if files.get(""):
    print("YES")
else:
    print("NO")

files.pop("")
print(files)
print(files.get(""))
if files.get(""):
    print("YES")
else:
    print("NO")
