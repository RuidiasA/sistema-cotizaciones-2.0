import pandas as pd
import os
import re

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
CARPETA_EXCEL = r"E:\TASA" 
VARIACIONES = [
    "cuaderno", "cuadernos", "anillados", "espirales",
    "libreta", "libretas", "journals", "notepads",
    "block", "blocks", "blocs de notas", "tacos de notas",
    "hoja", "hojas", "folios", "papeles",
    "agenda", "agendas", "planificadores", "diarios",
    "cuadernillo", "cuadernillos", "folletos", "pasquines",
    "cartuchera", "cartucheras", "estuches", "portautiles",
    "neceser", "neceseres", "bolsos de aseo", "organizadores",
    "lapicero", "lapiceros", "bolígrafos", "plumas", "esferos",
    "resaltador", "resaltadores", "plumones flúor", "marcadores de texto",
    "tarjeta", "tarjetas", "tarjetas personales", "business cards",
    "porta nombre acrílico", "porta nombres acrílicos", "identificadores", "fotochecks",
    "porta nombre madera", "porta nombres madera", "identificadores rústicos",
    "porta post it calendario", "porta post it calendarios", "organizadores de escritorio"
]

HOJAS_EXCLUIDAS = ["criterios", "tallas", "cronograma", "datos", "deuda", "producción", "proveedor", "proveedores", "costo de proyecto"]

acumulador_1, contador_1 = 0.0, 0
acumulador_2, contador_2 = 0.0, 0
acumulador_3, contador_3 = 0.0, 0

# ==========================================
# FUNCIONES DE APOYO
# ==========================================
def limpiar_y_entero(val):
    """Convierte la cantidad a entero puro. Si no es número, devuelve 0."""
    try:
        if pd.isna(val): return 0
        s = str(val).lower().replace(',', '').strip()
        # Extrae solo el primer número encontrado
        num_match = re.findall(r"\d+\.?\d*", s)
        if num_match:
            return int(float(num_match[0]))
        return 0
    except:
        return 0

def limpiar_precio(val):
    """Limpia valores monetarios."""
    try:
        if pd.isna(val): return 0.0
        s = str(val).lower().replace('s/.', '').replace('s/', '').replace(',', '').strip()
        matches = re.findall(r"\d+\.?\d*", s)
        return float(matches[0]) if matches else 0.0
    except:
        return 0.0

def cumple_busqueda_tokenizada(fila):
    """Busca palabra por palabra en toda la fila."""
    texto_unido = " ".join([str(x).lower() for x in fila if pd.notna(x)])
    # Divide el texto por cualquier cosa que no sea letra (espacios, guiones, puntos, etc.)
    palabras_en_fila = re.findall(r'\w+', texto_unido)
    for v in VARIACIONES:
        if v in palabras_en_fila:
            return True
    return False

# ==========================================
# 2. ESCANEO DE ARCHIVOS
# ==========================================
archivos_a_procesar = [os.path.join(CARPETA_EXCEL, f) for f in os.listdir(CARPETA_EXCEL) if f.endswith(('.xlsx', '.xls')) and not f.startswith('~$')]
print(f"📂 Procesando {len(archivos_a_procesar)} archivos...\n")

