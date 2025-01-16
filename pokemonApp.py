import streamlit as st 
import pandas as pd
import plotly.express as px
import requests

main_section_css = """
<style>
/* Target the main content area */
div[data-testid="stAppViewContainer"] {
    background-image: url('https://imgcdn.stablediffusionweb.com/2024/11/7/44067ec2-05cd-4165-b5bd-f313140318e7.jpg');
    background-size: cover; /* Adjust to cover the entire area */
    background-position: center; /* Center the image */
    background-repeat: no-repeat; /* Prevent tiling */
    background-attachment: fixed; /* Make the background fixed while scrolling */
}

[data-testid="stHeader"] {
background-color: rgba(0, 0, 0, 0);
} 

</style>
"""

# Inject the CSS
st.markdown(main_section_css, unsafe_allow_html=True)

# Take an input of a pokemon number from the user. (X)
# Multiple variants for same number
# Display the name, height, weight and other attributes of the pokemon. (X)
# Display the image of the pokemon. (X)
# Display a graph showing something like height / weight compared to a random selection of other pokemon.
# Note: Your app needs to be on the streamlit community cloud, the URL is something like: https://myapp.streamlit.app/ not https://probable-fishstick-4jwj75g6j6v25j9p.github.dev/


def get_number_for_variant_pokemon(pokemon_number,selected_variant):
    name_parts = selected_variant.split()
    if len(name_parts) >= 2:
    # Reorder the first two words (Mega and Charizard)
        reordered_name = name_parts[1] + " " + name_parts[0] + " " + " ".join(name_parts[2:])
    else:
    # If there's only one word, keep it as is
        reordered_name = selected_variant
    rename = reordered_name.lower().replace(" ", "-")
    if len(name_parts) == 2:
        rename = rename.rstrip('-')
    
    variant_url = "https://pokeapi.co/api/v2/pokemon-species/" + str(pokemon_number)
    response = requests.get(variant_url)
    data = response.json()
    for variant in data.get("varieties", []):
        if variant["pokemon"]["name"] == rename:
            url = variant["pokemon"]["url"]
            ending_number = url.rstrip('/').split('/')[-1]
            return (ending_number)
    return (pokemon_number)
    

IMG_ROOT = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/"

# st.title("Pokemon Number Input")
# pokemon_number = st.number_input("Number between 1 and 898", min_value = 1, max_value = 898)

df = pd.read_csv('./pokemon.csv')

# Sidebar and pokemon selection
# Get a list of the names, dropping any variants against the same pokedex number
df_no_dupes = df.drop_duplicates(subset='pokedex_number', keep='first')
df_no_dupes = df_no_dupes.reset_index(drop=True)
pokemon_names = df_no_dupes["name"].tolist()

# Set the default to 1
pokemon_number = 1


with st.sidebar:
    st.title("Select a Pokémon!")
    # Get a pokedex number
    pokemon_number = st.number_input("Enter a Pokédex number between 1 and 898", value=pokemon_number, min_value=1, max_value=898)
    # Get the index of the selected number to retrieve the corresponding name
    pokemon_index = int(df_no_dupes.index[df_no_dupes['pokedex_number'] == pokemon_number][0])
    # Update the name field to the selected number, or get a new number by selecting a name
    selected_name = st.selectbox("Select a Pokémon by name", pokemon_names, index=pokemon_index)
    # Updating the selected number based on the selected name
    pokemon_number = df[df["name"] == selected_name]['pokedex_number'].iloc[0]
    # Display the selected name and number
    st.write(f"You have selected Pokédex number {pokemon_number} which is {selected_name}!")

    selected_pokemon_data = df[df['pokedex_number'] == pokemon_number]



    # Check if there are variants:
    if selected_pokemon_data.shape[0] != 1:
        name_list = tuple(f'{name}' for name in selected_pokemon_data['name'])
        # Allow user to select from variants:
        selected_variant = st.selectbox('Select Pokemon Version:',
            (name_list))
        #Select the variant
        selected_pokemon_data = df[df['name'] == selected_variant]        
        pokemon_number = get_number_for_variant_pokemon(pokemon_number,selected_variant)
        
    selected_pokemon_data = selected_pokemon_data.iloc[0]
    shiny_bool = st.checkbox("Shiny Pokemon")
    if shiny_bool:
        IMG_ROOT = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/shiny/"

st.title(f"{selected_name} Statistics")

stats_df = pd.DataFrame({
    "Attribute": ["Name", "Weight (kg)", "Height (m)", "Type 1", "Type 2", "Total Points"],
    "Value": [
        selected_pokemon_data['name'],
        selected_pokemon_data['weight_kg'],
        selected_pokemon_data['height_m'],
        selected_pokemon_data['type_1'],
        selected_pokemon_data['type_2'],
        selected_pokemon_data['total_points']
    ]
})

st.table(stats_df)

img_url = IMG_ROOT + str(pokemon_number) + ".png"

st.image(img_url)


my_pokemon_df = pd.DataFrame(selected_pokemon_data)
my_pokemon_df = my_pokemon_df.T
sample_pokemon_df = df[df['pokedex_number'] != pokemon_number].sample(5)

# df_for_scatter = pd.concat([my_pokemon_df, sample_pokemon_df])
# #df_for_scatter

# st.subheader("""
# Draw Scatter plot showing height and weight against 5 random pokemon)
# """)
# height_weight_fig = px.scatter(data_frame = df_for_scatter,x='height_m',y='weight_kg',color='name')
# st.plotly_chart(height_weight_fig)

st.subheader("Pokémon Comparison Chart")

# Get the selection for the number of random pokemon to display on the chart
number_of_random = st.slider("How many random Pokemon do you want to compare to?", value=5, min_value=1, max_value=100)

# Make a df with the selected pokemon and the random pokemon
my_pokemon_df = pd.DataFrame(selected_pokemon_data)
my_pokemon_df = my_pokemon_df.T
sample_pokemon_df = df[df['pokedex_number'] != pokemon_number].sample(number_of_random)

df_for_scatter = pd.concat([my_pokemon_df, sample_pokemon_df])

# Interactive graph selection
# Create column objects
col1, col2 = st.columns(2)

# Get a list of the numerical columns in the dataframe and make the selections look nice
df_columns = df.select_dtypes(include=['number']).columns.tolist()
df_columns.pop(0)
df_columns_nice = [x.replace('_', ' ').title() if len(x) > 2 else x.upper() for x in df_columns]

# Show the columns with dropdown selection boxes
with col1:
    x_selection_nice = st.selectbox("Select what you want on the x axis", df_columns_nice)
    # Get the corresponding column title from the dataframe
    x_selection = df_columns[df_columns_nice.index(x_selection_nice)]

with col2:
    y_selection_nice = st.selectbox("Select what you want on the y axis", df_columns_nice)
    # Get the corresponding column title from the dataframe
    y_selection = df_columns[df_columns_nice.index(y_selection_nice)]
    
    
# Produce the figure
interactive_fig = px.scatter(data_frame = df_for_scatter,x=x_selection,y=y_selection, color='name')
# Update axis titles
interactive_fig.update_layout(
    title=f"{x_selection_nice} against {y_selection_nice}",
    xaxis_title=x_selection_nice,
    yaxis_title=y_selection_nice
)
# Show the plot
st.plotly_chart(interactive_fig, key=100)