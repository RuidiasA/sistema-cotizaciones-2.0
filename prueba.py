import pandas as pd
import os
import re
import unicodedata

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
CARPETA_EXCEL = r"E:\otros" 
VARIACIONES_POR_CATEGORIA = {
    "prendas de cabeza": [
        "gorro", "gorros", "gorra", "gorras", "chullo", "chullos", "beanies", "pasamontaña",
        "pasamontañas", "visera", "viseras", "parasoles", "parasoles", "viseras deportivas",
    ],
    "ropa y abrigo": [
        "casaca", "casacas", "chamarra", "chamarras", "camiseta", "camisetas", "cortavientos", 
        "jackets", "chaqueta", "chaquetas", "blazer", "blazers",
        "parka", "parkas", "abrigos largos", "gabardina", "gabardinas",
        "abrigo", "abrigos", "sobretodo", "sobretodos", "prendas de invierno",
        "polera", "poleras", "sudadera", "sudaderas", "hoodie", "hoodies", "buzo",
        "buzos", "chaleco", "chalecos", "gilets", "chalecos tácticos",
        "polo", "polos", "remera", "remeras", "t-shirt", "t-shirts",
    ],
    "textiles y hogar": [
        "toalla", "toallas", "toallones", "paño", "paños", "paños microfibra",
        "almohada", "almohadas", "almohadas de viaje", "cojin", "cojines",
        "mandil", "mandiles", "delantal", "delantales", "tabliers",
    ],
    "bolsos y transporte": [
        "mochila", "mochilas", "morral", "morrales", "morrales de espalda", "backpack",
        "backpacks", "canguro", "canguro", "canguros", "riñonera", "riñoneras", "koalas",
        "bolsa", "bolsas", "bolso", "bolsos", "bolsas ecológicas", "bolsos deportivos", 
        "bolsos cruzados", "totes", "notex", "chimpunera", "chimpuneras", "portacalzado",
        "portacalzados", "bandolera", "bandoleras", "maletin", "maletines",
    ],
    "papeleria y oficina": [
        "cuaderno", "cuadernos", "anillado", "anillados", "espirales",
        "libreta", "libretas", "journals", "notepad", "notepads",
        "block", "blocks", "blocs de notas", "tacos de notas", "nota", "notas",
        "hoja", "hojas", "folio", "folios", "papel", "papeles",
        "agenda", "agendas", "planificadores", "diario", "diarios",
        "cuadernillo", "cuadernillos", "folleto", "folletos", "pasquines",
        "cartuchera", "cartucheras", "estuche", "estuches", "portautiles",
        "neceser", "neceseres", "bolsos de aseo", "organizadores",
        "lapicero", "lapiceros", "bolígrafo", "bolígrafos", "pluma", "plumas", "esferos",
        "resaltador", "resaltadores", "plumon", "plumones", "plumones flúor", "marcadores de texto",
        "tarjeta", "tarjetas", "tarjetas personales", "business cards",
        "porta nombre acrílico", "porta nombres acrílicos", "identificadores", "fotochecks",
        "porta nombre madera", "porta nombres madera", "identificadores rústicos",
        "porta post it calendario", "porta post it calendarios", "organizadores de escritorio",
    ],
    "accesorios y premiaciones": [
        "llavero", "llaveros", "pendientes", "keychains",
        "pin", "pines", "prendedores", "insignia", "insignias", "broche",
        "broches", "trofeo", "trofeos", "copa", "copas", "galardon",
        "galardones", "medalla", "medallas", "preseas", "condecoracion", "condecoraciones",
        "placa", "placas", "placas grabadas", "reconocimiento", "reconocimientos", 
    ],
    "menaje y otros": [
        "tomatodo", "tomatodos", "botella", "botellas", "vino", "vinos", 
        "caramañolas", "shakers", "vaso", "vasos", "vasos térmicos",
        "copas", "copas", "taza", "tazas", "mugs", "pocillos",
        "cafetera", "cafeteras", "prensas francesas", "mokes",
        "cuchara", "cucharas", "cubiertos", "utensilios", "batidor",
        "batidores", "mezclador", "mezcladores", "espumadores", "sticker",
        "stickers", "calcomanía", "calcomanías", "adhesivo", "adhesivos",
        "caja", "cajas", "empaques", "packaging", "cubo", "cubos", "dado",
        "dados", "bloque", "bloques", "alcancía", "alcancías", "huchas", "chanchitos",
        "pad mouse", "mouse pad", "mousepad", "alfombrillas", "tapetes de escritorio",
        "prop selfie", "props selfie", "accesorios para fotos", "marcos selfie",
        "tablet tent", "tablet tents", "habladores", "carpas de mesa", "displays",
        "kit", "power bank", "manta", "mantas", "pastillero", "pastilleros",
        "porta frasco", "exhibidor", "pasa diapositiva",
    ],
}

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

