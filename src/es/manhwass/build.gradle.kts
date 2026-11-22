import io.github.keiyoushi.gradle.api.ContentWarning

plugins {
    alias(kei.plugins.extension)
}

keiyoushi {
    name = "ManhwaSS"
    versionCode = 1
    contentWarning = ContentWarning.MIXED
    libVersion = "1.6"

    source {
        lang = "es"
        baseUrl = "https://manhwass.lat"
    }

    deeplink {
        host("manhwass.lat")
        host("www.manhwass.lat")
        path("/manga/..*")
        path("/genero/..*")
        path("/explorar/.*")
    }
}
