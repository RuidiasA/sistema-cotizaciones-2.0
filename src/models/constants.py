DEFAULT_EXCEL_FOLDER = r"E:/COTIZACIONES 2026"

VARIACIONES_POR_CATEGORIA = {
    "agendas y planificadores": [
        {
            "tags": ["agenda", "agendas", "planificador", "planificadores", "diario", "diarios"],
            "exclude": []
        }
    ],
    "bolsas y packaging": [
        {
            "tags": ["bolsa", "bolsas", "bolsa ecologica", "bolsa tocuyo", "bolsas ecologicas", "bolsa de tela", "tote", "totes", "notex"],
            "exclude": ["plastico", "basura", "aseo", "celofan", "papel", "regalo"]
        }
    ],
    "bolsos, canguros y maletines": [
        {
            "tags": ["bolso", "bolsos", "bandolera", "bandoleras", "canguro", "canguros", "riñonera", "riñoneras", "koala", "koalas", "maletin", "maletines", "chimpunera", "chimpuneras", "portacalzado", "portacalzados"],
            "exclude": ["libreta", "resaltador"]
        }
    ],
    "cajas y empaques": [
        {
            "tags": ["caja", "cajas", "empaque", "empaques", "packaging"],
            "exclude": ["fuerte", "herramientas", "parlante", "taco", "usb"]
        }
    ],
    "camisas y blusas": [
        {
            "tags": ["camisa", "camisas", "blusa", "blusas"],
            "exclude": []
        }
    ],
    "casacas, chamarras y abrigos": [
        {
            "tags": ["casaca", "casacas", "chamarra", "chamarras", "jacket", "jackets", "chaqueta", "chaquetas", "cortavientos", "casaca cortavientos", "rompevientos", "parka", "parkas", "abrigo", "abrigos", "sobretodo", "sobretodos", "gabardina", "gabardinas", "prendas de invierno"],
            "exclude": ["cuero", "pantalon", "disfraz"]
        }
    ],
    "chalecos": [
        {
            "tags": ["chaleco", "chalecos", "gilet", "gilets", "chalecos tacticos", "chaleco corporativo", "chaleco corporativo acolchado", "chalecos polar", "chalecos promocional"],
            "exclude": ["salvavidas"]
        }
    ],
    "chalinas y accesorios de frio": [
        {
            "tags": ["chalina", "chalinas", "bufanda", "bufandas", "cuello polar"],
            "exclude": []
        }
    ],
    "credenciales y displays": [
        {
            "tags": ["fotocheck", "fotochecks", "identificador", "identificadores", "porta nombre", "porta nombres", "porta carnet", "porta carnets", "porta credencial", "porta credenciales", "tarjeta personal", "tarjetas personales", "porta flyer", "porta flyers", "porta afiche", "marco foto", "marcos foto", "porta foto", "porta fotos"],
            "exclude": ["credito", "debito", "reloj"]
        }
    ],
    "cuadernos y libretas": [
        {
            "tags": ["cuaderno", "cuadernos", "libreta", "libretas", "journal", "journals", "notepad", "notepads", "block", "blocks", "bloc de notas", "taco de notas", "cuadernillo", "cuadernillos", "anillado", "anillados"],
            "exclude": ["calculadora", "notebook"]
        }
    ],
    "escritorio y organizacion": [
        {
            "tags": ["mouse pad", "mousepad", "alfombrilla", "caledndario", "alfombrillas", "tapete de escritorio", "porta celular", "soporte celular", "tarjetero", "tarjeteros", "organizador", "organizadores", "porta lapiz", "portaboligrafo", "porta documentos", "portadocumentos", "marco foto", "marcos foto"],
            "exclude": ["reloj", "llavero"]
        }
    ],
    "estuches, cartucheras y neceseres": [
        {
            "tags": ["cartuchera", "cartucheras", "estuche", "estuches", "portautiles", "neceser", "neceseres", "bolso de aseo", "organizador", "organizadores"],
            "exclude": ["herramientas", "lapicero" "pergamino", "tarjeta", "thermo" ,"usb"]
        }
    ],
    "gorras, gorros y viseras": [
        {
            "tags": ["gorro", "gorros", "gorra", "gorras", "beanie", "beanies", "gorro corporativo", "gorro trucker", "gorro carbonero", "gorros drill", "gorros publicitarios", "gorros safari", "gorros tapanuca", "chullo", "chullos"],
            "exclude": ["natacion", "baño"]
        },
        {
            "tags": ["visera", "viseras", "parasol", "parasoles", "viseras deportivas", "visera promocional"],
            "exclude": ["auto", "coche"]
        },
        {
            "tags": ["pasamontaña", "pasamontañas", "balaclava"],
            "exclude": []
        }
    ],
    "lapiceros y escritura": [
        {
            "tags": ["lapicero", "lapiceros", "lapicero plastico", "boligrafo", "boligrafos", "pluma", "plumas", "esfero", "esferos"],
            "exclude": ["calculadora", "repuesto", "tinta"]
        },
        {
            "tags": ["resaltador", "resaltadores", "plumon", "plumones", "marcador", "marcadores", "marcadores de texto"],
            "exclude": ["pizarra", "reloj", "wincha"]
        }
    ],
    "llaveros": [
        {
            "tags": ["llavero", "llaveros", "keychain", "keychains"],
            "exclude": ["usb"]
        }
    ],
    "mamelucos y overoles": [
        {
            "tags": ["mameluco", "mamelucos", "overol", "overoles", "enterizo", "enterizos"],
            "exclude": []
        }
    ],
    "mandiles y delantales": [
        {
            "tags": ["mandil", "mandiles", "delantal", "delantales", "tablier", "tabliers"],
            "exclude": []
        }
    ],
    "mochilas y morrales": [
        {
            "tags": ["mochila", "mochilas", "backpack", "backpacks", "morral de espalda", "morral", "morrales"],
            "exclude": ["infantil", "escolar"]
        }
    ],
    "pantalones, shorts y bermudas": [
        {
            "tags": ["pantalon", "pantalones", "pantalon drill", "pantalon jean", "jean", "jeans", "denim", "short", "shorts", "bermuda", "bermudas"],
            "exclude": ["camisa", "polera", "sudadera"]
        }
    ],
    "pines y prendedores": [
        {
            "tags": ["pin", "pines", "prendedor", "prendedores", "insignia", "insignias", "broche", "broches", "boton", "botones", "botones publicitarios"],
            "exclude": ["audifono", "gorro", "lapicero", "tapasol"]
        }
    ],
    "placas y reconocimientos": [
        {
            "tags": ["placa", "placas", "placa grabada", "reconocimiento", "reconocimientos", "plaquita"],
            "exclude": ["auto", "vehiculo", "tarjetero"]
        }
    ],
    "poleras, buzos y sudaderas": [
        {
            "tags": ["polera", "poleras", "sudadera", "sudaderas", "hoodie", "hoodies", "buzo", "buzos"],
            "exclude": ["pantalon", "short"]
        }
    ],
    "polos y camisetas": [
        {
            "tags": ["polo", "polos", "polo camisero", "polos publicitarios", "remera", "remeras", "t-shirt", "t-shirts", "camiseta", "camisetas", "camiseta deportiva", "camisetas deportivas"],
            "exclude": ["manga larga", "tomatodo"]
        }
    ],
    "relojes": [
        {
            "tags": ["reloj", "relojes", "reloj de pared", "reloj digital", "reloj promocional"],
            "exclude": ["radio", "portaretrato", "porta retrato", "clip"]
        }
    ],
    "stickers y adhesivos": [
        {
            "tags": ["sticker", "stickers", "calcomania", "calcomanias", "adhesivo", "adhesivos", "etiqueta", "etiquetas"],
            "exclude": ["frasco", "libreta", "plaquita", "tarjetero", "vinil"]
        }
    ],
    "tecnologia y gadgets": [
        {
            "tags": ["usb", "memoria usb", "memorias usb", "power bank", "linterna", "puntero laser", "punteros laser", "parlante", "parlantes", "audifono", "audifonos", "cargador", "cargadores", "adaptador", "adaptadores"],
            "exclude": ["lapicero", "llavero" "lpaicero"]
        }
    ],
    "textiles de hogar y limpieza": [
        {
            "tags": ["toalla", "toallas", "toallon", "toallones", "toalla de mano", "toalla de baño", "paño", "paños", "paño microfibra", "paños microfibra", "mopa", "almohada", "almohadas", "almohada de viaje", "cojin", "cojines"],
            "exclude": ["papel", "lentes", "gorro"]
        }
    ],
    "tomatodos y botellas": [
        {
            "tags": ["tomatodo", "tomatodos", "botella", "botellas", "caramañola", "caramañolas", "shaker", "shakers", "termo", "termos", "thermo"],
            "exclude": ["vino", "licor", "llavero", "opcion"]
        }
    ],
    "trofeos y medallas": [
        {
            "tags": ["trofeo", "trofeos", "copa", "copas", "galardon", "galardones", "medalla", "medallas", "presea", "preseas", "condecoracion", "condecoraciones", "premio", "premios"],
            "exclude": ["vino", "agua", "vidrio", "cristal", "deportivo", "oro", "plata"]
        }
    ],
    "utensilios y cocina": [
        {
            "tags": ["cuchara", "cucharas", "cubierto", "cubiertos", "utensilio", "utensilios", "cafetera", "cafeteras", "prensa francesa", "moke", "mokes"],
            "exclude": []
        }
    ],
    "vasos, tazas y mugs": [
        {
            "tags": ["vaso", "vasos", "vaso termico", "vasos termicos", "taza", "tazas", "mug", "mugs", "pocillo", "pocillos"],
            "exclude": ["trofeo", "premios"]
        }
    ],
    "vinchas": [
        {
            "tags": ["vincha", "vinchas", "viceras", "visera"],
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
