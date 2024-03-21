from geopy.geocoders import Nominatim

def ottieni_coordinate(nome_citta):
    geolocatore = Nominatim(user_agent="nome_applicazione")
    posizione = geolocatore.geocode(nome_citta)
    if posizione:
        latitudine = posizione.latitude
        longitudine = posizione.longitude
        return latitudine, longitudine
    else:
        return None

# Esempio di utilizzo
nome_citta = "Brescia"
coordinate = ottieni_coordinate(nome_citta)
if coordinate:
    print(f"Le coordinate di {nome_citta} sono: {coordinate}")
else:
    print(f"Impossibile trovare le coordinate di {nome_citta}")
