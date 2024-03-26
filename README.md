## Readme

### Introduction
This code is a Streamlit web application for analyzing real estate data in Paris. It allows users to explore various aspects of property transactions, including average property prices, luxury property listings, and personalized property searches.

### Features
1. **Analyse Globale**: Provides an overview of average property prices per square meter in each district of Paris. It also includes a comparison between official and calculated average prices.
2. **Analyse Biens Onéreux**: Allows users to explore luxury property listings (properties priced over a million euros) in each district of Paris. Users can visualize the number of luxury properties per district and explore individual listings on a map.
3. **Recherche Appartement ou Maison**: Simulates a property search by allowing users to specify their preferences for district, budget, minimum surface area, and minimum number of rooms. It then displays relevant property listings based on the user's criteria.

### How to Use
1. **Installation**: Ensure you have Python 3 installed on your system along with the required dependencies listed in the `requirements.txt` file.
2. **Run the Application**: Execute the Python script `app.py` to launch the Streamlit web application.
3. **Interact with the App**: Use the sidebar menu to navigate between the different analysis options. Depending on the selected option, you can explore average property prices, luxury property listings, or conduct a personalized property search.

### Dependencies
- Streamlit
- NumPy
- Pandas
- Altair
- Pillow

### Dataset
The application uses real estate transaction data for Paris from the years 2016 to 2020, sourced from public datasets available online.
