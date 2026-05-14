DEFAULT_EXCEL_FOLDER = r"C:\Users\Karina\Downloads\Cotizacion-textil"

VARIACIONES_POR_CATEGORIA = {
    "prendas de cabeza": [
        {
            "tags": ["gorro", "gorros", "gorra", "gorras", "beanie", "beanies", "gorro corporativo", "gorro trucker", "gorro carbonero", "gorros drill", "gorros publicitarios", "gorros safari", "gorros tapanuca", "chullo", "chullos", ],
            "exclude": ["natacion", "baño"]
        },                                                                              {
            "tags": ["viera promocional"]
        },                                                                   
        {
            "tags": ["visera", "viseras", "parasol", "parasoles", "viseras deportivas"],
            "exclude": ["auto", "coche"]
        },
        {
            "tags": ["pasamontaña", "pasamontañas", "balaclava"],
            "exclude": []
        }
    ],
    "ropa y abrigo": [
        {
            "tags": ["casaca", "casacas", "chamarra", "chamarras", "jacket", "jackets", "chaqueta", "chaquetas", "cortavientos", "cascaca polar", "casaca corportativa", "rompevientos"],
            "exclude": ["cuero"]
        },
        {
            "tags": ["parka", "parkas", "abrigo", "abrigos", "sobretodo", "sobretodos", "gabardina", "gabardinas", "prendas de invierno"],
            "exclude": []
        },
        {
            "tags": ["polera", "poleras", "sudadera", "sudaderas", "hoodie", "hoodies", "buzo", "buzos"],
            "exclude": ["pantalon", "short"]
        },
        {
            "tags": ["polo", "polos", "polo cuello camisero", "polos prublicitarios", "remera", "remeras", "t-shirt", "t-shirts", "camiseta", "camisetas", "camiseta deportiva", "camisetas deportivas"],
            "exclude": ["manga larga"]
        },
        {
            "tags": ["camisa", "camisas", "blusa", "blusas"], 
            "exclude": [""]
        },
        {
            "tags": ["chaleco", "chalecos", "gilet", "gilets", "chalecos tacticos", "chaleco corporativo - acolchado", "chaleco corporativo", "chalecos polar", "chalecos promocional"],
            "exclude": ["salvavidas"]
        },
        {
            "tags": ["pantalon", "pantalones", "pantalon drill", "pantalon jean", "jean", "jeans", "denim", "short", "shorts", "bermuda", "bermudas"],
            "exclude": []
        },
        {
            "tags": ["blazer", "blazers", "saco", "sacos de vestir"],
            "exclude": ["saco de dormir", "saco de arena"]
        },
        {
            "tags": ["chalina", "chalinas"],
            "exclude": []
        },
        {
            "tags": ["mameluco", "mameluco", "overol", "overoles", "enterizo", "enterizos"],
        },
        {
            "tags": ["mangas", "manga", "manga larga", "mangas largas"],
        }
    ],
    "textiles y hogar": [
        {
            "tags": ["toalla", "toallas", "toallon", "toallones", "toalla de mano", "toalla de baño"],
            "exclude": ["papel"]
        },
        {
            "tags": ["paño", "paños", "paño microfibra", "paños microfibra", "mopa"],
            "exclude": ["lentes"]
        },
        {
            "tags": ["almohada", "almohadas", "almohada de viaje", "cojin", "cojines"],
            "exclude": []
        },
        {
            "tags": ["mandil", "mandiles", "delantal", "delantales", "tablier", "tabliers"],
            "exclude": []
        }
    ],
    "bolsos y transporte": [
        {
            "tags": ["mochila", "mochilas", "backpack", "backpacks", "morral de espalda"],
            "exclude": ["infantil", "escolar"]
        },
        {
            "tags": ["morral", "morrales", "bandolera", "bandoleras", "bolso cruzado", "bolsos cruzados"],
            "exclude": []
        },
        {
            "tags": ["canguro", "canguros", "riñonera", "riñoneras", "koala", "koalas"],
            "exclude": []
        },
        {
            "tags": ["bolsa", "bolsas", "bolso", "bolsos", "bolsa ecologica", "bolsas ecologicas", "tote", "totes", "notex", "bolsa de tela"],
            "exclude": ["plastico", "basura", "aseo", "celofan", "papel", "regalo"]
        },
        {
            "tags": ["maletin", "maletines", "chimpunera", "chimpuneras", "portacalzado", "portacalzados"],
            "exclude": []
        }
    ],
    "papeleria y oficina": [
        {
            "tags": ["cuaderno", "cuadernos", "libreta", "libretas", "journal", "journals", "notepad", "notepads", "block", "blocks", "bloc de notas", "taco de notas", "cuadernillo", "cuadernillos", "anillado", "anillados"],
            "exclude": []
        },
        {
            "tags": ["agenda", "agendas", "planificador", "planificadores", "diario", "diarios"],
            "exclude": []
        },
        {
            "tags": ["hoja", "hojas", "folio", "folios", "papel", "papeles", "resma"],
            "exclude": ["higienico", "toalla"]
        },
        {
            "tags": ["cartuchera", "cartucheras", "estuche", "estuches", "portautiles", "neceser", "neceseres", "bolso de aseo", "organizador", "organizadores"],
            "exclude": ["herramientas"]
        },
        {
            "tags": ["lapicero", "lapiceros", "boligrafo", "boligrafos", "pluma", "plumas", "esfero", "esferos"],
            "exclude": ["repuesto", "tinta"]
        },
        {
            "tags": ["resaltador", "resaltadores", "plumon", "plumones", "marcador", "marcadores", "marcadores de texto"],
            "exclude": ["pizarra"]
        },
        {
            "tags": ["tarjeta", "tarjetas", "tarjeta personal", "tarjetas personales", "business card", "business cards"],
            "exclude": ["credito", "debito"]
        },
        {
            "tags": ["fotocheck", "fotochecks", "identificador", "identificadores", "porta nombre", "identificadores rusticos"],
            "exclude": []
        }
    ],
    "accesorios y premiaciones": [
        {
            "tags": ["llavero", "llaveros", "keychain", "keychains"],
            "exclude": []
        },
        {
            "tags": ["pin", "pines", "prendedor", "prendedores", "insignia", "insignias", "broche", "broches"],
            "exclude": []
        },
        {
            "tags": ["trofeo", "trofeos", "copa", "copas", "galardon", "galardones", "medalla", "medallas", "presea", "preseas", "condecoracion", "condecoraciones"],
            "exclude": ["vino", "agua", "vidrio", "cristal"]
        },
        {
            "tags": ["vinchas"],
            "exclude": []
        },
        {
            "tags": ["placa", "placas", "placa grabada", "reconocimiento", "reconocimientos"],
            "exclude": ["auto", "vehiculo"]
        }
    ],
    "menaje y otros": [
        {
            "tags": ["tomatodo", "tomatodos", "botella", "botellas", "caramañola", "caramañolas", "shaker", "shakers"],
            "exclude": ["vino", "licor"]
        },
        {
            "tags": ["vaso", "vasos", "vaso termico", "vasos termicos", "taza", "tazas", "mug", "mugs", "pocillo", "pocillos"],
            "exclude": ["trofeo", "premios"]
        },
        {
            "tags": ["copa", "copas", "copa de vidrio", "copas de cristal"],
            "exclude": ["trofeo", "deportivo", "oro", "plata"]
        },
        {
            "tags": ["cafetera", "cafeteras", "prensa francesa", "moke", "mokes"],
            "exclude": []
        },
        {
            "tags": ["cuchara", "cucharas", "cubierto", "cubiertos", "utensilio", "utensilios"],
            "exclude": []
        },
        {
            "tags": ["sticker", "stickers", "calcomania", "calcomanias", "adhesivo", "adhesivos"],
            "exclude": []
        },
        {
            "tags": ["caja", "cajas", "empaque", "empaques", "packaging"],
            "exclude": ["fuerte", "herramientas"]
        },
        {
            "tags": ["mouse pad", "mousepad", "alfombrilla", "alfombrillas", "tapete de escritorio"],
            "exclude": []
        },
        {
            "tags": ["kit", "power bank", "manta", "pastillero", "alcancia"],
            "exclude": []
        }
    ]
}

HOJAS_EXCLUIDAS = [
    "criterios",
    "tallas",
    "cronograma",
    "datos",
    "deuda",
    "produccion",
    "proveedor",
    "proveedores",
    "costo de proyecto",
]
