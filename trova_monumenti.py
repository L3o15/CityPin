import requests

def ottieni_poi_principali(nome_citta):
    overpass_endpoint = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
        [out:json];
        area[name="{nome_citta}"]->.searchArea;
        (
            node["tourism"](area.searchArea);
            way["tourism"](area.searchArea);
            relation["tourism"](area.searchArea);
            node["amenity"](area.searchArea);
            way["amenity"](area.searchArea);
            relation["amenity"](area.searchArea);
            node["shop"](area.searchArea);
            way["shop"](area.searchArea);
            relation["shop"](area.searchArea);
            node["leisure"](area.searchArea);
            way["leisure"](area.searchArea);
            relation["leisure"](area.searchArea);
        );
        out center;
    """
    response = requests.post(overpass_endpoint, data=overpass_query)
    data = response.json()
    poi_principali = []
    if 'elements' in data:
        for elemento in data['elements']:
            if 'tags' in elemento:
                nome = elemento['tags'].get('name', 'Senza nome')
                if nome != 'Senza nome':
                    poi_principali.append(nome)
    return poi_principali

# Esempio di utilizzo
nome_citta = "Brescia"
poi_principali = ottieni_poi_principali(nome_citta)
print(f"Punti di interesse principali a {nome_citta}:")
print(f"Numero di POI principali trovati: {len(poi_principali)}")
