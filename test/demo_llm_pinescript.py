import google.generativeai as genai
import os
import json

# Configura tu clave
genai.configure(api_key="AIzaSyBEtkAxGdjfQwmD_7QRrlv13Bg8xsUMzT8")  # o directamente: api_key="tu_clave_aquí"

# Carga el modelo
model = genai.GenerativeModel("gemini-2.0-flash")

# Tu Pine Script
pine_script = """
maFast = ta.ema(close, 9)
maSlow = ta.ema(close, 21)
longCondition = ta.crossover(maFast, maSlow)
shortCondition = ta.crossunder(maFast, maSlow)
"""

# Dataset de prueba (simulado por ahora)
ohlcv_data = [
    {"open": 100, "high": 105, "low": 98, "close": 102, "volume": 1000},
    {"open": 102, "high": 108, "low": 101, "close": 107, "volume": 1500},
    {"open": 107, "high": 110, "low": 105, "close": 106, "volume": 1400},
    {"open": 106, "high": 109, "low": 104, "close": 105, "volume": 1200},
    {"open": 105, "high": 108, "low": 103, "close": 107, "volume": 1100},
]

# Armar el prompt
prompt = f"""
Tu tarea es analizar una estrategia de trading en Pine Script y determinar si en la última vela debe ejecutarse una señal de compra ("BUY"), venta ("SELL") o no hacer nada ("HOLD").

### Estrategia Pine Script ###
{pine_script}

### Velas OHLCV ###
Cada vela incluye: open, high, low, close, volume.
{json.dumps(ohlcv_data, indent=2)}

### Reglas ###
- Calculá las EMAs para cada vela.
- Detectá si hay un cruce alcista o bajista en la última vela.
- Si hay cruce alcista: devolver BUY.
- Si hay cruce bajista: devolver SELL.
- Si no hay cruce: devolver HOLD.

### Resultado esperado ###
Devolveme un JSON como este:
{{"signal": "BUY", "reason": "Explicación"}}
"""

# Enviar al modelo
response = model.generate_content(prompt)

# Mostrar respuesta
print(response.text)
