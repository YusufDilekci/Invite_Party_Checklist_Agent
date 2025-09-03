from datasets import load_dataset
import pandas as pd

data = load_dataset(path="agents-course/unit3-invitees")
df = pd.DataFrame(data["train"])
df.to_json("data.json", orient="records", force_ascii=False)