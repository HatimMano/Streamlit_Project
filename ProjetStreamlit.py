from logging import log
from altair.datasets import load_dataset
from altair.vegalite.v4.schema.channels import SizeValue
from numpy.core.fromnumeric import size
from pandas._config.config import options
from pandas.core.indexes.range import RangeIndex
import streamlit as st
import numpy as np
import pandas as pd 
import time
from functools import wraps
from time import time
from pathlib import Path
import csv
import altair as alt
from PIL import Image
from streamlit.util import index_
import statistics
st.set_option('deprecation.showPyplotGlobalUse', False)


file = open("temps.txt", "w+")
def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time()
        result = f(*args, **kwargs)
        end = time()
        file.write('Temps écoulé : {}'.format((end-start)) + "sec")
        return result
    return wrapper

@st.cache(allow_output_mutation=True)
def load_data(int,nmin):        #Loading du DataFrame contenant uniquement les lignes liées à la commune de Paris
    if int == 16:
        file = 'https://jtellier.fr/DataViz/full_2016.csv'
    if int == 17:
        file = 'https://jtellier.fr/DataViz/full_2017.csv'
    if int == 18:
        file = 'https://jtellier.fr/DataViz/full_2018.csv'
    if int == 19:
        file = 'https://jtellier.fr/DataViz/full_2019.csv'
    if int == 20:
        file = 'https://jtellier.fr/DataViz/full_2020.csv'
    data = pd.read_csv(file, skiprows = range(1,nmin))
    data = preprocessing(data)
    return data

def preprocessing(data): #Suppression des NaN, doublons et biens non 'vente', sélection des colonnes qui seront utiles
    data = pd.DataFrame(data, columns = ['code_postal','valeur_fonciere','surface_reelle_bati','type_local', 'nombre_pieces_principales','latitude','longitude','nature_mutation','adresse_nom_voie','date_mutation'])
    data['code_postal'] = data['code_postal']-75000
    data = data[data['surface_reelle_bati'].notna()]
    data = data[data['valeur_fonciere'].notna()]
    data = data.drop_duplicates(subset=['valeur_fonciere'])
    data = data[data['nature_mutation'] == 'Vente']
    data = data[data['valeur_fonciere'] > 50000]
    data = data[(data['type_local'] != "Local industriel. commercial ou assimilé")] 
    return data

def checkboxed(df,a):
    agree = st.checkbox(str(a))
    if agree:        
        st.write(df)

@timing
@st.cache(allow_output_mutation=True)
def concatenate_data():                 #Concaténation de l'ens des fichiers de 2016 à 2020 afin d'avoir un maximum de données
    df_16 = load_data(16,2881069)       
    df_17 = load_data(17,3317893)
    df_18 = load_data(18,3261018)
    df_19 = load_data(19,3465030)
    df_20 = load_data(20,2405432)            
    return pd.concat([df_16,df_17,df_18,df_19,df_20], axis = 0).sort_values(by = ['valeur_fonciere'])

def get_value(df, name_column, num_row):
    return df[str(name_column)][int(num_row)]

def write_smthg_stylish(text, font_family, color, font_size):
    st.title("")
    smthg = '<p style="font-family:' + font_family+ '; color:' + color + '; font-size:'+  str(font_size) + 'px;">' + text + '</p>'
    st.markdown(smthg, unsafe_allow_html=True)