def normalizar_texto(texto):
    """Normaliza texto para busqueda robusta (sin tildes ni simbolos)."""
    base = unicodedata.normalize("NFKD", str(texto).lower())
    sin_tildes = "".join(ch for ch in base if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", sin_tildes).strip()

def seleccionar_variaciones():
    opciones = "\n".join(f"  - {c}" for c in VARIACIONES_POR_CATEGORIA.keys())
    prompt = (
        "\n".join([
            "=" * 55,
            " Seleccion de producto",
            "=" * 55,
            "Ingresa una categoria o palabra clave:",
            opciones,
            "Ejemplos: lapicero | papeleria y oficina",
            ""  # linea en blanco antes del input
        ])
        + "> "
    )
    entrada = input(prompt).strip()
    entrada_norm = normalizar_texto(entrada)

    for categoria, lista in VARIACIONES_POR_CATEGORIA.items():
        if normalizar_texto(categoria) == entrada_norm:
            return lista

    todas = [v for grupo in VARIACIONES_POR_CATEGORIA.values() for v in grupo]
    filtradas = [v for v in todas if entrada_norm and entrada_norm in normalizar_texto(v)]
    return filtradas if filtradas else todas

VARIACIONES = seleccionar_variaciones()
VARIACIONES_NORMALIZADAS = [normalizar_texto(v) for v in VARIACIONES]

def cumple_busqueda_tokenizada(fila):
    """Busca palabra por palabra en toda la fila."""
    texto_unido = " ".join([str(x) for x in fila if pd.notna(x)])
    texto_norm = normalizar_texto(texto_unido)
    palabras_en_fila = set(texto_norm.split())
    for v in VARIACIONES_NORMALIZADAS:
        if v and (v in palabras_en_fila or v in texto_norm):
            return True
    return False

def convertir_total_a_unitario(col_nombre, valor, cantidad):
    """Convierte totales a precio unitario cuando corresponde."""
    if cantidad <= 0:
        return valor
    nombre = str(col_nombre).lower().strip()
    if "total producto" in nombre or "total.1" in nombre:
        return valor / cantidad if valor > 0 else valor
    if "total" in nombre and valor > cantidad:
        return valor / cantidad
    return valor

def buscar_precio_cliente(fila, cols_finals, cols_all, cantidad, v1):
    """Busca el mejor precio cliente; usa fallback si no hay columnas claras."""
    candidatos = []
    for c in cols_finals:
        val = limpiar_precio(fila[c])
        if val > v1:
            candidatos.append(val)

    if not candidatos:
        fallback_cols = [
            c for c in cols_all
            if any(kw in str(c).lower() for kw in ["venta", "precio", "pvp","no igv", "sin igv"])
        ]
        for c in fallback_cols:
            val = limpiar_precio(fila[c])
            val = convertir_total_a_unitario(c, val, cantidad)
            if val > v1:
                candidatos.append(val)

    return round(min(candidatos), 2) if candidatos else 0.0

def recortar_detalle(valor, max_len=20):
    """Recorta el detalle a un maximo de caracteres y agrega puntos suspensivos."""
    if pd.isna(valor):
        return ""
    texto = re.sub(r"\s+", " ", str(valor)).strip()
    if len(texto) <= max_len:
        return texto
    return texto[:max_len - 3].rstrip() + "..."

def imprimir_tabla_encabezado():
    ancho = 75
    print("   " + "-" * ancho)
    print("   " + f"{'Fila':>5} | {'Articulo':<20} | {'Cant':>5} | {'Prov':>10} | {'Cli':>10} | {'Margen%':>8}")
    print("   " + "-" * ancho)

def imprimir_fila_tabla(fila_id, articulo, cantidad, prov, cli, margen):
    print("   " + f"{str(fila_id):>5} | {str(articulo):<20} | {str(cantidad):>5} | {str(prov):>10} | {str(cli):>10} | {str(margen):>8}")

def imprimir_filas_fallidas(fallidas):
    if not fallidas:
        return
    ancho = 90
    print("   " + "-" * ancho)
    print("   " + f"{'No devueltas (motivo)':<28} | {'Fila':>5} | {'Articulo':<20} | {'Cant':>5} | {'Prov':>10} | {'Cli':>10}")
    print("   " + "-" * ancho)
    for item in fallidas:
        print(
            "   "
            + f"{item['motivo']:<28} | {str(item['fila']):>5} | {str(item['articulo']):<20} | {str(item['cant']):>5} | {str(item['prov']):>10} | {str(item['cli']):>10}"
        )

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
    print("\n" + "=" * 81)
    print(f"📄 Analizando: {nombre_archivo}")
    print("=" * 81)
    
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
                c_detalle = next((c for c in df_temp.columns if "detalle" in c.lower()), None)

                if c_cant and (c_provs or c_finals):
                    # Completa celdas combinadas para cantidad, detalle y precios
                    df_temp[c_cant] = df_temp[c_cant].ffill()
                    if c_detalle:
                        df_temp[c_detalle] = df_temp[c_detalle].ffill()
                    for c in (c_provs + c_finals):
                        df_temp[c] = df_temp[c].ffill()

                    mask = df_temp.apply(cumple_busqueda_tokenizada, axis=1)
                    if mask.sum() > max_casacas:
                        max_casacas = mask.sum()
                        mejor_hoja, mejor_df = nombre_hoja, df_temp
                        col_map = {'cant': c_cant, 'provs': c_provs, 'finals': c_finals, 'detalle': c_detalle}

        if mejor_df is None or max_casacas <= 0:
            print(f"   ❌ No se detectó una tabla válida.")
            continue

        vistos = set()
        sumadas = 0
        fallidas = []
        imprimir_tabla_encabezado()
        
        for idx, fila in mejor_df.iterrows():
            if not cumple_busqueda_tokenizada(fila):
                continue
            
            try:
                # REGLA DE ORO: Cantidad como Entero
                cantidad = limpiar_y_entero(fila[col_map['cant']])
                if cantidad <= 0:
                    fallidas.append({
                        "motivo": "cantidad",
                        "fila": idx,
                        "articulo": recortar_detalle(fila[col_map.get('detalle')] if col_map.get('detalle') else ""),
                        "cant": cantidad,
                        "prov": "-",
                        "cli": "-",
                    })
                    continue 

                # Buscar el mejor precio proveedor (> 15 soles para evitar bordados/setup)
                v1 = 0.0
                for c in col_map['provs']:
                    val = limpiar_precio(fila[c])
                    if val >= 0.2: v1 = round(val, 2); break
                
                # Buscar el mejor precio cliente
                v2 = buscar_precio_cliente(
                    fila,
                    col_map['finals'],
                    mejor_df.columns,
                    cantidad,
                    v1
                )

                min_diff = 0.5 if v1 >= 5 else 0.1
                if v1 <= 0 or v2 <= 0 or (v2 - v1) < min_diff:
                    fallidas.append({
                        "motivo": "precios",
                        "fila": idx,
                        "articulo": recortar_detalle(fila[col_map.get('detalle')] if col_map.get('detalle') else ""),
                        "cant": cantidad,
                        "prov": f"S/.{round(v1, 2)}",
                        "cli": f"S/.{round(v2, 2)}",
                    })
                    continue
                
                huella = (cantidad, round(v1, 2), round(v2, 2))
                if huella in vistos:
                    fallidas.append({
                        "motivo": "duplicado",
                        "fila": idx,
                        "articulo": recortar_detalle(fila[col_map.get('detalle')] if col_map.get('detalle') else ""),
                        "cant": cantidad,
                        "prov": f"S/.{round(v1, 2)}",
                        "cli": f"S/.{round(v2, 2)}",
                    })
                    continue

                margen = ((v2 - v1) / v1) * 100
                if margen > 450:
                    fallidas.append({
                        "motivo": "margen",
                        "fila": idx,
                        "articulo": recortar_detalle(fila[col_map.get('detalle')] if col_map.get('detalle') else ""),
                        "cant": cantidad,
                        "prov": f"S/.{round(v1, 2)}",
                        "cli": f"S/.{round(v2, 2)}",
                    })
                    continue # Filtro de seguridad

                vistos.add(huella)
                detalle_col = col_map.get('detalle')
                detalle_raw = fila[detalle_col] if detalle_col else ""
                detalle = recortar_detalle(detalle_raw)
                imprimir_fila_tabla(
                    idx,
                    detalle,
                    cantidad,
                    f"S/.{v1}",
                    f"S/.{v2}",
                    f"{margen:.2f}%"
                )
                
                if cantidad > 1000:
                    acumulador_1 += margen; contador_1 += 1
                elif cantidad > 500:
                    acumulador_2 += margen; contador_2 += 1
                else:
                    acumulador_3 += margen; contador_3 += 1
                sumadas += 1
            except:
                fallidas.append({
                    "motivo": "error",
                    "fila": idx,
                    "articulo": recortar_detalle(fila[col_map.get('detalle')] if col_map.get('detalle') else ""),
                    "cant": "-",
                    "prov": "-",
                    "cli": "-",
                })
                continue

        print(f"   ✅ Éxito en '{mejor_hoja}'. Filas: {sumadas}")
        imprimir_filas_fallidas(fallidas)

    except Exception as e:
        print(f"   💥 Error: {e}")

# ==========================================
# 4. RESULTADOS FINALES
# ==========================================
def promediar(acum, cont, contexto=None, margen_defecto=35.0, avisar=False):
    if cont > 0:
        return round(acum / cont, 2)
    if avisar:
        detalle = f" para {contexto}" if contexto else ""
        print(f"   ⚠️ Sin datos{detalle}; usando margen por defecto de {margen_defecto:.2f}%")
    return margen_defecto

def generar_cotizacion_rapida():
    print("\n" + "=" * 45)
    print(" Cotizacion rapida")
    print("=" * 45)

    articulo_nombre = input("Producto: ").strip()
    while True:
        try:
            cantidad_solicitada = int(input("Cantidad: ").strip())
            if cantidad_solicitada <= 0:
                print("   ⚠️ La cantidad debe ser mayor a 0.")
                continue
            break
        except ValueError:
            print("   ⚠️ Ingresa una cantidad valida (entero).")

    while True:
        try:
            precio_proveedor_nuevo = float(input("Precio proveedor (S/.): ").strip())
            if precio_proveedor_nuevo <= 0:
                print("   ⚠️ El precio debe ser mayor a 0.")
                continue
            break
        except ValueError:
            print("   ⚠️ Ingresa un precio valido (numero).")

    articulo_norm = normalizar_texto(articulo_nombre)
    variaciones_norm = [normalizar_texto(v) for grupo in VARIACIONES_POR_CATEGORIA.values() for v in grupo]
    coincide = any(
        articulo_norm and (articulo_norm in v or v in articulo_norm)
        for v in variaciones_norm
    )
    if not coincide:
        print("   ⚠️ El producto no coincide con las variaciones conocidas. Se continuara igualmente.")

    if cantidad_solicitada > 1000:
        margen_promedio = promediar(
            acumulador_1,
            contador_1,
            contexto=f"producto '{articulo_nombre}'",
            avisar=True,
        )
    elif cantidad_solicitada > 500:
        margen_promedio = promediar(
            acumulador_2,
            contador_2,
            contexto=f"producto '{articulo_nombre}'",
            avisar=True,
        )
    else:
        margen_promedio = promediar(
            acumulador_3,
            contador_3,
            contexto=f"producto '{articulo_nombre}'",
            avisar=True,
        )

    precio_final_unitario = round(precio_proveedor_nuevo * (1 + (margen_promedio / 100)), 2)
    total_cotizacion = round(precio_final_unitario * cantidad_solicitada, 2)

    print("\n" + "-" * 45)
    print(f"Producto: {articulo_nombre}")
    print(f"Cantidad: {cantidad_solicitada}")
    print(f"Margen promedio aplicado: {margen_promedio:.2f}%")
    print(f"Precio Unitario Cliente (S/.): {precio_final_unitario:.2f}")
    print(f"Total de la Cotizacion (S/.): {total_cotizacion:.2f}")
    print("-" * 45)

print("\n" + "="*45)
print(f"📊 Margen Promedio (> 1000): {promediar(acumulador_1, contador_1):.2f}% ({contador_1} casos)")
print(f"📊 Margen Promedio (> 500):  {promediar(acumulador_2, contador_2):.2f}% ({contador_2} casos)")
print(f"📊 Margen Promedio (Resto):  {promediar(acumulador_3, contador_3):.2f}% ({contador_3} casos)")
print("="*45)

generar_cotizacion_rapida()