# ManhwaSS — Extensión de Mihon/Aniyomi para manhwass.lat

Extensión de fuente de manga en español para [Mihon](https://github.com/mihonapp/mihon), [Aniyomi](https://github.com/aniyomiorg/aniyomi) y forks compatibles (Komikku, TachiyomiSY...), construida con el mismo sistema de build que [keiyoushi/extensions-source](https://github.com/keiyoushi/extensions-source) (licencia Apache 2.0; el sistema de build, `core` y utilidades provienen de ese repositorio).

**Sitio fuente:** https://manhwass.lat — plataforma Next.js (misma base que ManhwaShot), catálogo mixto con contenido +18 (la fuente se declara `ContentWarning.MIXED`).

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

GitHub Actions compila la extensión en cada push a `main` y publica el resultado en la branch `repo` (`index.min.json`, `index.json`, `index.pb`, `repo.json`, APK y JAR). El APK también queda como artefacto del workflow.

Compilación manual:

```bash
./gradlew :src:es:manhwass:assembleRelease
# salida: src/es/manhwass/build/outputs/apk/release/tachiyomi-es.manhwass-v1.6.1.apk
```

Requiere JDK 17+ (CI usa 25) y el SDK de Android (compileSdk 37).

## Estructura

```
src/es/manhwass/    # la fuente (ManhwaSS.kt, Dto.kt, Filters.kt)
core/               # librería compartida de keiyoushi (network, utils, KeiSource)
compiler/           # procesador KSP que genera el entrypoint de la extensión
lint-rules/         # reglas de lint
gradle/build-logic/ # plugins de build (kei.plugins.extension)
.github/            # workflow de CI y generación del índice del repositorio
```

## Detalles técnicos

- La web es una SPA Next.js: los listados y la página de serie se parsean del HTML SSR con Jsoup; el lector del capítulo se obtiene del payload RSC (`extractNextJs<ReaderDto>`), que incluye la lista completa de imágenes y el flag de bloqueo VIP.
- Fechas exactas de capítulos desde el payload (`dates`), formato relativo del SSR solo como respaldo visual.
- Filtros: tipo (+18/BL/Shoujo/Manga), estado y géneros (se obtienen en vivo de `/explorar/`).
- Búsqueda vía `/explorar/?q=`; popular = ranking histórico `/ranking/`; últimas = `/ultimas-actualizaciones/` (paginadas).
- Búsqueda por URL: pega un enlace `https://manhwass.lat/manga/<slug>/` en el buscador de la fuente.

## Créditos y licencia

- Sistema de build, `core`, `compiler` y `lint-rules`: [keiyoushi/extensions-source](https://github.com/keiyoushi/extensions-source) (Apache License 2.0). La fuente está adaptada de su extensión de ManhwaShot, que usa la misma plataforma web.
- Este repositorio: mismo licenciamiento Apache 2.0.
