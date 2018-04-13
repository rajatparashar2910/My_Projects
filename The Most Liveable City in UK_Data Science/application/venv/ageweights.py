import pandas as pd
import numpy as np

df = pd.read_excel("Survey all categories (not done yet).xlsx")
df.head()

df ["Gender"].describe()