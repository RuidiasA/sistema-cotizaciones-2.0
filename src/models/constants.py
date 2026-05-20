DEFAULT_EXCEL_FOLDER = r"E:/COTIZACIONES 2026"

MACRO_CATEGORIAS = {
    "Prendas de Vestir y Textil": {
        "global_exclude": ["altamura", "llavero", "disfraz", "tenerse", "tomatodo", "depsa"],
        "subcategorias": {
            "camisas y blusas": [
                {
                    "tags": ["camisa", "camisas", "blusa", "blusas"],
                    "exclude": []
                }
            ],
            "casacas, chamarras y abrigos": [
                {
                    "tags": ["casaca", "casacas", "chamarra", "chamarras", "jacket", "jackets", "chaqueta", "chaquetas", "cortavientos", "casaca cortavientos", "rompevientos", "parka", "parkas", "abrigo", "abrigos", "sobretodo", "sobretodos", "gabardina", "gabardinas", "prendas de invierno"],
                    "exclude": ["cuero"]
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
                },
                {
                    "tags": ["vincha", "vinchas", "viceras", "visera"],
                    "exclude": []
                }
            ],
            "mamelucos y overoles": [
                {
                    "tags": ["overall", "bailarina", "mameluco", "mamelucos", "overol", "overoles", "enterizo", "enterizos"],
                    "exclude": ["animadoras"]
                }
            ],
            "mandiles y delantales": [
                {
                    "tags": ["mandil", "mandiles", "delantal", "delantales", "tablier", "tabliers"],
                    "exclude": []
                }
            ],
            "pantalones, shorts y bermudas": [
                {
                    "tags": ["pantalon", "pantalones", "pantalon drill", "pantalon jean", "jean", "jeans", "denim", "short", "shorts", "bermuda", "bermudas"],
                    "exclude": ["bull", "bulk"]
                }
            ],
            "poleras, buzos y sudaderas": [
                {
                    "tags": ["polera", "poleras", "sudadera", "sudaderas", "hoodie", "hoodies", "buzo", "buzos"],
                    "exclude": []
                }
            ],
            "polos y camisetas": [
                {
                    "tags": ["polo", "polos", "polo camisero", "polos publicitarios", "remera", "remeras", "t-shirt", "t-shirts", "camiseta", "camisetas", "camiseta deportiva", "camisetas deportivas"],
                    "exclude": ["manga larga", "costoen", "uniforme"]
                }
            ]
        }
    },
    "Bolsos y Equipaje": {
        "global_exclude": ["audifono", "cargador", "farmage", "juego", "lapicero", "libreta", "linterna", "llavero", "pergamino", "plaquita", "resaltador", "usb"],
        "subcategorias": {
            "bolsos, canguros y maletines": [
                {
                    "tags": ["bolso", "bolsos", "bandolera", "bandoleras", "canguro", "canguros", "riñonera", "riñoneras", "koala", "koalas", "maletin", "maletines", "chimpunera", "chimpuneras", "portacalzado", "portacalzados"],
                    "exclude": ["colgador"]
                }
            ],
            "mochilas y morrales": [
                {
                    "tags": ["mochila", "mochilas", "backpack", "backpacks", "morral de espalda", "morral", "morrales"],
                    "exclude": ["infantil", "escolar"]
                }
            ],
            "estuches, cartucheras y neceseres": [
                {
                    "tags": ["cartuchera", "cartucheras", "estuche", "estuches", "esctuche", "esctuche" "portautiles", "neceser", "neceseres", "bolso de aseo", "organizador", "organizadores"],
                    "exclude": ["herramientas", "pergamino", "tarjeta", "calculadora", "claculadora", "cajita", "pisco", "power"]
                }
            ]
        }
    },
    "Empaques y Packaging": {
        "global_exclude": [],
        "subcategorias": {
            "bolsas y packaging": [
                {
                    "tags": ["bolsa", "bolsas", "bolsa ecologica", "bolsa tocuyo", "bolsas ecologicas", "bolsa de tela", "tote", "totes", "notex"],
                    "exclude": ["plastico", "basura", "aseo", "celofan", "papel", "regalo"]
                }
            ],
            "cajas y empaques": [
                {
                    "tags": ["caja", "cajas", "empaque", "empaques", "packaging"],
                    "exclude": ["fuerte", "herramientas", "taco"]
                }
            ]
        }
    },
    "Artículos de Oficina y Escritorio": {
        "global_exclude": [],
        "subcategorias": {
            "agendas y planificadores": [
                {
                    "tags": ["agenda", "agendas", "planificador", "planificadores", "diario", "diarios"],
                    "exclude": ["elegante", "elegant"]
                }
            ],
            "credenciales y displays": [
                {
                    "tags": ["fotocheck", "fotochecks", "identificador", "identificadores", "porta nombre", "porta nombres", "porta carnet", "porta carnets", "porta credencial", "porta credenciales", "tarjeta personal", "tarjetas personales", "porta flyer", "porta flyers", "porta afiche", "marco foto", "marcos foto", "porta foto", "porta fotos", "portaretrato", "porta retrato", "marco"],
                    "exclude": ["credito", "debito"]
                }
            ],
            "cuadernos y libretas": [
                {
                    "tags": ["cuaderno", "cuadernos", "libreta", "libretas", "journal", "journals", "notepad", "notepads", "block", "blocks", "bloc de notas", "taco de notas", "cuadernillo", "cuadernillos", "anillado", "anillados"],
                    "exclude": ["calculadora", "notebook", "claculadora", "separador", "taco"]
                }
            ],
            "escritorio y organizacion": [
                {
                    "tags": ["mouse pad", "mousepad", "alfombrilla", "caledndario", "alfombrillas", "tapete de escritorio", "porta celular", "soporte celular", "tarjetero", "tarjeteros", "organizador", "organizadores", "porta lapiz", "portaboligrafo", "porta documentos", "portadocumentos", "marco foto", "marcos foto", "portalapicero"],
                    "exclude": []
                }
            ],
            "lapiceros y escritura": [
                {
                    "tags": ["lapicero", "lapiceros", "lapicero plastico", "boligrafo", "boligrafos", "pluma", "plumas", "esfero", "esferos"],
                    "exclude": ["calculadora", "repuesto", "tinta", "ayudante", "claculadora", "calendario", "cinta", "clip", "compina"]
                },
                {
                    "tags": ["resaltador", "resaltadores", "plumon", "plumones", "marcador", "marcadores", "marcadores de texto"],
                    "exclude": ["pizarra", "wincha", "derby", "lisboa", "thunderbird"]
                }
            ]
        }
    },
    "Artículos de Hogar y Cocina": {
        "global_exclude": ["rotulos", "costo", "caracteristica", "opcion", "set", "llavero", "sport", "rjarro", "usb"],
        "subcategorias": {
            "textiles de hogar y limpieza": [
                {
                    "tags": ["toalla", "toallas", "toallon", "toallones", "toalla de mano", "toalla de baño", "paño", "paños", "paño microfibra", "paños microfibra", "mopa", "almohada", "almohadas", "almohada de viaje", "cojin", "cojines"],
                    "exclude": ["papel", "lentes"]
                }
            ],
            "utensilios y cocina": [
                {
                    "tags": ["cuchara", "cucharas", "cubierto", "cubiertos", "utensilio", "utensilios", "cafetera", "cafeteras", "prensa francesa", "moke", "mokes", "jarro"],
                    "exclude": ["gorro"]
                }
            ],
            "tomatodos y botellas": [
                {
                    "tags": ["tomatodo", "tomatodos", "botella", "botellas", "caramañola", "caramañolas", "shaker", "shakers", "termo", "termos", "thermo"],
                    "exclude": ["vino", "licor", "engrampador"]
                }
            ],
            "vasos, tazas y mugs": [
                {
                    "tags": ["vaso", "vasos", "vaso termico", "vasos termicos", "taza", "tazas", "mug", "mugs", "pocillo", "pocillos"],
                    "exclude": []
                }
            ]
        }
    },
    "Tecnología y Gadgets": {
        "global_exclude": [],
        "subcategorias": {
            "tecnologia y gadgets": [
                {
                    "tags": ["usb", "memoria usb", "memorias usb", "power bank", "linterna", "puntero laser", "punteros laser", "parlante", "parlantes", "audifono", "audifonos", "cargador", "cargadores", "adaptador", "adaptadores"],
                    "exclude": ["lpaicero", "pulsera", "tarjeta"]
                }
            ],
            "relojes": [
                {
                    "tags": ["reloj", "relojes", "reloj de pared", "reloj digital", "reloj promocional"],
                    "exclude": ["radio", "clip"]
                }
            ]
        }
    },
    "Merchandising y Promocionales": {
        "global_exclude": ["audifono", "camara", "gorro publicitario", "lapicero", "libreta", "polo", "taza"],
        "subcategorias": {
            "llaveros": [
                {
                    "tags": ["llavero", "llaveros", "keychain", "keychains"],
                    "exclude": ["pastillero"]
                }
            ],
            "pines y prendedores": [
                {
                    "tags": ["pin", "pines", "prendedor", "prendedores", "insignia", "insignias", "broche", "broches", "boton", "botones", "botones publicitarios"],
                    "exclude": ["tapasol", "pulsera"]
                }
            ],
            "placas y reconocimientos": [
                {
                    "tags": ["placa", "placas", "placa grabada", "reconocimiento", "reconocimientos", "plaquita"],
                    "exclude": ["auto", "vehiculo", "tarjeta"]
                }
            ],
            "stickers y adhesivos": [
                {
                    "tags": ["sticker", "stickers", "calcomania", "calcomanias", "adhesivo", "adhesivos", "etiqueta", "etiquetas"],
                    "exclude": ["frasco", "note", "calendario"]
                }
            ],
            "trofeos y medallas": [
                {
                    "tags": ["trofeo", "trofeos", "copa", "copas", "galardon", "galardones", "medalla", "medallas", "presea", "preseas", "condecoracion", "condecoraciones", "premio", "premios"],
                    "exclude": ["vino", "pisco", "agua", "vidrio", "cristal", "deportivo", "oro", "plata"]
                }
            ]
        }
    }
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
