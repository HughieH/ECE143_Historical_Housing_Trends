import pandas as pd

# Load raw HPI data
df = pd.read_csv('../data/raw/hpi_at_state_quarterly.csv', header=None, names=['State', 'Year', 'Quarter', 'HPI'])

# Create period column e.g. "1975 Q1"
df['Period'] = df['Year'].astype(str) + ' Q' + df['Quarter'].astype(str)

# Pivot to wide format: one row per state, one column per period
pivot = df.pivot_table(index='State', columns='Period', values='HPI', aggfunc='first')
pivot = pivot.reindex(sorted(pivot.columns, key=lambda x: (int(x.split()[0]), int(x.split()[1][1]))), axis=1)
pivot.reset_index(inplace=True)

# Map state abbreviations to full names
state_names = {
    'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AZ': 'Arizona',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia',
    'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii',
    'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts',
    'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota',
    'MO': 'Missouri', 'MS': 'Mississippi', 'MT': 'Montana', 'NC': 'North Carolina',
    'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island',
    'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas',
    'UT': 'Utah', 'VA': 'Virginia', 'VT': 'Vermont', 'WA': 'Washington',
    'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'
}

# Map states to US census regions
state_regions = {
    'AK': 'West', 'AL': 'South', 'AR': 'South', 'AZ': 'West',
    'CA': 'West', 'CO': 'West', 'CT': 'Northeast', 'DC': 'South',
    'DE': 'Northeast', 'FL': 'South', 'GA': 'South', 'HI': 'West',
    'IA': 'Midwest', 'ID': 'West', 'IL': 'Midwest', 'IN': 'Midwest',
    'KS': 'Midwest', 'KY': 'South', 'LA': 'South', 'MA': 'Northeast',
    'MD': 'South', 'ME': 'Northeast', 'MI': 'Midwest', 'MN': 'Midwest',
    'MO': 'Midwest', 'MS': 'South', 'MT': 'West', 'NC': 'South',
    'ND': 'Midwest', 'NE': 'Midwest', 'NH': 'Northeast', 'NJ': 'Northeast',
    'NM': 'West', 'NV': 'West', 'NY': 'Northeast', 'OH': 'Midwest',
    'OK': 'South', 'OR': 'West', 'PA': 'Northeast', 'RI': 'Northeast',
    'SC': 'South', 'SD': 'Midwest', 'TN': 'South', 'TX': 'South',
    'UT': 'West', 'VA': 'South', 'VT': 'Northeast', 'WA': 'West',
    'WI': 'Midwest', 'WV': 'South', 'WY': 'West'
}

# Add State Name, Region, and flag Image URL columns
pivot.insert(0, 'State Name', pivot['State'].map(state_names).fillna(pivot['State']))
pivot.insert(1, 'Region', pivot['State'].map(state_regions).fillna('Unknown'))
pivot.insert(2, 'Image URL', pivot['State'].apply(lambda s: f"https://flagcdn.com/us-{s.lower()}.svg"))


# Reorder columns
pivot.rename(columns={'State': 'State Abbr'}, inplace=True)
cols = ['State Name', 'Region', 'Image URL', 'State Abbr'] + [c for c in pivot.columns if c not in ['State Name', 'Region', 'Image URL', 'State Abbr']]
pivot = pivot[cols]

# Override DC flag URL
pivot.loc[pivot['State Abbr'] == 'DC', 'Image URL'] = 'https://upload.wikimedia.org/wikipedia/commons/0/03/Flag_of_Washington%2C_D.C.svg'

# Export to CSV
pivot.to_csv('../output/hpi_bar_chart_race.csv', index=False)