#INITIALISATION DE L'ENSEMBLE DES DATAFRAMES UTILISES
def main():

    df = concatenate_data()


    #1) Création DataFrame Moyenne :
    df['prix_m2'] = df['valeur_fonciere']/df['surface_reelle_bati']
    df_par_arrondisssement = df[['code_postal', 'valeur_fonciere','surface_reelle_bati']].groupby(['code_postal']).mean()
    df_par_arrondisssement.rename(columns={"valeur_fonciere": "valeur_fonciere_moyenne", "surface_reelle_bati" : "surface_reelle_bati_moyenne"},inplace = True)
    df_par_arrondisssement['arrondissement'] = range(1,21)
    df_par_arrondisssement['prix_moyen_m2'] = df_par_arrondisssement['valeur_fonciere_moyenne']/df_par_arrondisssement['surface_reelle_bati_moyenne']

    #2) Création du DataFrame Biens "de luxe" :
    df_luxe0 = pd.DataFrame(df, columns = ['valeur_fonciere','code_postal','latitude', 'longitude','surface_reelle_bati','nombre_pieces_principales','type_local'])
    df_luxe1 = pd.DataFrame(df, columns = ['valeur_fonciere','code_postal','latitude', 'longitude','surface_reelle_bati','nombre_pieces_principales','type_local','adresse_nom_voie'])
    df_luxe1['log_valeur_fonciere'] = np.log(df_luxe1['valeur_fonciere'])
    df_luxe2 = df_luxe0



    #SÉPARATION EN 3 ONGLETS

    #Création du sidebar
    st.sidebar.title('Menu')
    domaine = st.sidebar.selectbox("", ["Analyse Globale", "Analyse Biens Onéreux", "Recherche Appartement ou Maison"])



    if domaine == "Analyse Globale":

        
        #Affichage du DataFrame Moyenne : 
        st.title("Valeurs Moyennes des biens par arrondissement")
        st.write(df_par_arrondisssement)
        write_smthg_stylish("Voici le graphique représentant le prix moyen au m2 en fonction des arrondissements ",
            'cursive', 'White', 20)
        st.bar_chart(df_par_arrondisssement['prix_moyen_m2'])
        df_officiel = pd.DataFrame([13.3, 12.3, 13.4, 13.2, 13.2, 15.6, 13.4, 12.8, 11.7, 10.3, 10.6, 9.7, 9.2, 9.9, 10.8, 11.3, 11.4, 9.9, 9.4, 9.3], columns=['prix_moyen_m2_officiel'], index = range(1,21))
        df_ecart = df_par_arrondisssement
        df_ecart['ecart(€/m2)'] = abs(df_par_arrondisssement['prix_moyen_m2'] - df_officiel['prix_moyen_m2_officiel']*1000)
        prix_moyen_m2_officiel = df_officiel['prix_moyen_m2_officiel'].sum()*1000
        prix_moyen_m2_total = df_par_arrondisssement['prix_moyen_m2'].sum()
        ecart_moyen = (prix_moyen_m2_total - prix_moyen_m2_officiel)/20

        if st.button('Voir Commentaires...'):
            write_smthg_stylish("Le nombre de données analysées (50 000) ne nous permet pas d'avoir des chiffres précis. C'est pourquoi nous obtenons des valeurs parfois très différentes de la réalité. Comparons nos valeurs avec celles trouvées sur Internet",
            'cursive', 'White', 20)
            image = Image.open('test1.jpg')
            st.image(image, caption='Comparaison entre données officielles et calculées', width= 700)
            write_smthg_stylish("Ecart entre prix officel et prix calculé à partir du dataset",
            'cursive', 'White', 20)
            st.write(alt.Chart(df_ecart).mark_bar().encode(alt.X("arrondissement"),y='ecart(€/m2)'))
            st.write("On a un écart moyen de "+ str(round(ecart_moyen)) + "€/m2 par arrondissement.")
        
        write_smthg_stylish("Evolution du montant annuel investi sur l'immobilier dans Paris entre 2016 et 2020 ", 'cursive', 'White', 20)
        df['date_mutation'] = df['date_mutation'].astype(str).str[0:4]
        st.write(alt.Chart(df).mark_bar().encode(alt.X("date_mutation"),y='valeur_fonciere'))


    if domaine == "Analyse Biens Onéreux":

        #Affichage du DataFrame Biens "de luxe" :
        st.title('Visualisons les biens > 7 chiffres vendus dans chaque arrondissement.')
        
        write_smthg_stylish('Choisissez une valeur de bien (en M€)', 'cursive', 'Grey', 30)
        valeur_bien = st.select_slider('', options = range(0,101))
        df_luxe0 = df_luxe0[df_luxe0['valeur_fonciere'] > valeur_bien*1000000]

        df_nombre_bien_luxe_par_arrondissement = df_luxe0.groupby(['code_postal']).size().reset_index().rename(columns={0:'nombre_biens_par_arrondissement'} )
        df_nombre_bien_luxe_par_arrondissement.rename(columns={"code_postal": "arrondissement"},inplace = True)
        nb_arrondissement_biens = str(len(df_nombre_bien_luxe_par_arrondissement))
        max_biens = df_nombre_bien_luxe_par_arrondissement['nombre_biens_par_arrondissement'].max()
        total_biens = df_nombre_bien_luxe_par_arrondissement['nombre_biens_par_arrondissement'].sum()
        df0 = df_nombre_bien_luxe_par_arrondissement[df_nombre_bien_luxe_par_arrondissement['nombre_biens_par_arrondissement'] == max_biens].reset_index()
        if valeur_bien == 0:
            st.write('On retrouve des biens dans ' + nb_arrondissement_biens + ' arrondissements différents de Paris :')
        else :
            st.write('On retrouve des biens supérieurs à  ' + str(valeur_bien) + 'M€ dans ' + nb_arrondissement_biens + ' arrondissements différents de Paris dont '+ str(max_biens)+ ' dans le ' + str(round(get_value(df0,'arrondissement',0))) + "e arrondissement, c'est-à-dire "+ str(round(max_biens/total_biens*100)) + '%.')
        st.write(df_nombre_bien_luxe_par_arrondissement)
        st.write(alt.Chart(df_nombre_bien_luxe_par_arrondissement).mark_bar().encode(x = 'arrondissement', y = 'nombre_biens_par_arrondissement'))

        #Création Map1 :
        df_map = pd.DataFrame(df_luxe0, columns = ['nombre_biens_par_arrondissement','latitude','longitude'])
        df_map = df_map.fillna(0)
        mask = df_map['longitude']!= 0
        df_map = df_map.loc[mask]
        st.map(df_map)

        st.title('Choix arrondissement')
        write_smthg_stylish('Numéro Arrondissement', 'cursive', 'Grey', 30) 

        arrondissement = range(1,21)
        num_arrondisssement = st.selectbox('', arrondissement)
        if num_arrondisssement == 1:
            st.subheader('Bienvenue dans le ' + str(num_arrondisssement) + 'er arrondissement.' )
        else:
            st.subheader('Bienvenue dans le ' + str(num_arrondisssement) + 'ème arrondissement.' )

        valeur_bien2 = st.select_slider('', options = range(1,101))
        #Création Map2
        df_luxe2 = df_luxe2[df_luxe2['code_postal'] == num_arrondisssement]
        df_luxe2 = df_luxe2[df_luxe2['valeur_fonciere'] > valeur_bien2*1000000]
        df_map1 = pd.DataFrame(df_luxe2, columns = ['latitude','longitude'])
        df_map1 = df_map1.fillna(0)
        mask = df_map1['longitude']!= 0
        df_map1 = df_map1.loc[mask]
        nb_biens = len(df_map1)
        if nb_biens == 0:
            st.error("Il n'y a aucun bien supérieur à cette valeur dans cet arrondissement.")
        else :
            st.success('On retrouve ' + str(nb_biens) + ' bien(s) supérieur(s) à  ' + str(valeur_bien2) + 'M€ dans le ' + str(num_arrondisssement) + 'e arrondissement de Paris :')
        st.map(df_map1)
        
        checkboxed(pd.DataFrame(df_luxe2, columns = ['valeur_fonciere','surface_reelle_bati', 'type_local']),"Inspecter les valeurs des données :")




    if domaine == "Recherche Appartement ou Maison":

        st.title("Simulons une recherche de logement (Appart ou Maison) dans Paris")
        write_smthg_stylish('Revenons au 1er Janvier 2016 et supposons que vous cherchez un logement à acheter sur la capitale.', 'cursive', 'White',  30)
        df_luxe1 = df_luxe1.fillna(0)
        st.title('')
        mask = df_luxe1['nombre_pieces_principales']!= 0
        df_luxe1 = df_luxe1.loc[mask]
        
        
        #Choix Arrondissement
        arrondissement = range(1,21)
        write_smthg_stylish('Choisissez un arrondissement qui vous intéresse.', 'cursive', 'Grey', 20)
        num_arrondisssements = st.selectbox("", arrondissement)
        st.title('')
        df_luxe1 = df_luxe1[df_luxe1['code_postal'] == num_arrondisssements]
        
        #Choix Budget
        budget = range(100000,2100000, 100000)
        write_smthg_stylish('Budget max.', 'cursive', 'Grey', 20)
        valeur_bien1 = st.selectbox('', options = budget)
        df_luxe1 = df_luxe1[df_luxe1['valeur_fonciere'] < valeur_bien1] 
        
        #Choix Surface
        surface = range(10,2000,10)
        write_smthg_stylish('Surface min.', 'cursive', 'Grey', 20)
        surface_bien = st.selectbox('', surface)
        df_luxe1 = df_luxe1[df_luxe1['surface_reelle_bati'] > surface_bien*0.9]
        
        #Choix Nombre de Pièces
        chambre = range(1,10,1)    
        write_smthg_stylish('Nombre de chambres min.', 'cursive', 'Grey', 20)
        nombre_chambres = st.selectbox('', chambre)
        df_luxe1 = df_luxe1[df_luxe1['nombre_pieces_principales'] >= nombre_chambres]
        

        if len(df_luxe1) == 0:
            st.error("Malheureusement nous n'avons aucune offre à vous proposer. Soyez moins exigeant et revoyez vos critères.")
        else:
            st.success("Nous avons " + str(len(df_luxe1)) + " offre(s) à vous proposer.")

        st.write(pd.DataFrame(df_luxe1, columns = ['valeur_fonciere', 'surface_reelle_bati', 'nombre_pieces_principales', 'type_local']))
        
        agree = st.checkbox("Analyser le graphique :")
        if agree :
            st.write(alt.Chart(df_luxe1).mark_point().encode(x='valeur_fonciere', y='surface_reelle_bati', color = 'type_local').interactive())

        write_smthg_stylish('Inscrivez la référence du bien qui vous intéresse (colonne de gauche).', 'cursive', 'Grey', 20)
        df_map3 = pd.DataFrame(df_luxe1, columns = ['valeur_fonciere', 'surface_reelle_bati', 'nombre_pieces_principales', 'type_local','latitude','longitude','adresse_nom_voie', 'code_postal'])
        df_map3 = df_map3.fillna(0)
        mask = df_map3['longitude']!= 0
        df_map3 = df_map3.loc[mask]
        ref = st.text_input('')
        try:
            df_ref = df_map3.loc[[int(ref)]]
            st.map(df_ref)
            st.balloons()
            st.success('Votre bien se situe ' +  str(get_value(df_ref,'adresse_nom_voie', ref)) + ' dans le ' + str(int(get_value(df_ref,'code_postal', ref))) + 'e arrondissement.' )  

        except (ValueError,KeyError):
            st.error("La référence notée est incorrecte.")
        

if __name__ == "__main__":
    main()
    
