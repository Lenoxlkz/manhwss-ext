import io.github.keiyoushi.gradle.api.ContentWarning

plugins {
    alias(kei.plugins.extension)
}

keiyoushi {
    pkgName = "es.manhwaweb.lkz"
    name = "ManhwaWeb"
    versionCode = 1
    contentWarning = ContentWarning.MIXED
    libVersion = "1.6"

    source {
        lang = "es"
        baseUrl = "https://manhwaweb.com"
    }

    deeplink {
        path("/manhwa/..*")
    }
}
