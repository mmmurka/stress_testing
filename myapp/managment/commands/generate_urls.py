import os

start_id = 1
end_id = 1000001

base_url = "http://localhost:8000/api/orders/"

urls = [f"{base_url}{id}/" for id in range(start_id, end_id + 1)]

current_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_directory, "../../../"))

file_path = os.path.join(project_root, "urls.txt")

with open(file_path, "w") as file:
    for url in urls:
        file.write(url + "\n")

print(f"URLs have been saved to {file_path}")
