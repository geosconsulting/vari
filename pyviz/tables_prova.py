import pandas as pd
from great_tables import GT, md

df = pd.read_csv("../data/negozio/1-gen-giu-24.csv",
                 encoding="windows-1252",
                 sep=",")

print(df.sample(10))

my_table = (
    GT(df)
    .tab_header(
        title="Vendite",
        subtitle="Lista delle vendite",
    )
    .tab_source_note(md("**Data source**: the `great_tables` python library"))
    .tab_source_note(md("**Tutorial**: the *Python Graph Gallery*"))
)
my_table.show()
