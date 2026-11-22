package eu.kanade.tachiyomi.extension.es.lectortmovip

import kotlinx.serialization.Serializable

@Serializable
class ArchiveFilterDto(val data: ArchiveFilterDataDto)

@Serializable
class ArchiveFilterDataDto(val html: String)
