import json
import uuid
import time


id = str(uuid.uuid4())
t = time.time_ns()

data = json.dumps({"uid":id, "time":t})
print(json.loads(data))