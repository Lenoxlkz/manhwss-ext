import io.github.keiyoushi.gradle.api.ContentWarning

plugins {
    alias(kei.plugins.extension)
}

keiyoushi {
    pkgName = "es.lectortmoonline.lkz"
    name = "LectorTmo.online"
    versionCode = 1
    contentWarning = ContentWarning.MIXED
    libVersion = "1.6"

    source {
        lang = "es"
        baseUrl = "https://lectortmo.online"
    }

    deeplink {
        path("/..*")
    }
}