# ==========================================
# 3. BUCLE PRINCIPAL
# ==========================================
for ruta in archivos_a_procesar:
    nombre_archivo = os.path.basename(ruta)
    print(f"📄 Analizando: {nombre_archivo}")
    
    try:
        xls = pd.ExcelFile(ruta)
        mejor_hoja, mejor_df, col_map = None, None, {}
        max_casacas = -1

        for nombre_hoja in xls.sheet_names:
            if any(ex in nombre_hoja.lower() for ex in HOJAS_EXCLUIDAS): continue
            
            # Buscar cabecera de la tabla
            df_check = pd.read_excel(ruta, sheet_name=nombre_hoja, header=None, nrows=25)
            fila_header = -1
            for idx, fila in df_check.iterrows():
                linea = " ".join([str(x).lower() for x in fila.values])
                if ("cant" in linea or "cantidad" in linea) and ("costo" in linea or "s/." in linea or "uni" in linea):
                    fila_header = idx
                    break
            
            if fila_header != -1:
                df_temp = pd.read_excel(ruta, sheet_name=nombre_hoja, header=fila_header)
                df_temp.columns = [str(c).replace('\n', ' ').strip() for c in df_temp.columns]
                
                # Ubicar columnas de forma inteligente
                c_cant = next((c for c in df_temp.columns if any(kw in c.lower() for kw in ["cant. mín.", "cant.", "cant", "cantidad"])), None)
                c_finals = [c for c in df_temp.columns if any(kw in c.lower() for kw in ["unit", "uni.", "uni ", "no igv", "venta"])]
                c_provs = [c for c in df_temp.columns if any(kw in c.lower() for kw in ["costo s/.", "costo prov"]) 
                           and c not in c_finals and "total" not in c.lower()]

                if c_cant and (c_provs or c_finals):
                    mask = df_temp.apply(cumple_busqueda_tokenizada, axis=1)
                    if mask.sum() > max_casacas:
                        max_casacas = mask.sum()
                        mejor_hoja, mejor_df = nombre_hoja, df_temp
                        col_map = {'cant': c_cant, 'provs': c_provs, 'finals': c_finals}

        if mejor_df is None or max_casacas <= 0:
            print(f"   ❌ No se detectó una tabla válida.")
            continue

        vistos = set()
        sumadas = 0
        
        for idx, fila in mejor_df.iterrows():
            if not cumple_busqueda_tokenizada(fila): continue
            
            try:
                # REGLA DE ORO: Cantidad como Entero
                cantidad = limpiar_y_entero(fila[col_map['cant']])
                if cantidad <= 0: continue 

                # Buscar el mejor precio proveedor (> 15 soles para evitar bordados/setup)
                v1 = 0.0
                for c in col_map['provs']:
                    val = limpiar_precio(fila[c])
                    if val >= 15.0: v1 = val; break
                
                # Buscar el mejor precio cliente
                v2 = 0.0
                for c in col_map['finals']:
                    val = limpiar_precio(fila[c])
                    if val > v1: v2 = val; break # El precio cliente debe ser mayor al del proveedor

                if v1 <= 0 or v2 <= 0 or abs(v1-v2) < 0.5: continue
                
                huella = (cantidad, round(v1, 2), round(v2, 2))
                if huella in vistos: continue

                margen = ((v2 - v1) / v1) * 100
                if margen > 250: continue # Filtro de seguridad

                vistos.add(huella)
                print(f"   -> [Fila {idx}] OK | Cant: {cantidad} | Prov: S/.{v1} | Cli: S/.{v2} | Margen: {margen:.2f}%")
                
                if cantidad > 1000:
                    acumulador_1 += margen; contador_1 += 1
                elif cantidad > 500:
                    acumulador_2 += margen; contador_2 += 1
                else:
                    acumulador_3 += margen; contador_3 += 1
                sumadas += 1
            except: continue

        print(f"   ✅ Éxito en '{mejor_hoja}'. Filas: {sumadas}")

    except Exception as e:
        print(f"   💥 Error: {e}")

# ==========================================
# 4. RESULTADOS FINALES
# ==========================================
def promediar(acum, cont):
    return f"{round(acum / cont, 2)}%" if cont > 0 else "0.00%"

print("\n" + "="*45)
print(f"📊 Margen Promedio (> 1000): {promediar(acumulador_1, contador_1)} ({contador_1} casos)")
print(f"📊 Margen Promedio (> 500):  {promediar(acumulador_2, contador_2)} ({contador_2} casos)")
print(f"📊 Margen Promedio (Resto):  {promediar(acumulador_3, contador_3)} ({contador_3} casos)")
print("="*45)