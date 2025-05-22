
import requests

def obtener_precio_dolar_blue():
    try:
        response = requests.get("https://dolarapi.com/v1/dolares/blue", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("venta")
        else:
            return None
    except Exception as e:
        return None