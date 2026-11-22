# Extensiones de Mihon/Aniyomi — fuentes en español

Repositorio personal de extensiones de fuente de manga en español para [Mihon](https://github.com/mihonapp/mihon), [Aniyomi](https://github.com/aniyomiorg/aniyomi) y forks compatibles (Komikku, TachiyomiSY...), construido con el mismo sistema de build que [keiyoushi/extensions-source](https://github.com/keiyoushi/extensions-source) (licencia Apache 2.0; el sistema de build, `core` y utilidades provienen de ese repositorio).

**Fuentes incluidas (todas en español):**

| Extensión | Sitio | Contenido |
|---|---|---|
| ManhwaSS | https://manhwass.lat | MIXED (+18 entre el catálogo) |
| ManhwaWeb | https://manhwaweb.com | MIXED |
| LeerCapitulo | https://www.leercapitulo.co | SAFE |
| Olympus Scanlation | https://olympusxyz.com | SAFE |
| Ikigai Mangas (visor) | https://visorikigai.gettocaboca.com | MIXED |
| ZonaTMO.org | https://zonatmo.org | MIXED |
| LectorTmo.online | https://lectortmo.online | MIXED |
| LectorTmo.vip | https://lectortmo.vip | MIXED |
| Aedex | https://aedexnox.com | NSFW |

> Nota Ikigai: los dominios `visualikigai.cmpunjabrashancard.pk` y `visualikigai.com` redirigen actualmente a `visor.ikigaiweb.lat`, que está caído (NXDOMAIN). El visor vivo es `visorikigai.gettocaboca.com` (el mismo que usa keiyoushi). Estos sitios rotan de dominio constantemente: la URL se puede cambiar desde los ajustes de la propia extensión (baseUrl personalizable) y la fuente incluye detección de dominio vigente vía `ikigaimangas.com`.

> Nota ZonaTMO.org: la fuente de keiyoushi estaba rota — la biblioteca AJAX del sitio dejó de responder JSON (`{html: ...}`) y ahora devuelve la página HTML completa, con lo que búsqueda y populares crasheaban. Aquí se corrige con un parseo tolerante a ambos formatos; el resto de flujos (detalle, capítulos, lector, filtros) se validó en vivo contra el sitio.

## Instalación

1. En Mihon/Aniyomi: **Ajustes → Extensiones → Añadir repositorio** (o en "Buscar → Extensiones", icono de repositorios).
2. Añade esta URL:

   ```
   https://raw.githubusercontent.com/Lenoxlkz/manhwss-ext/repo
   ```

3. Instala la extensión **ManhwaSS**. Al ser un repositorio externo, la app pedirá confirmarla como de confianza ("trust") la primera vez.
4. Si la fuente no aparece, activa **Mostrar fuentes +18/NSFW** en los ajustes de la app (el catálogo del sitio mezcla contenido adulto).

### Actualizaciones de la extensión

Los APK se firman siempre con la misma clave (keystore secreto del repo), por lo que la app detecta las actualizaciones sin desinstalar nada.

## Compilación

GitHub Actions compila todas las fuentes en cada push a `main` y publica el resultado en la branch `repo` (`index.min.json`, `index.json`, `index.pb`, `repo.json`, APK y JAR). Los APK también quedan como artefactos del workflow.

Compilación manual (una fuente concreta):

```bash
./gradlew :src:es:manhwass:assembleRelease
# salida: src/es/manhwass/build/outputs/apk/release/tachiyomi-es.manhwass-v1.6.1.apk
```

Requiere JDK 17+ (CI usa 25) y el SDK de Android (compileSdk 37).

## Estructura

```
src/es/manhwass/          # ManhwaSS (manhwass.lat — SPA Next.js, código propio)
src/es/manhwaweb/         # ManhwaWeb (API JSON en api.manhwaweb.com)
src/es/leercapitulo/      # LeerCapitulo (HTML SSR con selectores lc-*)
src/es/olympusscanlation/ # Olympus Scanlation (API JSON en olympusxyz.com/api)
src/es/ikigaimangas/      # Ikigai Mangas visor (Qwik/HTML, baseUrl personalizable)
src/es/zonatmoorg/        # ZonaTMO.org (Laravel custom; fix del parseo JSON→HTML de la biblioteca)
src/es/lectortmoonline/   # LectorTmo.online (API JSON /api/mangas + /api/chapters)
src/es/lectortmovip/      # LectorTmo.vip (WordPress admin-ajax con nonce MnArchive)
src/es/aedex/             # Aedex (multisrc Catharsis: API firmada, lector XOR+descramble)
lib-multisrc/catharsis/   # base del multisrc Catharsis (dependencia de aedex)
lib/cronet, lib/cronetruntime/ # stack de red Chromium que usan las fuentes Catharsis
core/                     # librería compartida de keiyoushi (network, utils, KeiSource)
compiler/                 # procesador KSP que genera el entrypoint de la extensión
lint-rules/               # reglas de lint
gradle/build-logic/       # plugins de build (kei.plugins.extension)
.github/                  # workflow de CI y generación del índice del repositorio
```

## Detalles técnicos

- **ManhwaSS**: SPA Next.js — listados y ficha parseados del HTML SSR con Jsoup; lector desde el payload RSC (`extractNextJs`), con fechas exactas y capítulos VIP bloqueados (preferencia para mostrarlos). Búsqueda por URL soportada.
- **ManhwaWeb**: API JSON (`api.manhwaweb.com`) con filtros completos (tipo, demografía, estado, erótico, géneros, orden); capítulos por "versiones" (con scanlators) y búsqueda por URL.
- **LeerCapitulo**: HTML SSR con rate-limit (1 req/3s); filtros combinables con búsqueda por texto; lecturas con imágenes `data-src` (CDN ofuscado).
- **Olympus Scanlation**: API JSON con caché en memoria de la lista de series (1 h), rankings paginados, slug map persistido en preferencias; baseUrl personalizable y detección de dominio via `olympus.pages.dev`.
- **Ikigai Mangas**: sitio Qwik — búsqueda por texto vía protocolo Qwik (WebView captura `qfunc`), paginación de capítulos en paralelo; baseUrl personalizable + detección de dominio via `ikigaimangas.com`.
- **ZonaTMO.org**: plataforma Laravel custom — biblioteca vía AJAX (`/biblioteca`), últimas subidas `/ultimas-subidas`, detalle `zt-hd__*`, capítulos por `view_uploads` y lector `#reader-wrap img.reader-image`. Corregido el parseo de la biblioteca (JSON→HTML).
- **LectorTmo.online**: API JSON (`/api/mangas`, `/api/chapters`, `/api/genres` con filtrado de "géneros basura"); el CDN rechaza referer del sitio (headers sin Referer).
- **LectorTmo.vip**: WordPress — listados por `admin-ajax.php` (`mn_archive_filter`) con nonce extraído de `/manga/` (con re-intento si expira, código 403); capítulos `#mn-chapters-list` y lector `main#reader-strip img`.
- **Aedex**: multisrc Catharsis (`/api/backend`, headers `System: aedex` + `X-FK-Sistema`) — lector gratis con pase por IP (`ax_rp`), countdown WebSocket con firma ECDSA P-256, imágenes XOR-mascadas y descramble 8x8. Cadena completa: catharsis multisrc + lib/cronet + cronetruntime.
- Las 4 fuentes anteriores (ManhwaWeb, LeerCapitulo, Olympus, Ikigai) conservan los IDs de fuente de keiyoushi para migrar favoritos sin perder nada; no conviene tener instaladas a la vez ambas versiones de la misma fuente. Las de esta tanda (ZonaTMO.org, LectorTmo.*, Aedex) usan nombres propios sin sufijo "(unoriginal)", con IDs independientes.

## Créditos y licencia

- Sistema de build, `core`, `compiler` y `lint-rules`: [keiyoushi/extensions-source](https://github.com/keiyoushi/extensions-source) (Apache License 2.0). La fuente está adaptada de su extensión de ManhwaShot, que usa la misma plataforma web.
- Este repositorio: mismo licenciamiento Apache 2.0.
